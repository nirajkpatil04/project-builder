"""Pydantic request/response schemas (input validation lives here)."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from .engine.catalog import BRANCHES

Skill = Literal["beginner", "intermediate", "advanced"]
Budget = Literal["zero", "low", "medium", "high"]
Preference = Literal["software", "hardware", "hybrid"]
Difficulty = Literal["easy", "moderate", "challenging"]
Role = Literal["student", "mentor", "admin"]
Branch = str


def check_password_strength(v: str) -> str:
    if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
        raise ValueError("Password must contain at least one letter and one number")
    return v


# ── Auth ─────────────────────────────────────────────────────────────────────
class RegisterIn(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=120)
    password: str = Field(min_length=8, max_length=72)
    branch: str | None = None

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, v: str | None) -> str | None:
        if not v:
            return v
        v = " ".join(v.split())
        if not re.fullmatch(r"[\w .'\-]+", v):
            raise ValueError("Name contains invalid characters")
        return v

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        return check_password_strength(v)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class GoogleAuthIn(BaseModel):
    email: EmailStr
    name: str | None = None
    credential: str | None = None
    picture: str | None = None


class OnboardingIn(BaseModel):
    first_name: str = Field(min_length=1, max_length=60)
    last_name: str = Field(min_length=1, max_length=60)
    branch: str = Field(min_length=2, max_length=60)
    college: str | None = Field(default=None, max_length=160)
    semester: str | None = Field(default=None, max_length=60)

    @field_validator("branch")
    @classmethod
    def validate_branch(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if v_clean not in BRANCHES:
            # Fallback if unknown code passed: keep normalized
            return v_clean
        return v_clean


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    full_name: str
    role: str
    branch: str | None = None
    college: str | None = None
    semester: str | None = None
    has_completed_onboarding: bool = True
    is_active: bool
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    branch: str | None = None
    college: str | None = None
    semester: str | None = None


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)

    @field_validator("new_password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        return check_password_strength(v)


# ── Builder ──────────────────────────────────────────────────────────────────
class StudentProfile(BaseModel):
    goal: str = Field(default="I want to build a final-year project using AI", max_length=500)
    branch: Branch
    skill: Skill
    budget: Budget
    preference: Preference
    difficulty: Difficulty
    months: int = Field(ge=1, le=12)
    team_size: int = Field(ge=1, le=6)
    interests: list[str] = Field(default_factory=list, max_length=12)

    @field_validator("interests")
    @classmethod
    def clean_interests(cls, v: list[str]) -> list[str]:
        return [re.sub(r"[^a-z0-9\-]", "", i.lower())[:30] for i in v if i.strip()]


class SuggestIn(BaseModel):
    profile: StudentProfile
    limit: int = Field(default=3, ge=1, le=6)


class GenerateIn(BaseModel):
    profile: StudentProfile
    idea_key: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9\-]+$")
    level: Skill
    use_llm: bool = True


# ── Projects ─────────────────────────────────────────────────────────────────
class ProjectSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    idea_key: str
    level: str
    status: str
    source: str
    owner_id: int
    owner_name: str | None = None
    progress_pct: int = 0
    created_at: datetime
    updated_at: datetime


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    decision: str
    comment: str
    reviewer_name: str | None = None
    created_at: datetime


class FileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    original_name: str
    content_type: str
    size_bytes: int
    created_at: datetime


class ProjectDetail(ProjectSummary):
    profile: dict[str, Any]
    blueprint: dict[str, Any]
    progress: list[str]
    reviews: list[ReviewOut] = []
    files: list[FileOut] = []


class ProjectUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=200)


class ProgressIn(BaseModel):
    completed: list[str] = Field(default_factory=list, max_length=500)

    @field_validator("completed")
    @classmethod
    def valid_ids(cls, v: list[str]) -> list[str]:
        return sorted({i for i in v if re.fullmatch(r"p\d+-t\d+", i)})


class ReviewIn(BaseModel):
    decision: Literal["approved", "changes_requested", "comment"]
    comment: str = Field(min_length=1, max_length=2000)


# ── Admin ────────────────────────────────────────────────────────────────────
class UserAdminUpdate(BaseModel):
    role: Role | None = None
    is_active: bool | None = None
