"""Project builder wizard endpoints (options, recommendations, and blueprint compilation)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..engine.catalog import options_payload
from ..engine.generator import generate_blueprint
from ..engine.llm import enrich_blueprint_with_llm
from ..engine.recommender import suggest
from ..models import AuditLog, User
from ..schemas import GenerateIn, SuggestIn
from ..security import get_optional_user

router = APIRouter(prefix="/builder", tags=["builder"])


@router.get("/options")
def get_options():
    """Returns all selectable dropdown items, categories and configuration options."""
    return options_payload()


@router.post("/suggest")
def get_suggestions(
    payload: SuggestIn,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Takes student parameters and returns top-ranked project paths."""
    profile_dict = payload.profile.model_dump()
    results = suggest(profile_dict, limit=payload.limit)

    if current_user:
        db.add(
            AuditLog(
                user_id=current_user.id,
                action="suggest_projects",
                detail=f"Requested {len(results)} suggestions for branch={payload.profile.branch}",
            )
        )
        db.commit()

    return {"suggestions": results}


@router.post("/generate")
async def generate_project(
    payload: GenerateIn,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Generates the comprehensive blueprint for a specific idea and difficulty level."""
    profile_dict = payload.profile.model_dump()

    try:
        blueprint = generate_blueprint(payload.idea_key, payload.level, profile_dict)
    except ValueError as err:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(err))

    # Optional hybrid LLM enrichment
    if payload.use_llm:
        blueprint = await enrich_blueprint_with_llm(blueprint, profile_dict)

    if current_user:
        db.add(
            AuditLog(
                user_id=current_user.id,
                action="generate_blueprint",
                detail=f"Generated blueprint for {payload.idea_key} [{payload.level}]",
            )
        )
        db.commit()

    return {"blueprint": blueprint, "profile": profile_dict}
