# TalentLens AI

India's Recruiter Cognitive Twin

An AI-powered candidate discovery and ranking system that combines:

- Technical Fit Analysis
- Hireability Intelligence
- Authenticity Verification
- Honeypot Detection
- Explainable Candidate Ranking

## Tech Stack

Python, FastAPI, Sentence Transformers, FAISS, LLMs, RAG, Pandas, NumPy, HTML, CSS, JavaScript.

Built for the India Runs Data & AI Challenge.

## Innovation: Recruiter Cognitive Twin & Hidden Gem Detection

TalentLens now adds two recruiter-intelligence layers on top of the existing ranking engine while preserving the original final-score logic.

**Recruiter Cognitive Twin Score** simulates how an experienced recruiter would read the whole candidate story. It combines technical fit, experience, career consistency, behavioral signals, authenticity, and skill clusters into a 0-100 score with recruiter-style reasoning and evidence.

**Hidden Gem Detection** identifies high-upside candidates who may be missed by traditional screening. It looks for strong project evidence, technical skill ecosystems, learning velocity, GitHub activity, healthy behavioral signals, and lower experience or visibility. Outputs include `hidden_gem_score`, `hidden_gem_flag`, and `hidden_gem_reason`.

These fields are included in candidate intelligence cards, score breakdowns, and CSV exports:

- `recruiter_cognitive_twin_score`
- `recruiter_reasoning`
- `hidden_gem_score`
- `hidden_gem_flag`
- `hidden_gem_reason`

## Architecture

JD Understanding

↓

Semantic Embedding

↓

FAISS Candidate Retrieval

↓

Hybrid Scoring Engine

↓

Recruiter Cognitive Twin

↓

Hidden Gem Detection

↓

Optional LLM Reasoning

↓

Ranked CSV + Dashboard

TalentLens works offline using deterministic reasoning and fallback semantic retrieval. If an `OPENAI_API_KEY` or `GEMINI_API_KEY` is provided, recruiter reasoning, hidden-gem explanation, and interview recommendation can be upgraded with LLM-backed explanations.

## Workflow: Built-In Candidate Database

TalentLens now works as a database-first AI recruiter platform. Recruiters can enter a job title, choose a role family, paste a job description, and rank candidates from the stored TalentLens database immediately.

Resume upload is supported only on the Analyze Role page for Resume PDF, Resume DOCX, and Candidate JSON. Uploaded candidates are parsed into structured profiles, stored locally, marked `User Added`, and included in future rankings.

Frontend workflow:

- Home: search role, paste JD, analyze candidates
- Analyze Role: database-first job search with optional resume upload
- Rankings: ranks candidates from the stored database by default
- Candidate Database: view-only database with parsed profile details, scores, recruiter confidence, hidden-gem status, authenticity risk, and source
- Hidden Gems: surfaces overlooked high-potential talent with hidden-gem reasoning and recruiter recommendation
- AI Insights: analytics over score quality, experience, skill clusters, universities, confidence, risk, authenticity, and hidden-gem distribution
