"""Semantic retrieval helpers for TalentLens AI.

This module adds an optional embedding + FAISS retrieval layer on top of the
existing deterministic ranking engine. It is intentionally defensive:

- If `sentence-transformers` is installed, it uses a lightweight default model.
- If FAISS is installed, it builds a vector index for fast retrieval.
- If either dependency is missing, TalentLens falls back to deterministic
  hashed embeddings and NumPy/Python cosine similarity so the project still
  works offline.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import hashlib
import math
from typing import Any

try:
    import numpy as np
except ImportError:  # pragma: no cover - fallback keeps module importable
    np = None  # type: ignore[assignment]

try:
    import faiss  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - dependency is optional
    faiss = None  # type: ignore[assignment]

try:
    from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - dependency is optional
    SentenceTransformer = None  # type: ignore[assignment]


DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_HASH_DIMENSION = 384


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


def build_faiss_index(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a semantic retrieval structure for the provided candidates."""

    texts = [build_candidate_text(candidate) for candidate in candidates]
    embeddings, backend = _embed_texts(texts)
    candidate_ids = [_candidate_id(candidate) for candidate in candidates]
    index = None

    if faiss is not None and np is not None and len(candidates) > 0:
        matrix = np.asarray(embeddings, dtype="float32")
        normalized = _normalize_matrix(matrix)
        index = faiss.IndexFlatIP(normalized.shape[1])
        index.add(normalized)
        embeddings = normalized

    return {
        "index": index,
        "candidate_ids": candidate_ids,
        "candidates": candidates,
        "texts": texts,
        "embeddings": embeddings,
        "backend": backend,
        "model_name": DEFAULT_EMBEDDING_MODEL if SentenceTransformer is not None else "hashed-fallback",
    }


def retrieve_similar_candidates(
    job_description: str,
    candidates: list[dict[str, Any]],
    top_k: int = 100,
) -> list[dict[str, Any]]:
    """Retrieve the most semantically similar candidates for a JD."""

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


def semantic_retrieval_map(
    job_description: str,
    candidates: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Return retrieval metadata for every candidate keyed by candidate_id."""

    results = retrieve_similar_candidates(job_description, candidates, top_k=len(candidates))
    return {str(item["candidate_id"]): item for item in results}


def _semantic_scores_from_index(job_description: str, index_bundle: dict[str, Any]) -> list[float]:
    query_embedding, _backend = _embed_texts([job_description])
    if np is not None:
        query_matrix = np.asarray(query_embedding, dtype="float32")
        query_matrix = _normalize_matrix(query_matrix)
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


def _embed_texts(texts: list[str]) -> tuple[list[Any], str]:
    if SentenceTransformer is not None and np is not None:
        try:
            model = _load_sentence_model(DEFAULT_EMBEDDING_MODEL)
            vectors = model.encode(texts, normalize_embeddings=False)
            matrix = np.asarray(vectors, dtype="float32")
            return matrix, "sentence-transformers"
        except Exception:  # pragma: no cover - dependency/runtime fallback
            pass

    if np is not None:
        matrix = np.asarray([_hashed_embedding(text) for text in texts], dtype="float32")
        return matrix, "hashed-fallback"

    vectors = [_hashed_embedding(text) for text in texts]
    return vectors, "hashed-fallback"


@lru_cache(maxsize=2)
def _load_sentence_model(model_name: str) -> Any:
    if SentenceTransformer is None:  # pragma: no cover - dependency missing
        raise RuntimeError("sentence-transformers is not installed")
    return SentenceTransformer(model_name)


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


def _normalize_matrix(matrix: Any) -> Any:
    if np is None:
        return matrix
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
