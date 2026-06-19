<<<<<<< HEAD
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


SENIORITY_MULTIPLIERS = {
    "unspecified": 1.0,
    "junior": 0.75,
    "mid": 1.0,
    "senior": 1.15,
    "lead": 1.3,
}

SKILL_CLUSTERS: dict[str, set[str]] = {
    "data_science": {"python", "machine learning", "statistics", "pandas", "numpy", "sql"},
    "analytics": {"sql", "excel", "power bi", "tableau", "data analysis", "statistics"},
    "ml_engineering": {"python", "machine learning", "deep learning", "docker", "api development", "aws", "gcp", "azure"},
    "data_engineering": {"python", "sql", "data engineering", "spark", "aws", "gcp", "azure", "docker"},
    "full_stack": {"javascript", "react", "api development", "git", "docker", "sql"},
}


def technical_fit_score(candidate: dict[str, Any], requirements: JobRequirements | dict[str, Any]) -> ScoreResult:
    """Score skill alignment against parsed JD requirements."""

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
            metadata={"matched_skills": [], "missing_skills": [], "candidate_skills": sorted(candidate_skills)},
        )

    matched = [skill for skill in required_skills if skill in candidate_skills]
    missing = [skill for skill in required_skills if skill not in candidate_skills]
    direct_match_score = (len(matched) / len(required_skills)) * 90
    related_skill_bonus = _related_skill_bonus(missing, candidate_skills)
    certification_bonus = min(5.0, len(certifications) * 1.5)
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
        },
    )


def experience_score(candidate: dict[str, Any], requirements: JobRequirements | dict[str, Any]) -> ScoreResult:
    """Score candidate experience against JD years and seniority needs."""

    required_years = float(_requirements_value(requirements, "years_experience", default=0.0) or 0.0)
    seniority = str(_requirements_value(requirements, "seniority_level", default="unspecified") or "unspecified")
    candidate_years = estimate_years_experience(candidate)

    if required_years <= 0:
        score = _clamp(65 + min(candidate_years, 10) * 3)
        explanation = "The JD does not specify years of experience, so candidate experience is scored as supportive evidence."
        gaps: list[str] = []
    else:
        ratio = candidate_years / required_years if required_years else 1.0
        base_score = min(100.0, ratio * 85)
        if candidate_years >= required_years:
            base_score += 10
        score = _clamp(base_score * SENIORITY_MULTIPLIERS.get(seniority, 1.0))
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
        metadata={"candidate_years": round(candidate_years, 2), "required_years": required_years, "seniority_level": seniority},
    )


def career_consistency_score(candidate: dict[str, Any]) -> ScoreResult:
    """Score whether career history looks coherent, complete, and progressive."""

    entries = _career_entries(candidate)
    profile_years = estimate_years_experience(candidate)

    if not entries:
        return ScoreResult(
            score=35.0 if profile_years else 20.0,
            explanation="Career consistency is weak because structured career history is missing.",
            evidence=[f"Profile reports {profile_years:.1f} years"] if profile_years else [],
            gaps=["Missing structured career history"],
            metadata={"entry_count": 0, "profile_years": profile_years, "timeline_years": 0.0},
        )

    dated_ranges = [_entry_date_range(entry) for entry in entries]
    dated_ranges = [item for item in dated_ranges if item[0] is not None]
    timeline_years = _timeline_years(dated_ranges)
    gaps_months, overlap_months = _timeline_gaps_and_overlaps(dated_ranges)
    title_progression = _title_progression_score(entries)
    role_relevance = _role_relevance_score(entries, candidate)

    score = 40.0
    score += min(20.0, len(entries) * 4)
    score += min(15.0, timeline_years * 1.5)
    score += title_progression * 0.15
    score += role_relevance * 0.10

    if profile_years and timeline_years:
        delta = abs(profile_years - timeline_years)
        if delta <= 1.5:
            score += 10
        elif delta >= 4:
            score -= 15

    if gaps_months > 18:
        score -= min(15.0, (gaps_months - 18) / 3)
    if overlap_months > 6:
        score -= min(12.0, (overlap_months - 6) / 2)

    evidence = [f"{len(entries)} career role(s) provided"]
    if timeline_years:
        evidence.append(f"Career timeline covers about {timeline_years:.1f} years")
    if title_progression >= 65:
        evidence.append("Career titles show progression or stable specialization")
    if role_relevance >= 70:
        evidence.append("Career history aligns with declared profile/skills")

    gaps = []
    if not dated_ranges:
        gaps.append("Career entries do not include usable dates")
    if gaps_months > 18:
        gaps.append(f"Career timeline has about {gaps_months // 12:.0f}+ year(s) of unexplained gaps")
    if overlap_months > 6:
        gaps.append("Career timeline has overlapping roles that may need review")
    if profile_years and timeline_years and abs(profile_years - timeline_years) >= 4:
        gaps.append("Profile experience and career timeline do not agree closely")

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
        },
    )


def skill_cluster_bonus(candidate: dict[str, Any], requirements: JobRequirements | dict[str, Any]) -> ScoreResult:
    """Reward coherent skill groups that make the candidate stronger than keyword matching alone."""

    candidate_skills = _candidate_skill_set(candidate)
    required_skills = {
        _canonical_skill(skill)
        for skill in (_requirements_value(requirements, "required_skills", default=[]) or [])
        if _canonical_skill(skill)
    }

    cluster_hits: dict[str, list[str]] = {}
    for cluster_name, cluster_skills in SKILL_CLUSTERS.items():
        matched = sorted(candidate_skills & cluster_skills)
        if len(matched) >= 3:
            cluster_hits[cluster_name] = matched

    jd_aligned_clusters = {
        name: matched
        for name, matched in cluster_hits.items()
        if not required_skills or bool(required_skills & SKILL_CLUSTERS[name])
    }
    best_cluster_size = max((len(matched) for matched in jd_aligned_clusters.values()), default=0)
    bonus = min(8.0, best_cluster_size * 1.5 + max(0, len(jd_aligned_clusters) - 1))

    evidence = [
        f"{name.replace('_', ' ').title()} cluster: {', '.join(matched[:5])}"
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
        },
    )


def authenticity_score(candidate: dict[str, Any]) -> ScoreResult:
    """Score trustworthiness and profile authenticity from Redrob and profile data."""

    signals = candidate.get("redrob_signals") if isinstance(candidate.get("redrob_signals"), dict) else {}
    profile = candidate.get("profile") if isinstance(candidate.get("profile"), dict) else {}

    verified_email = _as_bool(signals.get("verified_email"))
    verified_phone = _as_bool(signals.get("verified_phone"))
    linkedin_connected = _as_bool(signals.get("linkedin_connected"))
    completeness = _score_rate(signals.get("profile_completeness_score"))
    career_history = candidate.get("career_history")
    education = candidate.get("education")
    skills = candidate.get("skills")

    evidence: list[str] = []
    gaps: list[str] = []
    score = 0.0

    score += 18 if verified_email else 0
    score += 14 if verified_phone else 0
    score += 14 if linkedin_connected else 0
    score += completeness * 0.22
    score += 12 if _has_content(career_history) else 0
    score += 8 if _has_content(education) else 0
    score += 8 if _has_content(skills) else 0
    score += 4 if _has_named_identity(profile) else 0

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

    generic_penalty = _generic_profile_penalty(candidate)
    if generic_penalty:
        score -= generic_penalty
        gaps.append("Profile text appears sparse or generic")

    score = _clamp(score)
    risk_level = authenticity_risk_level(score, gaps)
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
            "risk_level": risk_level,
        },
    )


def authenticity_risk_level(score: float, gaps: list[str] | None = None) -> str:
    """Classify authenticity risk for recruiter-facing explanations."""

    gap_count = len(gaps or [])
    if score >= 82 and gap_count <= 2:
        return "low"
    if score >= 62 and gap_count <= 4:
        return "medium"
    if score >= 42:
        return "high"
    return "critical"


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


def _canonical_skill(skill: Any) -> str:
    value = str(skill or "").strip().lower()
    if not value:
        return ""
    for canonical, aliases in SKILL_ALIASES.items():
        if value == canonical or value in {alias.lower() for alias in aliases}:
            return canonical
    return re.sub(r"\s+", " ", value)


def _related_skill_bonus(missing: list[str], candidate_skills: set[str]) -> float:
    if not missing:
        return 0.0
    candidate_text = " ".join(candidate_skills)
    bonus = 0.0
    for skill in missing:
        tokens = [token for token in re.split(r"[^a-z0-9]+", skill) if len(token) > 2]
        if tokens and any(token in candidate_text for token in tokens):
            bonus += 2.0
    return min(5.0, bonus)


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


def _generic_profile_penalty(candidate: dict[str, Any]) -> float:
    text = " ".join(_flatten_text_values(candidate.get("profile")))
    if not text.strip():
        return 8.0
    unique_words = set(re.findall(r"[a-zA-Z]{3,}", text.lower()))
    return 6.0 if len(unique_words) < 8 else 0.0


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))
=======

>>>>>>> 924a5b14fb6eb352666c781b20c0a7887ab2e0e7
