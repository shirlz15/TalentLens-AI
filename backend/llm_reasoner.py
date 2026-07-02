"""Optional LLM-backed recruiter reasoning for TalentLens AI.

The project must remain fully usable offline, so every public function falls
back to deterministic reasoning when no supported API key is available or when
the relevant SDK is not installed.
"""

from __future__ import annotations

import json
import os
from typing import Any


def generate_recruiter_reasoning(
    candidate: dict[str, Any],
    job_description: str,
    score_breakdown: dict[str, Any],
) -> str:
    """Return recruiter-style reasoning, preferring LLM output when available."""

    prompt = (
        "You are a senior recruiter. Explain in 3-5 concise sentences why this candidate "
        "ranked for the role. Ground the explanation in semantic fit, technical evidence, "
        "experience, authenticity, behavioral signals, and career consistency.\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Candidate:\n{json.dumps(_candidate_summary(candidate), ensure_ascii=True)}\n\n"
        f"Score Breakdown:\n{json.dumps(score_breakdown, ensure_ascii=True)}"
    )
    llm_output = _call_llm(prompt)
    if llm_output:
        return llm_output
    return _fallback_recruiter_reasoning(candidate, score_breakdown)


def generate_hidden_gem_reason(
    candidate: dict[str, Any],
    score_breakdown: dict[str, Any],
) -> str:
    """Return hidden-gem reasoning, preferring LLM output when available."""

    prompt = (
        "You are an expert recruiter. In 2-4 concise sentences, explain whether this "
        "candidate is a hidden gem and why. Focus on upside, underexposure, learning "
        "signals, projects, and recruiter-confidence signals.\n\n"
        f"Candidate:\n{json.dumps(_candidate_summary(candidate), ensure_ascii=True)}\n\n"
        f"Score Breakdown:\n{json.dumps(score_breakdown, ensure_ascii=True)}"
    )
    llm_output = _call_llm(prompt)
    if llm_output:
        return llm_output
    return _fallback_hidden_gem_reason(candidate, score_breakdown)


def generate_interview_recommendation(
    candidate: dict[str, Any],
    job_description: str,
) -> str:
    """Return a recruiter-style interview recommendation."""

    prompt = (
        "You are a senior recruiter. In 2-3 concise sentences, recommend whether to "
        "interview this candidate for the role. Mention the strongest reason and the main "
        "risk to validate in interview.\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Candidate:\n{json.dumps(_candidate_summary(candidate), ensure_ascii=True)}"
    )
    llm_output = _call_llm(prompt)
    if llm_output:
        return llm_output
    return _fallback_interview_recommendation(candidate)


def _call_llm(prompt: str) -> str:
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    if openai_key:
        result = _call_openai(prompt, openai_key)
        if result:
            return result
    if gemini_key:
        result = _call_gemini(prompt, gemini_key)
        if result:
            return result
    return ""


def _call_openai(prompt: str, api_key: str) -> str:
    try:
        from openai import OpenAI  # type: ignore[import-not-found]
    except ImportError:  # pragma: no cover - optional dependency
        return ""

    try:  # pragma: no cover - requires external API
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )
        return str(getattr(response, "output_text", "") or "").strip()
    except Exception:
        return ""


def _call_gemini(prompt: str, api_key: str) -> str:
    try:
        import google.generativeai as genai  # type: ignore[import-not-found]
    except ImportError:  # pragma: no cover - optional dependency
        return ""

    try:  # pragma: no cover - requires external API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return str(getattr(response, "text", "") or "").strip()
    except Exception:
        return ""


def _candidate_summary(candidate: dict[str, Any]) -> dict[str, Any]:
    profile = candidate.get("profile") if isinstance(candidate.get("profile"), dict) else {}
    return {
        "candidate_id": candidate.get("candidate_id") or profile.get("candidate_id") or candidate.get("id"),
        "name": profile.get("name") or profile.get("full_name") or candidate.get("name"),
        "headline": profile.get("headline") or candidate.get("headline"),
        "years_experience": profile.get("years_experience") or candidate.get("years_experience"),
        "skills": candidate.get("skills"),
        "education": candidate.get("education"),
        "career_history": candidate.get("career_history"),
        "certifications": candidate.get("certifications"),
        "projects": candidate.get("projects"),
        "redrob_signals": candidate.get("redrob_signals"),
    }


def _fallback_recruiter_reasoning(candidate: dict[str, Any], score_breakdown: dict[str, Any]) -> str:
    profile = candidate.get("profile") if isinstance(candidate.get("profile"), dict) else {}
    name = profile.get("name") or profile.get("full_name") or candidate.get("name") or "This candidate"
    technical = _score_value(score_breakdown, "technical")
    experience = _score_value(score_breakdown, "experience")
    consistency = _score_value(score_breakdown, "career_consistency")
    authenticity = _score_value(score_breakdown, "authenticity")
    matched = _metadata_list(score_breakdown, "technical", "matched_skills")
    return (
        f"{name} shows strongest value through matched skills such as {', '.join(matched[:4]) or 'core role-aligned evidence'}, "
        f"with technical fit {technical:.1f}, experience {experience:.1f}, career consistency {consistency:.1f}, "
        f"and authenticity {authenticity:.1f}. The profile is ranked on a blend of semantic fit, hybrid scoring evidence, "
        "and recruiter-confidence signals rather than keywords alone."
    )


def _fallback_hidden_gem_reason(candidate: dict[str, Any], score_breakdown: dict[str, Any]) -> str:
    hidden_gem = score_breakdown.get("hidden_gem", {})
    gaps = hidden_gem.get("gaps") or []
    evidence = hidden_gem.get("evidence") or []
    if evidence:
        return (
            f"Hidden-gem potential is driven by {', '.join(evidence[:3]).lower()}. "
            f"The main caution is {gaps[0].lower()}." if gaps else f"Hidden-gem potential is driven by {', '.join(evidence[:3]).lower()}."
        )
    return "This candidate is not currently flagged as a strong hidden gem under the available project, activity, and upside signals."


def _fallback_interview_recommendation(candidate: dict[str, Any]) -> str:
    profile = candidate.get("profile") if isinstance(candidate.get("profile"), dict) else {}
    name = profile.get("name") or profile.get("full_name") or candidate.get("name") or "This candidate"
    years = profile.get("years_experience") or candidate.get("years_experience") or "their stated"
    skills = candidate.get("skills") or []
    top_skills = ", ".join(str(skill) for skill in skills[:3]) or "role-aligned skills"
    return (
        f"Recommend interviewing {name} for roles requiring {top_skills} with roughly {years} years of experience. "
        "Use the screen to validate applied depth, communication quality, and supporting evidence for the strongest claimed skills."
    )


def _score_value(score_breakdown: dict[str, Any], key: str) -> float:
    value = score_breakdown.get(key, {}).get("score", 0.0)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _metadata_list(score_breakdown: dict[str, Any], key: str, metadata_key: str) -> list[str]:
    metadata = score_breakdown.get(key, {}).get("metadata", {})
    values = metadata.get(metadata_key) or []
    return [str(value) for value in values if str(value).strip()]
