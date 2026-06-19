"""Ranking pipeline for TalentLens AI.

This module can be used as a library or as a small CLI:

    python backend/ranker.py --jd-file job_description.txt \
        --candidates data/candidates.jsonl \
        --sample-submission data/sample_submission.csv \
        --output submission.csv
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any, Iterable

try:
    from .jd_parser import JobRequirements, parse_job_description
    from .scoring import (
        ScoreResult,
        authenticity_score,
        career_consistency_score,
        experience_score,
        skill_cluster_bonus,
        technical_fit_score,
    )
    from .signal_engine import BehavioralScore, compute_behavioral_score
except ImportError:  # pragma: no cover - supports direct script execution
    from jd_parser import JobRequirements, parse_job_description
    from scoring import (
        ScoreResult,
        authenticity_score,
        career_consistency_score,
        experience_score,
        skill_cluster_bonus,
        technical_fit_score,
    )
    from signal_engine import BehavioralScore, compute_behavioral_score


DEFAULT_WEIGHTS = {
    "technical_fit": 0.34,
    "experience": 0.20,
    "career_consistency": 0.11,
    "behavioral": 0.20,
    "authenticity": 0.15,
}

DEFAULT_OUTPUT_FIELDS = [
    "candidate_id",
    "rank",
    "final_score",
    "technical_fit_score",
    "experience_score",
    "career_consistency_score",
    "skill_cluster_bonus",
    "behavioral_score",
    "authenticity_score",
    "authenticity_risk_level",
    "explanation",
    "why_ranked",
    "candidate_strengths",
    "candidate_risks",
]


@dataclass(frozen=True)
class RankedCandidate:
    candidate_id: str
    rank: int
    final_score: float
    technical_fit: ScoreResult
    experience: ScoreResult
    career_consistency: ScoreResult
    skill_cluster: ScoreResult
    behavioral: BehavioralScore
    authenticity: ScoreResult
    explanation: str
    strengths: list[str]
    risks: list[str]
    raw_candidate: dict[str, Any] = field(repr=False)

    def to_row(self, headers: Iterable[str] | None = None) -> dict[str, Any]:
        row = {
            "candidate_id": self.candidate_id,
            "id": self.candidate_id,
            "rank": self.rank,
            "final_score": self.final_score,
            "score": self.final_score,
            "technical_fit_score": self.technical_fit.score,
            "technical_score": self.technical_fit.score,
            "experience_score": self.experience.score,
            "career_consistency_score": self.career_consistency.score,
            "skill_cluster_bonus": self.skill_cluster.score,
            "behavioral_score": self.behavioral.score,
            "redrob_score": self.behavioral.score,
            "authenticity_score": self.authenticity.score,
            "authenticity_risk_level": self.authenticity.metadata.get("risk_level", ""),
            "explanation": self.explanation,
            "summary": self.explanation,
            "why_ranked": self.explanation,
            "candidate_strengths": "; ".join(self.strengths),
            "strengths": "; ".join(self.strengths),
            "candidate_risks": "; ".join(self.risks),
            "risks": "; ".join(self.risks),
            "matched_skills": ", ".join(self.technical_fit.metadata.get("matched_skills", [])),
            "missing_skills": ", ".join(self.technical_fit.metadata.get("missing_skills", [])),
        }

        if not headers:
            return {field: row.get(field, "") for field in DEFAULT_OUTPUT_FIELDS}

        return {field: row.get(field, _candidate_value(self.raw_candidate, field)) for field in headers}

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "rank": self.rank,
            "final_score": self.final_score,
            "technical_fit": self.technical_fit.to_dict(),
            "experience": self.experience.to_dict(),
            "career_consistency": self.career_consistency.to_dict(),
            "skill_cluster": self.skill_cluster.to_dict(),
            "behavioral": self.behavioral.to_dict(),
            "authenticity": self.authenticity.to_dict(),
            "authenticity_risk_level": self.authenticity.metadata.get("risk_level", ""),
            "explanation": self.explanation,
            "why_ranked": self.explanation,
            "candidate_strengths": self.strengths,
            "candidate_risks": self.risks,
        }


def rank_candidates(
    candidates: list[dict[str, Any]],
    job_description: str | JobRequirements | dict[str, Any],
    weights: dict[str, float] | None = None,
) -> list[RankedCandidate]:
    """Score and rank candidates for a job description."""

    requirements = _ensure_requirements(job_description)
    active_weights = _normalize_weights(weights or DEFAULT_WEIGHTS)
    scored: list[RankedCandidate] = []

    for candidate in candidates:
        technical = technical_fit_score(candidate, requirements)
        experience = experience_score(candidate, requirements)
        consistency = career_consistency_score(candidate)
        cluster = skill_cluster_bonus(candidate, requirements)
        behavioral = compute_behavioral_score(candidate)
        authenticity = authenticity_score(candidate)
        final_score = _combine_scores(technical, experience, consistency, cluster, behavioral, authenticity, active_weights)
        strengths = candidate_strengths(technical, experience, consistency, cluster, behavioral, authenticity)
        risks = candidate_risks(technical, experience, consistency, behavioral, authenticity)
        explanation = generate_explanation(
            technical,
            experience,
            consistency,
            cluster,
            behavioral,
            authenticity,
            final_score,
            strengths,
            risks,
        )

        scored.append(
            RankedCandidate(
                candidate_id=_candidate_id(candidate),
                rank=0,
                final_score=final_score,
                technical_fit=technical,
                experience=experience,
                career_consistency=consistency,
                skill_cluster=cluster,
                behavioral=behavioral,
                authenticity=authenticity,
                explanation=explanation,
                strengths=strengths,
                risks=risks,
                raw_candidate=candidate,
            )
        )

    scored.sort(
        key=lambda item: (
            item.final_score,
            item.technical_fit.score,
            item.experience.score,
            item.career_consistency.score,
            item.authenticity.score,
            item.behavioral.score,
        ),
        reverse=True,
    )

    return [
        RankedCandidate(
            candidate_id=item.candidate_id,
            rank=index,
            final_score=item.final_score,
            technical_fit=item.technical_fit,
            experience=item.experience,
            career_consistency=item.career_consistency,
            skill_cluster=item.skill_cluster,
            behavioral=item.behavioral,
            authenticity=item.authenticity,
            explanation=item.explanation,
            strengths=item.strengths,
            risks=item.risks,
            raw_candidate=item.raw_candidate,
        )
        for index, item in enumerate(scored, start=1)
    ]


def generate_explanation(
    technical: ScoreResult,
    experience: ScoreResult,
    career_consistency: ScoreResult,
    skill_cluster: ScoreResult,
    behavioral: BehavioralScore,
    authenticity: ScoreResult,
    final_score: float,
    strengths: list[str] | None = None,
    risks: list[str] | None = None,
) -> str:
    """Create a recruiter-facing explanation for why the candidate ranked here."""

    strongest = max(
        (
            ("technical fit", technical.score),
            ("experience", experience.score),
            ("career consistency", career_consistency.score),
            ("behavioral signals", behavioral.score),
            ("authenticity", authenticity.score),
        ),
        key=lambda item: item[1],
    )
    strength_text = f" Strengths: {'; '.join((strengths or [])[:3])}." if strengths else ""
    risk_text = f" Risks: {'; '.join((risks or [])[:3])}." if risks else ""
    cluster_text = (
        f" Skill cluster bonus: +{skill_cluster.score:.2f} for {skill_cluster.evidence[0]}."
        if skill_cluster.score > 0 and skill_cluster.evidence
        else ""
    )

    return (
        f"Ranked on a {final_score:.2f} final score. Strongest dimension is {strongest[0]} "
        f"({strongest[1]:.2f}). {technical.explanation} {experience.explanation} "
        f"{career_consistency.explanation} {behavioral.explanation}{cluster_text}"
        f"{strength_text}{risk_text}"
    ).strip()


def candidate_strengths(
    technical: ScoreResult,
    experience: ScoreResult,
    career_consistency: ScoreResult,
    skill_cluster: ScoreResult,
    behavioral: BehavioralScore,
    authenticity: ScoreResult,
) -> list[str]:
    """Select the most recruiter-useful strengths from all dimensions."""

    strengths: list[str] = []
    strengths.extend(technical.evidence[:3])
    if experience.score >= 75:
        strengths.extend(experience.evidence[:2])
    if career_consistency.score >= 70:
        strengths.extend(career_consistency.evidence[:2])
    if skill_cluster.score > 0:
        strengths.extend(skill_cluster.evidence[:2])
    strengths.extend(behavioral.positive_signals[:3])
    if authenticity.score >= 75:
        strengths.extend(authenticity.evidence[:3])
    return _dedupe(strengths)[:8]


def candidate_risks(
    technical: ScoreResult,
    experience: ScoreResult,
    career_consistency: ScoreResult,
    behavioral: BehavioralScore,
    authenticity: ScoreResult,
) -> list[str]:
    """Select the most decision-relevant risks from all dimensions."""

    risks: list[str] = []
    risks.extend(technical.gaps[:3])
    risks.extend(experience.gaps[:2])
    risks.extend(career_consistency.gaps[:3])
    risks.extend(behavioral.risk_signals[:3])
    risks.extend(authenticity.gaps[:3])

    risk_level = authenticity.metadata.get("risk_level")
    if risk_level in {"high", "critical"}:
        risks.insert(0, f"Authenticity risk level is {risk_level}")
    return _dedupe(risks)[:8]


def load_candidates_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load candidates from JSONL, skipping blank lines and failing loudly on bad JSON."""

    path = Path(path)
    candidates: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number} in {path}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"Candidate record on line {line_number} must be a JSON object")
            candidates.append(record)
    return candidates


def export_ranked_candidates(
    ranked_candidates: list[RankedCandidate],
    output_path: str | Path,
    sample_submission_path: str | Path | None = None,
) -> None:
    """Export rankings to CSV, matching sample_submission.csv headers when present."""

    headers = load_sample_submission_headers(sample_submission_path) if sample_submission_path else DEFAULT_OUTPUT_FIELDS
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for candidate in ranked_candidates:
            writer.writerow(candidate.to_row(headers))


def load_sample_submission_headers(path: str | Path | None) -> list[str]:
    """Return sample CSV headers, falling back when the sample file is blank."""

    if not path:
        return DEFAULT_OUTPUT_FIELDS

    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return DEFAULT_OUTPUT_FIELDS

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            headers = [column.strip() for column in row if column.strip()]
            if headers:
                return headers
    return DEFAULT_OUTPUT_FIELDS


def run_ranking(
    job_description: str,
    candidates_path: str | Path = "data/candidates.jsonl",
    output_path: str | Path = "submission.csv",
    sample_submission_path: str | Path | None = "data/sample_submission.csv",
) -> list[RankedCandidate]:
    """Convenience function for the full ranking pipeline."""

    candidates = load_candidates_jsonl(candidates_path)
    ranked = rank_candidates(candidates, job_description)
    export_ranked_candidates(ranked, output_path, sample_submission_path)
    return ranked


def _ensure_requirements(job_description: str | JobRequirements | dict[str, Any]) -> JobRequirements | dict[str, Any]:
    if isinstance(job_description, str):
        return parse_job_description(job_description)
    return job_description


def _combine_scores(
    technical: ScoreResult,
    experience: ScoreResult,
    career_consistency: ScoreResult,
    skill_cluster: ScoreResult,
    behavioral: BehavioralScore,
    authenticity: ScoreResult,
    weights: dict[str, float],
) -> float:
    value = (
        technical.score * weights["technical_fit"]
        + experience.score * weights["experience"]
        + career_consistency.score * weights["career_consistency"]
        + behavioral.score * weights["behavioral"]
        + authenticity.score * weights["authenticity"]
        + skill_cluster.score
    )
    return round(min(100.0, value), 2)


def _normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    complete = {**DEFAULT_WEIGHTS, **weights}
    total = sum(complete.values())
    if total <= 0:
        return DEFAULT_WEIGHTS
    return {key: value / total for key, value in complete.items()}


def _dedupe(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = str(value).strip()
        key = cleaned.lower()
        if cleaned and key not in seen:
            seen.add(key)
            result.append(cleaned)
    return result


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


def _candidate_value(candidate: dict[str, Any], field: str) -> Any:
    if field in candidate:
        return candidate[field]
    profile = candidate.get("profile") if isinstance(candidate.get("profile"), dict) else {}
    if field in profile:
        return profile[field]
    return ""


def _read_job_description(args: argparse.Namespace) -> str:
    if args.jd_text:
        return args.jd_text
    if args.jd_file:
        return Path(args.jd_file).read_text(encoding="utf-8")
    raise ValueError("Provide either --jd-text or --jd-file")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rank candidates for a job description.")
    parser.add_argument("--jd-text", help="Job description text")
    parser.add_argument("--jd-file", help="Path to a file containing the job description")
    parser.add_argument("--candidates", default="data/candidates.jsonl", help="Path to candidates JSONL")
    parser.add_argument("--sample-submission", default="data/sample_submission.csv", help="Path to sample submission CSV")
    parser.add_argument("--output", default="submission.csv", help="Output CSV path")
    parser.add_argument("--json", action="store_true", help="Print ranked candidate details as JSON")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    job_description = _read_job_description(args)
    ranked = run_ranking(job_description, args.candidates, args.output, args.sample_submission)

    if args.json:
        print(json.dumps([candidate.to_dict() for candidate in ranked], indent=2))
    else:
        print(f"Wrote {len(ranked)} ranked candidates to {args.output}")


if __name__ == "__main__":
    main()
