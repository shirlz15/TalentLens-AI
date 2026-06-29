import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.resume_parser import parse_candidate_text


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
