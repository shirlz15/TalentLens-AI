"""Semantic retrieval smoke test for TalentLens AI."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.ranker import load_candidates_json, rank_candidates  # noqa: E402
from backend.semantic_search import build_faiss_index, retrieve_similar_candidates  # noqa: E402


SAMPLE_JOB_DESCRIPTION = """
Senior AI/ML Engineer for a recruiter intelligence platform.
Need Python, SQL, machine learning, deep learning, explainable AI,
retrieval-augmented generation, semantic search, and production API experience.
"""

SAMPLE_CANDIDATES_PATH = PROJECT_ROOT / "data" / "sample_candidates.json"
OUTPUT_PATH = PROJECT_ROOT / "output" / "semantic_results.csv"


def main() -> None:
    candidates = load_candidates_json(SAMPLE_CANDIDATES_PATH)
    index_bundle = build_faiss_index(candidates)
    retrieved = retrieve_similar_candidates(SAMPLE_JOB_DESCRIPTION, candidates, top_k=min(5, len(candidates)))
    ranked = rank_candidates(candidates, SAMPLE_JOB_DESCRIPTION)[:5]

    print(f"Semantic backend: {index_bundle['backend']}")
    for candidate in ranked:
        print(
            f"{candidate.rank}. {candidate.candidate_id} | "
            f"semantic={candidate.semantic_similarity.score:.2f} | "
            f"final={candidate.final_score:.2f}"
        )

    write_results(ranked, OUTPUT_PATH)
    print(f"Wrote semantic ranking results to {OUTPUT_PATH}")
    print(f"Top semantic retrieval IDs: {[item['candidate_id'] for item in retrieved]}")


def write_results(ranked_candidates: list[Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "rank",
        "candidate_id",
        "name",
        "final_score",
        "semantic_similarity_score",
        "retrieval_rank",
        "recruiter_cognitive_twin_score",
        "hidden_gem_score",
        "hiring_confidence_score",
        "why_ranked",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for candidate in ranked_candidates:
            writer.writerow(
                {
                    "rank": candidate.rank,
                    "candidate_id": candidate.candidate_id,
                    "name": candidate.raw_candidate.get("profile", {}).get("name", candidate.candidate_id),
                    "final_score": candidate.final_score,
                    "semantic_similarity_score": candidate.semantic_similarity.score,
                    "retrieval_rank": candidate.retrieval_rank,
                    "recruiter_cognitive_twin_score": candidate.recruiter_cognitive_twin.score,
                    "hidden_gem_score": candidate.hidden_gem.score,
                    "hiring_confidence_score": candidate.hiring_confidence.score,
                    "why_ranked": candidate.explanation,
                }
            )


if __name__ == "__main__":
    main()
