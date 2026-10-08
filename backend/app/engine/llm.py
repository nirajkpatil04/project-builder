"""Hybrid LLM integration (Gemini / OpenAI / Offline rule-based fallback).

Enriches the deterministic blueprint when an API key is available; gracefully
and silently falls back to the built-in rule-based output when keys are missing
or when the network is unreachable.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def enrich_blueprint_with_llm(
    blueprint: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    """Optionally enriches the blueprint using an LLM if configured and enabled."""
    provider = settings.llm_provider
    gemini_key = settings.gemini_api_key
    openai_key = settings.openai_api_key

    # Check if any provider is available
    active_provider = None
    if provider in ("gemini", "auto") and gemini_key:
        active_provider = "gemini"
    elif provider in ("openai", "auto") and openai_key:
        active_provider = "openai"

    if not active_provider:
        blueprint["source"] = "engine (offline deterministic)"
        return blueprint

    prompt = (
        f"You are a Distinguished AI Research Scientist and Principal Software Architect assisting a student "
        f"with their final-year engineering project. Given the student's profile and initial blueprint, provide "
        f"a personalized mentor guidance note and 3 custom advanced viva tips.\n\n"
        f"Student Profile:\n"
        f"- Branch: {profile.get('branch')}\n"
        f"- Skill Level: {profile.get('skill')}\n"
        f"- Target Duration: {profile.get('months')} months\n"
        f"- Team Size: {profile.get('team_size')}\n"
        f"- Goal: {profile.get('goal')}\n\n"
        f"Project Title: {blueprint.get('title')} ({blueprint.get('tier_title')})\n\n"
        f"Return ONLY a valid JSON object with the following schema:\n"
        f'{{"mentor_note": "A paragraph of advice tailored to this student\'s goal and background", '
        f'"examiner_focus_areas": ["tip 1", "tip 2", "tip 3"]}}'
    )

    try:
        if active_provider == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent?key={gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.4, "responseMimeType": "application/json"},
            }
            async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(raw_text)
                    blueprint["mentor_advice"] = parsed.get("mentor_note", "")
                    blueprint["examiner_focus_areas"] = parsed.get("examiner_focus_areas", [])
                    blueprint["source"] = f"hybrid ({settings.gemini_model} + engine)"
                    return blueprint

        elif active_provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
            payload = {
                "model": settings.openai_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4,
                "response_format": {"type": "json_object"},
            }
            async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    raw_text = data["choices"][0]["message"]["content"]
                    parsed = json.loads(raw_text)
                    blueprint["mentor_advice"] = parsed.get("mentor_note", "")
                    blueprint["examiner_focus_areas"] = parsed.get("examiner_focus_areas", [])
                    blueprint["source"] = f"hybrid ({settings.openai_model} + engine)"
                    return blueprint

    except Exception as exc:
        logger.warning(f"LLM enrichment failed or timed out: {exc}. Falling back to rule-based engine.")

    # Graceful fallback
    blueprint["source"] = "engine (offline fallback)"
    blueprint["mentor_advice"] = (
        f"Focus on solidifying your baseline model and building an ironclad evaluation pipeline. "
        f"External examiners reward students who can clearly explain why their model failed on certain edge cases "
        f"more than those who claim 99% accuracy on a clean dataset."
    )
    blueprint["examiner_focus_areas"] = [
        "Be prepared to explain your data split strategy and prove there was zero leakage between train and test.",
        "Justify every library and hyperparameter choice in your training script.",
        "Demonstrate the live system with an input sample that the examiners provide on the spot.",
    ]
    return blueprint
