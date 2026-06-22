"""Candidate scoring primitives for TalentLens AI."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
import re
from typing import Any

try:
    from .jd_parser import JobRequirements, SKILL_ALIASES
except ImportError:  # pragma: no cover - supports direct script execution
    from jd_parser import JobRequirements, SKILL_ALIASES


@dataclass(frozen=True)
class ScoreResult:
    score: float
    explanation: str
    evidence: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScoringConfig:
    """Configurable knobs for evidence-based scoring primitives."""

    technical_direct_match_cap: float = 90.0
    related_skill_bonus_cap: float = 5.0
    certification_bonus_cap: float = 5.0
    certification_bonus_per_item: float = 1.5
    experience_unspecified_base: float = 65.0
    experience_unspecified_year_bonus: float = 3.0
    experience_match_cap: float = 85.0
    experience_meets_requirement_bonus: float = 10.0
    seniority_multipliers: dict[str, float] = field(
        default_factory=lambda: {
            "unspecified": 1.0,
            "junior": 0.75,
            "mid": 1.0,
            "senior": 1.15,
            "lead": 1.3,
        }
    )
    career_base_score: float = 40.0
    career_entry_bonus: float = 4.0
    career_entry_bonus_cap: float = 20.0
    career_timeline_bonus_per_year: float = 1.5
    career_timeline_bonus_cap: float = 15.0
    career_title_progression_weight: float = 0.15
    career_role_relevance_weight: float = 0.10
    career_target_alignment_weight: float = 0.12
    career_consistent_timeline_bonus: float = 10.0
    career_large_timeline_delta_penalty: float = 15.0
    career_gap_grace_months: int = 18
    career_overlap_grace_months: int = 6
    unrelated_transition_penalty_cap: float = 18.0
    skill_cluster_minimum_hits: int = 3
    skill_cluster_bonus_cap: float = 8.0
    skill_cluster_points_per_skill: float = 1.5
    skill_cluster_extra_cluster_bonus: float = 1.0
    authenticity_weights: dict[str, float] = field(
        default_factory=lambda: {
            "verified_email": 18.0,
            "verified_phone": 14.0,
            "linkedin_connected": 14.0,
            "profile_completeness": 0.22,
            "career_history": 12.0,
            "education": 8.0,
            "skills": 8.0,
            "projects": 6.0,
            "corroborated_skill": 1.5,
            "corroborated_skill_cap": 10.0,
            "named_identity": 4.0,
        }
    )
    authenticity_generic_profile_penalty: float = 6.0
    authenticity_empty_profile_penalty: float = 8.0
    authenticity_suspicious_penalty_cap: float = 25.0
    authenticity_risk_thresholds: dict[str, float] = field(
        default_factory=lambda: {"low": 82.0, "medium": 62.0}
    )
    recruiter_cognitive_twin_weights: dict[str, float] = field(
        default_factory=lambda: {
            "technical_fit": 0.28,
            "experience": 0.18,
            "career_consistency": 0.18,
            "behavioral": 0.16,
            "authenticity": 0.12,
            "skill_cluster": 0.08,
        }
    )
    hidden_gem_weights: dict[str, float] = field(
        default_factory=lambda: {
            "technical_strength": 0.24,
            "project_strength": 0.20,
            "learning_velocity": 0.18,
            "github_activity": 0.14,
            "behavioral": 0.14,
            "underexposure": 0.10,
        }
    )
    hidden_gem_flag_threshold: float = 72.0
    hidden_gem_max_experience_years: float = 4.0


DEFAULT_SCORING_CONFIG = ScoringConfig()


SENIORITY_MULTIPLIERS = DEFAULT_SCORING_CONFIG.seniority_multipliers

SKILL_CLUSTERS: dict[str, set[str]] = {
    "ai_ml": {"python", "machine learning", "deep learning", "pytorch", "tensorflow", "statistics"},
    "genai": {"llm", "rag", "langchain", "vector db", "prompt engineering", "python", "nlp"},
    "data_science": {"python", "machine learning", "statistics", "pandas", "numpy", "sql"},
    "analytics": {"sql", "excel", "power bi", "tableau", "data analysis", "statistics"},
    "ml_engineering": {"python", "machine learning", "deep learning", "docker", "api development", "aws", "gcp", "azure"},
    "data_engineering": {"python", "sql", "data engineering", "spark", "airflow", "etl", "aws", "gcp", "azure", "docker"},
    "full_stack": {"javascript", "react", "api development", "git", "docker", "sql"},
}

CLUSTER_DISPLAY_NAMES: dict[str, str] = {
    "ai_ml": "AI/ML",
    "genai": "GenAI",
    "data_science": "Data Science",
    "analytics": "Analytics",
    "ml_engineering": "ML Engineering",
    "data_engineering": "Data Engineering",
    "full_stack": "Full Stack",
}

ROLE_FAMILIES: dict[str, set[str]] = {
    "ai_ml": {"machine learning", "deep learning", "pytorch", "tensorflow", "llm", "rag", "langchain", "nlp"},
    "data_science": {"python", "machine learning", "statistics", "data analysis", "pandas", "numpy", "sql", "data analyst", "data scientist"},
    "data_engineering": {"data engineering", "spark", "airflow", "etl", "sql", "data pipeline"},
    "analytics": {"sql", "excel", "power bi", "tableau", "data analysis", "analytics", "data analyst"},
    "software": {"api development", "javascript", "react", "docker", "git"},
}


def technical_fit_score(
    candidate: dict[str, Any],
    requirements: JobRequirements | dict[str, Any],
    config: ScoringConfig | None = None,
) -> ScoreResult:
    """Score skill alignment against parsed JD requirements."""

    active_config = config or DEFAULT_SCORING_CONFIG
    required_skills = _requirements_value(requirements, "required_skills", default=[]) or []
    required_skills = [_canonical_skill(skill) for skill in required_skills]
    candidate_skills = _candidate_skill_set(candidate)
    certifications = _flatten_text_values(candidate.get("certifications"))

    if not required_skills:
        return ScoreResult(
            score=50.0,
            explanation="No required skills were extracted from the job description; technical fit is neutral.",
            evidence=sorted(candidate_skills)[:8],
            gaps=[],
            metadata={
                "matched_skills": [],
                "missing_skills": [],
                "candidate_skills": sorted(candidate_skills),
                "reasoning": {"neutral_score": 50.0, "reason": "No required skills were available to match."},
            },
        )

    matched = [skill for skill in required_skills if skill in candidate_skills]
    missing = [skill for skill in required_skills if skill not in candidate_skills]
    direct_match_score = (len(matched) / len(required_skills)) * active_config.technical_direct_match_cap
    related_skill_bonus = _related_skill_bonus(missing, candidate_skills, active_config)
    certification_bonus = min(
        active_config.certification_bonus_cap,
        len(certifications) * active_config.certification_bonus_per_item,
    )
    score = _clamp(direct_match_score + related_skill_bonus + certification_bonus)

    evidence = [f"Matched required skill: {skill}" for skill in matched]
    if certification_bonus:
        evidence.append(f"Certification evidence available: {len(certifications)} item(s)")

    gaps = [f"Missing required skill: {skill}" for skill in missing]
    explanation = (
        f"Matched {len(matched)} of {len(required_skills)} required skills."
        if matched
        else "No required skills were directly matched."
    )

    return ScoreResult(
        score=round(score, 2),
        explanation=explanation,
        evidence=evidence,
        gaps=gaps,
        metadata={
            "matched_skills": matched,
            "missing_skills": missing,
            "candidate_skills": sorted(candidate_skills),
            "certification_bonus": round(certification_bonus, 2),
            "reasoning": {
                "direct_match_score": round(direct_match_score, 2),
                "related_skill_bonus": round(related_skill_bonus, 2),
                "certification_bonus": round(certification_bonus, 2),
            },
        },
    )


def experience_score(
    candidate: dict[str, Any],
    requirements: JobRequirements | dict[str, Any],
    config: ScoringConfig | None = None,
) -> ScoreResult:
    """Score candidate experience against JD years and seniority needs."""

    active_config = config or DEFAULT_SCORING_CONFIG
    required_years = float(_requirements_value(requirements, "years_experience", default=0.0) or 0.0)
    seniority = str(_requirements_value(requirements, "seniority_level", default="unspecified") or "unspecified")
    candidate_years = estimate_years_experience(candidate)

    if required_years <= 0:
        score = _clamp(active_config.experience_unspecified_base + min(candidate_years, 10) * active_config.experience_unspecified_year_bonus)
        explanation = "The JD does not specify years of experience, so candidate experience is scored as supportive evidence."
        gaps: list[str] = []
    else:
        ratio = candidate_years / required_years if required_years else 1.0
        base_score = min(100.0, ratio * active_config.experience_match_cap)
        if candidate_years >= required_years:
            base_score += active_config.experience_meets_requirement_bonus
        score = _clamp(base_score * active_config.seniority_multipliers.get(seniority, 1.0))
        explanation = f"Estimated {candidate_years:.1f} years against {required_years:.1f} required years."
        gaps = [] if candidate_years >= required_years else [f"Below required experience by {required_years - candidate_years:.1f} years"]

    evidence = [f"Estimated experience: {candidate_years:.1f} years"]
    if seniority != "unspecified":
        evidence.append(f"JD seniority level: {seniority}")

    return ScoreResult(
        score=round(score, 2),
        explanation=explanation,
        evidence=evidence,
        gaps=gaps,
        metadata={
            "candidate_years": round(candidate_years, 2),
            "required_years": required_years,
            "seniority_level": seniority,
            "reasoning": {
                "seniority_multiplier": active_config.seniority_multipliers.get(seniority, 1.0),
                "experience_match_cap": active_config.experience_match_cap,
                "meets_requirement_bonus": active_config.experience_meets_requirement_bonus
                if required_years and candidate_years >= required_years
                else 0.0,
            },
        },
    )


def career_consistency_score(
    candidate: dict[str, Any],
    requirements: JobRequirements | dict[str, Any] | None = None,
    config: ScoringConfig | None = None,
) -> ScoreResult:
    """Score whether career history looks coherent, complete, and progressive."""

    active_config = config or DEFAULT_SCORING_CONFIG
    entries = _career_entries(candidate)
    profile_years = estimate_years_experience(candidate)

    if not entries:
        return ScoreResult(
            score=35.0 if profile_years else 20.0,
            explanation="Career consistency is weak because structured career history is missing.",
            evidence=[f"Profile reports {profile_years:.1f} years"] if profile_years else [],
            gaps=["Missing structured career history"],
            metadata={
                "entry_count": 0,
                "profile_years": profile_years,
                "timeline_years": 0.0,
                "target_role_alignment_score": 0.0,
                "reasoning": {"base_reason": "No structured career entries were available to evaluate progression."},
            },
        )

    dated_ranges = [_entry_date_range(entry) for entry in entries]
    dated_ranges = [item for item in dated_ranges if item[0] is not None]
    timeline_years = _timeline_years(dated_ranges)
    gaps_months, overlap_months = _timeline_gaps_and_overlaps(dated_ranges)
    title_progression = _title_progression_score(entries)
    role_relevance = _role_relevance_score(entries, candidate)
    target_alignment = _target_role_alignment_score(entries, candidate, requirements)
    transition_penalty = _unrelated_transition_penalty(entries, requirements, active_config)

    entry_bonus = min(active_config.career_entry_bonus_cap, len(entries) * active_config.career_entry_bonus)
    timeline_bonus = min(
        active_config.career_timeline_bonus_cap,
        timeline_years * active_config.career_timeline_bonus_per_year,
    )
    progression_bonus = title_progression * active_config.career_title_progression_weight
    relevance_bonus = role_relevance * active_config.career_role_relevance_weight
    target_alignment_bonus = target_alignment * active_config.career_target_alignment_weight

    score = active_config.career_base_score
    score += entry_bonus
    score += timeline_bonus
    score += progression_bonus
    score += relevance_bonus
    score += target_alignment_bonus

    if profile_years and timeline_years:
        delta = abs(profile_years - timeline_years)
        if delta <= 1.5:
            score += active_config.career_consistent_timeline_bonus
        elif delta >= 4:
            score -= active_config.career_large_timeline_delta_penalty

    gap_penalty = 0.0
    overlap_penalty = 0.0
    if gaps_months > active_config.career_gap_grace_months:
        gap_penalty = min(15.0, (gaps_months - active_config.career_gap_grace_months) / 3)
        score -= gap_penalty
    if overlap_months > active_config.career_overlap_grace_months:
        overlap_penalty = min(12.0, (overlap_months - active_config.career_overlap_grace_months) / 2)
        score -= overlap_penalty
    if transition_penalty:
        score -= transition_penalty

    evidence = [f"{len(entries)} career role(s) provided"]
    if timeline_years:
        evidence.append(f"Career timeline covers about {timeline_years:.1f} years")
    if title_progression >= 65:
        evidence.append("Career titles show progression or stable specialization")
    if role_relevance >= 70:
        evidence.append("Career history aligns with declared profile/skills")
    if target_alignment >= 70:
        evidence.append("Career history aligns with the target role")

    gaps = []
    if not dated_ranges:
        gaps.append("Career entries do not include usable dates")
    if gaps_months > 18:
        gaps.append(f"Career timeline has about {gaps_months // 12:.0f}+ year(s) of unexplained gaps")
    if overlap_months > 6:
        gaps.append("Career timeline has overlapping roles that may need review")
    if profile_years and timeline_years and abs(profile_years - timeline_years) >= 4:
        gaps.append("Profile experience and career timeline do not agree closely")
    if target_alignment < 45:
        gaps.append("Career history has limited alignment with the target role")
    if transition_penalty:
        gaps.append("Career path includes unrelated transitions for a specialized role")

    return ScoreResult(
        score=round(_clamp(score), 2),
        explanation="Career consistency checks timeline completeness, progression, and profile corroboration.",
        evidence=evidence,
        gaps=gaps,
        metadata={
            "entry_count": len(entries),
            "profile_years": round(profile_years, 2),
            "timeline_years": round(timeline_years, 2),
            "gap_months": gaps_months,
            "overlap_months": overlap_months,
            "title_progression_score": round(title_progression, 2),
            "role_relevance_score": round(role_relevance, 2),
            "target_role_alignment_score": round(target_alignment, 2),
            "unrelated_transition_penalty": round(transition_penalty, 2),
            "reasoning": {
                "base_score": active_config.career_base_score,
                "entry_bonus": round(entry_bonus, 2),
                "timeline_bonus": round(timeline_bonus, 2),
                "progression_bonus": round(progression_bonus, 2),
                "role_relevance_bonus": round(relevance_bonus, 2),
                "target_alignment_bonus": round(target_alignment_bonus, 2),
                "gap_penalty": round(gap_penalty, 2),
                "overlap_penalty": round(overlap_penalty, 2),
            },
        },
    )


def skill_cluster_bonus(
    candidate: dict[str, Any],
    requirements: JobRequirements | dict[str, Any],
    config: ScoringConfig | None = None,
) -> ScoreResult:
    """Reward coherent skill groups that make the candidate stronger than keyword matching alone."""

    active_config = config or DEFAULT_SCORING_CONFIG
    candidate_skills = _candidate_skill_set(candidate)
    required_skills = {
        _canonical_skill(skill)
        for skill in (_requirements_value(requirements, "required_skills", default=[]) or [])
        if _canonical_skill(skill)
    }

    cluster_hits: dict[str, list[str]] = {}
    for cluster_name, cluster_skills in SKILL_CLUSTERS.items():
        matched = sorted(candidate_skills & cluster_skills)
        if len(matched) >= active_config.skill_cluster_minimum_hits:
            cluster_hits[cluster_name] = matched

    jd_aligned_clusters = {
        name: matched
        for name, matched in cluster_hits.items()
        if not required_skills or bool(required_skills & SKILL_CLUSTERS[name])
    }
    best_cluster_size = max((len(matched) for matched in jd_aligned_clusters.values()), default=0)
    bonus = min(
        active_config.skill_cluster_bonus_cap,
        best_cluster_size * active_config.skill_cluster_points_per_skill
        + max(0, len(jd_aligned_clusters) - 1) * active_config.skill_cluster_extra_cluster_bonus,
    )

    evidence = [
        f"{CLUSTER_DISPLAY_NAMES.get(name, name.replace('_', ' ').title())} cluster: {', '.join(matched[:5])}"
        for name, matched in sorted(jd_aligned_clusters.items())
    ]
    gaps = [] if evidence else ["No strong JD-aligned skill cluster detected"]

    return ScoreResult(
        score=round(bonus, 2),
        explanation=f"Skill cluster bonus adds up to 8 points for coherent, JD-aligned capability groups.",
        evidence=evidence,
        gaps=gaps,
        metadata={
            "bonus_points": round(bonus, 2),
            "clusters": jd_aligned_clusters,
            "candidate_skills": sorted(candidate_skills),
            "reasoning": {
                "minimum_cluster_hits": active_config.skill_cluster_minimum_hits,
                "best_cluster_size": best_cluster_size,
                "aligned_cluster_count": len(jd_aligned_clusters),
                "bonus_cap": active_config.skill_cluster_bonus_cap,
            },
        },
    )


def authenticity_score(candidate: dict[str, Any], config: ScoringConfig | None = None) -> ScoreResult:
    """Score trustworthiness and profile authenticity from Redrob and profile data."""

    active_config = config or DEFAULT_SCORING_CONFIG
    weights = active_config.authenticity_weights
    signals = candidate.get("redrob_signals") if isinstance(candidate.get("redrob_signals"), dict) else {}
    profile = candidate.get("profile") if isinstance(candidate.get("profile"), dict) else {}

    verified_email = _as_bool(signals.get("verified_email"))
    verified_phone = _as_bool(signals.get("verified_phone"))
    linkedin_connected = _as_bool(signals.get("linkedin_connected"))
    completeness = _score_rate(signals.get("profile_completeness_score"))
    career_history = candidate.get("career_history")
    education = candidate.get("education")
    skills = candidate.get("skills")
    projects = candidate.get("projects")
    candidate_skills = _candidate_skill_set(candidate)
    corroborated_skills, uncorroborated_skills = _skill_corroboration(candidate, candidate_skills)
    activity_score = _score_rate(signals.get("github_activity_score"))

    evidence: list[str] = []
    gaps: list[str] = []
    score = 0.0

    score += weights["verified_email"] if verified_email else 0
    score += weights["verified_phone"] if verified_phone else 0
    score += weights["linkedin_connected"] if linkedin_connected else 0
    score += completeness * weights["profile_completeness"]
    score += weights["career_history"] if _has_content(career_history) else 0
    score += weights["education"] if _has_content(education) else 0
    score += weights["skills"] if _has_content(skills) else 0
    score += weights["projects"] if _has_content(projects) else 0
    corroboration_bonus = min(
        weights["corroborated_skill_cap"],
        len(corroborated_skills) * weights["corroborated_skill"],
    )
    score += corroboration_bonus
    score += weights["named_identity"] if _has_named_identity(profile) else 0

    if verified_email:
        evidence.append("Verified email")
    else:
        gaps.append("Email is not verified")

    if verified_phone:
        evidence.append("Verified phone")
    else:
        gaps.append("Phone is not verified")

    if linkedin_connected:
        evidence.append("LinkedIn connected")
    else:
        gaps.append("LinkedIn is not connected")

    if completeness >= 75:
        evidence.append("High profile completeness")
    elif completeness < 45:
        gaps.append("Low profile completeness")

    if _has_content(career_history):
        evidence.append("Career history present")
    else:
        gaps.append("Missing career history")

    if _has_content(skills):
        evidence.append("Skills present")
    else:
        gaps.append("Missing skills")

    if _has_content(projects):
        evidence.append("Project evidence present")

    if corroborated_skills:
        evidence.append(f"Corroborated claimed skills: {', '.join(corroborated_skills[:5])}")

    generic_penalty = _generic_profile_penalty(candidate, active_config)
    if generic_penalty:
        score -= generic_penalty
        gaps.append("Profile text appears sparse or generic")

    suspicious_penalty, suspicious_flags = _suspicious_profile_penalty(
        candidate_skills,
        uncorroborated_skills,
        activity_score,
        _has_content(career_history),
        _has_content(projects),
        _has_content(candidate.get("certifications")),
        active_config,
    )
    if suspicious_penalty:
        score -= suspicious_penalty
        gaps.extend(suspicious_flags)

    score = _clamp(score)
    risk_level = authenticity_risk_level(score, gaps, suspicious_flags if suspicious_penalty else [], active_config)
    explanation = "Authenticity is based on verification, completeness, and evidence density."

    return ScoreResult(
        score=round(score, 2),
        explanation=explanation,
        evidence=evidence,
        gaps=gaps,
        metadata={
            "verified_email": verified_email,
            "verified_phone": verified_phone,
            "linkedin_connected": linkedin_connected,
            "profile_completeness_score": round(completeness, 2),
            "generic_penalty": generic_penalty,
            "activity_score": round(activity_score, 2),
            "corroborated_skills": corroborated_skills,
            "uncorroborated_skills": uncorroborated_skills,
            "suspicious_flags": suspicious_flags if suspicious_penalty else [],
            "suspicious_penalty": suspicious_penalty,
            "risk_level": risk_level,
            "reasoning": {
                "verification_points": round(
                    (weights["verified_email"] if verified_email else 0)
                    + (weights["verified_phone"] if verified_phone else 0)
                    + (weights["linkedin_connected"] if linkedin_connected else 0),
                    2,
                ),
                "profile_completeness_points": round(completeness * weights["profile_completeness"], 2),
                "corroboration_bonus": round(corroboration_bonus, 2),
                "generic_penalty": round(generic_penalty, 2),
                "suspicious_penalty": round(suspicious_penalty, 2),
            },
        },
    )


def authenticity_risk_level(
    score: float,
    gaps: list[str] | None = None,
    suspicious_flags: list[str] | None = None,
    config: ScoringConfig | None = None,
) -> str:
    """Classify authenticity risk for recruiter-facing explanations."""

    active_config = config or DEFAULT_SCORING_CONFIG
    low_threshold = active_config.authenticity_risk_thresholds["low"]
    medium_threshold = active_config.authenticity_risk_thresholds["medium"]
    gap_count = len(gaps or [])
    suspicious_count = len(suspicious_flags or [])
    if score >= low_threshold and gap_count <= 2 and suspicious_count == 0:
        return "LOW"
    if score >= medium_threshold and gap_count <= 5 and suspicious_count <= 1:
        return "MEDIUM"
    return "HIGH"


def recruiter_cognitive_twin_score(
    technical: ScoreResult,
    experience: ScoreResult,
    career_consistency: ScoreResult,
    skill_cluster: ScoreResult,
    behavioral: Any,
    authenticity: ScoreResult,
    config: ScoringConfig | None = None,
) -> ScoreResult:
    """Simulate an experienced recruiter's holistic read of the candidate."""

    active_config = config or DEFAULT_SCORING_CONFIG
    weights = active_config.recruiter_cognitive_twin_weights
    cluster_score = _clamp((skill_cluster.score / max(1.0, active_config.skill_cluster_bonus_cap)) * 100)
    score = (
        technical.score * weights["technical_fit"]
        + experience.score * weights["experience"]
        + career_consistency.score * weights["career_consistency"]
        + behavioral.score * weights["behavioral"]
        + authenticity.score * weights["authenticity"]
        + cluster_score * weights["skill_cluster"]
    )

    evidence: list[str] = []
    gaps: list[str] = []

    if technical.score >= 75:
        evidence.append("Strong technical match to the target role")
    elif technical.score >= 60:
        evidence.append("Solid technical base with some missing JD skills")
    else:
        gaps.extend(technical.gaps[:2] or ["Technical match needs recruiter validation"])

    if career_consistency.score >= 80:
        evidence.append("Career path shows coherent progression and role alignment")
    elif career_consistency.score < 60:
        gaps.extend(career_consistency.gaps[:2] or ["Career story is not yet fully convincing"])

    if experience.score >= 85:
        evidence.append("Experience level fits the seniority expectation")
    elif experience.gaps:
        gaps.extend(experience.gaps[:1])

    if behavioral.score >= 75:
        evidence.append("High recruiter engagement and activity signals")
    elif getattr(behavioral, "risk_signals", None):
        gaps.extend(behavioral.risk_signals[:2])

    if authenticity.score >= 80 and authenticity.metadata.get("risk_level") == "LOW":
        evidence.append("Low authenticity risk with profile evidence support")
    elif authenticity.gaps:
        gaps.extend(authenticity.gaps[:2])

    if skill_cluster.score > 0 and skill_cluster.evidence:
        evidence.append(f"Meaningful skill ecosystem detected: {skill_cluster.evidence[0]}")

    reasoning_parts = evidence[:4]
    if gaps:
        reasoning_parts.append(f"Minor concern: {gaps[0]}")
    explanation = "Recruiter cognitive twin combines fit, trajectory, trust, engagement, and skill ecosystem signals."

    return ScoreResult(
        score=round(_clamp(score), 2),
        explanation=explanation,
        evidence=evidence,
        gaps=_dedupe(gaps),
        metadata={
            "reasoning": {
                "weights": weights,
                "skill_cluster_normalized_score": round(cluster_score, 2),
                "dimension_scores": {
                    "technical_fit": technical.score,
                    "experience": experience.score,
                    "career_consistency": career_consistency.score,
                    "behavioral": behavioral.score,
                    "authenticity": authenticity.score,
                    "skill_cluster": skill_cluster.score,
                },
            },
            "recruiter_reasoning": " ".join(reasoning_parts),
        },
    )


def hidden_gem_score(
    candidate: dict[str, Any],
    technical: ScoreResult,
    experience: ScoreResult,
    skill_cluster: ScoreResult,
    behavioral: Any,
    config: ScoringConfig | None = None,
) -> ScoreResult:
    """Find high-upside candidates that may be under-ranked by traditional screening."""

    active_config = config or DEFAULT_SCORING_CONFIG
    weights = active_config.hidden_gem_weights
    candidate_years = float(experience.metadata.get("candidate_years", estimate_years_experience(candidate)) or 0.0)
    signals = candidate.get("redrob_signals") if isinstance(candidate.get("redrob_signals"), dict) else {}
    github_activity = _score_rate(signals.get("github_activity_score"))
    search_visibility = _score_rate(signals.get("search_appearance_30d"))
    recruiter_saves = _score_rate(signals.get("saved_by_recruiters_30d"))
    project_strength = _project_strength_score(candidate)
    learning_velocity = _learning_velocity_score(candidate, candidate_years)
    cluster_strength = _clamp((skill_cluster.score / max(1.0, active_config.skill_cluster_bonus_cap)) * 100)
    candidate_skills = _candidate_skill_set(candidate)
    advanced_skills = {
        "machine learning",
        "deep learning",
        "pytorch",
        "tensorflow",
        "llm",
        "rag",
        "langchain",
        "vector db",
        "spark",
        "airflow",
    }
    skill_breadth_strength = _clamp(len(candidate_skills) * 12.0 + len(candidate_skills & advanced_skills) * 8.0)
    technical_strength = max(
        _clamp(technical.score * 0.7 + cluster_strength * 0.3),
        skill_breadth_strength,
    )
    underexposure = _underexposure_score(candidate_years, search_visibility, recruiter_saves, active_config)

    score = (
        technical_strength * weights["technical_strength"]
        + project_strength * weights["project_strength"]
        + learning_velocity * weights["learning_velocity"]
        + github_activity * weights["github_activity"]
        + behavioral.score * weights["behavioral"]
        + underexposure * weights["underexposure"]
    )
    score = round(_clamp(score), 2)

    evidence: list[str] = []
    gaps: list[str] = []
    if project_strength >= 65:
        evidence.append("Project evidence suggests practical build ability")
    else:
        gaps.append("Limited project evidence for hidden-gem confidence")
    if technical_strength >= 70:
        evidence.append("Technical skills and clusters show strong upside")
    if learning_velocity >= 70:
        evidence.append("Learning velocity appears high for experience level")
    if github_activity >= 60:
        evidence.append("GitHub activity supports hands-on learning signal")
    elif github_activity < 35:
        gaps.append("GitHub activity is not strong enough for a hidden-gem signal")
    if behavioral.score >= 60:
        evidence.append("Behavioral signals are healthy enough for recruiter follow-up")
    if underexposure >= 60:
        evidence.append("Lower experience or visibility suggests the candidate may be overlooked")

    flag = (
        score >= active_config.hidden_gem_flag_threshold
        and candidate_years <= active_config.hidden_gem_max_experience_years
        and project_strength >= 55
        and technical_strength >= 65
        and github_activity >= 55
        and behavioral.score >= 55
    )
    if flag:
        reason = "Potential high-growth candidate that may be missed by traditional screening."
    elif score >= 65:
        reason = "Shows some hidden-gem traits, but evidence is not strong enough to flag."
    else:
        reason = "Not a hidden-gem profile under the current evidence thresholds."

    return ScoreResult(
        score=score,
        explanation=reason,
        evidence=evidence,
        gaps=_dedupe(gaps),
        metadata={
            "hidden_gem_flag": flag,
            "hidden_gem_reason": _hidden_gem_reason(flag, evidence, gaps),
            "reasoning": {
                "weights": weights,
                "candidate_years": round(candidate_years, 2),
                "technical_strength": round(technical_strength, 2),
                "skill_breadth_strength": round(skill_breadth_strength, 2),
                "project_strength": round(project_strength, 2),
                "learning_velocity": round(learning_velocity, 2),
                "github_activity": round(github_activity, 2),
                "behavioral": behavioral.score,
                "underexposure": round(underexposure, 2),
                "flag_threshold": active_config.hidden_gem_flag_threshold,
            },
        },
    )


def estimate_years_experience(candidate: dict[str, Any]) -> float:
    """Estimate total professional experience from profile and career history."""

    profile = candidate.get("profile") if isinstance(candidate.get("profile"), dict) else {}
    direct_years = _first_number(
        profile.get("years_experience"),
        profile.get("total_experience"),
        profile.get("experience_years"),
        candidate.get("years_experience"),
        candidate.get("total_experience"),
    )
    if direct_years is not None:
        return max(0.0, direct_years)

    career_history = candidate.get("career_history")
    entries = career_history if isinstance(career_history, list) else []
    total_months = 0

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        explicit_years = _first_number(entry.get("years"), entry.get("duration_years"), entry.get("experience_years"))
        if explicit_years is not None:
            total_months += int(explicit_years * 12)
            continue

        duration_text = " ".join(str(value) for value in entry.values() if value is not None)
        duration_years = _years_from_duration_text(duration_text)
        if duration_years is not None:
            total_months += int(duration_years * 12)
            continue

        start = _parse_date(entry.get("start_date") or entry.get("from") or entry.get("start"))
        end = _parse_date(entry.get("end_date") or entry.get("to") or entry.get("end")) or date.today()
        if start and end and end >= start:
            total_months += (end.year - start.year) * 12 + (end.month - start.month)

    return round(max(0.0, total_months / 12), 2)


def _career_entries(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    career_history = candidate.get("career_history")
    if not isinstance(career_history, list):
        return []
    return [entry for entry in career_history if isinstance(entry, dict)]


def _entry_date_range(entry: dict[str, Any]) -> tuple[date | None, date | None]:
    start = _parse_date(
        entry.get("start_date")
        or entry.get("from")
        or entry.get("start")
        or entry.get("started_at")
    )
    end = _parse_date(
        entry.get("end_date")
        or entry.get("to")
        or entry.get("end")
        or entry.get("ended_at")
    )
    if start and not end:
        end = date.today()
    return start, end


def _timeline_years(ranges: list[tuple[date | None, date | None]]) -> float:
    months = 0
    for start, end in ranges:
        if start and end and end >= start:
            months += (end.year - start.year) * 12 + (end.month - start.month)
    return max(0.0, months / 12)


def _timeline_gaps_and_overlaps(ranges: list[tuple[date | None, date | None]]) -> tuple[int, int]:
    usable = sorted(
        [(start, end or date.today()) for start, end in ranges if start],
        key=lambda item: item[0],
    )
    gap_months = 0
    overlap_months = 0
    for previous, current in zip(usable, usable[1:]):
        previous_end = previous[1]
        current_start = current[0]
        delta = (current_start.year - previous_end.year) * 12 + (current_start.month - previous_end.month)
        if delta > 1:
            gap_months += delta
        elif delta < 0:
            overlap_months += abs(delta)
    return gap_months, overlap_months


def _title_progression_score(entries: list[dict[str, Any]]) -> float:
    titles = [
        str(entry.get("title") or entry.get("role") or entry.get("position") or "").lower()
        for entry in entries
    ]
    titles = [title for title in titles if title]
    if not titles:
        return 35.0

    seniority_points = []
    for title in titles:
        if any(keyword in title for keyword in ("lead", "principal", "staff", "head", "architect")):
            seniority_points.append(4)
        elif any(keyword in title for keyword in ("senior", "sr")):
            seniority_points.append(3)
        elif any(keyword in title for keyword in ("associate", "mid", "ii")):
            seniority_points.append(2)
        elif any(keyword in title for keyword in ("intern", "trainee", "junior", "jr")):
            seniority_points.append(1)
        else:
            seniority_points.append(2)

    stable_or_growing = sum(1 for earlier, later in zip(seniority_points, seniority_points[1:]) if later >= earlier)
    if len(seniority_points) == 1:
        return 60.0
    return _clamp(45 + stable_or_growing / (len(seniority_points) - 1) * 55)


def _role_relevance_score(entries: list[dict[str, Any]], candidate: dict[str, Any]) -> float:
    candidate_skills = _candidate_skill_set(candidate)
    if not candidate_skills:
        return 35.0

    career_text = " ".join(
        " ".join(str(value) for value in entry.values() if value is not None)
        for entry in entries
    ).lower()
    matched = 0
    for skill in candidate_skills:
        aliases = SKILL_ALIASES.get(skill, (skill,))
        if any(_contains_phrase(career_text, alias.lower()) for alias in aliases):
            matched += 1
    return _clamp((matched / max(1, len(candidate_skills))) * 100)


def _target_role_alignment_score(
    entries: list[dict[str, Any]],
    candidate: dict[str, Any],
    requirements: JobRequirements | dict[str, Any] | None,
) -> float:
    required_skills = _required_skill_set(requirements)
    if not required_skills:
        return _role_relevance_score(entries, candidate)

    career_text = _career_text(entries)
    matched_required = 0
    for skill in required_skills:
        aliases = SKILL_ALIASES.get(skill, (skill,))
        if any(_contains_phrase(career_text, alias.lower()) for alias in aliases):
            matched_required += 1

    role_family = _dominant_role_family(required_skills)
    family_score = 0.0
    if role_family:
        family_terms = ROLE_FAMILIES[role_family]
        family_hits = sum(1 for term in family_terms if any(alias in career_text for alias in SKILL_ALIASES.get(term, (term,))))
        family_score = min(100.0, family_hits / max(1, min(4, len(family_terms))) * 100)

    required_score = matched_required / max(1, len(required_skills)) * 100
    return _clamp(required_score * 0.7 + family_score * 0.3)


def _unrelated_transition_penalty(
    entries: list[dict[str, Any]],
    requirements: JobRequirements | dict[str, Any] | None,
    config: ScoringConfig | None = None,
) -> float:
    active_config = config or DEFAULT_SCORING_CONFIG
    required_skills = _required_skill_set(requirements)
    role_family = _dominant_role_family(required_skills)
    if not role_family or len(entries) < 2:
        return 0.0

    unrelated_count = 0
    for entry in entries:
        entry_text = " ".join(str(value) for value in entry.values() if value is not None).lower()
        family_terms = ROLE_FAMILIES[role_family]
        if not any(term in entry_text for term in family_terms):
            unrelated_count += 1

    unrelated_ratio = unrelated_count / len(entries)
    if unrelated_ratio < 0.4:
        return 0.0
    return min(active_config.unrelated_transition_penalty_cap, unrelated_ratio * 20)


def _required_skill_set(requirements: JobRequirements | dict[str, Any] | None) -> set[str]:
    required = _requirements_value(requirements, "required_skills", default=[]) if requirements else []
    return {_canonical_skill(skill) for skill in required if _canonical_skill(skill)}


def _dominant_role_family(required_skills: set[str]) -> str | None:
    if not required_skills:
        return None
    scores = {
        family: len(required_skills & skills)
        for family, skills in ROLE_FAMILIES.items()
    }
    family, score = max(scores.items(), key=lambda item: item[1])
    return family if score >= 2 else None


def _career_text(entries: list[dict[str, Any]]) -> str:
    return " ".join(
        " ".join(str(value) for value in entry.values() if value is not None)
        for entry in entries
    ).lower()


def _candidate_skill_set(candidate: dict[str, Any]) -> set[str]:
    values = _flatten_text_values(candidate.get("skills"))
    text = " ".join(values)
    profile = candidate.get("profile") if isinstance(candidate.get("profile"), dict) else {}
    text = " ".join([text, *[str(value) for value in profile.values() if isinstance(value, str)]])

    skill_set: set[str] = set()
    lowered = text.lower()
    for canonical, aliases in SKILL_ALIASES.items():
        if any(_contains_phrase(lowered, alias.lower()) for alias in aliases):
            skill_set.add(canonical)

    for value in values:
        canonical = _canonical_skill(value)
        if canonical:
            skill_set.add(canonical)

    return skill_set


def _skill_corroboration(candidate: dict[str, Any], candidate_skills: set[str]) -> tuple[list[str], list[str]]:
    evidence_text = " ".join(
        _flatten_text_values(candidate.get("career_history"))
        + _flatten_text_values(candidate.get("certifications"))
        + _flatten_text_values(candidate.get("projects"))
        + _flatten_text_values(candidate.get("education"))
    ).lower()

    corroborated: list[str] = []
    uncorroborated: list[str] = []
    for skill in sorted(candidate_skills):
        aliases = SKILL_ALIASES.get(skill, (skill,))
        if any(_contains_phrase(evidence_text, alias.lower()) for alias in aliases):
            corroborated.append(skill)
        else:
            uncorroborated.append(skill)
    return corroborated, uncorroborated


def _suspicious_profile_penalty(
    candidate_skills: set[str],
    uncorroborated_skills: list[str],
    activity_score: float,
    has_career_history: bool,
    has_projects: bool,
    has_certifications: bool,
    config: ScoringConfig | None = None,
) -> tuple[float, list[str]]:
    active_config = config or DEFAULT_SCORING_CONFIG
    flags: list[str] = []
    penalty = 0.0

    if len(candidate_skills) >= 8 and len(uncorroborated_skills) / max(1, len(candidate_skills)) >= 0.55:
        flags.append("Many claimed skills are not supported by experience, projects, or certifications")
        penalty += 12

    advanced_skills = {"machine learning", "deep learning", "pytorch", "tensorflow", "llm", "rag", "langchain", "vector db"}
    advanced_claims = sorted(candidate_skills & advanced_skills)
    unsupported_advanced = [skill for skill in advanced_claims if skill in uncorroborated_skills]
    if len(unsupported_advanced) >= 3 and activity_score < 35 and not has_projects:
        flags.append("Advanced AI/ML claims have weak project and activity support")
        penalty += 14

    if not has_career_history and len(candidate_skills) >= 5:
        flags.append("Multiple skills claimed without structured career history")
        penalty += 8

    if not has_projects and not has_certifications and len(candidate_skills) >= 7:
        flags.append("Broad skill profile lacks project or certification evidence")
        penalty += 8

    return min(active_config.authenticity_suspicious_penalty_cap, penalty), flags


def _canonical_skill(skill: Any) -> str:
    value = str(skill or "").strip().lower()
    if not value:
        return ""
    for canonical, aliases in SKILL_ALIASES.items():
        if value == canonical or value in {alias.lower() for alias in aliases}:
            return canonical
    return re.sub(r"\s+", " ", value)


def _related_skill_bonus(
    missing: list[str],
    candidate_skills: set[str],
    config: ScoringConfig | None = None,
) -> float:
    active_config = config or DEFAULT_SCORING_CONFIG
    if not missing:
        return 0.0
    candidate_text = " ".join(candidate_skills)
    bonus = 0.0
    for skill in missing:
        tokens = [token for token in re.split(r"[^a-z0-9]+", skill) if len(token) > 2]
        if tokens and any(token in candidate_text for token in tokens):
            bonus += 2.0
    return min(active_config.related_skill_bonus_cap, bonus)


def _flatten_text_values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [str(item) for item in value.values() if item is not None]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(_flatten_text_values(item))
        return result
    return [str(value)]


def _requirements_value(requirements: JobRequirements | dict[str, Any], key: str, default: Any = None) -> Any:
    if isinstance(requirements, dict):
        return requirements.get(key, default)
    return getattr(requirements, key, default)


def _score_rate(value: Any) -> float:
    number = _first_number(value)
    if number is None:
        return 0.0
    if 0 <= number <= 1:
        number *= 100
    return _clamp(number)


def _first_number(*values: Any) -> float | None:
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            match = re.search(r"\d+(?:\.\d+)?", value.replace(",", ""))
            if match:
                return float(match.group())
    return None


def _years_from_duration_text(text: str) -> float | None:
    lowered = text.lower()
    year_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:years|yrs|year)", lowered)
    month_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:months|month|mos)", lowered)
    years = float(year_match.group(1)) if year_match else 0.0
    months = float(month_match.group(1)) if month_match else 0.0
    total = years + months / 12
    return total if total else None


def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    text = str(value).strip().lower()
    if not text or text in {"present", "current", "now"}:
        return date.today()

    formats = ("%Y-%m-%d", "%Y-%m", "%Y", "%b %Y", "%B %Y", "%m/%Y", "%d/%m/%Y")
    for fmt in formats:
        try:
            parsed = datetime.strptime(text.title(), fmt)
            return parsed.date().replace(day=1)
        except ValueError:
            continue
    return None


def _contains_phrase(text: str, phrase: str) -> bool:
    escaped = re.escape(phrase).replace(r"\ ", r"\s+")
    return bool(re.search(rf"(?<![a-z0-9+#.]){escaped}(?![a-z0-9+#.])", text))


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "y", "1", "verified", "connected"}
    return False


def _has_content(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def _has_named_identity(profile: dict[str, Any]) -> bool:
    return any(_has_content(profile.get(key)) for key in ("name", "full_name", "candidate_name", "headline", "title"))


def _generic_profile_penalty(candidate: dict[str, Any], config: ScoringConfig | None = None) -> float:
    active_config = config or DEFAULT_SCORING_CONFIG
    text = " ".join(_flatten_text_values(candidate.get("profile")))
    if not text.strip():
        return active_config.authenticity_empty_profile_penalty
    unique_words = set(re.findall(r"[a-zA-Z]{3,}", text.lower()))
    return active_config.authenticity_generic_profile_penalty if len(unique_words) < 8 else 0.0


def _project_strength_score(candidate: dict[str, Any]) -> float:
    projects = candidate.get("projects")
    values = _flatten_text_values(projects)
    if not values:
        return 35.0

    project_text = " ".join(values).lower()
    score = min(55.0, len(values) * 18.0)
    build_terms = (
        "deployed",
        "production",
        "api",
        "pipeline",
        "ranking",
        "rag",
        "llm",
        "model",
        "dashboard",
        "open source",
        "github",
    )
    score += min(30.0, sum(1 for term in build_terms if term in project_text) * 5.0)
    if any(_contains_phrase(project_text, skill) for skill in ("machine learning", "deep learning", "python", "sql")):
        score += 10.0
    return _clamp(score)


def _learning_velocity_score(candidate: dict[str, Any], candidate_years: float) -> float:
    skills = _candidate_skill_set(candidate)
    certifications = _flatten_text_values(candidate.get("certifications"))
    projects = _flatten_text_values(candidate.get("projects"))
    education = _flatten_text_values(candidate.get("education"))
    advanced_skills = {
        "machine learning",
        "deep learning",
        "pytorch",
        "tensorflow",
        "llm",
        "rag",
        "langchain",
        "vector db",
        "spark",
        "airflow",
    }
    score = 30.0
    score += min(30.0, len(skills) * 4.0)
    score += min(18.0, len(skills & advanced_skills) * 6.0)
    score += min(14.0, len(certifications) * 7.0)
    score += min(14.0, len(projects) * 7.0)
    if education and candidate_years <= 3:
        score += 6.0
    if candidate_years <= 2 and len(skills) >= 4:
        score += 8.0
    elif candidate_years <= 4 and len(skills) >= 6:
        score += 6.0
    return _clamp(score)


def _underexposure_score(
    candidate_years: float,
    search_visibility: float,
    recruiter_saves: float,
    config: ScoringConfig,
) -> float:
    experience_signal = max(
        0.0,
        (config.hidden_gem_max_experience_years - candidate_years)
        / max(1.0, config.hidden_gem_max_experience_years)
        * 100,
    )
    visibility_gap = max(0.0, 70.0 - search_visibility)
    recruiter_gap = max(0.0, 55.0 - recruiter_saves)
    return _clamp(experience_signal * 0.55 + visibility_gap * 0.30 + recruiter_gap * 0.15)


def _hidden_gem_reason(flag: bool, evidence: list[str], gaps: list[str]) -> str:
    if flag:
        if evidence:
            return f"Potential high-growth candidate: {evidence[0].lower()}."
        return "Potential high-growth candidate that may be missed by traditional screening."
    if evidence:
        return f"Some hidden-gem signals present, but {gaps[0].lower() if gaps else 'the profile does not cross the flag threshold'}."
    return "Insufficient hidden-gem evidence under the current thresholds."


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = str(value).strip()
        key = cleaned.lower()
        if cleaned and key not in seen:
            seen.add(key)
            result.append(cleaned)
    return result


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))
