"""Run TalentLens ranking on sample candidates and export top 10 results."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.ranker import rank_candidates, score_breakdown  # noqa: E402


SAMPLE_JOB_DESCRIPTION = """
Senior Data Scientist required for a high-growth recruiting intelligence team.
Must have Python, SQL, machine learning, statistics, and data analysis experience.
Minimum 5 years of experience. Strong communication, stakeholder collaboration,
and evidence-driven problem solving are important. Nice to have: cloud exposure,
GitHub activity, and experience building explainable ranking systems.
"""

SAMPLE_CANDIDATES_PATH = PROJECT_ROOT / "data" / "sample_candidates.json"
OUTPUT_PATH = PROJECT_ROOT / "output" / "results.csv"

OUTPUT_FIELDS = [
    "rank",
    "candidate_id",
    "final_score",
    "technical_fit_score",
    "experience_score",
    "career_consistency_score",
    "skill_cluster_bonus",
    "behavioral_score",
    "authenticity_score",
    "authenticity_risk_level",
    "risk_level",
    "recruiter_cognitive_twin_score",
    "recruiter_reasoning",
    "hidden_gem_score",
    "hidden_gem_flag",
    "hidden_gem_reason",
    "recruiter_decision",
    "recruiter_decision_reason",
    "hiring_confidence_score",
    "confidence_level",
    "executive_recruiter_summary",
    "score_breakdown",
    "intelligence_card",
    "candidate_strengths",
    "candidate_risks",
    "weaknesses",
    "why_ranked",
    "explanation",
]


def main() -> None:
    candidates = load_sample_candidates(SAMPLE_CANDIDATES_PATH)
    ranked = rank_candidates(candidates, SAMPLE_JOB_DESCRIPTION)[:10]
    write_results(ranked, OUTPUT_PATH)
    print(f"Wrote top {len(ranked)} ranked candidates to {OUTPUT_PATH}")


def load_sample_candidates(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing sample candidates file: {path}")

    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"{path} is empty. Add sample candidate records before running this script.")

    data = json.loads(content)
    if isinstance(data, list):
        candidates = data
    elif isinstance(data, dict):
        candidates = data.get("candidates") or data.get("data") or [data]
    else:
        raise ValueError("sample_candidates.json must contain a JSON array, a candidate object, or a candidates/data key.")

    if not all(isinstance(candidate, dict) for candidate in candidates):
        raise ValueError("Every sample candidate must be a JSON object.")
    return candidates


def write_results(ranked_candidates: list[Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for candidate in ranked_candidates:
            writer.writerow(to_result_row(candidate))


def to_result_row(candidate: Any) -> dict[str, Any]:
    breakdown = score_breakdown(candidate)
    intelligence_card = candidate.intelligence_card()

    return {
        "rank": candidate.rank,
        "candidate_id": candidate.candidate_id,
        "final_score": candidate.final_score,
        "technical_fit_score": candidate.technical_fit.score,
        "experience_score": candidate.experience.score,
        "career_consistency_score": candidate.career_consistency.score,
        "skill_cluster_bonus": candidate.skill_cluster.score,
        "behavioral_score": candidate.behavioral.score,
        "authenticity_score": candidate.authenticity.score,
        "authenticity_risk_level": candidate.authenticity.metadata.get("risk_level", ""),
        "risk_level": candidate.authenticity.metadata.get("risk_level", ""),
        "recruiter_cognitive_twin_score": candidate.recruiter_cognitive_twin.score,
        "recruiter_reasoning": candidate.recruiter_cognitive_twin.metadata.get("recruiter_reasoning", ""),
        "hidden_gem_score": candidate.hidden_gem.score,
        "hidden_gem_flag": candidate.hidden_gem.metadata.get("hidden_gem_flag", False),
        "hidden_gem_reason": candidate.hidden_gem.metadata.get("hidden_gem_reason", ""),
        "recruiter_decision": candidate.recruiter_decision.get("decision", ""),
        "recruiter_decision_reason": candidate.recruiter_decision.get("reason", ""),
        "hiring_confidence_score": candidate.hiring_confidence.score,
        "confidence_level": candidate.hiring_confidence.metadata.get("confidence_level", ""),
        "executive_recruiter_summary": candidate.executive_recruiter_summary,
        "score_breakdown": json.dumps(breakdown, sort_keys=True),
        "intelligence_card": json.dumps(intelligence_card, sort_keys=True),
        "candidate_strengths": "; ".join(candidate.strengths),
        "candidate_risks": "; ".join(candidate.risks),
        "weaknesses": "; ".join(candidate.risks),
        "why_ranked": candidate.explanation,
        "explanation": candidate.explanation,
    }


if __name__ == "__main__":
    main()
