"""Lazy semantic retrieval helpers for TalentLens AI.

Render free instances have a tight memory ceiling, so this module keeps startup
light: no SentenceTransformer, FAISS, torch, transformers, or NumPy imports
happen at module import time. Heavy dependencies are imported only from /rank
execution paths and cached after the first successful use. If any semantic
dependency is unavailable, retrieval falls back to deterministic hashed vectors.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
import os
import threading
from typing import Any


DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_HASH_DIMENSION = 384

_model_lock = threading.Lock()
_index_lock = threading.Lock()
_sentence_model_cache: dict[str, Any] = {}
_index_cache: dict[str, dict[str, Any]] = {}
_sentence_transformers_available: bool | None = None
_faiss_available: bool | None = None
_numpy_available: bool | None = None
_last_backend: str = "not-initialized"
_model_load_count = 0
_index_build_count = 0


def semantic_retrieval_map(
    job_description: str,
    candidates: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Return retrieval metadata for every candidate keyed by candidate_id."""

    results = retrieve_similar_candidates(job_description, candidates, top_k=len(candidates))
    return {str(item["candidate_id"]): item for item in results}


def retrieve_similar_candidates(
    job_description: str,
    candidates: list[dict[str, Any]],
    top_k: int = 100,
) -> list[dict[str, Any]]:
    """Retrieve semantically similar candidates with lazy FAISS/model loading."""

    if not candidates:
        return []

    index_bundle = build_faiss_index(candidates)
    top_k = max(1, min(top_k, len(candidates)))
    scores = _semantic_scores_from_index(job_description, index_bundle)
    scored = []

    for candidate, score in zip(candidates, scores, strict=False):
        scored.append(
            {
                "candidate_id": _candidate_id(candidate),
                "candidate": candidate,
                "semantic_similarity_score": round(_similarity_to_percentage(score), 2),
                "raw_similarity": round(float(score), 6),
                "backend": index_bundle["backend"],
            }
        )

    scored.sort(
        key=lambda item: (
            item["semantic_similarity_score"],
            item["candidate_id"],
        ),
        reverse=True,
    )
    for rank, item in enumerate(scored, start=1):
        item["retrieval_rank"] = rank
    return scored[:top_k]


def semantic_similarity_score(job_description: str, candidate: dict[str, Any]) -> float:
    """Return a 0-100 semantic similarity score for one candidate."""

    results = retrieve_similar_candidates(job_description, [candidate], top_k=1)
    if not results:
        return 0.0
    return float(results[0]["semantic_similarity_score"])


def build_faiss_index(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Build and cache the semantic retrieval structure for candidate profiles."""

    cache_key = _candidate_cache_key(candidates)
    cached = _index_cache.get(cache_key)
    if cached is not None:
        return cached

    with _index_lock:
        cached = _index_cache.get(cache_key)
        if cached is not None:
            return cached

        bundle = _build_index_uncached(candidates)
        _index_cache[cache_key] = bundle
        _trim_index_cache(max_items=2)
        return bundle


def semantic_runtime_status() -> dict[str, Any]:
    """Expose lightweight diagnostics for local deployment verification."""

    return {
        "backend": _last_backend,
        "semantic_backend_mode": _semantic_backend_mode(),
        "model_cached": bool(_sentence_model_cache),
        "model_load_count": _model_load_count,
        "index_cache_entries": len(_index_cache),
        "index_build_count": _index_build_count,
        "sentence_transformers_available": _sentence_transformers_available,
        "faiss_available": _faiss_available,
        "numpy_available": _numpy_available,
    }


def build_candidate_text(candidate: dict[str, Any]) -> str:
    """Combine candidate evidence into a single retrieval document."""

    profile = candidate.get("profile") if isinstance(candidate.get("profile"), dict) else {}
    education = candidate.get("education") if isinstance(candidate.get("education"), list) else []
    career_history = candidate.get("career_history") if isinstance(candidate.get("career_history"), list) else []
    projects = _list_values(candidate.get("projects"))
    certifications = _list_values(candidate.get("certifications"))
    skills = _list_values(candidate.get("skills"))
    signals = candidate.get("redrob_signals") if isinstance(candidate.get("redrob_signals"), dict) else {}

    sections: list[str] = []
    name = _value(profile, "name", "full_name")
    headline = _value(profile, "headline", "role", "summary")
    summary = _value(profile, "summary", "about", "bio")
    years_experience = _value(profile, "years_experience")

    if name:
        sections.append(f"Name: {name}")
    if headline:
        sections.append(f"Headline: {headline}")
    if summary:
        sections.append(f"Summary: {summary}")
    if years_experience not in ("", None):
        sections.append(f"Experience: {years_experience} years")
    if skills:
        sections.append(f"Skills: {', '.join(skills)}")

    education_lines = []
    for item in education:
        if isinstance(item, dict):
            pieces = [
                str(item.get("degree") or "").strip(),
                str(item.get("college") or item.get("school") or item.get("institution") or "").strip(),
                str(item.get("specialization") or item.get("field") or "").strip(),
            ]
            line = ", ".join(piece for piece in pieces if piece)
        else:
            line = str(item).strip()
        if line:
            education_lines.append(line)
    if education_lines:
        sections.append(f"Education: {'; '.join(education_lines)}")

    career_lines = []
    for item in career_history:
        if isinstance(item, dict):
            pieces = [
                str(item.get("title") or "").strip(),
                str(item.get("company") or item.get("organization") or "").strip(),
                str(item.get("description") or "").strip(),
            ]
            timeline = " to ".join(
                piece
                for piece in (
                    str(item.get("start_date") or "").strip(),
                    str(item.get("end_date") or "").strip(),
                )
                if piece
            )
            line_parts = [", ".join(piece for piece in pieces[:2] if piece)]
            if timeline:
                line_parts.append(f"({timeline})")
            if pieces[2]:
                line_parts.append(pieces[2])
            line = " ".join(part for part in line_parts if part).strip()
        else:
            line = str(item).strip()
        if line:
            career_lines.append(line)
    if career_lines:
        sections.append(f"Career History: {'; '.join(career_lines)}")

    if projects:
        sections.append(f"Projects: {'; '.join(projects)}")
    if certifications:
        sections.append(f"Certifications: {'; '.join(certifications)}")

    signal_summary = _summarize_redrob_signals(signals)
    if signal_summary:
        sections.append(f"Redrob Signals: {signal_summary}")

    return "\n".join(section for section in sections if section).strip()


def _build_index_uncached(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    global _index_build_count, _last_backend

    texts = [build_candidate_text(candidate) for candidate in candidates]
    embeddings, backend = _embed_texts(texts)
    candidate_ids = [_candidate_id(candidate) for candidate in candidates]
    np = _import_numpy()
    faiss = _import_faiss()
    index = None

    if faiss is not None and np is not None and len(candidates) > 0:
        try:
            matrix = np.asarray(embeddings, dtype="float32")
            normalized = _normalize_matrix(matrix, np)
            index = faiss.IndexFlatIP(normalized.shape[1])
            index.add(normalized)
            embeddings = normalized
            backend = f"{backend}+faiss"
        except Exception:
            index = None

    _index_build_count += 1
    _last_backend = backend
    return {
        "index": index,
        "candidate_ids": candidate_ids,
        "candidates": candidates,
        "texts": texts,
        "embeddings": embeddings,
        "backend": backend,
        "model_name": DEFAULT_EMBEDDING_MODEL if backend.startswith("sentence-transformers") else "hashed-fallback",
    }


def _semantic_scores_from_index(job_description: str, index_bundle: dict[str, Any]) -> list[float]:
    query_embedding, _backend = _embed_texts([job_description])
    np = _import_numpy()

    if np is not None:
        query_matrix = np.asarray(query_embedding, dtype="float32")
        query_matrix = _normalize_matrix(query_matrix, np)
        if index_bundle["index"] is not None:
            distances, indices = index_bundle["index"].search(query_matrix, len(index_bundle["candidate_ids"]))
            score_by_position = [0.0] * len(index_bundle["candidate_ids"])
            for idx, distance in zip(indices[0], distances[0], strict=False):
                score_by_position[int(idx)] = float(distance)
            return score_by_position

        candidate_matrix = np.asarray(index_bundle["embeddings"], dtype="float32")
        if candidate_matrix.size == 0:
            return [0.0] * len(index_bundle["candidate_ids"])
        return [float(value) for value in candidate_matrix.dot(query_matrix[0])]

    query_vector = query_embedding[0]
    return [_cosine_similarity(query_vector, vector) for vector in index_bundle["embeddings"]]


def _embed_texts(texts: list[str]) -> tuple[Any, str]:
    global _last_backend

    np = _import_numpy()
    model = _get_sentence_model()
    if model is not None and np is not None:
        try:
            vectors = model.encode(texts, normalize_embeddings=False)
            matrix = np.asarray(vectors, dtype="float32")
            _last_backend = "sentence-transformers"
            return matrix, "sentence-transformers"
        except Exception:
            pass

    vectors = [_hashed_embedding(text) for text in texts]
    if np is not None:
        matrix = np.asarray(vectors, dtype="float32")
        _last_backend = "hashed-fallback"
        return matrix, "hashed-fallback"

    _last_backend = "hashed-fallback"
    return vectors, "hashed-fallback"


def _get_sentence_model() -> Any | None:
    global _model_load_count

    if not _sentence_transformers_enabled():
        return None
    if DEFAULT_EMBEDDING_MODEL in _sentence_model_cache:
        return _sentence_model_cache[DEFAULT_EMBEDDING_MODEL]

    with _model_lock:
        if DEFAULT_EMBEDDING_MODEL in _sentence_model_cache:
            return _sentence_model_cache[DEFAULT_EMBEDDING_MODEL]
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]

            model = SentenceTransformer(DEFAULT_EMBEDDING_MODEL)
        except Exception:
            _disable_sentence_transformers()
            return None

        _sentence_model_cache[DEFAULT_EMBEDDING_MODEL] = model
        _model_load_count += 1
        return model


def _sentence_transformers_enabled() -> bool:
    global _sentence_transformers_available

    if _semantic_backend_mode() in {"deterministic", "hashed", "hash", "fallback"}:
        _sentence_transformers_available = False
        return False
    if _sentence_transformers_available is not None:
        return _sentence_transformers_available
    try:
        import sentence_transformers  # noqa: F401  # type: ignore[import-not-found]

        _sentence_transformers_available = True
    except Exception:
        _sentence_transformers_available = False
    return _sentence_transformers_available


def _semantic_backend_mode() -> str:
    return os.getenv("TALENTLENS_SEMANTIC_BACKEND", "auto").strip().lower() or "auto"


def _disable_sentence_transformers() -> None:
    global _sentence_transformers_available

    _sentence_transformers_available = False


def _import_numpy() -> Any | None:
    global _numpy_available

    if _numpy_available is False:
        return None
    try:
        import numpy as np  # type: ignore[import-not-found]

        _numpy_available = True
        return np
    except Exception:
        _numpy_available = False
        return None


def _import_faiss() -> Any | None:
    global _faiss_available

    if _faiss_available is False:
        return None
    try:
        import faiss  # type: ignore[import-not-found]

        _faiss_available = True
        return faiss
    except Exception:
        _faiss_available = False
        return None


def _hashed_embedding(text: str) -> list[float]:
    tokens = _tokenize(text)
    counts = Counter(tokens)
    vector = [0.0] * DEFAULT_HASH_DIMENSION
    if not counts:
        return vector

    for token, weight in counts.items():
        digest = hashlib.md5(token.encode("utf-8")).hexdigest()
        index = int(digest[:8], 16) % DEFAULT_HASH_DIMENSION
        vector[index] += float(weight)

    norm = math.sqrt(sum(value * value for value in vector))
    if norm <= 0:
        return vector
    return [value / norm for value in vector]


def _normalize_matrix(matrix: Any, np: Any) -> Any:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm <= 0 or right_norm <= 0:
        return 0.0
    return dot / (left_norm * right_norm)


def _similarity_to_percentage(value: float) -> float:
    bounded = max(-1.0, min(1.0, float(value)))
    return max(0.0, min(100.0, (bounded + 1.0) * 50.0))


def _candidate_cache_key(candidates: list[dict[str, Any]]) -> str:
    fingerprint = [
        {
            "id": _candidate_id(candidate),
            "text": build_candidate_text(candidate),
        }
        for candidate in candidates
    ]
    payload = json.dumps(fingerprint, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _trim_index_cache(max_items: int) -> None:
    while len(_index_cache) > max_items:
        oldest_key = next(iter(_index_cache))
        _index_cache.pop(oldest_key, None)


def _tokenize(text: str) -> list[str]:
    normalized = []
    for raw in str(text or "").lower().replace("/", " ").replace("-", " ").split():
        token = "".join(ch for ch in raw if ch.isalnum() or ch in {"+", "#"})
        if len(token) >= 2:
            normalized.append(token)
    return normalized


def _list_values(value: Any) -> list[str]:
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            if isinstance(item, dict):
                line = ", ".join(str(piece).strip() for piece in item.values() if str(piece).strip())
            else:
                line = str(item).strip()
            if line:
                result.append(line)
        return result
    if value in (None, ""):
        return []
    return [str(value).strip()]


def _value(container: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in container and container[key] not in (None, ""):
            return container[key]
    return ""


def _summarize_redrob_signals(signals: dict[str, Any]) -> str:
    if not signals:
        return ""
    highlights: list[str] = []
    response = signals.get("recruiter_response_rate")
    completeness = signals.get("profile_completeness_score")
    github = signals.get("github_activity_score")

    if response not in (None, ""):
        highlights.append(f"recruiter response rate {response}")
    if completeness not in (None, ""):
        highlights.append(f"profile completeness {completeness}")
    if github not in (None, ""):
        highlights.append(f"github activity {github}")
    if signals.get("open_to_work_flag"):
        highlights.append("open to work")
    if signals.get("verified_email"):
        highlights.append("verified email")
    if signals.get("verified_phone"):
        highlights.append("verified phone")
    if signals.get("linkedin_connected"):
        highlights.append("linkedin connected")
    return ", ".join(highlights)


def _candidate_id(candidate: dict[str, Any]) -> str:
    profile = candidate.get("profile") if isinstance(candidate.get("profile"), dict) else {}
    for key in ("candidate_id", "id", "profile_id", "user_id"):
        value = candidate.get(key) or profile.get(key)
        if value not in (None, ""):
            return str(value)
    for key in ("email", "linkedin_url", "name", "full_name"):
        value = profile.get(key)
        if value not in (None, ""):
            return str(value)
    return "unknown"
