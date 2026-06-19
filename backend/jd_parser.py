"""Job description parsing utilities for TalentLens AI.

The parser is intentionally deterministic: challenge submissions should be
repeatable, auditable, and easy to explain. It extracts only the structured
signals needed by the ranking engine.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Iterable


@dataclass(frozen=True)
class JobRequirements:
    """Structured requirements extracted from a job description."""

    required_skills: list[str]
    years_experience: float
    seniority_level: str
    raw_text: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "python": ("python", "py"),
    "sql": ("sql", "postgres", "postgresql", "mysql", "sqlite"),
    "machine learning": ("machine learning", "ml", "scikit-learn", "sklearn"),
    "deep learning": ("deep learning", "neural network", "pytorch", "tensorflow", "keras"),
    "nlp": ("nlp", "natural language processing", "llm", "large language model"),
    "data analysis": ("data analysis", "analytics", "eda", "exploratory data analysis"),
    "data engineering": ("data engineering", "etl", "elt", "data pipeline", "airflow"),
    "statistics": ("statistics", "statistical", "hypothesis testing", "probability"),
    "excel": ("excel", "google sheets", "spreadsheet"),
    "pandas": ("pandas",),
    "numpy": ("numpy",),
    "power bi": ("power bi", "powerbi"),
    "tableau": ("tableau",),
    "spark": ("spark", "pyspark", "apache spark"),
    "aws": ("aws", "amazon web services"),
    "gcp": ("gcp", "google cloud"),
    "azure": ("azure", "microsoft azure"),
    "docker": ("docker", "containerization"),
    "kubernetes": ("kubernetes", "k8s"),
    "git": ("git", "github", "gitlab"),
    "api development": ("api", "rest api", "fastapi", "flask", "django"),
    "javascript": ("javascript", "typescript", "node.js", "nodejs"),
    "react": ("react", "react.js", "reactjs"),
    "communication": ("communication", "stakeholder", "presentation"),
}

SENIORITY_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("lead", ("lead", "principal", "staff", "architect", "head of")),
    ("senior", ("senior", "sr.", "sr ", "sde iii", "level 3")),
    ("mid", ("mid", "intermediate", "associate", "sde ii", "level 2")),
    ("junior", ("junior", "entry", "fresher", "graduate", "intern", "trainee", "sde i", "level 1")),
)

REQUIRED_SECTION_MARKERS = (
    "required",
    "requirements",
    "must have",
    "must-have",
    "minimum qualifications",
    "qualifications",
    "what you need",
    "you have",
)

PREFERRED_SECTION_MARKERS = (
    "preferred",
    "nice to have",
    "good to have",
    "bonus",
    "plus",
)


def parse_job_description(text: str | None) -> JobRequirements:
    """Parse free-form JD text into ranking requirements."""

    raw_text = text or ""
    required_skills = extract_required_skills(raw_text)
    years_experience = extract_years_experience(raw_text)
    seniority_level = extract_seniority_level(raw_text, years_experience)

    return JobRequirements(
        required_skills=required_skills,
        years_experience=years_experience,
        seniority_level=seniority_level,
        raw_text=raw_text,
    )


def extract_required_skills(text: str | None, skill_aliases: dict[str, Iterable[str]] | None = None) -> list[str]:
    """Extract required skill names from JD text.

    The parser first looks at requirement-like sections. If those are missing,
    it falls back to the full JD so sparse challenge inputs still work.
    """

    if not text:
        return []

    aliases = skill_aliases or SKILL_ALIASES
    required_text = _requirement_focused_text(text)
    matches = _find_skill_matches(required_text, aliases)

    if not matches:
        matches = _find_skill_matches(text, aliases)

    return [skill for skill, _position in sorted(matches.items(), key=lambda item: item[1])]


def extract_years_experience(text: str | None) -> float:
    """Extract the minimum years of experience requested by the JD."""

    if not text:
        return 0.0

    lowered = _normalize_text(text)
    patterns = (
        r"(?:minimum|min\.?|at least)\s*(\d+(?:\.\d+)?)\+?\s*(?:years|yrs|year)",
        r"(\d+(?:\.\d+)?)\+?\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:years|yrs|year)",
        r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs|year)(?:\s+of)?\s+experience",
        r"experience\s*(?:of|:)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years|yrs|year)",
    )

    values: list[float] = []
    for pattern in patterns:
        for match in re.finditer(pattern, lowered):
            values.append(float(match.group(1)))

    return min(values) if values else 0.0


def extract_seniority_level(text: str | None, years_experience: float | None = None) -> str:
    """Extract seniority from explicit JD language or years required."""

    lowered = _normalize_text(text or "")
    for level, keywords in SENIORITY_KEYWORDS:
        if any(_contains_phrase(lowered, keyword) for keyword in keywords):
            return level

    years = years_experience or 0.0
    if years >= 8:
        return "lead"
    if years >= 5:
        return "senior"
    if years >= 2:
        return "mid"
    if years > 0:
        return "junior"
    return "unspecified"


def _requirement_focused_text(text: str) -> str:
    lowered = _normalize_text(text)
    marker_positions = [lowered.find(marker) for marker in REQUIRED_SECTION_MARKERS if lowered.find(marker) >= 0]
    if not marker_positions:
        return text

    start = min(marker_positions)
    end = len(lowered)
    preferred_positions = [lowered.find(marker, start + 1) for marker in PREFERRED_SECTION_MARKERS]
    preferred_positions = [position for position in preferred_positions if position >= 0]
    if preferred_positions:
        end = min(preferred_positions)

    return text[start:end]


def _find_skill_matches(text: str, aliases: dict[str, Iterable[str]]) -> dict[str, int]:
    lowered = _normalize_text(text)
    matches: dict[str, int] = {}

    for canonical, variants in aliases.items():
        positions = [
            lowered.find(_normalize_text(variant))
            for variant in variants
            if _contains_phrase(lowered, _normalize_text(variant))
        ]
        if positions:
            matches[canonical] = min(position for position in positions if position >= 0)

    return matches


def _contains_phrase(text: str, phrase: str) -> bool:
    if not phrase:
        return False
    escaped = re.escape(phrase).replace(r"\ ", r"\s+")
    return bool(re.search(rf"(?<![a-z0-9+#.]){escaped}(?![a-z0-9+#.])", text))


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()
