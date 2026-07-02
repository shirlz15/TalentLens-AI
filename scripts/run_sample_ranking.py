"""Run TalentLens ranking on sample candidates and export top 10 results."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.ranker import rank_candidates  # noqa: E402
from backend.report_export import build_ranked_report_rows, write_ranked_report_csv, write_ranked_report_xlsx  # noqa: E402


SAMPLE_JOB_DESCRIPTION = """
Senior Data Scientist required for a high-growth recruiting intelligence team.
Must have Python, SQL, machine learning, statistics, and data analysis experience.
Minimum 5 years of experience. Strong communication, stakeholder collaboration,
and evidence-driven problem solving are important. Nice to have: cloud exposure,
GitHub activity, and experience building explainable ranking systems.
"""

SAMPLE_CANDIDATES_PATH = PROJECT_ROOT / "data" / "sample_candidates.json"
OUTPUT_PATH = PROJECT_ROOT / "output" / "results.csv"
XLSX_OUTPUT_PATH = PROJECT_ROOT / "output" / "TalentLens_AI_Ranked_Candidates_2026-07-02.xlsx"

def main() -> None:
    candidates = load_sample_candidates(SAMPLE_CANDIDATES_PATH)
    ranked = rank_candidates(candidates, SAMPLE_JOB_DESCRIPTION)[:10]
    rows = build_ranked_report_rows(ranked)
    write_ranked_report_csv(rows, OUTPUT_PATH)
    write_ranked_report_xlsx(rows, XLSX_OUTPUT_PATH)
    print(f"Wrote top {len(ranked)} ranked candidates to {OUTPUT_PATH}")
    print(f"Wrote recruiter workbook to {XLSX_OUTPUT_PATH}")


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


if __name__ == "__main__":
    main()
