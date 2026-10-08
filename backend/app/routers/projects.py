"""Project management, saving, progress tracking, reviews, exports and attachments."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AuditLog, Project, ProjectFile, Review, User
from ..schemas import FileOut, ProgressIn, ProjectDetail, ProjectSummary, ProjectUpdate, ReviewIn, ReviewOut
from ..security import can_edit_project, can_view_project, get_current_user, require_roles
from ..services.exporter import export_markdown, export_printable_html
from ..services.storage import get_file_path, save_upload_file

router = APIRouter(prefix="/projects", tags=["projects"])


def _calculate_progress_pct(project: Project) -> int:
    completed = len(project.progress or [])
    total = 0
    roadmap = (project.blueprint or {}).get("roadmap", [])
    for phase in roadmap:
        total += len(phase.get("tasks", []))
    if total == 0:
        return 0
    return min(100, round((completed / total) * 100))


@router.get("", response_model=list[ProjectSummary])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Project)
    if current_user.role == "student":
        query = query.filter(Project.owner_id == current_user.id)
    projects = query.order_by(Project.created_at.desc()).all()

    summaries = []
    for p in projects:
        summary = ProjectSummary(
            id=p.id,
            title=p.title,
            idea_key=p.idea_key,
            level=p.level,
            status=p.status,
            source=p.source,
            owner_id=p.owner_id,
            owner_name=p.owner.full_name if p.owner else "Unknown",
            progress_pct=_calculate_progress_pct(p),
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        summaries.append(summary)
    return summaries


@router.post("", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    blueprint = payload.get("blueprint")
    profile = payload.get("profile", {})
    if not blueprint or not isinstance(blueprint, dict):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Missing blueprint payload")

    title = blueprint.get("title", "Untitled Project")
    idea_key = blueprint.get("idea_key", "custom")
    level = blueprint.get("level", "intermediate")
    source = blueprint.get("source", "engine")

    project = Project(
        owner_id=current_user.id,
        title=title,
        idea_key=idea_key,
        level=level,
        status="active",
        source=source,
        profile=profile,
        blueprint=blueprint,
        progress=[],
    )
    db.add(project)
    db.flush()

    db.add(AuditLog(user_id=current_user.id, action="project_saved", detail=f"Saved project #{project.id}: {title}"))
    db.commit()
    db.refresh(project)

    return get_project_detail(project.id, current_user, db)


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project_detail(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")
    if not can_view_project(current_user, project):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

    reviews_out = [
        ReviewOut(
            id=r.id,
            decision=r.decision,
            comment=r.comment,
            reviewer_name=r.reviewer.full_name if r.reviewer else "Mentor",
            created_at=r.created_at,
        )
        for r in project.reviews
    ]

    files_out = [
        FileOut(
            id=f.id,
            original_name=f.original_name,
            content_type=f.content_type,
            size_bytes=f.size_bytes,
            created_at=f.created_at,
        )
        for f in project.files
    ]

    return ProjectDetail(
        id=project.id,
        title=project.title,
        idea_key=project.idea_key,
        level=project.level,
        status=project.status,
        source=project.source,
        owner_id=project.owner_id,
        owner_name=project.owner.full_name if project.owner else "Unknown",
        progress_pct=_calculate_progress_pct(project),
        created_at=project.created_at,
        updated_at=project.updated_at,
        profile=project.profile,
        blueprint=project.blueprint,
        progress=project.progress or [],
        reviews=reviews_out,
        files=files_out,
    )


@router.put("/{project_id}", response_model=ProjectSummary)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")
    if not can_edit_project(current_user, project):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

    project.title = payload.title
    db.commit()
    db.refresh(project)

    return ProjectSummary(
        id=project.id,
        title=project.title,
        idea_key=project.idea_key,
        level=project.level,
        status=project.status,
        source=project.source,
        owner_id=project.owner_id,
        owner_name=project.owner.full_name if project.owner else "",
        progress_pct=_calculate_progress_pct(project),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")
    if not can_edit_project(current_user, project):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

    db.add(AuditLog(user_id=current_user.id, action="project_deleted", detail=f"Deleted project #{project.id}"))
    db.delete(project)
    db.commit()


@router.put("/{project_id}/progress")
def update_progress(
    project_id: int,
    payload: ProgressIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")
    if not can_edit_project(current_user, project):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

    project.progress = payload.completed
    db.commit()
    db.refresh(project)
    return {"completed": project.progress, "progress_pct": _calculate_progress_pct(project)}


@router.post("/{project_id}/reviews", response_model=ReviewOut)
def submit_review(
    project_id: int,
    payload: ReviewIn,
    current_user: User = Depends(require_roles("mentor", "admin")),
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")

    review = Review(
        project_id=project.id,
        reviewer_id=current_user.id,
        decision=payload.decision,
        comment=payload.comment,
    )
    db.add(review)

    if payload.decision == "approved":
        project.status = "approved"
    elif payload.decision == "changes_requested":
        project.status = "revisions_needed"

    db.add(
        AuditLog(
            user_id=current_user.id,
            action="review_submitted",
            detail=f"Reviewed project #{project.id} ({payload.decision})",
        )
    )
    db.commit()
    db.refresh(review)

    return ReviewOut(
        id=review.id,
        decision=review.decision,
        comment=review.comment,
        reviewer_name=current_user.full_name,
        created_at=review.created_at,
    )


@router.get("/{project_id}/export/markdown")
def download_markdown(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if not project or not can_view_project(current_user, project):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")

    md_content = export_markdown(project.title, project.blueprint)
    filename = f"{project.idea_key}_blueprint.md"
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{project_id}/export/html")
def view_or_print_html(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if not project or not can_view_project(current_user, project):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")

    html_content = export_printable_html(project.title, project.blueprint)
    return Response(content=html_content, media_type="text/html")


@router.post("/{project_id}/files", response_model=FileOut)
def upload_attachment(
    project_id: int,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if not project or not can_edit_project(current_user, project):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")

    storage_key, orig_name, size = save_upload_file(file, project.id)
    pfile = ProjectFile(
        project_id=project.id,
        uploader_id=current_user.id,
        original_name=orig_name,
        storage_key=storage_key,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=size,
    )
    db.add(pfile)
    db.commit()
    db.refresh(pfile)

    return FileOut.model_validate(pfile)


@router.get("/{project_id}/files/{file_id}")
def download_attachment(
    project_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if not project or not can_view_project(current_user, project):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")

    pfile = db.get(ProjectFile, file_id)
    if not pfile or pfile.project_id != project.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")

    file_path = get_file_path(pfile.storage_key)
    return FileResponse(
        path=str(file_path),
        filename=pfile.original_name,
        media_type=pfile.content_type,
    )
