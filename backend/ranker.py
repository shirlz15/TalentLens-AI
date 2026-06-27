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
    from .llm_reasoner import (
        generate_hidden_gem_reason,
        generate_interview_recommendation,
        generate_recruiter_reasoning,
    )
    from .scoring import (
        DEFAULT_SCORING_CONFIG,
        ScoreResult,
        ScoringConfig,
        authenticity_score,
        career_consistency_score,
        experience_score,
        hidden_gem_score,
        recruiter_cognitive_twin_score,
        skill_cluster_bonus,
        technical_fit_score,
    )
    from .semantic_search import semantic_retrieval_map
    from .signal_engine import BehavioralConfig, BehavioralScore, DEFAULT_BEHAVIORAL_CONFIG, compute_behavioral_score
except ImportError:  # pragma: no cover - supports direct script execution
    from jd_parser import JobRequirements, parse_job_description
    from llm_reasoner import (
        generate_hidden_gem_reason,
        generate_interview_recommendation,
        generate_recruiter_reasoning,
    )
    from scoring import (
        DEFAULT_SCORING_CONFIG,
        ScoreResult,
        ScoringConfig,
        authenticity_score,
        career_consistency_score,
        experience_score,
        hidden_gem_score,
        recruiter_cognitive_twin_score,
        skill_cluster_bonus,
        technical_fit_score,
    )
    from semantic_search import semantic_retrieval_map
    from signal_engine import BehavioralConfig, BehavioralScore, DEFAULT_BEHAVIORAL_CONFIG, compute_behavioral_score


@dataclass(frozen=True)
class RankingConfig:
    """Configurable ranking knobs for recruiter-intelligence scoring."""

    score_weights: dict[str, float] = field(
        default_factory=lambda: {
            "technical_fit": 0.34,
            "experience": 0.20,
            "career_consistency": 0.11,
            "behavioral": 0.20,
            "authenticity": 0.15,
        }
    )
    scoring: ScoringConfig = DEFAULT_SCORING_CONFIG
    behavioral: BehavioralConfig = DEFAULT_BEHAVIORAL_CONFIG
    max_strengths: int = 8
    max_weaknesses: int = 8
    append_intelligence_export_fields: bool = True
    semantic_weight: float = 0.15
    hybrid_weight: float = 0.85
    semantic_retrieval_k: int = 100
    llm_reasoning_enabled: bool = True

    @property
    def weights(self) -> dict[str, float]:
        """Backward-compatible alias for earlier callers."""

        return self.score_weights


DEFAULT_CONFIG = RankingConfig()
DEFAULT_WEIGHTS = DEFAULT_CONFIG.score_weights

DEFAULT_OUTPUT_FIELDS = [
    "candidate_id",
    "rank",
    "final_score",
    "semantic_similarity_score",
    "retrieval_rank",
    "technical_fit_score",
    "experience_score",
    "career_consistency_score",
    "skill_cluster_bonus",
    "behavioral_score",
    "authenticity_score",
    "authenticity_risk_level",
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
    "explanation",
    "why_ranked",
    "candidate_strengths",
    "candidate_risks",
    "weaknesses",
    "intelligence_card",
    "score_breakdown",
]


@dataclass(frozen=True)
class RankedCandidate:
    candidate_id: str
    rank: int
    final_score: float
    semantic_similarity: ScoreResult
    retrieval_rank: int
    technical_fit: ScoreResult
    experience: ScoreResult
    career_consistency: ScoreResult
    skill_cluster: ScoreResult
    behavioral: BehavioralScore
    authenticity: ScoreResult
    recruiter_cognitive_twin: ScoreResult
    hidden_gem: ScoreResult
    recruiter_decision: dict[str, Any]
    hiring_confidence: ScoreResult
    executive_recruiter_summary: str
    explanation: str
    interview_recommendation: str
    strengths: list[str]
    risks: list[str]
    raw_candidate: dict[str, Any] = field(repr=False)

    def to_row(self, headers: Iterable[str] | None = None) -> dict[str, Any]:
        card = self.intelligence_card()
        breakdown = score_breakdown(self)
        row = {
            "candidate_id": self.candidate_id,
            "id": self.candidate_id,
            "rank": self.rank,
            "final_score": self.final_score,
            "score": self.final_score,
            "semantic_similarity_score": self.semantic_similarity.score,
            "retrieval_rank": self.retrieval_rank,
            "technical_fit_score": self.technical_fit.score,
            "technical_score": self.technical_fit.score,
            "experience_score": self.experience.score,
            "career_consistency_score": self.career_consistency.score,
            "skill_cluster_bonus": self.skill_cluster.score,
            "behavioral_score": self.behavioral.score,
            "redrob_score": self.behavioral.score,
            "authenticity_score": self.authenticity.score,
            "authenticity_risk_level": self.authenticity.metadata.get("risk_level", ""),
            "risk_level": self.authenticity.metadata.get("risk_level", ""),
            "recruiter_cognitive_twin_score": self.recruiter_cognitive_twin.score,
            "recruiter_reasoning": self.recruiter_cognitive_twin.metadata.get("recruiter_reasoning", ""),
            "hidden_gem_score": self.hidden_gem.score,
            "hidden_gem_flag": self.hidden_gem.metadata.get("hidden_gem_flag", False),
            "hidden_gem_reason": self.hidden_gem.metadata.get("hidden_gem_reason", ""),
            "recruiter_decision": self.recruiter_decision.get("decision", ""),
            "recruiter_decision_reason": self.recruiter_decision.get("reason", ""),
            "hiring_confidence_score": self.hiring_confidence.score,
            "confidence_level": self.hiring_confidence.metadata.get("confidence_level", ""),
            "executive_recruiter_summary": self.executive_recruiter_summary,
            "explanation": self.explanation,
            "summary": self.explanation,
            "why_ranked": self.explanation,
            "candidate_strengths": "; ".join(self.strengths),
            "strengths": "; ".join(self.strengths),
            "candidate_risks": "; ".join(self.risks),
            "risks": "; ".join(self.risks),
            "weaknesses": "; ".join(self.risks),
            "interview_recommendation": self.interview_recommendation,
            "intelligence_card": json.dumps(card, sort_keys=True),
            "score_breakdown": json.dumps(breakdown, sort_keys=True),
            "matched_skills": ", ".join(self.technical_fit.metadata.get("matched_skills", [])),
            "missing_skills": ", ".join(self.technical_fit.metadata.get("missing_skills", [])),
        }

        if not headers:
            return {field: row.get(field, "") for field in DEFAULT_OUTPUT_FIELDS}

        return {field: row.get(field, _candidate_value(self.raw_candidate, field)) for field in headers}

    def to_dict(self) -> dict[str, Any]:
        card = self.intelligence_card()
        return {
            "candidate_id": self.candidate_id,
            "rank": self.rank,
            "final_score": self.final_score,
            "semantic_similarity": self.semantic_similarity.to_dict(),
            "semantic_similarity_score": self.semantic_similarity.score,
            "retrieval_rank": self.retrieval_rank,
            "technical_fit": self.technical_fit.to_dict(),
            "experience": self.experience.to_dict(),
            "career_consistency": self.career_consistency.to_dict(),
            "skill_cluster": self.skill_cluster.to_dict(),
            "behavioral": self.behavioral.to_dict(),
            "authenticity": self.authenticity.to_dict(),
            "recruiter_cognitive_twin": self.recruiter_cognitive_twin.to_dict(),
            "hidden_gem": self.hidden_gem.to_dict(),
            "authenticity_risk_level": self.authenticity.metadata.get("risk_level", ""),
            "recruiter_cognitive_twin_score": self.recruiter_cognitive_twin.score,
            "recruiter_reasoning": self.recruiter_cognitive_twin.metadata.get("recruiter_reasoning", ""),
            "hidden_gem_score": self.hidden_gem.score,
            "hidden_gem_flag": self.hidden_gem.metadata.get("hidden_gem_flag", False),
            "hidden_gem_reason": self.hidden_gem.metadata.get("hidden_gem_reason", ""),
            "recruiter_decision": self.recruiter_decision,
            "hiring_confidence": self.hiring_confidence.to_dict(),
            "hiring_confidence_score": self.hiring_confidence.score,
            "confidence_level": self.hiring_confidence.metadata.get("confidence_level", ""),
            "executive_recruiter_summary": self.executive_recruiter_summary,
            "explanation": self.explanation,
            "why_ranked": self.explanation,
            "candidate_strengths": self.strengths,
            "candidate_risks": self.risks,
            "weaknesses": self.risks,
            "interview_recommendation": self.interview_recommendation,
            "score_breakdown": score_breakdown(self),
            "intelligence_card": card,
        }

    def intelligence_card(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "final_score": self.final_score,
            "semantic_similarity_score": self.semantic_similarity.score,
            "retrieval_rank": self.retrieval_rank,
            "technical_score": self.technical_fit.score,
            "experience_score": self.experience.score,
            "behavioral_score": self.behavioral.score,
            "authenticity_score": self.authenticity.score,
            "career_consistency_score": self.career_consistency.score,
            "recruiter_cognitive_twin_score": self.recruiter_cognitive_twin.score,
            "hidden_gem_score": self.hidden_gem.score,
            "hidden_gem_flag": self.hidden_gem.metadata.get("hidden_gem_flag", False),
            "recruiter_decision": self.recruiter_decision.get("decision", ""),
            "recruiter_decision_reason": self.recruiter_decision.get("reason", ""),
            "hiring_confidence_score": self.hiring_confidence.score,
            "confidence_level": self.hiring_confidence.metadata.get("confidence_level", ""),
            "risk_level": self.authenticity.metadata.get("risk_level", ""),
            "strengths": self.strengths,
            "weaknesses": self.risks,
            "why_ranked": self.explanation,
            "recruiter_reasoning": self.recruiter_cognitive_twin.metadata.get("recruiter_reasoning", ""),
            "hidden_gem_reason": self.hidden_gem.metadata.get("hidden_gem_reason", ""),
            "interview_recommendation": self.interview_recommendation,
            "executive_recruiter_summary": self.executive_recruiter_summary,
            "score_breakdown": score_breakdown(self),
        }


def rank_candidates(
    candidates: list[dict[str, Any]],
    job_description: str | JobRequirements | dict[str, Any],
    weights: dict[str, float] | None = None,
    config: RankingConfig | None = None,
) -> list[RankedCandidate]:
    """Score and rank candidates for a job description."""

    active_config = config or DEFAULT_CONFIG
    requirements = _ensure_requirements(job_description)
    job_description_text = _job_description_text(job_description, requirements)
    active_weights = _normalize_weights(weights or active_config.score_weights, active_config)
    retrieval = semantic_retrieval_map(job_description_text, candidates) if job_description_text.strip() else {}
    scored: list[RankedCandidate] = []

    for candidate in candidates:
        retrieval_entry = retrieval.get(_candidate_id(candidate), {})
        semantic_score = float(retrieval_entry.get("semantic_similarity_score", 0.0) or 0.0)
        semantic = ScoreResult(
            score=round(semantic_score, 2),
            explanation=(
                f"Semantic retrieval matched this profile at rank {retrieval_entry.get('retrieval_rank', len(candidates) or 1)} "
                f"with a {semantic_score:.2f} similarity score."
                if retrieval_entry
                else "Semantic retrieval fallback did not find additional similarity evidence."
            ),
            evidence=[
                f"Semantic backend: {retrieval_entry.get('backend', 'deterministic-fallback')}",
                f"Retrieval rank: {retrieval_entry.get('retrieval_rank', len(candidates) or 1)}",
            ],
            gaps=[] if semantic_score >= 45 else ["Semantic similarity is weaker than the strongest retrieved profiles"],
            metadata={
                "retrieval_rank": int(retrieval_entry.get("retrieval_rank", len(candidates) or 1)),
                "raw_similarity": retrieval_entry.get("raw_similarity", 0.0),
                "backend": retrieval_entry.get("backend", "deterministic-fallback"),
            },
        )
        technical = technical_fit_score(candidate, requirements, active_config.scoring)
        experience = experience_score(candidate, requirements, active_config.scoring)
        consistency = career_consistency_score(candidate, requirements, active_config.scoring)
        cluster = skill_cluster_bonus(candidate, requirements, active_config.scoring)
        behavioral = compute_behavioral_score(candidate, active_config.behavioral)
        authenticity = authenticity_score(candidate, active_config.scoring)
        recruiter_twin = recruiter_cognitive_twin_score(
            technical,
            experience,
            consistency,
            cluster,
            behavioral,
            authenticity,
            active_config.scoring,
        )
        hidden_gem = hidden_gem_score(
            candidate,
            technical,
            experience,
            cluster,
            behavioral,
            active_config.scoring,
        )
        final_score = _combine_scores(
            semantic,
            technical,
            experience,
            consistency,
            cluster,
            behavioral,
            authenticity,
            active_weights,
            active_config,
        )
        strengths = candidate_strengths(technical, experience, consistency, cluster, behavioral, authenticity, active_config)
        risks = candidate_risks(technical, experience, consistency, behavioral, authenticity, active_config)
        decision = recruiter_decision_output(final_score, technical, experience, consistency, behavioral, authenticity)
        confidence = hiring_confidence_score(technical, experience, consistency, behavioral, authenticity)
        retrieval_rank = int(retrieval_entry.get("retrieval_rank", len(candidates) or 1))
        explanation = generate_explanation(
            semantic,
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
        recruiter_reasoning = (
            generate_recruiter_reasoning(candidate, job_description_text, _breakdown_payload(semantic, technical, experience, consistency, cluster, behavioral, authenticity))
            if active_config.llm_reasoning_enabled
            else recruiter_twin.metadata.get("recruiter_reasoning", "")
        )
        hidden_gem_reason = (
            generate_hidden_gem_reason(candidate, _breakdown_payload(semantic, technical, experience, consistency, cluster, behavioral, authenticity))
            if active_config.llm_reasoning_enabled
            else hidden_gem.metadata.get("hidden_gem_reason", "")
        )
        if recruiter_reasoning:
            recruiter_twin = ScoreResult(
                score=recruiter_twin.score,
                explanation=recruiter_twin.explanation,
                evidence=recruiter_twin.evidence,
                gaps=recruiter_twin.gaps,
                metadata={**recruiter_twin.metadata, "recruiter_reasoning": recruiter_reasoning},
            )
        if hidden_gem_reason:
            hidden_gem = ScoreResult(
                score=hidden_gem.score,
                explanation=hidden_gem.explanation,
                evidence=hidden_gem.evidence,
                gaps=hidden_gem.gaps,
                metadata={**hidden_gem.metadata, "hidden_gem_reason": hidden_gem_reason},
            )
        executive_summary = generate_executive_recruiter_summary(
            final_score,
            semantic,
            decision,
            technical,
            experience,
            consistency,
            cluster,
            behavioral,
            authenticity,
            risks,
        )
        interview_recommendation = generate_interview_recommendation(candidate, job_description_text)

        scored.append(
            RankedCandidate(
                candidate_id=_candidate_id(candidate),
                rank=0,
                final_score=final_score,
                semantic_similarity=semantic,
                retrieval_rank=retrieval_rank,
                technical_fit=technical,
                experience=experience,
                career_consistency=consistency,
                skill_cluster=cluster,
                behavioral=behavioral,
                authenticity=authenticity,
                recruiter_cognitive_twin=recruiter_twin,
                hidden_gem=hidden_gem,
                recruiter_decision=decision,
                hiring_confidence=confidence,
                executive_recruiter_summary=executive_summary,
                explanation=explanation,
                interview_recommendation=interview_recommendation,
                strengths=strengths,
                risks=risks,
                raw_candidate=candidate,
            )
        )

    scored.sort(
        key=lambda item: (
            item.final_score,
            item.semantic_similarity.score,
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
            semantic_similarity=item.semantic_similarity,
            retrieval_rank=item.retrieval_rank,
            technical_fit=item.technical_fit,
            experience=item.experience,
            career_consistency=item.career_consistency,
            skill_cluster=item.skill_cluster,
            behavioral=item.behavioral,
            authenticity=item.authenticity,
            recruiter_cognitive_twin=item.recruiter_cognitive_twin,
            hidden_gem=item.hidden_gem,
            recruiter_decision=item.recruiter_decision,
            hiring_confidence=item.hiring_confidence,
            executive_recruiter_summary=item.executive_recruiter_summary,
            explanation=item.explanation,
            interview_recommendation=item.interview_recommendation,
            strengths=item.strengths,
            risks=item.risks,
            raw_candidate=item.raw_candidate,
        )
        for index, item in enumerate(scored, start=1)
    ]


def generate_explanation(
    semantic: ScoreResult,
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
            ("semantic similarity", semantic.score),
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
    semantic_text = (
        f" {semantic.explanation}"
        if semantic.score > 0
        else " Semantic retrieval added limited supporting evidence for this profile."
    )

    return (
        f"Ranked on a {final_score:.2f} final score. Strongest dimension is {strongest[0]} "
        f"({strongest[1]:.2f}).{semantic_text} {technical.explanation} {experience.explanation} "
        f"{career_consistency.explanation} {behavioral.explanation}{cluster_text}"
        f"{strength_text}{risk_text}"
    ).strip()


def recruiter_decision_output(
    final_score: float,
    technical: ScoreResult,
    experience: ScoreResult,
    career_consistency: ScoreResult,
    behavioral: BehavioralScore,
    authenticity: ScoreResult,
) -> dict[str, Any]:
    """Convert ranking evidence into a recruiter decision bucket."""

    risk_level = str(authenticity.metadata.get("risk_level", "")).upper()
    if risk_level == "HIGH" or final_score < 55:
        decision = "Reject"
    elif final_score >= 85 and risk_level == "LOW":
        decision = "Shortlist"
    elif final_score >= 75 and risk_level in {"LOW", "MEDIUM"}:
        decision = "Strong Consideration"
    elif final_score >= 60:
        decision = "Hold"
    else:
        decision = "Reject"

    reasons: list[str] = []
    if decision == "Shortlist":
        reasons.append("High final score with strong fit evidence and low authenticity risk")
    elif decision == "Strong Consideration":
        reasons.append("Good overall evidence, but recruiter validation is recommended before shortlist")
    elif decision == "Hold":
        reasons.append("Some useful signals, but score or evidence gaps limit immediate confidence")
    else:
        reasons.append("Insufficient score quality or elevated risk for this role")

    if technical.gaps:
        reasons.append(f"Key gap: {technical.gaps[0]}")
    if experience.gaps:
        reasons.append(f"Experience concern: {experience.gaps[0]}")
    if career_consistency.gaps:
        reasons.append(f"Career concern: {career_consistency.gaps[0]}")
    if behavioral.risk_signals:
        reasons.append(f"Signal concern: {behavioral.risk_signals[0]}")
    if risk_level != "LOW":
        reasons.append(f"Authenticity risk is {risk_level}")

    return {
        "decision": decision,
        "reason": ". ".join(reasons[:3]) + ".",
        "evidence": {
            "final_score": final_score,
            "technical_score": technical.score,
            "experience_score": experience.score,
            "career_consistency_score": career_consistency.score,
            "behavioral_score": behavioral.score,
            "authenticity_score": authenticity.score,
            "risk_level": risk_level,
        },
    }


def hiring_confidence_score(
    technical: ScoreResult,
    experience: ScoreResult,
    career_consistency: ScoreResult,
    behavioral: BehavioralScore,
    authenticity: ScoreResult,
) -> ScoreResult:
    """Estimate how much confidence a recruiter should have in the recommendation."""

    completeness = float(authenticity.metadata.get("profile_completeness_score", 0.0) or 0.0)
    evidence_quality = _evidence_quality_score(technical, experience, career_consistency, behavioral, authenticity)
    consistency_strength = career_consistency.score
    signal_strength = (behavioral.score * 0.55) + (authenticity.score * 0.45)
    score = round(
        min(
            100.0,
            evidence_quality * 0.30
            + completeness * 0.20
            + consistency_strength * 0.25
            + signal_strength * 0.25,
        ),
        2,
    )
    if score >= 80:
        level = "High"
    elif score >= 60:
        level = "Medium"
    else:
        level = "Low"

    evidence = [
        f"Evidence quality score: {evidence_quality:.1f}",
        f"Profile completeness: {completeness:.1f}",
        f"Career consistency: {career_consistency.score:.1f}",
        f"Behavioral/authenticity signal blend: {signal_strength:.1f}",
    ]
    gaps = []
    if technical.gaps:
        gaps.append(technical.gaps[0])
    if behavioral.risk_signals:
        gaps.append(behavioral.risk_signals[0])
    if authenticity.gaps:
        gaps.append(authenticity.gaps[0])

    return ScoreResult(
        score=score,
        explanation=f"{level} hiring confidence based on evidence quality, completeness, consistency, and signal strength.",
        evidence=evidence,
        gaps=_dedupe(gaps),
        metadata={
            "confidence_level": level,
            "reasoning": {
                "evidence_quality": round(evidence_quality, 2),
                "profile_completeness": round(completeness, 2),
                "career_consistency": career_consistency.score,
                "signal_strength": round(signal_strength, 2),
                "weights": {
                    "evidence_quality": 0.30,
                    "profile_completeness": 0.20,
                    "career_consistency": 0.25,
                    "signal_strength": 0.25,
                },
            },
        },
    )


def generate_executive_recruiter_summary(
    final_score: float,
    semantic: ScoreResult,
    decision: dict[str, Any],
    technical: ScoreResult,
    experience: ScoreResult,
    career_consistency: ScoreResult,
    skill_cluster: ScoreResult,
    behavioral: BehavioralScore,
    authenticity: ScoreResult,
    risks: list[str],
) -> str:
    """Create a compact 2-3 sentence recruiter summary for demos and judging."""

    risk_level = authenticity.metadata.get("risk_level", "")
    profile_type = "candidate"
    if technical.score >= 75 and skill_cluster.score > 0:
        profile_type = "technically aligned candidate"
    elif career_consistency.score >= 80:
        profile_type = "career-consistent candidate"
    elif behavioral.score >= 75:
        profile_type = "high-engagement candidate"

    first = (
        f"Strong {profile_type} with a {final_score:.2f} final score, "
        f"{experience.score:.0f} experience score, {career_consistency.score:.0f} career consistency, "
        f"{semantic.score:.0f} semantic similarity, and {risk_level} authenticity risk."
    )
    technical_clause = technical.explanation.rstrip(".").lower()
    behavioral_clause = behavioral.explanation.rstrip(".").lower()
    second = (
        f"Recommended decision: {decision.get('decision', 'Hold')} based on "
        f"{technical_clause} and {behavioral_clause}"
    )
    if risks:
        third = f"Primary concern: {risks[0]}."
        return f"{first} {second}. {third}"
    return f"{first} {second}."


def _evidence_quality_score(
    technical: ScoreResult,
    experience: ScoreResult,
    career_consistency: ScoreResult,
    behavioral: BehavioralScore,
    authenticity: ScoreResult,
) -> float:
    evidence_count = (
        len(technical.evidence)
        + len(experience.evidence)
        + len(career_consistency.evidence)
        + len(behavioral.positive_signals)
        + len(authenticity.evidence)
    )
    gap_count = (
        len(technical.gaps)
        + len(experience.gaps)
        + len(career_consistency.gaps)
        + len(behavioral.risk_signals)
        + len(authenticity.gaps)
    )
    return max(0.0, min(100.0, 45.0 + evidence_count * 4.5 - gap_count * 5.0))


def candidate_strengths(
    technical: ScoreResult,
    experience: ScoreResult,
    career_consistency: ScoreResult,
    skill_cluster: ScoreResult,
    behavioral: BehavioralScore,
    authenticity: ScoreResult,
    config: RankingConfig | None = None,
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
    active_config = config or DEFAULT_CONFIG
    return _dedupe(strengths)[: active_config.max_strengths]


def candidate_risks(
    technical: ScoreResult,
    experience: ScoreResult,
    career_consistency: ScoreResult,
    behavioral: BehavioralScore,
    authenticity: ScoreResult,
    config: RankingConfig | None = None,
) -> list[str]:
    """Select the most decision-relevant risks from all dimensions."""

    risks: list[str] = []
    risks.extend(technical.gaps[:3])
    risks.extend(experience.gaps[:2])
    risks.extend(career_consistency.gaps[:3])
    risks.extend(behavioral.risk_signals[:3])
    risks.extend(authenticity.gaps[:3])

    risk_level = authenticity.metadata.get("risk_level")
    if str(risk_level).upper() == "HIGH":
        risks.insert(0, f"Authenticity risk level is {risk_level}")
    active_config = config or DEFAULT_CONFIG
    return _dedupe(risks)[: active_config.max_weaknesses]


def score_breakdown(candidate: RankedCandidate) -> dict[str, Any]:
    """Transparent score details with evidence and reasoning for every dimension."""

    return {
        "semantic_similarity": candidate.semantic_similarity.to_dict(),
        "technical": candidate.technical_fit.to_dict(),
        "experience": candidate.experience.to_dict(),
        "career_consistency": candidate.career_consistency.to_dict(),
        "skill_cluster_bonus": candidate.skill_cluster.to_dict(),
        "behavioral": {
            "score": candidate.behavioral.score,
            "explanation": candidate.behavioral.explanation,
            "evidence": candidate.behavioral.positive_signals,
            "gaps": candidate.behavioral.risk_signals,
            "metadata": {
                "component_scores": {
                    key: value
                    for key, value in candidate.behavioral.components.items()
                    if key != "signal_config"
                },
                "reasoning": candidate.behavioral.components.get("signal_config", {}),
            },
        },
        "authenticity": candidate.authenticity.to_dict(),
        "recruiter_cognitive_twin": candidate.recruiter_cognitive_twin.to_dict(),
        "hidden_gem": candidate.hidden_gem.to_dict(),
        "recruiter_decision": candidate.recruiter_decision,
        "hiring_confidence": candidate.hiring_confidence.to_dict(),
        "interview_recommendation": candidate.interview_recommendation,
        "executive_recruiter_summary": {
            "summary": candidate.executive_recruiter_summary,
            "evidence": {
                "decision": candidate.recruiter_decision.get("decision", ""),
                "confidence_level": candidate.hiring_confidence.metadata.get("confidence_level", ""),
                "confidence_score": candidate.hiring_confidence.score,
            },
        },
    }


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


def load_candidates_json(path: str | Path) -> list[dict[str, Any]]:
    """Load candidates from a JSON array or an object containing `candidates`."""

    path = Path(path)
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    data = json.loads(raw)
    if isinstance(data, list):
        candidates = data
    elif isinstance(data, dict):
        candidates = data.get("candidates") or data.get("data") or [data]
    else:
        raise ValueError(f"Unsupported JSON candidate payload in {path}")
    if not all(isinstance(candidate, dict) for candidate in candidates):
        raise ValueError(f"Every candidate in {path} must be a JSON object")
    return list(candidates)


def load_candidates_dataset(path: str | Path) -> list[dict[str, Any]]:
    """Load candidates from JSONL or JSON, returning an empty list for empty files."""

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".json":
        return load_candidates_json(path)
    if path.suffix.lower() == ".jsonl":
        return load_candidates_jsonl(path)
    raise ValueError(f"Unsupported candidate dataset format: {path.suffix}")


def load_default_candidates(
    preferred_paths: Iterable[str | Path] | None = None,
) -> list[dict[str, Any]]:
    """Load the first available non-empty candidate dataset."""

    paths = list(preferred_paths or ("data/candidates.jsonl", "data/sample_candidates.json"))
    for path in paths:
        try:
            candidates = load_candidates_dataset(path)
        except FileNotFoundError:
            continue
        if candidates:
            return candidates
    return []


def export_ranked_candidates(
    ranked_candidates: list[RankedCandidate],
    output_path: str | Path,
    sample_submission_path: str | Path | None = None,
    config: RankingConfig | None = None,
) -> None:
    """Export rankings to CSV, preserving sample headers and adding intelligence fields when possible."""

    active_config = config or DEFAULT_CONFIG
    headers = load_sample_submission_headers(sample_submission_path) if sample_submission_path else DEFAULT_OUTPUT_FIELDS
    if active_config.append_intelligence_export_fields:
        headers = _append_intelligence_headers(headers)
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


def _append_intelligence_headers(headers: list[str]) -> list[str]:
    """Append recruiter-intelligence fields without disturbing caller-provided column order."""

    enhanced = list(headers)
    for field_name in DEFAULT_OUTPUT_FIELDS:
        if field_name not in enhanced:
            enhanced.append(field_name)
    return enhanced


def run_ranking(
    job_description: str,
    candidates_path: str | Path = "data/candidates.jsonl",
    output_path: str | Path = "submission.csv",
    sample_submission_path: str | Path | None = "data/sample_submission.csv",
    config: RankingConfig | None = None,
) -> list[RankedCandidate]:
    """Convenience function for the full ranking pipeline."""

    candidates = load_candidates_dataset(candidates_path)
    ranked = rank_candidates(candidates, job_description, config=config)
    export_ranked_candidates(ranked, output_path, sample_submission_path, config=config)
    return ranked


def _ensure_requirements(job_description: str | JobRequirements | dict[str, Any]) -> JobRequirements | dict[str, Any]:
    if isinstance(job_description, str):
        return parse_job_description(job_description)
    return job_description


def _job_description_text(
    job_description: str | JobRequirements | dict[str, Any],
    requirements: JobRequirements | dict[str, Any],
) -> str:
    if isinstance(job_description, str):
        return job_description
    if isinstance(requirements, JobRequirements):
        return requirements.raw_text
    if isinstance(job_description, dict):
        for key in ("raw_text", "job_description", "description", "jd_text"):
            value = job_description.get(key)
            if value not in (None, ""):
                return str(value)
    return ""


def _breakdown_payload(
    semantic: ScoreResult,
    technical: ScoreResult,
    experience: ScoreResult,
    career_consistency: ScoreResult,
    skill_cluster: ScoreResult,
    behavioral: BehavioralScore,
    authenticity: ScoreResult,
) -> dict[str, Any]:
    return {
        "semantic_similarity": semantic.to_dict(),
        "technical": technical.to_dict(),
        "experience": experience.to_dict(),
        "career_consistency": career_consistency.to_dict(),
        "skill_cluster_bonus": skill_cluster.to_dict(),
        "behavioral": {
            "score": behavioral.score,
            "explanation": behavioral.explanation,
            "evidence": behavioral.positive_signals,
            "gaps": behavioral.risk_signals,
            "metadata": behavioral.components,
        },
        "authenticity": authenticity.to_dict(),
    }


def _combine_scores(
    semantic: ScoreResult,
    technical: ScoreResult,
    experience: ScoreResult,
    career_consistency: ScoreResult,
    skill_cluster: ScoreResult,
    behavioral: BehavioralScore,
    authenticity: ScoreResult,
    weights: dict[str, float],
    config: RankingConfig | None = None,
) -> float:
    active_config = config or DEFAULT_CONFIG
    cluster_bonus = min(active_config.scoring.skill_cluster_bonus_cap, skill_cluster.score)
    hybrid_score = min(
        100.0,
        technical.score * weights["technical_fit"]
        + experience.score * weights["experience"]
        + career_consistency.score * weights["career_consistency"]
        + behavioral.score * weights["behavioral"]
        + authenticity.score * weights["authenticity"]
        + cluster_bonus
    )
    value = hybrid_score * active_config.hybrid_weight + semantic.score * active_config.semantic_weight
    return round(min(100.0, value), 2)


def _normalize_weights(weights: dict[str, float], config: RankingConfig | None = None) -> dict[str, float]:
    active_config = config or DEFAULT_CONFIG
    complete = {**active_config.weights, **weights}
    total = sum(complete.values())
    if total <= 0:
        return active_config.weights
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
