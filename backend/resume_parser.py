"""Resume parsing helpers for TalentLens uploads."""

from __future__ import annotations

import io
import json
import re
import time
from dataclasses import dataclass
from typing import Any

try:  # pragma: no cover - optional dependency
    import fitz  # type: ignore
except Exception:  # pragma: no cover
    fitz = None

try:  # pragma: no cover - optional dependency
    import pdfplumber  # type: ignore
except Exception:  # pragma: no cover
    pdfplumber = None

try:  # pragma: no cover - optional dependency
    from docx import Document  # type: ignore
except Exception:  # pragma: no cover
    Document = None

try:  # pragma: no cover - optional dependency
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover
    Image = None

try:  # pragma: no cover - optional dependency
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover
    pytesseract = None


SKILL_LIBRARY: list[tuple[str, tuple[str, ...]]] = [
    ("Python", ("python",)),
    ("Java", ("java",)),
    ("JavaScript", ("javascript", " js ")),
    ("TypeScript", ("typescript", " ts ")),
    ("React", ("react",)),
    ("Node.js", ("node.js", "nodejs", " node ")),
    ("Express", ("express", "express.js")),
    ("FastAPI", ("fastapi",)),
    ("Flask", ("flask",)),
    ("Django", ("django",)),
    ("HTML", ("html",)),
    ("CSS", ("css",)),
    ("Tailwind", ("tailwind", "tailwindcss")),
    ("Vite", ("vite",)),
    ("SQL", ("sql",)),
    ("MongoDB", ("mongodb", "mongo db")),
    ("Supabase", ("supabase",)),
    ("Firebase", ("firebase",)),
    ("PostgreSQL", ("postgresql", "postgres")),
    ("MySQL", ("mysql",)),
    ("Machine Learning", ("machine learning", " ml ", "ml models")),
    ("Deep Learning", ("deep learning",)),
    ("NLP", ("nlp", "natural language processing")),
    ("Computer Vision", ("computer vision",)),
    ("LLMs", (" llm", "llms", "large language model", "genai")),
    ("RAG", (" rag", "retrieval augmented generation")),
    ("Sentence Transformers", ("sentence transformers", "sentence-transformers")),
    ("FAISS", ("faiss", "vector search", "semantic search")),
    ("LangChain", ("langchain",)),
    ("PyTorch", ("pytorch",)),
    ("TensorFlow", ("tensorflow",)),
    ("Pandas", ("pandas",)),
    ("NumPy", ("numpy",)),
    ("Scikit-learn", ("scikit-learn", "sklearn")),
    ("GCP", ("gcp", "google cloud")),
    ("Azure", ("azure",)),
    ("AWS", ("aws", "amazon web services")),
    ("Docker", ("docker",)),
    ("Git", (" git ",)),
    ("GitHub", ("github",)),
    ("REST API", ("rest api", "restful api", "api development")),
    ("Data Analysis", ("data analysis", "analytics")),
    ("Spark", ("spark", "apache spark")),
    ("Airflow", ("airflow",)),
    ("ETL", ("etl",)),
    ("Prompt Engineering", ("prompt engineering",)),
    ("Vector DB", ("vector db", "vector database")),
    ("Cybersecurity", ("cybersecurity", "cyber security")),
    ("IoT", ("iot", "internet of things")),
]

SECTION_HEADERS = {
    "skills",
    "education",
    "projects",
    "project",
    "experience",
    "certifications",
    "certification",
    "contact",
    "summary",
    "profile",
    "resume",
    "stream",
    "objective",
}

NAME_NOISE = {
    "skills",
    "education",
    "projects",
    "experience",
    "summary",
    "certifications",
    "contact",
    "stream",
    "resume",
    "profile",
    "python",
    "sql",
    "rag",
    "git",
    "fastapi",
    "react",
    "machine",
    "learning",
    "ai",
    "ml",
}


@dataclass
class ParsedResume:
    text: str
    candidate_profile: dict[str, Any]


def parse_uploaded_candidate(filename: str, payload: bytes) -> ParsedResume:
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix == "json":
        profile = parse_candidate_json(payload.decode("utf-8"))
        return ParsedResume(text=profile.get("resumeText", ""), candidate_profile=profile)
    if suffix == "pdf":
        text = extract_pdf_text(payload)
        if not text.strip():
            raise ValueError("Could not extract text from PDF.")
        return ParsedResume(text=text, candidate_profile=parse_candidate_text(text))
    if suffix == "docx":
        text = extract_docx_text(payload)
        if not text.strip():
            raise ValueError("Could not extract text from DOCX.")
        return ParsedResume(text=text, candidate_profile=parse_candidate_text(text))
    if suffix in {"png", "jpg", "jpeg", "webp"}:
        text = extract_image_text(payload)
        if not text.strip():
            raise ValueError("Image parsing requires OCR support.")
        return ParsedResume(text=text, candidate_profile=parse_candidate_text(text))
    raise ValueError("Unsupported file type. Use JSON, PDF, DOCX, or image.")


def extract_pdf_text(payload: bytes) -> str:
    chunks: list[str] = []
    if fitz is not None:
        with fitz.open(stream=payload, filetype="pdf") as document:
            chunks.extend(page.get_text("text") for page in document)
    if not "".join(chunks).strip() and pdfplumber is not None:
        with pdfplumber.open(io.BytesIO(payload)) as document:
            chunks.extend((page.extract_text() or "") for page in document.pages)
    return normalize_resume_text("\n".join(chunks))


def extract_docx_text(payload: bytes) -> str:
    if Document is None:
        return ""
    document = Document(io.BytesIO(payload))
    parts = [paragraph.text for paragraph in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            parts.append(" ".join(cell.text for cell in row.cells))
    return normalize_resume_text("\n".join(parts))


def extract_image_text(payload: bytes) -> str:
    if Image is None or pytesseract is None:
        return ""
    image = Image.open(io.BytesIO(payload))
    return normalize_resume_text(pytesseract.image_to_string(image))


def parse_candidate_json(text: str) -> dict[str, Any]:
    parsed = json.loads(text)
    profile = parsed.get("profile") if isinstance(parsed, dict) and isinstance(parsed.get("profile"), dict) else parsed
    skills = normalize_skills((parsed.get("skills") if isinstance(parsed, dict) else None) or profile.get("skills") or [])
    projects = normalize_list((parsed.get("projects") if isinstance(parsed, dict) else None) or profile.get("projects") or [])
    education_raw = (parsed.get("education") if isinstance(parsed, dict) else None) or profile.get("education") or []
    education_list = normalize_list(education_raw)
    degree = normalize_text(profile.get("degree") or (parsed.get("degree") if isinstance(parsed, dict) else ""))
    college = normalize_text(profile.get("college") or (parsed.get("college") if isinstance(parsed, dict) else ""))
    role = clean_role(profile.get("headline") or profile.get("role") or infer_role_from_skills(skills))
    experience = int(float(profile.get("years_experience") or parsed.get("years_experience") or 0)) if isinstance(parsed, dict) else 0
    education = format_education(degree, college, " - ".join(education_list))
    experience_summary = build_experience_summary("", projects, experience, role, degree)
    profile_label = build_profile_label(role, degree, experience_summary)
    candidate_name = pick_name_from_value(
        profile.get("name") or profile.get("full_name") or (parsed.get("name") if isinstance(parsed, dict) else "")
    ) or "Candidate Profile"
    confidence = compute_confidence(candidate_name, skills, projects, degree, college, bool(profile.get("email")), bool(profile.get("phone")))
    return {
        "candidate_id": f"USER_{int(time.time() * 1000)}",
        "name": candidate_name,
        "candidate_name": candidate_name,
        "profile_label": profile_label,
        "role": role or profile_label or "Candidate Profile",
        "education": education,
        "college": college,
        "degree": degree,
        "skills": skills,
        "projects": projects,
        "experience": experience,
        "experience_summary": experience_summary,
        "email": normalize_text(profile.get("email") or (parsed.get("email") if isinstance(parsed, dict) else "")),
        "phone": normalize_text(profile.get("phone") or (parsed.get("phone") if isinstance(parsed, dict) else "")),
        "linkedin": normalize_text(profile.get("linkedin_url") or profile.get("linkedin") or (parsed.get("linkedin") if isinstance(parsed, dict) else "")),
        "github": normalize_text(profile.get("github_url") or profile.get("github") or (parsed.get("github") if isinstance(parsed, dict) else "")),
        "source": "USER_ADDED",
        "parsing_confidence": confidence,
        "resumeText": normalize_resume_text(text),
    }


def parse_candidate_text(text: str) -> dict[str, Any]:
    cleaned = normalize_resume_text(text)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    skills = extract_skills(cleaned)
    projects = extract_section_items(cleaned, "projects?|project experience")
    experience = infer_experience_years(cleaned, projects)
    degree = infer_degree(cleaned)
    college = infer_college(cleaned)
    role = infer_role(cleaned, skills)
    education = format_education(degree, college, "")
    candidate_name = pick_candidate_name(lines, cleaned) or "Candidate Profile"
    email_match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", cleaned, re.I)
    phone_match = re.search(r"(?:\+?91[-\s]?)?[6-9]\d{9}", cleaned)
    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s)]+", cleaned, re.I)
    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[^\s)]+", cleaned, re.I)
    experience_summary = build_experience_summary(cleaned, projects, experience, role, degree)
    profile_label = build_profile_label(role, degree, experience_summary)
    confidence = compute_confidence(candidate_name, skills, projects, degree, college, bool(email_match), bool(phone_match))
    return {
        "candidate_id": f"USER_{int(time.time() * 1000)}",
        "name": candidate_name,
        "candidate_name": candidate_name,
        "profile_label": profile_label,
        "role": profile_label if profile_label and "Student" in profile_label else role,
        "education": education or "Candidate Profile",
        "college": college,
        "degree": degree,
        "skills": skills,
        "projects": projects,
        "experience": experience,
        "experience_summary": experience_summary,
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0) if phone_match else "",
        "linkedin": linkedin_match.group(0) if linkedin_match else "",
        "github": github_match.group(0) if github_match else "",
        "source": "USER_ADDED",
        "parsing_confidence": confidence,
        "resumeText": cleaned,
    }


def normalize_resume_text(text: str) -> str:
    cleaned = text.replace("\r", "\n").replace("\u00a0", " ")
    cleaned = re.sub(r"[•●▪◦·]", "\n", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


def normalize_text(value: Any) -> str:
    return str(value or "").strip()


def normalize_list(value: Any) -> list[str]:
    if isinstance(value, list):
        values: list[str] = []
        for item in value:
            if isinstance(item, dict):
                text = item.get("name") or item.get("title") or item.get("degree") or item.get("school") or item.get("description")
            else:
                text = item
            if normalize_text(text):
                values.append(normalize_text(text))
        return values
    if not value:
        return []
    return [item.strip() for item in re.split(r"[\n,;|]", str(value)) if item.strip()]


def normalize_skills(value: Any) -> list[str]:
    text = " ".join(normalize_list(value)) if isinstance(value, list) else str(value or "")
    return extract_skills(text)


def pick_name_from_value(value: Any) -> str:
    clean = clean_name(value)
    tokens = clean.split()
    if 2 <= len(tokens) <= 4 and all(is_name_token(token) for token in tokens):
        return clean
    return ""


def pick_candidate_name(lines: list[str], text: str) -> str:
    labeled = re.search(r"(?:candidate\s+name|full\s+name|name)\s*[:\-]\s*([A-Za-z][A-Za-z .'-]{1,60})", text, re.I)
    if labeled:
        candidate = pick_name_from_value(labeled.group(1))
        if candidate:
            return candidate
    for line in lines[:5]:
        clean = clean_name(re.sub(r"\b(email|phone|linkedin|github)\b.*$", "", line, flags=re.I))
        tokens = clean.split()
        if not clean or len(clean) > 48 or re.search(r"\d|@|https?://", line):
            continue
        if is_section_header(clean):
            continue
        if 2 <= len(tokens) <= 4 and all(is_name_token(token) for token in tokens):
            return clean
    return ""


def clean_name(value: Any) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^A-Za-z .'-]", " ", str(value or ""))).strip()


def is_name_token(token: str) -> bool:
    cleaned = token.replace(".", "")
    if cleaned.lower() in NAME_NOISE:
        return False
    return bool(re.fullmatch(r"[A-Z][a-z]+|[A-Z]", cleaned))


def is_section_header(text: str) -> bool:
    return normalize_text(text).strip(" :-").lower() in SECTION_HEADERS


def extract_skills(text: str) -> list[str]:
    lowered = f" {text.lower()} "
    found: list[str] = []
    for canonical, aliases in SKILL_LIBRARY:
        if any(alias.lower() in lowered for alias in aliases):
            found.append(canonical)
    return found


def extract_section_items(text: str, labels: str) -> list[str]:
    match = re.search(
        rf"(?:{labels})\s*[:\-]?\s*([\s\S]{{0,900}}?)(?=\n\s*(?:education|skills|experience|certifications?|projects?|summary|objective|achievements?|contact)\b|$)",
        text,
        re.I,
    )
    if not match:
        return []
    values = [item.strip(" -*") for item in re.split(r"[\n;]", match.group(1)) if item.strip()]
    return [item for item in values if len(item) > 3 and not is_section_header(item)][:6]


def infer_experience_years(text: str, projects: list[str]) -> int:
    explicit = re.search(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs|year)\b", text, re.I)
    if explicit:
        return max(0, min(20, round(float(explicit.group(1)))))
    current_year = 2026
    month_map = {"jan": 0, "feb": 1, "mar": 2, "apr": 3, "may": 4, "jun": 5, "jul": 6, "aug": 7, "sep": 8, "oct": 9, "nov": 10, "dec": 11}
    months = 0
    range_pattern = re.compile(
        r"\b(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*)?(20\d{2}|19\d{2})\s*(?:-|to)\s*(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*)?(present|current|20\d{2}|19\d{2})\b",
        re.I,
    )
    for match in range_pattern.finditer(text):
        start_month = month_map.get((match.group(1) or "jan")[:3].lower(), 0)
        start_year = int(match.group(2))
        if re.fullmatch(r"present|current", match.group(4), re.I):
            end_year = current_year
            end_month = 5
        else:
            end_year = int(match.group(4))
            end_month = month_map.get((match.group(3) or "dec")[:3].lower(), 11)
        months += max(1, (end_year - start_year) * 12 + (end_month - start_month))
    if months > 0:
        return max(1, min(20, round(months / 12)))
    years = [int(match.group(0)) for match in re.finditer(r"\b(?:19|20)\d{2}\b", text)]
    if len(years) >= 2:
        return max(1, min(12, max(years) - min(years)))
    internships = len(re.findall(r"\b(intern|internship|trainee|apprentice)\b", text, re.I))
    work_signals = len(re.findall(r"\b(experience|worked|developed|built|engineer|developer|analyst|freelance|startup|consultant)\b", text, re.I))
    project_signals = len(re.findall(r"\b(built|developed|designed|deployed|implemented|created|launched|maintained)\b", " ".join(projects), re.I))
    if internships >= 2 or work_signals >= 8 or project_signals >= 3:
        return 2
    if internships or work_signals >= 3 or project_signals >= 1:
        return 1
    return 0


def infer_degree(text: str) -> str:
    patterns = [
        r"\b(B\.?\s?Tech|B\.?\s?E\.?|M\.?\s?Tech|M\.?\s?E\.?|BSc|B\.?\s?Sc|MSc|M\.?\s?Sc|MBA|BCA|MCA|PhD|MS|BS|BE|ME)\b[^\n,;]*",
        r"\b(Bachelor of Technology|Master of Technology|Bachelor of Engineering|Master of Engineering)\b[^\n,;]*",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return clean_role(match.group(0))
    return ""


def infer_college(text: str) -> str:
    for line in [line.strip() for line in text.splitlines() if line.strip()]:
        if re.search(r"(university|college|institute|school|iit|nit|iiit|bits|karunya)", line, re.I) and not is_section_header(line):
            return clean_role(line)
    match = re.search(r"(?:at|from|of)\s+([A-Z][A-Za-z&.,'() -]{2,80}(?:University|College|Institute|School|Campus)?)", text)
    return clean_role(match.group(1)) if match else ""


def infer_role(text: str, skills: list[str]) -> str:
    headline = next(
        (
            line.strip()
            for line in text.splitlines()[:8]
            if re.search(r"\b(engineer|developer|analyst|scientist|designer|intern|consultant|manager)\b", line, re.I)
        ),
        "",
    )
    if headline:
        return clean_role(headline)
    lowered = text.lower()
    if re.search(r"\b(student|undergraduate|graduate)\b", lowered):
        return "Student / Intern Profile"
    return infer_role_from_skills(skills)


def infer_role_from_skills(skills: list[str]) -> str:
    lowered = {skill.lower() for skill in skills}
    if {"machine learning", "deep learning"} & lowered or {"pytorch", "rag", "llms", "sentence transformers"} & lowered:
        return "AI/ML Engineer"
    if "sql" in lowered and ("spark" in lowered or "airflow" in lowered or "etl" in lowered):
        return "Data Engineer"
    if {"react", "javascript", "node.js", "typescript"} & lowered:
        return "Software Engineer"
    if {"sql", "data analysis", "pandas"} & lowered:
        return "Data Scientist"
    return "Candidate Profile"


def clean_role(value: Any) -> str:
    cleaned = re.sub(r"\s+", " ", re.sub(r"[^A-Za-z /&+.-]", " ", str(value or ""))).strip()
    cleaned = re.sub(r"\b(resume|curriculum|vitae|profile|summary|objective)\b", "", cleaned, flags=re.I).strip()
    return cleaned[:60] if cleaned else ""


def degree_short_label(degree: str) -> str:
    if not degree:
        return ""
    lowered = degree.lower()
    if "bachelor of technology" in lowered or "b.tech" in lowered or "b tech" in lowered:
        prefix = "B.Tech"
    elif "bachelor of engineering" in lowered or "b.e" in lowered or lowered.startswith("be "):
        prefix = "B.E"
    elif "master of technology" in lowered or "m.tech" in lowered or "m tech" in lowered:
        prefix = "M.Tech"
    elif "master of engineering" in lowered or "m.e" in lowered or lowered.startswith("me "):
        prefix = "M.E"
    elif "m.sc" in lowered or lowered.startswith("msc"):
        prefix = "M.Sc"
    elif "b.sc" in lowered or lowered.startswith("bsc"):
        prefix = "B.Sc"
    else:
        return degree

    if re.search(r"computer science and engineering|\bcse\b", lowered):
        suffix = " CSE"
    elif re.search(r"computer science\b|\bcs\b", lowered):
        suffix = " CS"
    elif re.search(r"information technology|\bit\b", lowered):
        suffix = " IT"
    elif re.search(r"artificial intelligence", lowered):
        suffix = " AI"
    elif re.search(r"data science", lowered):
        suffix = " DS"
    else:
        suffix = ""
    return f"{prefix}{suffix}".strip()


def format_education(degree: str, college: str, fallback: str) -> str:
    pieces = [piece for piece in (degree, college) if piece]
    if pieces:
        return " - ".join(pieces)
    return fallback if fallback and fallback.lower() not in {"not specified", "stream"} else ""


def build_experience_summary(text: str, projects: list[str], experience: int, role: str, degree: str = "") -> str:
    lowered = f"{role} {text} {degree}".lower()
    degree_lower = degree.lower()
    is_student_degree = bool(re.search(r"(b\.tech|btech|bachelor of technology|bachelor of engineering|b\.e\b)", degree_lower))
    has_student_words = bool(re.search(r"\b(student|undergraduate|graduate)\b", lowered))
    has_internship = bool(re.search(r"\b(intern|internship|trainee|apprentice)\b", lowered))
    if experience > 1:
        return f"{experience} year{'s' if experience != 1 else ''} experience"
    if has_internship:
        if has_student_words or is_student_degree:
            return "Student / Intern Profile"
        return "Internship Experience"
    if has_student_words or (is_student_degree and experience == 0):
        return "Student / Intern Profile"
    if experience > 0:
        return f"{experience} year{'s' if experience != 1 else ''} experience"
    if re.search(r"\b(worked|developed|built|freelance|consultant|startup|maintained|deployed)\b", lowered) or projects:
        return "Experience evidence available"
    return "Candidate Profile"


def build_profile_label(role: str, degree: str, experience_summary: str) -> str:
    degree_label = degree_short_label(degree)
    if experience_summary == "Student / Intern Profile":
        return f"{degree_label} Student".strip() if degree_label else "Student / Intern Profile"
    if role and role != "Candidate Profile":
        return role
    return degree_label or "Candidate Profile"


def compute_confidence(
    name: str,
    skills: list[str],
    projects: list[str],
    degree: str,
    college: str,
    has_email: bool,
    has_phone: bool,
) -> int:
    score = 0
    if name and name != "Candidate Profile":
        score += 26
    if has_email:
        score += 10
    if has_phone:
        score += 8
    if degree:
        score += 14
    if college:
        score += 12
    score += min(20, len(skills) * 3)
    score += min(10, len(projects) * 3)
    return min(100, score)
