"""FastAPI application for TalentLens AI.

The API layer is intentionally thin: semantic retrieval, hybrid ranking, and
candidate intelligence remain in the existing backend modules. This file wraps
that logic into routes without changing the frontend-oriented workflow.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

try:
    from fastapi import FastAPI, File, HTTPException, UploadFile
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field

    FASTAPI_AVAILABLE = True
except ImportError:  # pragma: no cover - keeps module importable before deps are installed
    FASTAPI_AVAILABLE = False

    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str) -> None:
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class BaseModel:
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def Field(default: Any = None, **_: Any) -> Any:
        return default

    def File(default: Any = None, **_: Any) -> Any:
        return default

    class UploadFile:  # pragma: no cover - placeholder for import-time compatibility
        filename: str | None = None

    class CORSMiddleware:  # pragma: no cover - placeholder for import-time compatibility
        pass

    class _PlaceholderApp:
        def get(self, *_args: Any, **_kwargs: Any):
            def decorator(func: Any) -> Any:
                return func

            return decorator

        def post(self, *_args: Any, **_kwargs: Any):
            def decorator(func: Any) -> Any:
                return func

            return decorator

    def FastAPI(*_args: Any, **_kwargs: Any) -> Any:
        return _PlaceholderApp()

try:
    from .ranker import RankedCandidate, load_default_candidates, rank_candidates
    from .resume_parser import parse_uploaded_candidate
except ImportError:  # pragma: no cover - direct execution support
    from ranker import RankedCandidate, load_default_candidates, rank_candidates
    from resume_parser import parse_uploaded_candidate


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATE_PATHS = (
    PROJECT_ROOT / "data" / "candidates.jsonl",
    PROJECT_ROOT / "data" / "sample_candidates.json",
)
ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:4173",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:4173",
]


class RankRequest(BaseModel):
    job_description: str = Field(..., description="Target job description")
    top_k: int = Field(default=10, ge=1, le=100)
    candidates: list[dict[str, Any]] = Field(default_factory=list)


class CompareRequest(BaseModel):
    candidate_a_id: str = Field(...)
    candidate_b_id: str = Field(...)
    job_description: str = Field(...)
    candidates: list[dict[str, Any]] = Field(default_factory=list)


app = FastAPI(title="TalentLens AI Backend") if FASTAPI_AVAILABLE else FastAPI()

if FASTAPI_AVAILABLE:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
def root() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "TalentLens AI backend is running",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return root()


@app.post("/rank")
def rank(request: RankRequest) -> dict[str, Any]:
    _ensure_backend_available()
    candidates = _resolve_candidates(getattr(request, "candidates", []))
    ranked = rank_candidates(candidates, request.job_description)
    top_k = max(1, min(int(getattr(request, "top_k", 10) or 10), len(ranked) or 1))
    return {
        "job_description": request.job_description,
        "count": min(top_k, len(ranked)),
        "results": [_rank_response(candidate) for candidate in ranked[:top_k]],
    }


@app.post("/compare")
def compare(request: CompareRequest) -> dict[str, Any]:
    _ensure_backend_available()
    candidate_a_id = str(getattr(request, "candidate_a_id", "")).strip()
    candidate_b_id = str(getattr(request, "candidate_b_id", "")).strip()

    if not candidate_a_id or not candidate_b_id:
        raise HTTPException(status_code=400, detail="Both candidate IDs are required.")
    if candidate_a_id == candidate_b_id:
        raise HTTPException(status_code=400, detail="Comparison requires two unique candidates.")

    candidates = _resolve_candidates(getattr(request, "candidates", []))
    by_id = {_candidate_id(candidate): candidate for candidate in candidates}
    if candidate_a_id not in by_id or candidate_b_id not in by_id:
        raise HTTPException(status_code=404, detail="One or both candidate IDs were not found.")

    ranked = rank_candidates([by_id[candidate_a_id], by_id[candidate_b_id]], request.job_description)
    ranked_by_id = {candidate.candidate_id: candidate for candidate in ranked}
    candidate_a = ranked_by_id[candidate_a_id]
    candidate_b = ranked_by_id[candidate_b_id]
    winner = candidate_a if candidate_a.final_score >= candidate_b.final_score else candidate_b

    return {
        "job_description": request.job_description,
        "candidate_a": _compare_response(candidate_a),
        "candidate_b": _compare_response(candidate_b),
        "winner_candidate_id": winner.candidate_id,
        "winner_name": _candidate_name(winner.raw_candidate),
        "score_delta": round(abs(candidate_a.final_score - candidate_b.final_score), 2),
    }


@app.post("/upload-candidate")
async def upload_candidate(file: UploadFile | None = File(default=None)) -> dict[str, Any]:
    _ensure_backend_available()
    if file is None:
        return {
            "status": "awaiting_file",
            "message": "Upload a candidate JSON, PDF, DOCX, or image file.",
            "supported_formats": ["json", "pdf", "docx", "png", "jpg", "jpeg", "webp"],
        }

    filename = getattr(file, "filename", None) or "candidate"
    payload = await file.read()
    try:
        parsed = parse_uploaded_candidate(filename, payload)
    except json.JSONDecodeError as exc:  # pragma: no cover - validation path
        raise HTTPException(status_code=400, detail="Invalid JSON candidate upload.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    candidate_profile = parsed.candidate_profile
    return {
        "status": "parsed",
        "message": f"{Path(filename).suffix.lower().lstrip('.').upper() or 'Document'} parsed successfully.",
        "candidate_profile": candidate_profile,
        "candidate_record": _normalize_candidate_record(candidate_profile),
        "parsed_summary": {
            "candidate_id": str(candidate_profile.get("candidate_id") or "unknown"),
            "name": str(candidate_profile.get("name") or "Candidate Profile"),
            "skills": candidate_profile.get("skills") or [],
            "education": candidate_profile.get("education") or "",
            "experience_summary": candidate_profile.get("experience_summary") or "",
            "source": "User Added",
        },
    }


def create_app() -> Any:
    """Factory primarily for import tests and future deployment hooks."""

    return app


def _ensure_backend_available() -> None:
    if not FASTAPI_AVAILABLE:
        raise RuntimeError(
            "FastAPI is not installed in this environment. Install requirements.txt to run the TalentLens backend API."
        )


def _load_candidates() -> list[dict[str, Any]]:
    custom_path = os.getenv("TALENTLENS_CANDIDATES_PATH", "").strip()
    paths = (custom_path,) if custom_path else DEFAULT_CANDIDATE_PATHS
    candidates = load_default_candidates(paths)
    if candidates:
        return candidates
    raise HTTPException(status_code=404, detail="No candidate dataset is available.")


def _resolve_candidates(extra_candidates: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for candidate in _load_candidates():
        candidate_id = _candidate_id(candidate)
        if candidate_id in seen_ids:
            continue
        seen_ids.add(candidate_id)
        merged.append(candidate)

    for candidate in extra_candidates or []:
        normalized = _normalize_candidate_record(candidate)
        candidate_id = _candidate_id(normalized)
        if candidate_id in seen_ids:
            continue
        seen_ids.add(candidate_id)
        merged.append(normalized)

    return merged


def _rank_response(candidate: RankedCandidate) -> dict[str, Any]:
    breakdown = candidate.to_dict().get("score_breakdown", {})
    raw = candidate.raw_candidate
    skills = _candidate_skills(raw)
    experience_summary = _experience_summary(raw)
    education_summary = _education_summary(raw)
    name = _candidate_name(raw)
    risk_level = _risk_level(candidate)
    hidden_reasoning = (
        candidate.hidden_gem.metadata.get("reasoning", {})
        if isinstance(candidate.hidden_gem.metadata, dict)
        else {}
    )
    learning_velocity = float(hidden_reasoning.get("learning_velocity", candidate.hidden_gem.score) or candidate.hidden_gem.score)
    technical_depth = float(hidden_reasoning.get("technical_strength", candidate.technical_fit.score) or candidate.technical_fit.score)
    payload = {
        "id": candidate.candidate_id,
        "candidate_id": candidate.candidate_id,
        "rank": candidate.rank,
        "name": name,
        "initials": _candidate_initials(name),
        "role": _candidate_role(raw),
        "profileLabel": _candidate_role(raw),
        "profile_label": _candidate_role(raw),
        "company": _candidate_company(raw),
        "location": _candidate_location(raw),
        "source": _candidate_source(raw),
        "education": education_summary,
        "degree": _candidate_degree(raw),
        "college": _candidate_college(raw),
        "experience": _experience_years(raw, candidate),
        "experienceSummary": experience_summary,
        "experience_summary": experience_summary,
        "skills": skills,
        "projects": _candidate_projects(raw),
        "certifications": _candidate_certifications(raw),
        "finalScore": candidate.final_score,
        "final_score": candidate.final_score,
        "semantic_similarity_score": candidate.semantic_similarity.score,
        "retrieval_rank": candidate.retrieval_rank,
        "technicalScore": candidate.technical_fit.score,
        "technical_fit_score": candidate.technical_fit.score,
        "experienceScore": candidate.experience.score,
        "experience_score": candidate.experience.score,
        "careerConsistency": candidate.career_consistency.score,
        "career_consistency_score": candidate.career_consistency.score,
        "skillClusterBonus": candidate.skill_cluster.score,
        "skill_cluster_bonus": candidate.skill_cluster.score,
        "behavioralScore": candidate.behavioral.score,
        "behavioral_score": candidate.behavioral.score,
        "authenticityScore": candidate.authenticity.score,
        "authenticity_score": candidate.authenticity.score,
        "cognitiveTwinScore": candidate.recruiter_cognitive_twin.score,
        "recruiter_cognitive_twin_score": candidate.recruiter_cognitive_twin.score,
        "hiddenGem": bool(candidate.hidden_gem.metadata.get("hidden_gem_flag", False)),
        "hidden_gem_flag": bool(candidate.hidden_gem.metadata.get("hidden_gem_flag", False)),
        "hiddenGemScore": candidate.hidden_gem.score,
        "hidden_gem_score": candidate.hidden_gem.score,
        "growthPotential": candidate.hidden_gem.score,
        "learningVelocity": round(learning_velocity, 2),
        "technicalDepth": round(technical_depth, 2),
        "hiringConfidence": candidate.hiring_confidence.score,
        "hiring_confidence": candidate.hiring_confidence.score,
        "confidenceLevel": candidate.hiring_confidence.metadata.get("confidence_level", ""),
        "riskLevel": risk_level,
        "risk_level": risk_level,
        "strengths": candidate.strengths,
        "weaknesses": candidate.risks,
        "risks": candidate.risks,
        "whyRanked": candidate.explanation,
        "why_ranked": candidate.explanation,
        "recruiterReasoning": candidate.recruiter_cognitive_twin.metadata.get("recruiter_reasoning", ""),
        "recruiter_reasoning": candidate.recruiter_cognitive_twin.metadata.get("recruiter_reasoning", ""),
        "authenticityRisk": _authenticity_risk_text(candidate),
        "authenticity_risk": _authenticity_risk_text(candidate),
        "interviewRecommendation": candidate.interview_recommendation,
        "interview_recommendation": candidate.interview_recommendation,
        "executiveSummary": candidate.executive_recruiter_summary,
        "executive_recruiter_summary": candidate.executive_recruiter_summary,
        "hiddenGemReason": candidate.hidden_gem.metadata.get("hidden_gem_reason", ""),
        "hidden_gem_reason": candidate.hidden_gem.metadata.get("hidden_gem_reason", ""),
        "searchReason": candidate.technical_fit.explanation,
        "search_reason": candidate.technical_fit.explanation,
        "gradient": _candidate_gradient(candidate.candidate_id),
        "scoreBreakdown": breakdown,
        "score_breakdown": breakdown,
    }
    return {
        **payload,
        "intelligence_card": candidate.intelligence_card(),
    }


def _compare_response(candidate: RankedCandidate) -> dict[str, Any]:
    return _rank_response(candidate)


def _candidate_id(candidate: dict[str, Any]) -> str:
    profile = candidate.get("profile") if isinstance(candidate.get("profile"), dict) else {}
    for key in ("candidate_id", "id", "profile_id", "user_id"):
        value = candidate.get(key) or profile.get(key)
        if value not in (None, ""):
            return str(value)
    return "unknown"


def _candidate_name(candidate: dict[str, Any]) -> str:
    profile = candidate.get("profile") if isinstance(candidate.get("profile"), dict) else {}
    return str(profile.get("name") or profile.get("full_name") or candidate.get("name") or "Candidate Profile")


def _candidate_skills(candidate: dict[str, Any]) -> list[str]:
    skills = candidate.get("skills") or []
    if isinstance(skills, list):
        return [str(skill) for skill in skills]
    if skills in (None, ""):
        return []
    return [str(skills)]


def _normalize_candidate_record(candidate: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(candidate, dict):
        return {}

    if isinstance(candidate.get("profile"), dict):
        profile = dict(candidate.get("profile") or {})
        normalized = dict(candidate)
    else:
        profile = {}
        normalized = {}

    candidate_id = str(
        candidate.get("candidate_id")
        or candidate.get("id")
        or profile.get("candidate_id")
        or profile.get("id")
        or f"user_{abs(hash(json.dumps(candidate, sort_keys=True, default=str)))}"
    )
    name = str(
        profile.get("name")
        or profile.get("full_name")
        or candidate.get("name")
        or candidate.get("candidate_name")
        or "Candidate Profile"
    )
    role = str(
        candidate.get("role")
        or candidate.get("profile_label")
        or profile.get("headline")
        or profile.get("role")
        or "Candidate Profile"
    )
    location = str(profile.get("location") or candidate.get("location") or "India")
    experience_years = _coerce_float(
        candidate.get("experience")
        or candidate.get("years_experience")
        or profile.get("years_experience")
        or profile.get("total_experience")
    )
    career_history = candidate.get("career_history") if isinstance(candidate.get("career_history"), list) else []
    if not career_history and (role or experience_years):
        career_history = [
            {
                "title": role or "Candidate Profile",
                "company": candidate.get("company") or candidate.get("college") or candidate.get("source") or "Candidate Profile",
                "duration_years": experience_years or 0.0,
                "summary": candidate.get("experience_summary") or candidate.get("experienceSummary") or candidate.get("resumeText") or "",
            }
        ]

    education = candidate.get("education")
    if isinstance(education, list):
        education_entries = education
    else:
        degree = str(candidate.get("degree") or profile.get("degree") or "")
        college = str(candidate.get("college") or profile.get("college") or "")
        education_entries = []
        if degree or college or education:
            education_entries.append(
                {
                    "degree": degree,
                    "institution": college,
                    "summary": str(education or ""),
                }
            )

    normalized_profile = {
        **profile,
        "candidate_id": candidate_id,
        "name": name,
        "headline": role,
        "years_experience": experience_years or 0.0,
        "location": location,
        "email": profile.get("email") or candidate.get("email") or "",
        "phone": profile.get("phone") or candidate.get("phone") or "",
        "linkedin": profile.get("linkedin") or candidate.get("linkedin") or "",
        "github": profile.get("github") or candidate.get("github") or "",
        "summary": profile.get("summary")
        or candidate.get("resumeText")
        or candidate.get("experience_summary")
        or candidate.get("experienceSummary")
        or "",
    }

    normalized.update(
        {
            "candidate_id": candidate_id,
            "profile": normalized_profile,
            "career_history": career_history,
            "education": education_entries,
            "skills": _ensure_text_list(candidate.get("skills")),
            "projects": _ensure_text_list(candidate.get("projects")),
            "certifications": _ensure_text_list(candidate.get("certifications")),
            "redrob_signals": candidate.get("redrob_signals") if isinstance(candidate.get("redrob_signals"), dict) else {},
            "source": candidate.get("source") or "User Added",
        }
    )
    return normalized


def _ensure_text_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value in (None, ""):
        return []
    return [str(value).strip()]


def _coerce_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _candidate_role(candidate: dict[str, Any]) -> str:
    profile = candidate.get("profile") if isinstance(candidate.get("profile"), dict) else {}
    return str(
        candidate.get("role")
        or candidate.get("profile_label")
        or profile.get("headline")
        or profile.get("role")
        or "Candidate Profile"
    )


def _candidate_company(candidate: dict[str, Any]) -> str:
    profile = candidate.get("profile") if isinstance(candidate.get("profile"), dict) else {}
    if candidate.get("company"):
        return str(candidate.get("company"))
    career_history = candidate.get("career_history") if isinstance(candidate.get("career_history"), list) else []
    for entry in career_history:
        if isinstance(entry, dict):
            company = entry.get("company") or entry.get("organization")
            if company:
                return str(company)
    return str(profile.get("company") or _candidate_college(candidate) or candidate.get("source") or "Candidate Profile")


def _candidate_location(candidate: dict[str, Any]) -> str:
    profile = candidate.get("profile") if isinstance(candidate.get("profile"), dict) else {}
    return str(profile.get("location") or candidate.get("location") or "India")


def _candidate_source(candidate: dict[str, Any]) -> str:
    source = str(candidate.get("source") or "Built-In").replace("_", " ").strip()
    return source.title() if source.isupper() else source


def _candidate_degree(candidate: dict[str, Any]) -> str:
    if candidate.get("degree"):
        return str(candidate.get("degree"))
    education = candidate.get("education") if isinstance(candidate.get("education"), list) else []
    for entry in education:
        if isinstance(entry, dict) and entry.get("degree"):
            return str(entry.get("degree"))
    return ""


def _candidate_college(candidate: dict[str, Any]) -> str:
    if candidate.get("college"):
        return str(candidate.get("college"))
    education = candidate.get("education") if isinstance(candidate.get("education"), list) else []
    for entry in education:
        if isinstance(entry, dict):
            college = entry.get("institution") or entry.get("college") or entry.get("school")
            if college:
                return str(college)
    return ""


def _education_summary(candidate: dict[str, Any]) -> str:
    if candidate.get("education") and not isinstance(candidate.get("education"), list):
        return str(candidate.get("education"))
    degree = _candidate_degree(candidate)
    college = _candidate_college(candidate)
    parts = [part for part in (degree, college) if part]
    return " - ".join(parts) if parts else "Candidate Profile"


def _candidate_projects(candidate: dict[str, Any]) -> list[str]:
    return _ensure_text_list(candidate.get("projects"))


def _candidate_certifications(candidate: dict[str, Any]) -> list[str]:
    return _ensure_text_list(candidate.get("certifications"))


def _experience_summary(candidate: dict[str, Any]) -> str:
    for key in ("experience_summary", "experienceSummary"):
        value = candidate.get(key)
        if value not in (None, ""):
            return str(value)
    years = _coerce_float(
        candidate.get("experience")
        or candidate.get("years_experience")
        or (candidate.get("profile") or {}).get("years_experience")
    )
    if years > 0:
        return f"{years:.0f} year{'s' if years != 1 else ''} experience"
    return "Candidate Profile"


def _experience_years(candidate: dict[str, Any], ranked: RankedCandidate) -> float:
    years = ranked.experience.metadata.get("candidate_years")
    if years not in (None, ""):
        return float(years)
    return _coerce_float(
        candidate.get("experience")
        or candidate.get("years_experience")
        or (candidate.get("profile") or {}).get("years_experience")
    )


def _risk_level(candidate: RankedCandidate) -> str:
    level = str(candidate.authenticity.metadata.get("risk_level", "") or "MEDIUM").upper()
    return level.title()


def _authenticity_risk_text(candidate: RankedCandidate) -> str:
    level = _risk_level(candidate)
    if candidate.authenticity.gaps:
        return f"{level} authenticity risk. {candidate.authenticity.gaps[0]}"
    if candidate.authenticity.evidence:
        return f"{level} authenticity risk. {candidate.authenticity.evidence[0]}"
    return f"{level} authenticity risk based on verification, profile completeness, and corroborating evidence."


def _candidate_initials(name: str) -> str:
    tokens = [token for token in str(name).split() if token]
    if not tokens:
        return "CP"
    if len(tokens) == 1:
        return tokens[0][:2].upper()
    return (tokens[0][0] + tokens[-1][0]).upper()


def _candidate_gradient(seed: str) -> str:
    gradients = (
        "linear-gradient(135deg,#8b5cf6,#3b82f6)",
        "linear-gradient(135deg,#06b6d4,#8b5cf6)",
        "linear-gradient(135deg,#10b981,#3b82f6)",
        "linear-gradient(135deg,#f59e0b,#ef4444)",
        "linear-gradient(135deg,#ec4899,#8b5cf6)",
    )
    return gradients[abs(hash(seed)) % len(gradients)]
