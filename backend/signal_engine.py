"""Redrob signal processing for TalentLens AI."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class BehavioralScore:
    score: float
    explanation: str
    positive_signals: list[str] = field(default_factory=list)
    risk_signals: list[str] = field(default_factory=list)
    components: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


REDROB_SIGNAL_WEIGHTS: dict[str, float] = {
    "recruiter_response_rate": 0.18,
    "github_activity_score": 0.14,
    "profile_completeness_score": 0.16,
    "interview_completion_rate": 0.18,
    "open_to_work_flag": 0.06,
    "saved_by_recruiters_30d": 0.12,
    "search_appearance_30d": 0.10,
    "verification_strength": 0.06,
}


def compute_behavioral_score(candidate: dict[str, Any]) -> BehavioralScore:
    """Compute behavioral fit from Redrob engagement and intent signals."""

    signals = _redrob_signals(candidate)

    components = {
        "recruiter_response_rate": _score_rate(signals.get("recruiter_response_rate")),
        "github_activity_score": _score_rate(signals.get("github_activity_score")),
        "profile_completeness_score": _score_rate(signals.get("profile_completeness_score")),
        "interview_completion_rate": _score_rate(signals.get("interview_completion_rate")),
        "open_to_work_flag": 100.0 if _as_bool(signals.get("open_to_work_flag")) else 40.0,
        "saved_by_recruiters_30d": _score_capped_count(signals.get("saved_by_recruiters_30d"), cap=25),
        "search_appearance_30d": _score_capped_count(signals.get("search_appearance_30d"), cap=200),
        "verification_strength": _verification_strength(signals),
    }

    score = _weighted_average(components, REDROB_SIGNAL_WEIGHTS)
    positives, risks = _explain_components(components, signals)

    if score >= 80:
        summary = "Strong Redrob behavioral signals with high engagement and recruiter confidence."
    elif score >= 60:
        summary = "Healthy Redrob behavioral signals with some areas that can be stronger."
    elif score >= 40:
        summary = "Moderate behavioral signal strength; ranking should rely more on hard fit evidence."
    else:
        summary = "Limited behavioral confidence from Redrob signals."

    return BehavioralScore(
        score=round(score, 2),
        explanation=summary,
        positive_signals=positives,
        risk_signals=risks,
        components={key: round(value, 2) for key, value in components.items()},
    )


def _redrob_signals(candidate: dict[str, Any]) -> dict[str, Any]:
    signals = candidate.get("redrob_signals") or {}
    return signals if isinstance(signals, dict) else {}


def _score_rate(value: Any) -> float:
    number = _as_float(value)
    if number is None:
        return 0.0
    if 0 <= number <= 1:
        number *= 100
    return _clamp(number)


def _score_capped_count(value: Any, cap: float) -> float:
    number = _as_float(value)
    if number is None or number <= 0:
        return 0.0
    return _clamp((number / cap) * 100)


def _verification_strength(signals: dict[str, Any]) -> float:
    checks = (
        signals.get("verified_email"),
        signals.get("verified_phone"),
        signals.get("linkedin_connected"),
    )
    return sum(1 for value in checks if _as_bool(value)) / len(checks) * 100


def _weighted_average(components: dict[str, float], weights: dict[str, float]) -> float:
    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0.0
    return sum(components[key] * weights[key] for key in weights) / total_weight


def _explain_components(components: dict[str, float], signals: dict[str, Any]) -> tuple[list[str], list[str]]:
    positives: list[str] = []
    risks: list[str] = []

    if components["recruiter_response_rate"] >= 70:
        positives.append("High recruiter response rate")
    elif components["recruiter_response_rate"] < 35:
        risks.append("Low recruiter response rate")

    if components["interview_completion_rate"] >= 70:
        positives.append("Strong interview completion rate")
    elif components["interview_completion_rate"] < 35:
        risks.append("Weak interview completion history")

    if components["github_activity_score"] >= 70:
        positives.append("Strong GitHub activity")
    elif components["github_activity_score"] < 25:
        risks.append("Limited GitHub activity signal")

    if _as_bool(signals.get("open_to_work_flag")):
        positives.append("Candidate is open to work")

    if components["saved_by_recruiters_30d"] >= 60:
        positives.append("Frequently saved by recruiters in the last 30 days")

    if components["search_appearance_30d"] >= 60:
        positives.append("Strong recent search visibility")

    if components["profile_completeness_score"] >= 75:
        positives.append("Complete Redrob profile")
    elif components["profile_completeness_score"] < 45:
        risks.append("Incomplete Redrob profile")

    if components["verification_strength"] >= 100:
        positives.append("Email, phone, and LinkedIn are verified/connected")
    elif components["verification_strength"] < 70:
        risks.append("Missing one or more trust verification signals")

    return positives, risks


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace("%", "")
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "y", "1", "verified", "connected"}
    return False


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))
