import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AuditLog, User
from ..schemas import (
    GoogleAuthIn,
    LoginIn,
    OnboardingIn,
    PasswordChange,
    ProfileUpdate,
    RegisterIn,
    TokenOut,
    UserOut,
)
from ..security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")

    name = payload.full_name or payload.email.split("@")[0].capitalize()
    has_onboarded = bool(payload.full_name and payload.branch)

    user = User(
        email=payload.email.lower(),
        full_name=name,
        password_hash=hash_password(payload.password),
        branch=payload.branch,
        role="student",
        has_completed_onboarding=has_onboarded,
        is_active=True,
    )
    db.add(user)
    db.flush()

    # Audit log
    db.add(AuditLog(user_id=user.id, action="user_registered", detail=f"Registered as student ({user.email})"))
    db.commit()
    db.refresh(user)

    token = create_access_token(user)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/google", response_model=TokenOut)
def google_auth(payload: GoogleAuthIn, db: Session = Depends(get_db)):
    """Single Sign-On with Google OAuth 2.0 (Step 1 Option 2)."""
    clean_email: str | None = None
    display_name = payload.name

    if payload.credential:
        try:
            # Google ID tokens are standard JWTs containing email, name, picture
            claims = jwt.decode(payload.credential, options={"verify_signature": False})
            if "email" in claims:
                clean_email = str(claims["email"]).lower().strip()
            if "name" in claims and not display_name:
                display_name = str(claims["name"]).strip()
        except Exception as e:
            logger.warning(f"Could not parse Google ID token credential: {e}")

    if not clean_email and payload.email:
        clean_email = str(payload.email).lower().strip()

    if not clean_email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Valid Google email or credential token is required")

    user = db.query(User).filter(User.email == clean_email).first()

    if not user:
        # Create new student user via Google SSO
        final_name = display_name or clean_email.split("@")[0].replace(".", " ").title()
        user = User(
            email=clean_email,
            full_name=final_name,
            password_hash=hash_password(uuid.uuid4().hex + "G@oogle99!"),
            branch=None,
            role="student",
            has_completed_onboarding=False,  # Guide to Step 2 onboarding!
            is_active=True,
        )
        db.add(user)
        db.flush()
        db.add(AuditLog(user_id=user.id, action="google_signup", detail=f"Signed up via Google SSO ({user.email})"))
    else:
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Account has been deactivated")
        db.add(AuditLog(user_id=user.id, action="google_login", detail=f"Logged in via Google SSO ({user.email})"))

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    token = create_access_token(user)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/clerk", response_model=TokenOut)
def clerk_auth(payload: GoogleAuthIn, db: Session = Depends(get_db)):
    """Single Sign-On with Clerk Authentication."""
    clean_email: str | None = None
    display_name = payload.name

    if payload.credential:
        try:
            claims = jwt.decode(payload.credential, options={"verify_signature": False})
            if "email" in claims:
                clean_email = str(claims["email"]).lower().strip()
            elif "sub" in claims:
                clean_email = f"clerk_{claims['sub']}@clerk.dev"
            if "name" in claims and not display_name:
                display_name = str(claims["name"]).strip()
        except Exception as e:
            logger.warning(f"Could not parse Clerk credential: {e}")

    if not clean_email and payload.email:
        clean_email = str(payload.email).lower().strip()

    if not clean_email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Valid email or credential token is required")

    user = db.query(User).filter(User.email == clean_email).first()

    if not user:
        final_name = display_name or clean_email.split("@")[0].replace(".", " ").title()
        user = User(
            email=clean_email,
            full_name=final_name,
            password_hash=hash_password(uuid.uuid4().hex + "ClerkAuth99!"),
            branch=None,
            role="student",
            has_completed_onboarding=False,
            is_active=True,
        )
        db.add(user)
        db.flush()
        db.add(AuditLog(user_id=user.id, action="clerk_signup", detail=f"Signed up via Clerk ({user.email})"))
    else:
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Account has been deactivated")
        db.add(AuditLog(user_id=user.id, action="clerk_login", detail=f"Logged in via Clerk ({user.email})"))

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    token = create_access_token(user)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/onboarding", response_model=TokenOut)
def complete_onboarding(
    payload: OnboardingIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Step 2: Profile Setup / Second Authenticator Screen (Onboarding)."""
    full_name = f"{payload.first_name.strip()} {payload.last_name.strip()}"
    current_user.full_name = full_name
    current_user.branch = payload.branch.strip().lower()
    if payload.college:
        current_user.college = payload.college.strip()
    if payload.semester:
        current_user.semester = payload.semester.strip()
    current_user.has_completed_onboarding = True

    db.add(AuditLog(
        user_id=current_user.id,
        action="profile_onboarded",
        detail=f"Completed profile onboarding for branch {current_user.branch}",
    ))
    db.commit()
    db.refresh(current_user)

    token = create_access_token(current_user)
    return TokenOut(access_token=token, user=UserOut.model_validate(current_user))


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")

    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account has been deactivated")

    user.last_login_at = datetime.now(timezone.utc)
    db.add(AuditLog(user_id=user.id, action="user_login", detail=f"User {user.email} logged in"))
    db.commit()
    db.refresh(user)

    token = create_access_token(user)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)


@router.put("/profile", response_model=UserOut)
def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.branch is not None:
        current_user.branch = payload.branch

    db.add(AuditLog(user_id=current_user.id, action="profile_updated", detail="Profile updated"))
    db.commit()
    db.refresh(current_user)
    return UserOut.model_validate(current_user)


@router.post("/change-password")
def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password does not match")

    current_user.password_hash = hash_password(payload.new_password)
    db.add(AuditLog(user_id=current_user.id, action="password_changed", detail="Password updated"))
    db.commit()
    return {"message": "Password changed successfully"}
