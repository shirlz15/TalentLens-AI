"""Semantic retrieval smoke test for TalentLens AI."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.ranker import load_candidates_json, rank_candidates  # noqa: E402
from backend.report_export import build_ranked_report_rows, write_ranked_report_csv  # noqa: E402
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

    write_ranked_report_csv(build_ranked_report_rows(ranked), OUTPUT_PATH)
    print(f"Wrote semantic ranking results to {OUTPUT_PATH}")
    print(f"Top semantic retrieval IDs: {[item['candidate_id'] for item in retrieved]}")


if __name__ == "__main__":
    main()
