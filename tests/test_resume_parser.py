import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.resume_parser import (
    parse_candidate_text,
    build_profile_label,
    build_experience_summary,
    degree_short_label,
    _is_forbidden_label,
    pick_candidate_name,
    is_name_token,
    clean_name,
)


FORBIDDEN_NAMES = {
    "Imported Candidate",
    "Data Candidate",
    "Uploaded Candidate",
    "Stream",
    "Resume",
    "Profile",
    "filename",
}


EXPECTATIONS = {
    "student_resume.txt": {
        "candidate_name": "Priya Nair",
        "email": "priya.nair@example.com",
        "phone": "+91 9123456780",
        "college": "Anna University",
        "degree_contains": "Information Technology",
        "education_contains": "Anna University",
        "skills": {"Python", "JavaScript", "React", "FastAPI", "SQL", "GitHub"},
        "projects_min": 2,
        "experience_summary": "Student / Intern Profile",
        "linkedin": "linkedin.com/in/priyanair",
        "github": "github.com/priyanair",
        "profile_label": "B.Tech IT Student",
    },
    "intern_resume.txt": {
        "candidate_name": "Arjun Kumar",
        "email": "arjun.kumar@example.com",
        "phone": "+91 9876501234",
        "college": "PSG College of Technology",
        "degree_contains": "Computer Science and Engineering",
        "education_contains": "PSG College of Technology",
        "skills": {"JavaScript", "React", "Node.js", "SQL", "Python", "REST API", "Git"},
        "projects_min": 1,
        "experience_summary": "Student / Intern Profile",
        "linkedin": "linkedin.com/in/arjunkumar",
        "github": "github.com/arjunkumar",
        "profile_label": "B.E CSE Student",
    },
    "software_engineer_resume.txt": {
        "candidate_name": "Aisha Kapoor",
        "email": "aisha.kapoor@example.com",
        "phone": "+91 9988776655",
        "college": "PES University",
        "degree_contains": "Computer Science and Engineering",
        "education_contains": "PES University",
        "skills": {"TypeScript", "JavaScript", "React", "Node.js", "Express", "PostgreSQL", "Docker", "AWS", "GitHub"},
        "projects_min": 2,
        "experience_summary": "5 years experience",
        "linkedin": "linkedin.com/in/aishakapoor",
        "github": "github.com/aishakapoor",
        "profile_label": "Senior Software Engineer",
    },
    "data_scientist_resume.txt": {
        "candidate_name": "Rohan Mehta",
        "email": "rohan.mehta@example.com",
        "phone": "+91 9090909090",
        "college": "Indian Institute of Science",
        "degree_contains": "Data Science",
        "education_contains": "Indian Institute of Science",
        "skills": {"Python", "Pandas", "NumPy", "Scikit-learn", "SQL", "Data Analysis", "GitHub"},
        "projects_min": 2,
        "experience_summary": "4 years experience",
        "linkedin": "linkedin.com/in/rohanmehta",
        "github": "github.com/rohanmehta",
        "profile_label": "Data Scientist",
    },
    "ai_ml_engineer_resume.txt": {
        "candidate_name": "John M Doe",
        "email": "john.doe@example.com",
        "phone": "+91 9012345678",
        "college": "IIIT Hyderabad",
        "degree_contains": "Artificial Intelligence",
        "education_contains": "IIIT Hyderabad",
        "skills": {"Python", "Machine Learning", "LLMs", "RAG", "Sentence Transformers", "FAISS", "LangChain", "PyTorch", "Docker", "GitHub"},
        "projects_min": 2,
        "experience_summary": "4 years experience",
        "linkedin": "linkedin.com/in/johnmdoe",
        "github": "github.com/johnmdoe",
        "profile_label": "AI/ML Engineer",
    },
    "shirley_resume.txt": {
        "candidate_name": "Shirley S",
        "email": "shirley.s@example.com",
        "phone": "+91 9876543210",
        "college": "Karunya Institute of Technology and Sciences",
        "degree_contains": "Computer Science and Engineering",
        "education_contains": "Karunya Institute of Technology and Sciences",
        "skills": {"Python", "FastAPI", "React", "LLMs", "RAG", "Sentence Transformers", "FAISS", "GitHub"},
        "projects_min": 2,
        "experience_summary": "Student / Intern Profile",
        "linkedin": "linkedin.com/in/shirleys",
        "github": "github.com/shirleys",
        "profile_label": "B.Tech CSE Student",
    },
}


class ResumeParserTests(unittest.TestCase):
    def test_resume_fixtures(self) -> None:
        sample_dir = ROOT / "tests" / "resume_samples"
        for fixture_name, expected in EXPECTATIONS.items():
            with self.subTest(fixture=fixture_name):
                parsed = parse_candidate_text((sample_dir / fixture_name).read_text(encoding="utf-8"))
                self.assertEqual(parsed["candidate_name"], expected["candidate_name"])
                self.assertNotIn(parsed["candidate_name"], FORBIDDEN_NAMES)
                self.assertEqual(parsed["email"], expected["email"])
                self.assertEqual(parsed["phone"], expected["phone"])
                self.assertIn(expected["college"], parsed["college"])
                self.assertIn(expected["degree_contains"], parsed["degree"])
                self.assertIn(expected["education_contains"], parsed["education"])
                self.assertTrue(expected["skills"].issubset(set(parsed["skills"])))
                self.assertGreaterEqual(len(parsed["projects"]), expected["projects_min"])
                self.assertEqual(parsed["experience_summary"], expected["experience_summary"])
                self.assertEqual(parsed["linkedin"], expected["linkedin"])
                self.assertEqual(parsed["github"], expected["github"])
                self.assertEqual(parsed["profile_label"], expected["profile_label"])
                self.assertGreaterEqual(parsed["parsing_confidence"], 60)


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------
# Unit tests for degree_short_label
# ---------------------------------------------------------------------------

class DegreeShortLabelTests(unittest.TestCase):
    """degree_short_label must produce correct abbreviated labels."""

    CASES: list[tuple[str, str]] = [
        ("B.Tech Computer Science and Engineering", "B.Tech CSE"),
        ("B.E Computer Science and Engineering",    "B.E CSE"),
        ("Bachelor of Technology Computer Science and Engineering", "B.Tech CSE"),
        ("M.Tech Artificial Intelligence",          "M.Tech AI"),
        ("M.Sc Data Science",                       "M.Sc DS"),
        ("B.Tech Information Technology",           "B.Tech IT"),
        ("MBA Analytics",                           "MBA"),
        ("",                                        ""),
    ]

    def test_degree_labels(self) -> None:
        for inp, want in self.CASES:
            with self.subTest(inp=inp):
                self.assertEqual(degree_short_label(inp), want)


# ---------------------------------------------------------------------------
# Unit tests for build_profile_label
# ---------------------------------------------------------------------------

class BuildProfileLabelTests(unittest.TestCase):
    """build_profile_label must produce correct, non-placeholder labels."""

    def test_btech_cse_student(self) -> None:
        label = build_profile_label(
            "AI/ML Engineer",
            "B.Tech Computer Science and Engineering",
            "Student / Intern Profile",
        )
        self.assertEqual(label, "B.Tech CSE Student")

    def test_be_cse_student(self) -> None:
        label = build_profile_label(
            "Software Engineering Intern",
            "B.E Computer Science and Engineering",
            "Student / Intern Profile",
        )
        self.assertEqual(label, "B.E CSE Student")

    def test_btech_it_student(self) -> None:
        label = build_profile_label(
            "Candidate Profile",
            "B.Tech Information Technology",
            "Student / Intern Profile",
        )
        self.assertEqual(label, "B.Tech IT Student")

    def test_professional_role_preserved(self) -> None:
        label = build_profile_label(
            "Senior Software Engineer",
            "B.E Computer Science and Engineering",
            "5 years experience",
        )
        self.assertEqual(label, "Senior Software Engineer")

    def test_data_scientist_label(self) -> None:
        label = build_profile_label(
            "Data Scientist",
            "M.Sc Data Science",
            "4 years experience",
        )
        self.assertEqual(label, "Data Scientist")

    def test_ai_ml_engineer_label(self) -> None:
        label = build_profile_label(
            "AI/ML Engineer",
            "M.Tech Artificial Intelligence",
            "4 years experience",
        )
        self.assertEqual(label, "AI/ML Engineer")

    def test_fallback_is_candidate_profile(self) -> None:
        label = build_profile_label("", "", "Candidate Profile")
        self.assertEqual(label, "Candidate Profile")

    def test_no_forbidden_labels(self) -> None:
        """profile_label must never be a known placeholder string."""
        forbidden_inputs = [
            ("Imported Candidate",   "", "Candidate Profile"),
            ("Data Candidate",       "", "Candidate Profile"),
            ("Uploaded Candidate",   "", "Candidate Profile"),
            ("Stream",               "", "Candidate Profile"),
            ("Resume",               "", "Candidate Profile"),
            ("Not specified",        "", "Candidate Profile"),
            ("",                     "", "Candidate Profile"),
        ]
        for role, degree, exp_sum in forbidden_inputs:
            with self.subTest(role=role):
                label = build_profile_label(role, degree, exp_sum)
                self.assertFalse(
                    _is_forbidden_label(label),
                    msg=f"build_profile_label returned forbidden label {label!r} for role={role!r}",
                )


# ---------------------------------------------------------------------------
# Unit tests for build_experience_summary (internship logic)
# ---------------------------------------------------------------------------

class BuildExperienceSummaryTests(unittest.TestCase):
    """build_experience_summary must classify intern/student profiles correctly."""

    def test_internship_with_btech_degree(self) -> None:
        summary = build_experience_summary(
            "Software Engineering Intern, June 2024 - December 2024",
            ["Bug triage assistant"],
            1,
            "Software Engineering Intern",
            "B.E Computer Science and Engineering",
        )
        self.assertEqual(summary, "Student / Intern Profile")

    def test_student_no_experience(self) -> None:
        summary = build_experience_summary(
            "Student at Anna University",
            [],
            0,
            "Candidate Profile",
            "B.Tech Information Technology",
        )
        self.assertEqual(summary, "Student / Intern Profile")

    def test_professional_experience(self) -> None:
        summary = build_experience_summary(
            "Senior Engineer, 2023 - Present",
            [],
            5,
            "Senior Software Engineer",
            "B.E Computer Science and Engineering",
        )
        self.assertEqual(summary, "5 years experience")

    def test_internship_no_degree_returns_internship_experience(self) -> None:
        summary = build_experience_summary(
            "Internship at TechCorp",
            [],
            1,
            "Data Analyst Intern",
            "MBA Analytics",
        )
        self.assertEqual(summary, "Internship Experience")


# ---------------------------------------------------------------------------
# Role field never a forbidden placeholder
# ---------------------------------------------------------------------------

FORBIDDEN_ROLE_VALUES = {
    "imported candidate",
    "data candidate",
    "uploaded candidate",
    "resume profile",
    "not specified",
    "stream",
    "resume",
    "filename",
}


class RoleFieldTests(unittest.TestCase):
    """The `role` field in parse_candidate_text must never be a placeholder."""

    def test_role_not_placeholder_in_all_fixtures(self) -> None:
        sample_dir = ROOT / "tests" / "resume_samples"
        for fixture_name in EXPECTATIONS:
            with self.subTest(fixture=fixture_name):
                parsed = parse_candidate_text(
                    (sample_dir / fixture_name).read_text(encoding="utf-8")
                )
                role = str(parsed.get("role", "")).strip().lower()
                self.assertNotIn(
                    role,
                    FORBIDDEN_ROLE_VALUES,
                    msg=f"{fixture_name}: role={parsed['role']!r} is a forbidden placeholder",
                )


# ---------------------------------------------------------------------------
# Unit tests for candidate name extraction
# ---------------------------------------------------------------------------

class IsNameTokenTests(unittest.TestCase):
    """is_name_token must accept human-name tokens and reject tech/noise words."""

    SHOULD_ACCEPT = [
        "Shirley", "S", "Priya", "Nair", "Arjun", "Kumar",
        "Aisha", "Kapoor", "Rohan", "Mehta", "John", "M", "Doe",
        "Iyer", "Singh", "Verma", "Bose", "Rao",
    ]
    SHOULD_REJECT = [
        # Tech words that look like capitalised names
        "Python", "Docker", "Azure", "Flask", "Airflow",
        "Vite", "Pandas", "Spark", "Github",
        # Section headers
        "Skills", "Education", "Projects", "Experience",
        "Certifications", "Contact", "Summary", "Profile",
        "Resume", "Stream",
        # Known abbreviations / noise
        "AI", "ML", "RAG", "FAISS", "Git", "SQL",
        # Empty / numeric
        "", "123",
    ]

    def test_accepted_tokens(self) -> None:
        for token in self.SHOULD_ACCEPT:
            with self.subTest(token=token):
                self.assertTrue(is_name_token(token), msg=f"{token!r} should be accepted")

    def test_rejected_tokens(self) -> None:
        for token in self.SHOULD_REJECT:
            with self.subTest(token=token):
                self.assertFalse(is_name_token(token), msg=f"{token!r} should be rejected")


class PickCandidateNameTests(unittest.TestCase):
    """pick_candidate_name must extract the correct name or fall back cleanly."""

    # ── helper ───────────────────────────────────────────────────────────────
    @staticmethod
    def _lines_and_text(resume: str) -> tuple[list[str], str]:
        from backend.resume_parser import normalize_resume_text
        cleaned = normalize_resume_text(resume)
        lines = [l.strip() for l in cleaned.splitlines() if l.strip()]
        return lines, cleaned

    # ── Shirley S — key acceptance test from requirements spec ───────────────
    def test_shirley_s(self) -> None:
        """Shirley resume must yield candidate_name == 'Shirley S'."""
        sample = (ROOT / "tests" / "resume_samples" / "shirley_resume.txt").read_text(encoding="utf-8")
        result = parse_candidate_text(sample)
        self.assertEqual(result["candidate_name"], "Shirley S")

    # ── Other fixture names ───────────────────────────────────────────────────
    def test_priya_nair(self) -> None:
        lines, text = self._lines_and_text("Priya Nair\nB.Tech IT\nAnna University\n")
        self.assertEqual(pick_candidate_name(lines, text), "Priya Nair")

    def test_arjun_kumar(self) -> None:
        lines, text = self._lines_and_text("Arjun Kumar\nB.E CSE\nPSG College\n")
        self.assertEqual(pick_candidate_name(lines, text), "Arjun Kumar")

    def test_three_part_name(self) -> None:
        lines, text = self._lines_and_text("John M Doe\nAI/ML Engineer\nIIIT Hyderabad\n")
        self.assertEqual(pick_candidate_name(lines, text), "John M Doe")

    # ── Section headers must be ignored ──────────────────────────────────────
    def test_ignores_skills_header(self) -> None:
        lines, text = self._lines_and_text("Skills\nPriya Nair\nB.Tech IT\n")
        self.assertEqual(pick_candidate_name(lines, text), "Priya Nair")

    def test_ignores_education_header(self) -> None:
        lines, text = self._lines_and_text("Education\nArjun Kumar\nB.E CSE\n")
        self.assertEqual(pick_candidate_name(lines, text), "Arjun Kumar")

    # ── Tech words must NOT be treated as names ───────────────────────────────
    def test_does_not_pick_python(self) -> None:
        lines, text = self._lines_and_text("Python\nSQL\nReact\nPriya Nair\n")
        self.assertEqual(pick_candidate_name(lines, text), "Priya Nair")

    def test_does_not_pick_docker(self) -> None:
        lines, text = self._lines_and_text("Docker\nAzure\nRohan Mehta\n")
        self.assertEqual(pick_candidate_name(lines, text), "Rohan Mehta")

    # ── Filename must never become the candidate name ─────────────────────────
    def test_does_not_use_filename(self) -> None:
        """parse_candidate_text must not return a filename as candidate_name."""
        resume = "myresume.pdf\nPriya Nair\nB.Tech IT\nAnna University\n"
        result = parse_candidate_text(resume)
        self.assertNotEqual(result["candidate_name"], "myresume.pdf")
        self.assertNotEqual(result["candidate_name"], "myresume")

    def test_does_not_use_docx_filename(self) -> None:
        resume = "candidate_resume_2024.docx\nArjun Kumar\nB.E CSE\nPSG College\n"
        result = parse_candidate_text(resume)
        self.assertNotIn("docx", result["candidate_name"].lower())
        self.assertNotIn("resume", result["candidate_name"].lower())

    # ── Labeled "Name:" line ──────────────────────────────────────────────────
    def test_labeled_name_field(self) -> None:
        resume = "Candidate Name: Shirley S\nB.Tech CSE\nKarunya Institute\n"
        lines, text = self._lines_and_text(resume)
        self.assertEqual(pick_candidate_name(lines, text), "Shirley S")

    def test_full_name_field(self) -> None:
        resume = "Full Name: Priya Nair\nEmail: priya@example.com\n"
        lines, text = self._lines_and_text(resume)
        self.assertEqual(pick_candidate_name(lines, text), "Priya Nair")

    # ── Fallback to "Candidate Profile" ──────────────────────────────────────
    def test_fallback_when_no_name(self) -> None:
        resume = "Skills\nPython SQL React\nProjects\n"
        result = parse_candidate_text(resume)
        self.assertEqual(result["candidate_name"], "Candidate Profile")

    def test_fallback_for_all_tech_lines(self) -> None:
        resume = "Python\nDocker\nAzure\nFastAPI\n"
        result = parse_candidate_text(resume)
        self.assertEqual(result["candidate_name"], "Candidate Profile")

    # ── Forbidden name values ─────────────────────────────────────────────────
    def test_name_never_forbidden_across_fixtures(self) -> None:
        """candidate_name must never be a known placeholder across all fixtures."""
        forbidden = {
            "imported candidate", "data candidate", "uploaded candidate",
            "stream", "resume", "profile", "filename", "",
        }
        sample_dir = ROOT / "tests" / "resume_samples"
        for fixture_name in EXPECTATIONS:
            with self.subTest(fixture=fixture_name):
                result = parse_candidate_text(
                    (sample_dir / fixture_name).read_text(encoding="utf-8")
                )
                self.assertNotIn(
                    result["candidate_name"].lower(),
                    forbidden,
                    msg=f"{fixture_name}: candidate_name={result['candidate_name']!r}",
                )


# ---------------------------------------------------------------------------
# Unit tests for extract_skills
# ---------------------------------------------------------------------------

class ExtractSkillsTests(unittest.TestCase):
    """extract_skills must detect all required skills without duplicates."""

    # ── helper ───────────────────────────────────────────────────────────────
    @staticmethod
    def _skills(text: str) -> set[str]:
        from backend.resume_parser import extract_skills
        return set(extract_skills(text))

    @staticmethod
    def _raw(text: str) -> list[str]:
        from backend.resume_parser import extract_skills
        return extract_skills(text)

    # ── GitHub ────────────────────────────────────────────────────────────────
    def test_github_detected_in_comma_list(self) -> None:
        skills = self._skills(
            "Python, FastAPI, React, LLMs, RAG, Sentence Transformers, FAISS, GitHub"
        )
        self.assertIn("GitHub", skills)

    def test_github_detected_on_own_line(self) -> None:
        self.assertIn("GitHub", self._skills("GitHub\nRAG\nFAISS"))

    def test_github_does_not_trigger_git(self) -> None:
        """'github' must not cause Git to appear when git itself is absent."""
        skills = self._skills("github actions and github pages")
        self.assertIn("GitHub", skills)
        self.assertNotIn("Git", skills)

    def test_git_detected_when_present(self) -> None:
        skills = self._skills("Skills: Python, Git, GitHub, Docker")
        self.assertIn("Git", skills)
        self.assertIn("GitHub", skills)

    # ── REST API ──────────────────────────────────────────────────────────────
    def test_rest_api_phrase(self) -> None:
        self.assertIn("REST API", self._skills("REST API integration"))

    def test_restful_api_phrase(self) -> None:
        self.assertIn("REST API", self._skills("RESTful API design"))

    def test_api_development_phrase(self) -> None:
        self.assertIn("REST API", self._skills("api development experience"))

    def test_skills_line_with_rest_api(self) -> None:
        skills = self._skills(
            "Skills: JavaScript, React, Node.js, SQL, Python, REST API, Git"
        )
        self.assertIn("REST API", skills)

    # ── RAG ───────────────────────────────────────────────────────────────────
    def test_rag_on_own_line(self) -> None:
        """RAG on its own line (newline-separated) must be detected."""
        self.assertIn("RAG", self._skills("GitHub\nRAG\nFAISS"))

    def test_rag_in_comma_list(self) -> None:
        self.assertIn("RAG", self._skills("LLMs, RAG, Sentence Transformers"))

    def test_rag_in_sentence(self) -> None:
        self.assertIn("RAG", self._skills("Built with llm and rag pipelines"))

    def test_rag_not_matched_in_fragment(self) -> None:
        """'rag' must not match inside unrelated words."""
        self.assertNotIn("RAG", self._skills("fragrant garage storage"))

    # ── FAISS ─────────────────────────────────────────────────────────────────
    def test_faiss_detected(self) -> None:
        self.assertIn("FAISS", self._skills("Using FAISS for vector search"))

    # ── Sentence Transformers ─────────────────────────────────────────────────
    def test_sentence_transformers_space_form(self) -> None:
        self.assertIn("Sentence Transformers",
                      self._skills("sentence transformers library"))

    def test_sentence_transformers_hyphen_form(self) -> None:
        self.assertIn("Sentence Transformers",
                      self._skills("sentence-transformers==2.2.2"))

    # ── LLMs ─────────────────────────────────────────────────────────────────
    def test_llms_plural(self) -> None:
        self.assertIn("LLMs", self._skills("Working with LLMs"))

    def test_llm_singular(self) -> None:
        self.assertIn("LLMs", self._skills("an llm based system"))

    def test_large_language_model(self) -> None:
        self.assertIn("LLMs", self._skills("large language model fine-tuning"))

    # ── FastAPI ───────────────────────────────────────────────────────────────
    def test_fastapi_detected(self) -> None:
        self.assertIn("FastAPI", self._skills("backend built with FastAPI"))

    # ── Python / React / JavaScript ───────────────────────────────────────────
    def test_python_detected(self) -> None:
        self.assertIn("Python", self._skills("Python, SQL, Machine Learning"))

    def test_react_detected(self) -> None:
        self.assertIn("React", self._skills("React, Node.js, TypeScript"))

    def test_javascript_detected(self) -> None:
        self.assertIn("JavaScript", self._skills("javascript and typescript"))

    # ── No duplicates anywhere ────────────────────────────────────────────────
    def test_no_duplicates_in_dense_text(self) -> None:
        text = (
            "Python FastAPI React LLMs RAG FAISS GitHub REST API "
            "Python fastapi react llms rag faiss github rest api"
        )
        raw = self._raw(text)
        for skill in raw:
            self.assertEqual(raw.count(skill), 1,
                             msg=f"Duplicate in output: {skill!r}")

    # ── Fixture: shirley_resume.txt ───────────────────────────────────────────
    def test_shirley_fixture_skills(self) -> None:
        """Shirley resume must include all expected skills."""
        text = (ROOT / "tests/resume_samples/shirley_resume.txt").read_text(
            encoding="utf-8"
        )
        skills = self._skills(text)
        for required in ("Python", "FastAPI", "React", "LLMs", "RAG",
                         "Sentence Transformers", "FAISS", "GitHub"):
            with self.subTest(skill=required):
                self.assertIn(required, skills)

    # ── Fixture: intern_resume.txt — REST API + Git ───────────────────────────
    def test_intern_fixture_rest_api_and_git(self) -> None:
        """Intern resume must include REST API and Git."""
        text = (ROOT / "tests/resume_samples/intern_resume.txt").read_text(
            encoding="utf-8"
        )
        skills = self._skills(text)
        self.assertIn("REST API", skills)
        self.assertIn("Git", skills)

    # ── Fixture: all fixtures — no duplicates ─────────────────────────────────
    def test_no_duplicates_across_all_fixtures(self) -> None:
        sample_dir = ROOT / "tests" / "resume_samples"
        for fixture_name in EXPECTATIONS:
            with self.subTest(fixture=fixture_name):
                text = (sample_dir / fixture_name).read_text(encoding="utf-8")
                raw = self._raw(text)
                for skill in raw:
                    self.assertEqual(
                        raw.count(skill), 1,
                        msg=f"{fixture_name}: duplicate skill {skill!r}",
                    )


# ---------------------------------------------------------------------------
# Unit tests for PDF / DOCX extraction validation
# ---------------------------------------------------------------------------

class ExtractionValidationTests(unittest.TestCase):
    """_assert_usable_text, extract_pdf_text, extract_docx_text behaviour."""

    # ── _assert_usable_text ───────────────────────────────────────────────────
    def test_assert_usable_raises_on_empty(self) -> None:
        from backend.resume_parser import _assert_usable_text
        with self.assertRaises(ValueError) as ctx:
            _assert_usable_text("", "PDF", ["PyMuPDF returned empty text."])
        self.assertIn("Unable to extract any text", str(ctx.exception))
        self.assertIn("PDF", str(ctx.exception))

    def test_assert_usable_raises_on_too_short(self) -> None:
        from backend.resume_parser import _assert_usable_text, _MIN_RESUME_TEXT_LENGTH
        short = "x" * (_MIN_RESUME_TEXT_LENGTH - 1)
        with self.assertRaises(ValueError) as ctx:
            _assert_usable_text(short, "DOCX", ["python-docx extracted 79 chars."])
        msg = str(ctx.exception)
        self.assertIn("too short", msg)
        self.assertIn("DOCX", msg)

    def test_assert_usable_passes_on_good_text(self) -> None:
        from backend.resume_parser import _assert_usable_text
        # Should not raise for a realistic resume snippet
        good = "Priya Nair\nB.Tech IT\nAnna University\nPython, React, SQL\n" * 3
        _assert_usable_text(good, "PDF", [])  # no exception

    def test_assert_usable_error_contains_log(self) -> None:
        from backend.resume_parser import _assert_usable_text
        log = ["PyMuPDF: 0 chars.", "pdfplumber: 0 chars."]
        with self.assertRaises(ValueError) as ctx:
            _assert_usable_text("", "PDF", log)
        msg = str(ctx.exception)
        self.assertIn("PyMuPDF", msg)
        self.assertIn("pdfplumber", msg)

    # ── extract_pdf_text public wrapper ───────────────────────────────────────
    def test_extract_pdf_text_returns_string_for_bad_input(self) -> None:
        """extract_pdf_text must return '' not raise for a non-PDF payload."""
        from backend.resume_parser import extract_pdf_text
        # Pass random bytes that are not a valid PDF
        result = extract_pdf_text(b"not a pdf at all")
        self.assertIsInstance(result, str)
        # Should be empty or near-empty — either way, no exception
        self.assertLess(len(result.strip()), 20)

    # ── extract_docx_text public wrapper ─────────────────────────────────────
    def test_extract_docx_text_returns_string_for_bad_input(self) -> None:
        """extract_docx_text must return '' not raise for a corrupt payload."""
        from backend.resume_parser import extract_docx_text
        result = extract_docx_text(b"not a docx file")
        self.assertIsInstance(result, str)

    # ── parse_uploaded_candidate: clear error for unsupported type ───────────
    def test_unsupported_file_type_raises(self) -> None:
        from backend.resume_parser import parse_uploaded_candidate
        with self.assertRaises(ValueError) as ctx:
            parse_uploaded_candidate("resume.xlsx", b"some bytes")
        self.assertIn("Unsupported", str(ctx.exception))
        self.assertIn("xlsx", str(ctx.exception))

    # ── parse_uploaded_candidate: JSON path works and has extraction_log ──────
    def test_json_upload_produces_extraction_log(self) -> None:
        from backend.resume_parser import parse_uploaded_candidate
        import json as _json
        payload = _json.dumps({
            "name": "Priya Nair",
            "skills": ["Python", "SQL"],
            "degree": "B.Tech Information Technology",
            "college": "Anna University",
            "email": "priya@example.com",
            "phone": "+91 9123456780",
        }).encode()
        result = parse_uploaded_candidate("candidate.json", payload)
        self.assertIsInstance(result.extraction_log, list)
        self.assertTrue(len(result.extraction_log) > 0)
        self.assertIn("JSON", result.extraction_log[0])

    # ── parse_uploaded_candidate: text-too-short raises meaningful error ──────
    def test_empty_pdf_payload_raises_clear_error(self) -> None:
        """An all-zero/garbage PDF payload must raise ValueError, not crash."""
        from backend.resume_parser import parse_uploaded_candidate
        with self.assertRaises(ValueError) as ctx:
            parse_uploaded_candidate("resume.pdf", b"%PDF-1.4 garbage content")
        msg = str(ctx.exception)
        # Must be a clean error, not a raw library traceback string
        self.assertTrue(
            "extract" in msg.lower() or "short" in msg.lower()
            or "unable" in msg.lower() or "text" in msg.lower(),
            msg=f"Expected descriptive extraction error, got: {msg!r}",
        )

    # ── _extract_pdf_text_with_log log structure ──────────────────────────────
    def test_pdf_log_is_populated(self) -> None:
        from backend.resume_parser import _extract_pdf_text_with_log
        _, log = _extract_pdf_text_with_log(b"not a pdf")
        self.assertIsInstance(log, list)
        self.assertTrue(len(log) >= 1, "Log should have at least one entry")

    def test_docx_log_is_populated(self) -> None:
        from backend.resume_parser import _extract_docx_text_with_log
        _, log = _extract_docx_text_with_log(b"not a docx")
        self.assertIsInstance(log, list)
        self.assertTrue(len(log) >= 1, "Log should have at least one entry")

    # ── debug_extraction smoke test (just must not raise) ─────────────────────
    def test_debug_extraction_does_not_raise(self) -> None:
        """debug_extraction is a diagnostic print utility; it must never raise."""
        from backend.resume_parser import debug_extraction
        import io as _io, contextlib
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            debug_extraction("test.pdf", b"not a real pdf")
            debug_extraction("test.docx", b"not a real docx")
            debug_extraction("test.json", b'{"name": "Test"}')
            debug_extraction("test.xyz", b"unknown format")
        output = buf.getvalue()
        self.assertIn("debug_extraction", output)
        self.assertIn("test.pdf", output)
