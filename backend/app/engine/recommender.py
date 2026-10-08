"""Idea recommender.

A lightweight, dependency-free ML ranking model:
  1. TF-IDF vectors + cosine similarity between the student's free-text goal and each idea.
  2. A weighted, explainable scoring function over the structured profile
     (branch, preference, budget, skill, difficulty, interests).
  3. Capacity planning (team size × months) to recommend the right path level.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from functools import lru_cache
from typing import Any

from .catalog import (
    AI_DOMAINS,
    APPLICATION_AREAS,
    BRANCHES,
    BUDGET_CAP,
    LEVEL_LABELS,
    is_physical_branch,
)
from .ideas import IDEAS, Idea

LEVELS = ["beginner", "intermediate", "advanced"]
DIFF_RANK = {"easy": 0, "moderate": 1, "challenging": 2}
BASE_EFFORT_PERSON_WEEKS = {"beginner": 7, "intermediate": 13, "advanced": 22}
DIFF_FACTOR = {"easy": 0.8, "moderate": 1.0, "challenging": 1.3}
PART_TIME_FACTOR = 0.5  # students work part-time on projects alongside classes

STOPWORDS = set(
    "a an and are as at be by for from has have i in is it its of on or that the this to was were will with "
    "want build project final year using use make based system my we our can like some into".split()
)


# ── TF-IDF ───────────────────────────────────────────────────────────────────
def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    out = []
    for t in tokens:
        if t in STOPWORDS or len(t) < 2:
            continue
        if len(t) > 4 and t.endswith("s") and not t.endswith("ss"):
            t = t[:-1]  # naive stemming: "diseases" -> "disease"
        out.append(t)
    return out


class TfidfIndex:
    def __init__(self, docs: list[str]):
        self.doc_tokens = [tokenize(d) for d in docs]
        n = len(docs)
        df: Counter[str] = Counter()
        for toks in self.doc_tokens:
            df.update(set(toks))
        self.idf = {term: math.log((1 + n) / (1 + freq)) + 1 for term, freq in df.items()}
        self.doc_vectors = [self._vectorize(toks) for toks in self.doc_tokens]

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        vec = {t: (1 + math.log(c)) * self.idf.get(t, 0.0) for t, c in tf.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {t: v / norm for t, v in vec.items()}

    def similarities(self, query: str) -> list[float]:
        q = self._vectorize(tokenize(query))
        return [sum(w * d.get(t, 0.0) for t, w in q.items()) for d in self.doc_vectors]


def _idea_document(idea: Idea) -> str:
    domain_words = " ".join(AI_DOMAINS.get(d, d) for d in idea["domains"])
    interest_words = " ".join(APPLICATION_AREAS.get(i, i) for i in idea["interests"])
    tiers = " ".join(t[0] + " " + t[1] for t in idea["tiers"].values())
    return " ".join([idea["title"], idea["tagline"], idea["problem"], idea["keywords"], domain_words, interest_words, tiers])


_INDEX = TfidfIndex([_idea_document(i) for i in IDEAS])


# ── Capacity / level planning ────────────────────────────────────────────────
def effort_person_weeks(idea: Idea, level: str) -> float:
    return BASE_EFFORT_PERSON_WEEKS[level] * DIFF_FACTOR[idea["difficulty"]]


def team_capacity(months: int, team_size: int) -> float:
    return months * 4.3 * team_size * PART_TIME_FACTOR


def feasibility(idea: Idea, level: str, months: int, team_size: int) -> dict[str, Any]:
    effort = effort_person_weeks(idea, level)
    capacity = team_capacity(months, team_size)
    ratio = effort / capacity if capacity else 99
    if ratio <= 0.8:
        label = "Comfortable"
    elif ratio <= 1.15:
        label = "Achievable"
    elif ratio <= 1.5:
        label = "Tight"
    else:
        label = "Risky"
    return {
        "label": label,
        "effort_person_weeks": round(effort, 1),
        "capacity_person_weeks": round(capacity, 1),
        "load_pct": round(ratio * 100),
    }


def recommend_level(profile: dict, idea: Idea) -> str:
    idx = LEVELS.index(profile["skill"])
    if profile["difficulty"] == "challenging":
        idx += 1
    elif profile["difficulty"] == "easy":
        idx -= 1
    idx = max(0, min(2, idx))
    capacity = team_capacity(profile["months"], profile["team_size"])
    cap = BUDGET_CAP[profile["budget"]]
    while idx > 0 and (effort_person_weeks(idea, LEVELS[idx]) > capacity * 1.15 or idea["cost"][LEVELS[idx]] > cap):
        idx -= 1
    return LEVELS[idx]


# ── Scoring ──────────────────────────────────────────────────────────────────
def _score(profile: dict, idea: Idea, text_sim: float) -> tuple[float, list[str], str]:
    reasons: list[str] = []
    score = 0.0
    level = recommend_level(profile, idea)

    # Branch fit (20)
    student_branch = profile.get("branch", "cse")
    branch_name = BRANCHES.get(student_branch, student_branch.upper())
    is_phys = is_physical_branch(student_branch)

    if student_branch in idea.get("branches", []):
        score += 20
        reasons.append(f"Well aligned with {branch_name} curriculum")
    elif is_phys and idea.get("type") in ("physical", "hybrid", "hardware"):
        score += 18
        reasons.append(f"Fabrication & hardware-first engineering match for {branch_name}")
    elif (not is_phys) and idea.get("type") == "software":
        score += 14
        reasons.append(f"Curriculum-compatible engineering project for {branch_name}")
    else:
        score += 6

    # Software / hardware / physical preference (18)
    pref, kind = profile.get("preference", "software"), idea.get("type", "software")
    if pref == kind or (pref == "hardware" and kind == "physical"):
        score += 18
        reasons.append(f"Matches your {pref} engineering focus")
    elif is_phys and kind == "physical":
        score += 16
        reasons.append("Prioritizes physical fabrication and CAD/FEA simulation")
    elif "hybrid" in (pref, kind):
        score += 10

    # Budget (14)
    cap = BUDGET_CAP[profile["budget"]]
    if idea["cost"][level] <= cap:
        score += 14
        if idea["cost"][level] == 0:
            reasons.append("Can be built at zero hardware cost")
        else:
            reasons.append(f"Fits your budget (≈ ₹{idea['cost'][level]:,})")
    elif idea["cost"]["beginner"] <= cap:
        score += 8
    else:
        score += 1

    # Skill readiness (14)
    gap = LEVELS.index(profile["skill"]) - LEVELS.index(idea["min_skill"])
    score += 14 if gap >= 0 else (6 if gap == -1 else 0)

    # Difficulty match (8)
    score += max(0, 8 - 4 * abs(DIFF_RANK[profile["difficulty"]] - DIFF_RANK[idea["difficulty"]]))

    # Interests (14)
    tags = set(idea["interests"]) | set(idea["domains"])
    wanted = set(profile.get("interests") or [])
    if wanted:
        overlap = tags & wanted
        score += 14 * min(1.0, len(overlap) / min(len(wanted), 2))
        if overlap:
            names = [APPLICATION_AREAS.get(t) or AI_DOMAINS.get(t) or t for t in sorted(overlap)]
            reasons.append("Covers your interests: " + ", ".join(names[:3]))
    else:
        score += 7

    # Free-text goal similarity (12)
    score += 12 * text_sim
    if text_sim > 0.55:
        reasons.append("Closely matches what you described")

    fz = feasibility(idea, level, profile["months"], profile["team_size"])
    if fz["label"] in ("Comfortable", "Achievable"):
        reasons.append(f"{fz['label']} in {profile['months']} month(s) with a team of {profile['team_size']}")
    return round(min(score, 100), 1), reasons, level


def build_path(idea: Idea, recommended: str, months: int, team_size: int) -> list[dict]:
    path = []
    for lvl in LEVELS:
        title, summary, features = idea["tiers"][lvl]
        path.append({
            "level": lvl,
            "level_label": LEVEL_LABELS[lvl],
            "title": title,
            "summary": summary,
            "features": features,
            "cost_inr": idea["cost"][lvl],
            "feasibility": feasibility(idea, lvl, months, team_size),
            "recommended": lvl == recommended,
        })
    return path


@lru_cache(maxsize=512)
def _cached_rank(profile_key: tuple) -> tuple:
    profile = dict(profile_key)
    profile["interests"] = list(profile["interests"])
    query = " ".join([profile.get("goal", "")] + [APPLICATION_AREAS.get(i) or AI_DOMAINS.get(i) or i for i in profile["interests"]])
    sims = _INDEX.similarities(query)
    max_sim = max(sims) or 1.0
    ranked = []
    for idea, sim in zip(IDEAS, sims):
        score, reasons, level = _score(profile, idea, sim / max_sim if max_sim > 0 else 0)
        ranked.append((score, idea["key"], tuple(reasons), level))
    ranked.sort(key=lambda r: r[0], reverse=True)
    return tuple(ranked)


def _profile_key(profile: dict) -> tuple:
    p = dict(profile)
    p["interests"] = tuple(sorted(p.get("interests") or []))
    return tuple(sorted(p.items()))


def suggest(profile: dict, limit: int = 3) -> list[dict]:
    from .ideas import IDEA_INDEX

    results = []
    for score, key, reasons, level in _cached_rank(_profile_key(profile))[:limit]:
        idea = IDEA_INDEX[key]
        results.append({
            "key": key,
            "title": idea["title"],
            "tagline": idea["tagline"],
            "score": score,
            "reasons": list(reasons),
            "domains": [{"value": d, "label": AI_DOMAINS.get(d, d)} for d in idea["domains"]],
            "type": idea["type"],
            "difficulty": idea["difficulty"],
            "recommended_level": level,
            "path": build_path(idea, level, profile["months"], profile["team_size"]),
        })
    return results
