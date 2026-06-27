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
except ImportError:  # pragma: no cover - direct execution support
    from ranker import RankedCandidate, load_default_candidates, rank_candidates


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATE_PATHS = (
    PROJECT_ROOT / "data" / "candidates.jsonl",
    PROJECT_ROOT / "data" / "sample_candidates.json",
)


class RankRequest(BaseModel):
    job_description: str = Field(..., description="Target job description")
    top_k: int = Field(default=10, ge=1, le=100)


class CompareRequest(BaseModel):
    candidate_a_id: str = Field(...)
    candidate_b_id: str = Field(...)
    job_description: str = Field(...)


app = FastAPI(title="TalentLens AI Backend") if FASTAPI_AVAILABLE else FastAPI()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "TalentLens AI backend is running",
    }


@app.post("/rank")
def rank(request: RankRequest) -> dict[str, Any]:
    _ensure_backend_available()
    candidates = _load_candidates()
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

    candidates = _load_candidates()
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
            "message": "Upload a candidate JSON, PDF, or DOCX file.",
            "supported_formats": ["json", "pdf", "docx"],
        }

    filename = getattr(file, "filename", None) or "candidate"
    suffix = Path(filename).suffix.lower()

    if suffix == ".json":
        payload = await file.read()
        try:
            parsed = json.loads(payload.decode("utf-8"))
        except Exception as exc:  # pragma: no cover - validation path
            raise HTTPException(status_code=400, detail="Invalid JSON candidate upload.") from exc
        candidate = parsed.get("profile") if isinstance(parsed, dict) and isinstance(parsed.get("profile"), dict) else parsed
        return {
            "status": "parsed",
            "message": "Candidate JSON parsed successfully.",
            "candidate_profile": parsed,
            "parsed_summary": {
                "candidate_id": _candidate_id(parsed if isinstance(parsed, dict) else {}),
                "name": _candidate_name(parsed if isinstance(parsed, dict) else {}),
                "skills": _candidate_skills(parsed if isinstance(parsed, dict) else {}),
                "education": (parsed.get("education") if isinstance(parsed, dict) else []) or [],
                "source": "Uploaded JSON",
            },
        }

    if suffix in {".pdf", ".docx"}:
        return {
            "status": "not_implemented",
            "message": (
                "Backend route structure is ready, but this backend demo currently supports structured JSON upload only. "
                "PDF and DOCX resume parsing remains available in the frontend workflow."
            ),
            "supported_formats": ["json"],
            "received_filename": filename,
        }

    raise HTTPException(status_code=400, detail="Unsupported file type. Use JSON, PDF, or DOCX.")


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


def _rank_response(candidate: RankedCandidate) -> dict[str, Any]:
    return {
        "rank": candidate.rank,
        "candidate_id": candidate.candidate_id,
        "name": _candidate_name(candidate.raw_candidate),
        "final_score": candidate.final_score,
        "semantic_similarity_score": candidate.semantic_similarity.score,
        "retrieval_rank": candidate.retrieval_rank,
        "recruiter_cognitive_twin_score": candidate.recruiter_cognitive_twin.score,
        "hidden_gem_score": candidate.hidden_gem.score,
        "hiring_confidence": candidate.hiring_confidence.score,
        "strengths": candidate.strengths,
        "weaknesses": candidate.risks,
        "why_ranked": candidate.explanation,
        "interview_recommendation": candidate.interview_recommendation,
    }


def _compare_response(candidate: RankedCandidate) -> dict[str, Any]:
    return {
        "candidate_id": candidate.candidate_id,
        "name": _candidate_name(candidate.raw_candidate),
        "final_score": candidate.final_score,
        "semantic_similarity_score": candidate.semantic_similarity.score,
        "retrieval_rank": candidate.retrieval_rank,
        "technical_fit_score": candidate.technical_fit.score,
        "experience_score": candidate.experience.score,
        "career_consistency_score": candidate.career_consistency.score,
        "behavioral_score": candidate.behavioral.score,
        "authenticity_score": candidate.authenticity.score,
        "recruiter_cognitive_twin_score": candidate.recruiter_cognitive_twin.score,
        "hidden_gem_score": candidate.hidden_gem.score,
        "hiring_confidence": candidate.hiring_confidence.score,
        "strengths": candidate.strengths,
        "weaknesses": candidate.risks,
        "why_ranked": candidate.explanation,
        "interview_recommendation": candidate.interview_recommendation,
    }


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
