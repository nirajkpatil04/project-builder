"""Admin and mentor governance endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AuditLog, Project, Review, User
from ..schemas import UserAdminUpdate, UserOut
from ..security import require_roles

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(
    _admin: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.put("/users/{user_id}", response_model=UserOut)
def update_user_status(
    user_id: int,
    payload: UserAdminUpdate,
    admin: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    if target.id == admin.id and payload.is_active is False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot deactivate your own admin account")

    if payload.role is not None:
        target.role = payload.role
    if payload.is_active is not None:
        target.is_active = payload.is_active

    db.add(AuditLog(user_id=admin.id, action="admin_user_update", detail=f"Updated user #{target.id} ({target.email})"))
    db.commit()
    db.refresh(target)
    return UserOut.model_validate(target)


@router.get("/stats")
def get_platform_stats(
    _admin_or_mentor: User = Depends(require_roles("admin", "mentor")),
    db: Session = Depends(get_db),
):
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_projects = db.query(func.count(Project.id)).scalar() or 0
    total_reviews = db.query(func.count(Review.id)).scalar() or 0

    role_counts = dict(db.query(User.role, func.count(User.id)).group_by(User.role).all())
    level_counts = dict(db.query(Project.level, func.count(Project.id)).group_by(Project.level).all())
    status_counts = dict(db.query(Project.status, func.count(Project.id)).group_by(Project.status).all())

    return {
        "total_users": total_users,
        "total_projects": total_projects,
        "total_reviews": total_reviews,
        "users_by_role": role_counts,
        "projects_by_level": level_counts,
        "projects_by_status": status_counts,
    }


@router.get("/audit-logs")
def get_audit_logs(
    limit: int = 50,
    _admin: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "detail": log.detail,
            "created_at": log.created_at,
        }
        for log in logs
    ]
