"""Main FastAPI application entry point.

Assembles routers, configures CORS, initializes the database tables,
seeds the default platform administrator and sample mentor on first run,
and provides system health check endpoints.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .config import get_settings
from .database import Base, SessionLocal, engine, get_db
from .models import User
from .routers import admin, auth, builder, projects
from .security import hash_password

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("project_builder")

settings = get_settings()


def _migrate_db_columns():
    """Adds missing columns to SQLite database if created prior to onboarding fields."""
    with engine.begin() as conn:
        try:
            result = conn.exec_driver_sql("PRAGMA table_info(users)")
            existing_cols = {row[1] for row in result.fetchall()}
            if existing_cols:
                if "college" not in existing_cols:
                    conn.exec_driver_sql("ALTER TABLE users ADD COLUMN college VARCHAR(160)")
                if "semester" not in existing_cols:
                    conn.exec_driver_sql("ALTER TABLE users ADD COLUMN semester VARCHAR(60)")
                if "has_completed_onboarding" not in existing_cols:
                    conn.exec_driver_sql("ALTER TABLE users ADD COLUMN has_completed_onboarding BOOLEAN DEFAULT 1")
        except Exception as e:
            logger.info(f"Database column migration info: {e}")


def _seed_initial_accounts():
    """Seeds the platform administrator and a sample faculty mentor account on first startup."""
    with SessionLocal() as db:
        # Seed Admin
        admin_user = db.query(User).filter(User.email == settings.admin_email).first()
        if not admin_user:
            logger.info(f"Seeding default administrator account: {settings.admin_email}")
            admin_user = User(
                email=settings.admin_email,
                full_name=settings.admin_name,
                password_hash=hash_password(settings.admin_password),
                role="admin",
                branch="cse",
                has_completed_onboarding=True,
                is_active=True,
            )
            db.add(admin_user)
        else:
            admin_user.has_completed_onboarding = True

        # Seed Sample Mentor
        sample_mentor_email = "mentor@projectbuilder.dev"
        mentor_user = db.query(User).filter(User.email == sample_mentor_email).first()
        if not mentor_user:
            logger.info(f"Seeding default mentor account: {sample_mentor_email}")
            mentor_user = User(
                email=sample_mentor_email,
                full_name="Prof. Sarah Jenkins (AI & Robotics Guide)",
                password_hash=hash_password("Mentor@12345"),
                role="mentor",
                branch="cse",
                has_completed_onboarding=True,
                is_active=True,
            )
            db.add(mentor_user)
        else:
            mentor_user.has_completed_onboarding = True

        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and initial users are seeded
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)
    _migrate_db_columns()
    _seed_initial_accounts()
    logger.info("Project Builder backend ready.")
    yield
    # Shutdown logic if needed
    logger.info("Project Builder backend shutting down.")


# Module-level database initialization to ensure tables and migrations exist even outside lifespan
Base.metadata.create_all(bind=engine)
_migrate_db_columns()


# REQUIREMENT 3: Public docs disabled (docs_url=None, redoc_url=None, openapi_url=None)
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Autonomous Final-Year Engineering Project Builder & Architecture Platform.",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(builder.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


# ── Internal Admin-Only API Documentation Routes (Requirement 3) ──────────────
def _verify_admin_jwt(request: Request, token: str | None = None, db: Session = Depends(get_db)) -> User:
    """Strictly authenticates that the requester has a valid Admin JWT token.

    Checks:
    1. Query parameter ?token=...
    2. Header Authorization: Bearer <token>
    3. Cookie access_token
    Returns 403 Forbidden for any unauthenticated or non-admin visitor.
    """
    raw_token = token
    if not raw_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            raw_token = auth_header[7:].strip()
    if not raw_token:
        raw_token = request.cookies.get("access_token")

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: API documentation is restricted to platform administrators.",
        )

    try:
        payload = jwt.decode(raw_token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Invalid or expired administrator session.",
        )

    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: API documentation is restricted to platform administrators.",
        )

    user = db.get(User, int(payload.get("sub", 0)))
    if not user or not user.is_active or user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Administrator account inactive or unauthorized.",
        )

    return user


@app.get("/openapi.json", include_in_schema=False)
def admin_openapi_json(request: Request, token: str | None = None, db: Session = Depends(get_db)):
    """Serves OpenAPI JSON schema strictly to authenticated administrators."""
    _verify_admin_jwt(request, token=token, db=db)
    return JSONResponse(
        get_openapi(
            title=f"{settings.app_name} - Admin API Specification",
            version=settings.version,
            description="Autonomous Final-Year Engineering Project Builder & Blueprint Generator Internal API.",
            routes=app.routes,
        )
    )


@app.get("/docs", include_in_schema=False)
def admin_swagger_ui(request: Request, token: str | None = None, db: Session = Depends(get_db)):
    """Serves Swagger UI documentation strictly to authenticated administrators."""
    _verify_admin_jwt(request, token=token, db=db)
    openapi_url = f"/openapi.json?token={token}" if token else "/openapi.json"
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=f"{settings.app_name} - Admin Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
def admin_redoc(request: Request, token: str | None = None, db: Session = Depends(get_db)):
    """Serves ReDoc documentation strictly to authenticated administrators."""
    _verify_admin_jwt(request, token=token, db=db)
    openapi_url = f"/openapi.json?token={token}" if token else "/openapi.json"
    return get_redoc_html(
        openapi_url=openapi_url,
        title=f"{settings.app_name} - Admin ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )


@app.get("/", tags=["health"])
def root():
    return {
        "app": settings.app_name,
        "version": settings.version,
        "environment": settings.env,
        "docs": "Restricted (Admin authentication required at /docs)",
        "status": "online",
    }


@app.get("/health", tags=["health"])
def health():
    return {
        "status": "healthy",
        "database": "connected",
        "llm_provider": settings.llm_provider,
        "storage": settings.storage_backend,
    }
