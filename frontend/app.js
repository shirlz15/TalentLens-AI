// ── MOCK DATA ──────────────────────────────────────────────────────────────
const CANDIDATES = [
  {
    id: 1, name: "Aisha Kapoor", initials: "AK",
    role: "Senior ML Engineer", company: "Google DeepMind", location: "Bangalore",
    experience: 6, finalScore: 94, technicalScore: 96, experienceScore: 91,
    behavioralScore: 89, authenticityScore: 97, cognitiveTwinScore: 93,
    hiddenGem: false, riskLevel: "Low",
    skills: ["PyTorch","Transformers","MLOps","Kubernetes","Python","LLMs","RAG"],
    strengths: ["Deep transformer architecture expertise","Strong open-source contributions","Exceptional problem decomposition"],
    weaknesses: ["Limited product management exposure","Prefers async collaboration"],
    whyRanked: "Exceptional alignment with JD requirements. 6 years of cutting-edge ML work at top-tier labs.",
    recruiterReasoning: "Rare combination of research depth and production-grade ML deployment. Immediate value.",
    authenticityRisk: "Minimal — verified publications and GitHub contributions corroborate all claims.",
    careerConsistency: 95, growthPotential: 88, learningVelocity: 92, technicalDepth: 96,
    education: "IIT Bombay · M.Tech CS", gradient: "linear-gradient(135deg,#8b5cf6,#6366f1)"
  },
  {
    id: 2, name: "Rohan Mehta", initials: "RM",
    role: "AI Product Engineer", company: "Sarvam AI", location: "Pune",
    experience: 4, finalScore: 88, technicalScore: 84, experienceScore: 86,
    behavioralScore: 94, authenticityScore: 90, cognitiveTwinScore: 87,
    hiddenGem: true, riskLevel: "Low",
    skills: ["React","Node.js","FastAPI","Vector DBs","Prompt Engineering","TypeScript","Python"],
    strengths: ["Full-stack AI product builder","Exceptional user empathy","Rapid prototyping velocity"],
    weaknesses: ["Less exposure to distributed systems","Early-stage ML research gaps"],
    whyRanked: "Strong product-AI bridge profile. Rare ability to translate ML outputs into delightful UX.",
    recruiterReasoning: "Hidden gem — career trajectory shows 3x acceleration. Would thrive in a fast-moving AI startup.",
    authenticityRisk: "Low — product demos and live links validate all claimed projects.",
    careerConsistency: 88, growthPotential: 96, learningVelocity: 94, technicalDepth: 80,
    education: "BITS Pilani · B.E. CS", gradient: "linear-gradient(135deg,#06b6d4,#6366f1)"
  },
  {
    id: 3, name: "Priya Sharma", initials: "PS",
    role: "Data Science Lead", company: "Flipkart AI", location: "Bangalore",
    experience: 8, finalScore: 91, technicalScore: 89, experienceScore: 95,
    behavioralScore: 88, authenticityScore: 92, cognitiveTwinScore: 90,
    hiddenGem: false, riskLevel: "Low",
    skills: ["Python","Spark","XGBoost","A/B Testing","SQL","Airflow","dbt","Tableau"],
    strengths: ["Proven impact at scale (100M+ users)","Strong stakeholder management","Data strategy leadership"],
    weaknesses: ["Primarily non-deep-learning background","Traditional ML stack preference"],
    whyRanked: "8 years of measurable business impact. Leads teams that ship high-quality, production-stable models.",
    recruiterReasoning: "Safe, high-value hire. Brings institutional knowledge of large-scale data infra.",
    authenticityRisk: "Negligible — LinkedIn endorsements and project details are consistent.",
    careerConsistency: 97, growthPotential: 78, learningVelocity: 82, technicalDepth: 85,
    education: "IIM Calcutta · MBA + IIT Delhi · B.Tech", gradient: "linear-gradient(135deg,#ec4899,#8b5cf6)"
  },
  {
    id: 4, name: "Kiran Nair", initials: "KN",
    role: "ML Research Scientist", company: "Wadhwani AI", location: "Mumbai",
    experience: 3, finalScore: 82, technicalScore: 90, experienceScore: 70,
    behavioralScore: 80, authenticityScore: 85, cognitiveTwinScore: 83,
    hiddenGem: true, riskLevel: "Medium",
    skills: ["JAX","Flax","Research","NLP","Computer Vision","RLHF","Python"],
    strengths: ["Published NeurIPS & ICML papers","Novel algorithmic thinking","Strong theoretical foundations"],
    weaknesses: ["Limited production deployment experience","Industry transition is ongoing"],
    whyRanked: "Research-grade talent with significant upside. Papers show innovative thinking beyond most 3-year profiles.",
    recruiterReasoning: "High-ceiling hidden gem. 2 years from becoming a principal-level researcher or tech lead.",
    authenticityRisk: "Low — publications are publicly verifiable.",
    careerConsistency: 82, growthPotential: 97, learningVelocity: 95, technicalDepth: 93,
    education: "IISc Bangalore · Ph.D. (ongoing)", gradient: "linear-gradient(135deg,#10b981,#06b6d4)"
  },
  {
    id: 5, name: "Arjun Verma", initials: "AV",
    role: "MLOps Platform Engineer", company: "PhonePe", location: "Bangalore",
    experience: 5, finalScore: 85, technicalScore: 88, experienceScore: 84,
    behavioralScore: 82, authenticityScore: 88, cognitiveTwinScore: 84,
    hiddenGem: false, riskLevel: "Low",
    skills: ["Kubernetes","Kubeflow","MLflow","Terraform","Docker","Python","Prometheus"],
    strengths: ["End-to-end ML platform ownership","FinTech domain expertise","High operational reliability mindset"],
    weaknesses: ["Less model development experience","Narrow vertical experience"],
    whyRanked: "Solid infrastructure-layer candidate. Ensures models reach production reliably at scale.",
    recruiterReasoning: "Production-first mindset is rare. Critical for any team scaling beyond POC stage.",
    authenticityRisk: "Low — certifications and internal project descriptions match.",
    careerConsistency: 90, growthPotential: 80, learningVelocity: 80, technicalDepth: 82,
    education: "NIT Trichy · B.Tech CS", gradient: "linear-gradient(135deg,#f59e0b,#ef4444)"
  },
  {
    id: 6, name: "Sneha Patel", initials: "SP",
    role: "Conversational AI Engineer", company: "Ola Krutrim", location: "Hyderabad",
    experience: 4, finalScore: 79, technicalScore: 82, experienceScore: 78,
    behavioralScore: 76, authenticityScore: 80, cognitiveTwinScore: 78,
    hiddenGem: true, riskLevel: "Medium",
    skills: ["Rasa","Dialogflow","LangChain","Python","NLU","TTS","STT","Hindi NLP"],
    strengths: ["Multilingual AI expertise","Conversational flow design","Real-world deployment in Indic languages"],
    weaknesses: ["Limited foundation model experience","Salary expectations uncertain"],
    whyRanked: "Niche expertise in Indic language AI — highly differentiated for India-first products.",
    recruiterReasoning: "Hidden gem for India-focused AI companies. Understands nuances that generic AI engineers miss.",
    authenticityRisk: "Medium — one project timeline appears inconsistent. Recommend verification.",
    careerConsistency: 80, growthPotential: 92, learningVelocity: 91, technicalDepth: 78,
    education: "IIIT Hyderabad · M.S. CSE", gradient: "linear-gradient(135deg,#8b5cf6,#ec4899)"
  },
  {
    id: 7, name: "Asha Rao", initials: "AR", role: "Senior Data Scientist", company: "TalentLens Dataset", location: "India",
    experience: 6, finalScore: 96, technicalScore: 77, experienceScore: 100, behavioralScore: 85, authenticityScore: 100, cognitiveTwinScore: 90,
    hiddenGem: false, riskLevel: "Low", skills: ["Python","SQL","Machine Learning","Statistics","Pandas","Data Analysis"],
    strengths: ["Senior data science progression","Strong Python and ML evidence","Verified profile signals"], weaknesses: ["Communication not explicit in profile"],
    whyRanked: "Strong senior data scientist from the stored TalentLens dataset.", recruiterReasoning: "Immediate shortlist for data science roles with strong technical and trust signals.",
    authenticityRisk: "Low", careerConsistency: 94, growthPotential: 82, learningVelocity: 78, technicalDepth: 84, education: "BTech Computer Science", gradient: "linear-gradient(135deg,#10b981,#3b82f6)"
  },
  {
    id: 8, name: "Rohan Mehta", initials: "RM", role: "ML Engineer", company: "TalentLens Dataset", location: "India",
    experience: 5, finalScore: 84, technicalScore: 62, experienceScore: 100, behavioralScore: 84, authenticityScore: 100, cognitiveTwinScore: 82,
    hiddenGem: false, riskLevel: "Low", skills: ["Python","Machine Learning","Deep Learning","Docker","AWS","API Development","SQL"],
    strengths: ["ML engineering deployment profile","Strong GitHub activity","Cloud and API exposure"], weaknesses: ["Statistics not explicit"],
    whyRanked: "Good ML engineering fit from the built-in database.", recruiterReasoning: "Strong consideration for ML engineering roles, especially model deployment.",
    authenticityRisk: "Low", careerConsistency: 84, growthPotential: 80, learningVelocity: 82, technicalDepth: 82, education: "MSc Data Science", gradient: "linear-gradient(135deg,#6366f1,#06b6d4)"
  },
  {
    id: 9, name: "Nisha Iyer", initials: "NI", role: "Analytics Lead", company: "TalentLens Dataset", location: "India",
    experience: 8, finalScore: 91, technicalScore: 62, experienceScore: 100, behavioralScore: 83, authenticityScore: 100, cognitiveTwinScore: 84,
    hiddenGem: false, riskLevel: "Low", skills: ["SQL","Excel","Power BI","Tableau","Data Analysis","Statistics","Communication"],
    strengths: ["Analytics leadership","Strong recruiter engagement","Excellent verification"], weaknesses: ["Python and ML are not explicit"],
    whyRanked: "Strong analytics leader with excellent behavioral signals.", recruiterReasoning: "Strong analytics or BI shortlist, validate ML depth for AI roles.",
    authenticityRisk: "Low", careerConsistency: 93, growthPotential: 74, learningVelocity: 76, technicalDepth: 72, education: "MBA Analytics", gradient: "linear-gradient(135deg,#ec4899,#f59e0b)"
  },
  {
    id: 10, name: "Kabir Singh", initials: "KS", role: "Data Engineer", company: "TalentLens Dataset", location: "India",
    experience: 5, finalScore: 77, technicalScore: 45, experienceScore: 100, behavioralScore: 69, authenticityScore: 100, cognitiveTwinScore: 76,
    hiddenGem: false, riskLevel: "Low", skills: ["Python","SQL","Data Engineering","Spark","GCP","Docker"],
    strengths: ["Data engineering foundation","Cloud data certification","Reliable profile evidence"], weaknesses: ["Limited ML role overlap"],
    whyRanked: "Strong data engineer for pipeline-heavy roles.", recruiterReasoning: "Best considered for data platform roles adjacent to AI teams.",
    authenticityRisk: "Low", careerConsistency: 86, growthPotential: 72, learningVelocity: 76, technicalDepth: 76, education: "BTech Information Technology", gradient: "linear-gradient(135deg,#06b6d4,#10b981)"
  },
  {
    id: 11, name: "Priya Shah", initials: "PS", role: "NLP Engineer", company: "TalentLens Dataset", location: "India",
    experience: 4, finalScore: 68, technicalScore: 47, experienceScore: 78, behavioralScore: 73, authenticityScore: 88, cognitiveTwinScore: 72,
    hiddenGem: true, riskLevel: "Low", skills: ["Python","NLP","Deep Learning","Machine Learning","Pandas","Git","LLMs","RAG"],
    strengths: ["NLP and LLM project evidence","High learning velocity","Strong GitHub activity"], weaknesses: ["Less senior experience"],
    whyRanked: "Hidden gem from the stored database with project-heavy AI profile.", recruiterReasoning: "High-upside AI/NLP candidate who may be missed by seniority-first screening.",
    authenticityRisk: "Low", careerConsistency: 69, growthPotential: 90, learningVelocity: 88, technicalDepth: 80, education: "MTech AI", gradient: "linear-gradient(135deg,#8b5cf6,#06b6d4)"
  }
];

const JD_MOCK = {
  title: "Senior AI/ML Engineer",
  company: "TalentLens AI",
  seniority: "Senior (L5-L6)",
  experience: "4-8 years",
  skills: {
    must: ["Python","Machine Learning","Deep Learning","MLOps","System Design"],
    good: ["LLMs","RAG","Kubernetes","Transformers","PyTorch","TensorFlow"],
    bonus: ["Research publications","Open source","Startup experience"]
  },
  responsibilities: [
    "Design and deploy scalable ML systems serving millions of users",
    "Lead technical architecture for ML platform and model serving",
    "Mentor junior engineers and drive research roadmap",
    "Collaborate cross-functionally with product and data teams"
  ],
  culture: ["Fast-paced","Ownership mindset","Deep technical excellence","User obsession"]
};

// ── SHARED UTILITIES ────────────────────────────────────────────────────────

function getScoreColor(score) {
  if (score >= 90) return '#10b981';
  if (score >= 75) return '#6366f1';
  if (score >= 60) return '#f59e0b';
  return '#ef4444';
}

function buildScoreRing(score, size = 80, strokeWidth = 6) {
  const r = (size - strokeWidth * 2) / 2;
  const circ = 2 * Math.PI * r;
  const pct = score / 100;
  const color = getScoreColor(score);
  return `
    <div class="score-ring" style="width:${size}px;height:${size}px;">
      <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
        <circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="${strokeWidth}"/>
        <circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none" stroke="${color}" stroke-width="${strokeWidth}"
          stroke-dasharray="${circ}" stroke-dashoffset="${circ*(1-pct)}"
          stroke-linecap="round" style="transition:stroke-dashoffset 1s cubic-bezier(0.4,0,0.2,1);"/>
      </svg>
      <div class="ring-value" style="font-size:${size/4}px;color:${color};">${score}</div>
    </div>`;
}

function buildProgressBar(value, cls = '') {
  return `<div class="progress-bar"><div class="progress-fill ${cls}" style="width:0%" data-target="${value}"></div></div>`;
}

function animateProgressBars() {
  document.querySelectorAll('.progress-fill').forEach(el => {
    const t = el.dataset.target;
    requestAnimationFrame(() => { setTimeout(() => { el.style.width = t + '%'; }, 100); });
  });
}

function buildNav(activePage) {
  const links = [
    { href:'index.html', label:'Home' },
    { href:'jd-analysis.html', label:'Analyze Role' },
    { href:'dashboard.html', label:'Rankings' },
    { href:'candidate-database.html', label:'Database' },
    { href:'hidden-gems.html', label:'Hidden Gems' },
    { href:'comparison.html', label:'Compare' },
    { href:'insights.html', label:'AI Insights' },
  ];
  return `
  <nav class="nav">
    <a href="index.html" class="nav-logo">
      <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
        <circle cx="14" cy="14" r="13" stroke="url(#lg)" stroke-width="2"/>
        <path d="M8 14l4 4 8-8" stroke="url(#lg2)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        <defs>
          <linearGradient id="lg" x1="0" y1="0" x2="28" y2="28"><stop stop-color="#8b5cf6"/><stop offset="1" stop-color="#3b82f6"/></linearGradient>
          <linearGradient id="lg2" x1="0" y1="0" x2="28" y2="28"><stop stop-color="#8b5cf6"/><stop offset="1" stop-color="#06b6d4"/></linearGradient>
        </defs>
      </svg>
      TalentLens AI
    </a>
    <div class="nav-links">
      ${links.map(l=>`<a href="${l.href}" class="nav-link${activePage===l.href?' active':''}">${l.label}</a>`).join('')}
    </div>
    <a href="jd-analysis.html" class="nav-cta">Analyze Candidates</a>
  </nav>`;
}

// Built-in TalentLens database workflow
const TALENTLENS_DB_KEY = 'talentlens_user_candidates_v1';
const TALENTLENS_SEARCH_KEY = 'talentlens_active_search_v1';
const LOW_CONFIDENCE_LABEL = 'Candidate Profile';
const LOW_CONFIDENCE_ERROR = 'Unable to confidently parse this resume. Please upload a clearer PDF/DOCX/JSON.';
const ADMIN_DELETE_PASSWORD = 'TalentLensAdmin2026';
const BACKEND_UPLOAD_ENDPOINT = 'http://127.0.0.1:8000/upload-candidate';
const PLACEHOLDER_NAME_PATTERN = /^(imported candidate|data candidate|uploaded candidate|resume profile|resume-based talent profile|candidate profile|not specified|stream)$/i;
const NAME_NOISE_WORDS = new Set([
  'skills', 'skill', 'education', 'projects', 'project', 'experience', 'summary', 'certifications',
  'certification', 'contact', 'stream', 'resume', 'profile', 'github', 'linkedin', 'python', 'sql',
  'rag', 'ai', 'ml', 'git', 'fastapi', 'react', 'machine', 'learning', 'developer', 'engineer', 'student', 'intern', 'objective'
]);
const CONTROLLED_SKILL_LIBRARY = [
  { name: 'Python', aliases: ['python'] },
  { name: 'Java', aliases: ['java'] },
  { name: 'JavaScript', aliases: ['javascript', ' js '] },
  { name: 'TypeScript', aliases: ['typescript'] },
  { name: 'React', aliases: ['react'] },
  { name: 'Node.js', aliases: ['node.js', 'nodejs'] },
  { name: 'Express', aliases: ['express', 'express.js'] },
  { name: 'FastAPI', aliases: ['fastapi'] },
  { name: 'Flask', aliases: ['flask'] },
  { name: 'Django', aliases: ['django'] },
  { name: 'HTML', aliases: ['html'] },
  { name: 'CSS', aliases: ['css'] },
  { name: 'Tailwind', aliases: ['tailwind', 'tailwindcss'] },
  { name: 'Vite', aliases: ['vite'] },
  { name: 'SQL', aliases: ['sql'] },
  { name: 'MongoDB', aliases: ['mongodb', 'mongo db'] },
  { name: 'Supabase', aliases: ['supabase'] },
  { name: 'Firebase', aliases: ['firebase'] },
  { name: 'PostgreSQL', aliases: ['postgresql', 'postgres', 'psql'] },
  { name: 'MySQL', aliases: ['mysql'] },
  { name: 'Machine Learning', aliases: ['machine learning', ' ml ', 'ml models'] },
  { name: 'Deep Learning', aliases: ['deep learning'] },
  { name: 'NLP', aliases: ['nlp', 'natural language processing'] },
  { name: 'Computer Vision', aliases: ['computer vision'] },
  { name: 'LLMs', aliases: ['llm', 'llms', 'large language model', 'large language models'] },
  { name: 'RAG', aliases: ['rag', 'retrieval augmented generation'] },
  { name: 'Sentence Transformers', aliases: ['sentence transformers', 'sentence-transformers'] },
  { name: 'FAISS', aliases: ['faiss'] },
  { name: 'LangChain', aliases: ['langchain'] },
  { name: 'PyTorch', aliases: ['pytorch'] },
  { name: 'TensorFlow', aliases: ['tensorflow'] },
  { name: 'Pandas', aliases: ['pandas'] },
  { name: 'NumPy', aliases: ['numpy'] },
  { name: 'Scikit-learn', aliases: ['scikit-learn', 'sklearn'] },
  { name: 'GCP', aliases: ['gcp', 'google cloud'] },
  { name: 'Azure', aliases: ['azure'] },
  { name: 'AWS', aliases: ['aws', 'amazon web services'] },
  { name: 'Docker', aliases: ['docker'] },
  { name: 'Git', aliases: [' git '] },
  { name: 'GitHub', aliases: ['github'] },
  { name: 'REST API', aliases: ['rest api', 'restful api', 'api development'] },
  { name: 'Data Analysis', aliases: ['data analysis', 'analytics'] },
  { name: 'Spark', aliases: ['spark', 'apache spark'] },
  { name: 'Airflow', aliases: ['airflow', 'apache airflow'] },
  { name: 'ETL', aliases: ['etl'] },
  { name: 'Prompt Engineering', aliases: ['prompt engineering'] },
  { name: 'Vector DB', aliases: ['vector db', 'vector database', 'vector databases'] },
  { name: 'Cybersecurity', aliases: ['cybersecurity', 'cyber security'] },
  { name: 'IoT', aliases: ['iot', 'internet of things'] }
];

function normalizeTextValue(value) {
  return String(value || '')
    .replace(/[\u200b-\u200d\uFEFF]/g, '')
    .replace(/\u00a0/g, ' ')
    .replace(/[ \t]+/g, ' ')
    .trim();
}

function isPlaceholderValue(value) {
  const clean = normalizeTextValue(value);
  return !clean || PLACEHOLDER_NAME_PATTERN.test(clean);
}

function isLikelySectionHeader(line) {
  return /^(skills?|education|projects?|experience|summary|certifications?|contact|stream|resume|profile|objective|achievements?)$/i.test(normalizeTextValue(line).replace(/[:\-]+$/, ''));
}

function isLikelyNameToken(token) {
  const clean = token.replace(/\./g, '');
  if (!clean) return false;
  if (NAME_NOISE_WORDS.has(clean.toLowerCase())) return false;
  return /^[A-Z][a-z]+$/.test(clean) || /^[A-Z]$/.test(clean);
}

function getCandidateOrganization(candidate) {
  const values = [candidate.company, candidate.college, candidate.location, candidate.source];
  const meaningful = values.find(value => !isPlaceholderValue(value));
  return meaningful || LOW_CONFIDENCE_LABEL;
}

function getCandidateExperienceSummary(candidate) {
  const explicit = normalizeTextValue(candidate.experienceSummary || candidate.experience_summary);
  if (explicit) return explicit;
  return buildExperienceSummary(
    candidate.resumeText || '',
    candidate.projects || [],
    Number(candidate.experience || 0),
    candidate.role || '',
    candidate.degree || ''
  );
}

function getCandidateExperienceBadge(candidate) {
  const experience = Number(candidate.experience || 0);
  if (experience > 0) return `${experience} yrs exp`;
  return getCandidateExperienceSummary(candidate);
}

function degreeShortLabel(degree) {
  const text = normalizeTextValue(degree);
  if (!text) return '';
  const lower = text.toLowerCase();
  let prefix = '';
  if (/(bachelor of technology|b\.?\s?tech|b tech)/i.test(text)) prefix = 'B.Tech';
  else if (/(bachelor of engineering|b\.?\s?e\.?)/i.test(text)) prefix = 'B.E';
  else if (/(master of technology|m\.?\s?tech|m tech)/i.test(text)) prefix = 'M.Tech';
  else if (/(master of engineering|m\.?\s?e\.?)/i.test(text)) prefix = 'M.E';
  else if (/m\.?\s?sc|msc/i.test(text)) prefix = 'M.Sc';
  else if (/b\.?\s?sc|bsc/i.test(text)) prefix = 'B.Sc';
  else return text;
  if (/computer science and engineering|\bcse\b/i.test(lower)) return `${prefix} CSE`;
  if (/computer science|\bcs\b/i.test(lower)) return `${prefix} CS`;
  if (/information technology|\bit\b/i.test(lower)) return `${prefix} IT`;
  if (/artificial intelligence/i.test(lower)) return `${prefix} AI`;
  if (/data science/i.test(lower)) return `${prefix} DS`;
  return prefix;
}

function buildProfileLabel(role, degree, experienceSummary) {
  const degreeLabel = degreeShortLabel(degree);
  if (experienceSummary === 'Student / Intern Profile') return degreeLabel ? `${degreeLabel} Student` : 'Student / Intern Profile';
  const cleanRole = normalizeTextValue(role);
  if (cleanRole && cleanRole !== LOW_CONFIDENCE_LABEL) return cleanRole;
  return degreeLabel || LOW_CONFIDENCE_LABEL;
}

function getCandidateHeadline(candidate) {
  return normalizeTextValue(candidate.profileLabel || candidate.profile_label || candidate.role) || LOW_CONFIDENCE_LABEL;
}

function getCandidateDatabase() {
  const userAdded = JSON.parse(localStorage.getItem(TALENTLENS_DB_KEY) || '[]');
  return [
    ...CANDIDATES.map(c => normalizeStoredCandidate(c, 'Built-In')),
    ...userAdded.map(c => normalizeStoredCandidate(c, 'User Added'))
  ];
}

function normalizeStoredCandidate(candidate, source) {
  const resumeText = candidate.resumeText || '';
  const parsed = resumeText ? extractCandidateProfileFromText(resumeText) : null;
  const name = resolveCandidateName(candidate, parsed);
  const skills = normalizeSkillList(candidate.skills || parsed?.skills || []);
  const projects = normalizeTextList(candidate.projects || parsed?.projects || []);
  const certifications = normalizeTextList(candidate.certifications || parsed?.certifications || []);
  const degree = candidate.degree || parsed?.degree || inferDegreeFromEducation(candidate.education || parsed?.education || '');
  const college = candidate.college || parsed?.college || '';
  const education = formatEducation(degree, college, candidate.education || parsed?.education || '');
  const email = candidate.email || parsed?.email || '';
  const phone = candidate.phone || parsed?.phone || '';
  const linkedin = candidate.linkedin || parsed?.linkedin || '';
  const github = candidate.github || parsed?.github || '';
  const experience = normalizeExperience(candidate.experience ?? parsed?.experience, resumeText, projects);
  const experienceSummary = normalizeTextValue(candidate.experienceSummary || candidate.experience_summary || parsed?.experienceSummary || parsed?.experience_summary || '');
  const role = candidate.role || (parsed?.role || inferRoleFromResume(resumeText, skills));
  const profileLabel = normalizeTextValue(candidate.profileLabel || candidate.profile_label || parsed?.profileLabel || parsed?.profile_label || buildProfileLabel(role, degree, experienceSummary || buildExperienceSummary(resumeText, projects, experience, role, degree)));
  const parsingConfidence = getParsingConfidence({
    name,
    skills,
    projects,
    certifications,
    degree,
    college,
    education,
    email,
    phone,
    linkedin,
    github,
    experience,
    experienceSummary,
    resumeText
  });
  const displayName = isMeaningfulDisplayName(name) ? name : LOW_CONFIDENCE_LABEL;
  const initials = candidate.initials || initialsFromName(name);
  const finalExperienceSummary = experienceSummary || buildExperienceSummary(resumeText, projects, experience, role, degree);
  return {
    ...candidate,
    source: candidate.source || source,
    name: displayName,
    displayName,
    extractedName: name,
    candidate_name: name,
    initials,
    role: profileLabel || role,
    degree,
    college,
    education,
    email,
    phone,
    linkedin,
    github,
    experience,
    experienceSummary: finalExperienceSummary,
    skills,
    projects,
    certifications,
    parsingConfidence,
    profileLabel: profileLabel || role || LOW_CONFIDENCE_LABEL,
    profile_label: profileLabel || role || LOW_CONFIDENCE_LABEL
  };
}

function resolveCandidateName(candidate, parsed) {
  const raw = [
    candidate.name,
    candidate.candidate_name,
    parsed?.name,
    parsed?.candidate_name,
  ].find(value => isMeaningfulDisplayName(value));
  return raw ? cleanName(raw) : LOW_CONFIDENCE_LABEL;
}

function isMeaningfulDisplayName(value) {
  const clean = cleanName(value);
  if (!clean) return false;
  if (clean.length > 60) return false;
  if (PLACEHOLDER_NAME_PATTERN.test(clean)) return false;
  const tokens = clean.split(/\s+/).filter(Boolean);
  if (!tokens.length || tokens.length > 4) return false;
  return tokens.every(isLikelyNameToken);
}

function normalizeSkillList(skills) {
  const text = Array.isArray(skills)
    ? skills.map(value => stringifyEvidenceItem(value)).join('\n')
    : String(skills || '');
  const lower = ` ${text.toLowerCase().replace(/[^a-z0-9.+#/\s-]+/g, ' ')} `;
  return CONTROLLED_SKILL_LIBRARY
    .filter(entry => entry.aliases.some(alias => lower.includes(alias.toLowerCase())))
    .map(entry => entry.name);
}

function normalizeTextList(values) {
  if (Array.isArray(values)) return values.map(value => stringifyEvidenceItem(value)).filter(Boolean);
  if (!values) return [];
  return String(values).split(/\n|[,;/|]/).map(value => normalizeTextValue(value)).filter(Boolean);
}

function stringifyEvidenceItem(value) {
  if (value == null) return '';
  if (typeof value === 'string') return normalizeTextValue(value);
  if (typeof value === 'object') {
    const primary = [value.title, value.name, value.project_name, value.role].find(Boolean);
    const secondary = [value.tech_stack, value.technologies, value.description, value.summary, value.organization].find(Boolean);
    return [primary, secondary].map(item => normalizeTextValue(item)).filter(Boolean).join(' - ');
  }
  return normalizeTextValue(value);
}

function buildExperienceSummary(resumeText, projects, experience, role, degree = '') {
  const normalized = `${resumeText || ''} ${role || ''} ${degree || ''}`.toLowerCase();
  const degreeLower = String(degree || '').toLowerCase();
  const isStudentDegree = /(b\.tech|btech|bachelor of technology|bachelor of engineering|b\.e\b)/.test(degreeLower);
  const hasStudentWords = /\b(student|undergraduate|graduate)\b/.test(normalized);
  const hasInternship = /\b(intern|internship|trainee|apprentice)\b/.test(normalized) || /\b(intern|trainee)\b/i.test(role || '');
  if (experience > 1) return `${experience} year${experience === 1 ? '' : 's'} experience`;
  if (hasInternship) {
    if (hasStudentWords || isStudentDegree) {
      return 'Student / Intern Profile';
    }
    return 'Internship Experience';
  }
  if (hasStudentWords || (isStudentDegree && experience === 0) || projects.length >= 2) {
    return 'Student / Intern Profile';
  }
  if (experience > 0) return `${experience} year${experience === 1 ? '' : 's'} experience`;
  if (/\b(worked|developed|built|freelance|startup|maintained|deployed|consultant)\b/.test(normalized) || projects.length) {
    return 'Experience evidence available';
  }
  return 'Candidate Profile';
}

function formatEducation(degree, college, fallback) {
  const pieces = [degree, college].map(value => normalizeTextValue(value)).filter(Boolean);
  if (pieces.length) return pieces.join(' - ');
  if (pieces.length) return pieces.join(' · ');
  const fallbackText = normalizeTextValue(fallback);
  return fallbackText && !/not specified|uploaded|stream/i.test(fallbackText) ? fallbackText : '';
}

function inferDegreeFromEducation(value) {
  const text = String(value || '');
  const match = text.match(/\b(B\.?\s?Tech|B\.?\s?E\.?|BSc|B\.?\s?Sc|M\.?\s?Tech|M\.?\s?E\.?|MSc|M\.?\s?Sc|MBA|BCA|MCA|PhD|MS|BS|BE|ME)\b[^\n,;]*/i);
  return match ? cleanRole(match[0]) : '';
}

function normalizeExperience(value, resumeText, projects) {
  const direct = Number(value);
  if (Number.isFinite(direct) && direct >= 0) return direct;
  return inferExperienceFromText(resumeText || '', projects || []);
}

function getParsingConfidence(candidate) {
  let score = 0;
  if (isMeaningfulDisplayName(candidate.name)) score += 20;
  if (candidate.email) score += 10;
  if (candidate.phone) score += 8;
  if (candidate.linkedin) score += 8;
  if (candidate.github) score += 8;
  if (candidate.degree) score += 12;
  if (candidate.college) score += 10;
  if ((candidate.skills || []).length) score += Math.min(22, (candidate.skills.length / 8) * 22);
  if ((candidate.projects || []).length) score += Math.min(10, candidate.projects.length * 3);
  if (Number(candidate.experience || 0) > 0 || /Student \/ Intern Profile|Internship Experience|Experience evidence available/i.test(normalizeTextValue(candidate.experienceSummary))) score += 10;
  if ((candidate.resumeText || '').length > 500) score += 4;
  return Math.max(0, Math.min(100, Math.round(score)));
}

function initialsFromName(name) {
  const parts = String(name || '').split(/\s+/).filter(Boolean);
  if (!parts.length) return 'CP';
  return parts.slice(0, 2).map(part => part[0]).join('').toUpperCase();
}

function getCandidateEducationSummary(candidate) {
  const degree = normalizeTextValue(candidate.degree);
  const college = normalizeTextValue(candidate.college);
  if (degree && college) return `${degree} - ${college}`;
  if (degree && college) return `${degree} · ${college}`;
  if (degree) return degree;
  if (college) return college;
  const education = normalizeTextValue(candidate.education);
  if (education && !/resume education profile|not specified|uploaded|stream/i.test(education)) return education;
  return candidate.parsingConfidence < 45 ? LOW_CONFIDENCE_LABEL : '';
}

function buildCareerEvidenceTimeline(candidate) {
  const items = [];
  const role = String(candidate.role || '').trim() || LOW_CONFIDENCE_LABEL;
  const organization = getCandidateOrganization(candidate);
  items.push({
    title: role,
    organization,
    detail: getCandidateExperienceSummary(candidate)
  });

  (candidate.projects || []).slice(0, 2).forEach(project => {
    items.push({
      title: 'Project Evidence',
      organization: String(project || '').trim(),
      detail: 'Hands-on project extracted from resume'
    });
  });

  if ((candidate.certifications || []).length) {
    items.push({
      title: 'Certification',
      organization: String(candidate.certifications[0] || '').trim(),
      detail: 'Certification extracted from profile'
    });
  }

  const educationSummary = getCandidateEducationSummary(candidate);
  if (educationSummary) {
    const parts = educationSummary.split(/\s+-\s+/).map(part => part.trim()).filter(Boolean);
    items.push({
      title: parts[0] || 'Education',
      organization: parts[1] || parts[0] || 'Education Evidence',
      detail: 'Education evidence extracted from profile'
    });
  }

  return items.slice(0, 4);
}

function getCandidateSourceSummary(candidate) {
  return candidate.source || 'Built-In';
}

function saveTalentSearch(search) {
  localStorage.setItem(TALENTLENS_SEARCH_KEY, JSON.stringify(search));
}

function getTalentSearch() {
  return JSON.parse(localStorage.getItem(TALENTLENS_SEARCH_KEY) || JSON.stringify({
    title: JD_MOCK.title,
    role: 'AI/ML Engineering',
    jd: JD_MOCK.responsibilities.join(' ')
  }));
}

function extractRoleSkills(search) {
  const text = `${search.title || ''} ${search.role || ''} ${search.jd || ''}`.toLowerCase();
  const vocabulary = ['Python','SQL','Machine Learning','Deep Learning','PyTorch','TensorFlow','LLMs','RAG','LangChain','Vector DBs','MLOps','Kubernetes','Spark','Airflow','React','FastAPI','Docker','NLP','Tableau','Power BI'];
  const found = vocabulary.filter(skill => text.includes(skill.toLowerCase()) || (skill === 'LLMs' && text.includes('llm')));
  if (found.length) return found;
  if (text.includes('data')) return ['Python','SQL','Machine Learning','Statistics'];
  if (text.includes('frontend') || text.includes('full stack')) return ['React','TypeScript','FastAPI','SQL'];
  return JD_MOCK.skills.must;
}

function rankCandidateForSearch(candidate, search) {
  const required = extractRoleSkills(search);
  const candidateSkills = candidate.skills.map(s => s.toLowerCase());
  const matches = required.filter(skill => candidateSkills.some(cSkill => cSkill.includes(skill.toLowerCase()) || skill.toLowerCase().includes(cSkill)));
  const technical = Math.round(Math.min(100, (matches.length / Math.max(1, required.length)) * 72 + candidate.technicalScore * 0.28));
  const roleText = `${search.title || ''} ${search.role || ''}`.toLowerCase();
  const roleBoost = roleText && candidate.role.toLowerCase().split(/\s+/).some(token => token.length > 2 && roleText.includes(token)) ? 6 : 0;
  const finalScore = Math.round(Math.min(100, technical * 0.34 + candidate.experienceScore * 0.20 + candidate.behavioralScore * 0.20 + candidate.authenticityScore * 0.15 + candidate.careerConsistency * 0.11 + roleBoost));
  return {
    ...candidate,
    finalScore,
    technicalScore: technical,
    matchedSkills: matches,
    searchReason: matches.length
      ? `Matched ${matches.length} stored database skill signals: ${matches.join(', ')}.`
      : 'Limited direct skill overlap; retained for adjacent recruiter review.'
  };
}

function getRankedCandidatesForActiveSearch() {
  const search = getTalentSearch();
  return getCandidateDatabase()
    .map(candidate => rankCandidateForSearch(candidate, search))
    .sort((a, b) => b.finalScore - a.finalScore || b.cognitiveTwinScore - a.cognitiveTwinScore);
}

function addCandidateToDatabase(candidate) {
  const normalizedCandidate = normalizeStoredCandidate({
    ...candidate,
    source: 'User Added'
  }, 'User Added');
  if ((normalizedCandidate.parsingConfidence || 0) < 60) {
    return { added: false, error: LOW_CONFIDENCE_ERROR };
  }
  const existing = JSON.parse(localStorage.getItem(TALENTLENS_DB_KEY) || '[]');
  const duplicate = getCandidateDatabase().find(item => {
    const sameName = isMeaningfulDisplayName(item.extractedName || item.name)
      && isMeaningfulDisplayName(normalizedCandidate.extractedName || normalizedCandidate.name)
      && getNameSimilarity(item.extractedName || item.name, normalizedCandidate.extractedName || normalizedCandidate.name) >= 0.86;
    const sameEmail = item.email && normalizedCandidate.email && item.email.trim().toLowerCase() === normalizedCandidate.email.trim().toLowerCase();
    const samePhone = item.phone && normalizedCandidate.phone && item.phone.replace(/\D/g, '') === normalizedCandidate.phone.replace(/\D/g, '');
    const sameLinkedin = item.linkedin && normalizedCandidate.linkedin && normalizeUrl(item.linkedin) === normalizeUrl(normalizedCandidate.linkedin);
    const sameGithub = item.github && normalizedCandidate.github && normalizeUrl(item.github) === normalizeUrl(normalizedCandidate.github);
    return sameName || sameEmail || samePhone || sameLinkedin || sameGithub;
  });
  if (duplicate) return { added: false, candidate: duplicate };
  const nextId = Math.max(100, ...getCandidateDatabase().map(c => Number(c.id) || 0)) + 1;
  const resumeText = normalizedCandidate.resumeText || '';
  const generated = generateCandidateIntelligence(normalizedCandidate);
  existing.push({
    id: nextId,
    initials: normalizedCandidate.initials || initialsFromName(normalizedCandidate.name),
    name: normalizedCandidate.name,
    displayName: normalizedCandidate.displayName,
    extractedName: normalizedCandidate.extractedName,
    candidate_name: normalizedCandidate.extractedName || normalizedCandidate.name,
    profileLabel: normalizedCandidate.profileLabel || normalizedCandidate.role,
    profile_label: normalizedCandidate.profileLabel || normalizedCandidate.role,
    email: normalizedCandidate.email || '',
    phone: normalizedCandidate.phone || '',
    linkedin: normalizedCandidate.linkedin || '',
    github: normalizedCandidate.github || '',
    role: normalizedCandidate.role || inferRoleFromSkills(normalizedCandidate.skills || []),
    company: normalizedCandidate.company || normalizedCandidate.college || normalizedCandidate.location || 'User Added',
    location: candidate.location || 'India',
    experience: Number(normalizedCandidate.experience || 0),
    experienceSummary: normalizedCandidate.experienceSummary || getCandidateExperienceSummary(normalizedCandidate),
    finalScore: Number(candidate.finalScore || generated.finalScore),
    technicalScore: Number(candidate.technicalScore || generated.technicalScore),
    experienceScore: Number(candidate.experienceScore || generated.experienceScore),
    behavioralScore: Number(candidate.behavioralScore || generated.behavioralScore),
    authenticityScore: Number(candidate.authenticityScore || generated.authenticityScore),
    cognitiveTwinScore: Number(candidate.cognitiveTwinScore || generated.cognitiveTwinScore),
    hiddenGem: Boolean(candidate.hiddenGem || generated.hiddenGem),
    riskLevel: candidate.riskLevel || generated.riskLevel,
    skills: normalizedCandidate.skills || [],
    strengths: candidate.strengths || generated.strengths,
    weaknesses: candidate.weaknesses || generated.weaknesses,
    whyRanked: candidate.whyRanked || generated.whyRanked,
    recruiterReasoning: candidate.recruiterReasoning || generated.recruiterReasoning,
    authenticityRisk: candidate.authenticityRisk || generated.authenticityRisk,
    careerConsistency: Number(candidate.careerConsistency || generated.careerConsistency),
    growthPotential: Number(candidate.growthPotential || generated.growthPotential),
    learningVelocity: Number(candidate.learningVelocity || generated.learningVelocity),
    technicalDepth: Number(candidate.technicalDepth || generated.technicalDepth),
    education: normalizedCandidate.education || normalizedCandidate.degree || normalizedCandidate.college || LOW_CONFIDENCE_LABEL,
    degree: normalizedCandidate.degree || '',
    college: normalizedCandidate.college || '',
    projects: normalizedCandidate.projects || [],
    certifications: normalizedCandidate.certifications || [],
    parsingConfidence: Number(normalizedCandidate.parsingConfidence || 0),
    resumeText,
    gradient: candidate.gradient || 'linear-gradient(135deg,#06b6d4,#8b5cf6)',
    source: 'User Added',
    source_code: 'USER_ADDED'
  });
  localStorage.setItem(TALENTLENS_DB_KEY, JSON.stringify(existing));
  return { added: true, candidate: existing[existing.length - 1] };
}

function deleteUserAddedCandidates(password) {
  const existing = JSON.parse(localStorage.getItem(TALENTLENS_DB_KEY) || '[]');
  if (password !== ADMIN_DELETE_PASSWORD) {
    return { ok: false, error: 'Incorrect admin password.' };
  }
  localStorage.setItem(TALENTLENS_DB_KEY, JSON.stringify([]));
  return { ok: true, deletedCount: existing.length, message: `Deleted ${existing.length} user-added candidate${existing.length === 1 ? '' : 's'}.` };
}

function getHiddenGemScore(candidate) {
  return Math.round(Math.min(100, (candidate.growthPotential || 70) * 0.35 + (candidate.learningVelocity || 70) * 0.25 + (candidate.technicalScore || 70) * 0.20 + (candidate.behavioralScore || 70) * 0.12 + Math.max(0, 100 - (candidate.experience || 0) * 8) * 0.08));
}

function getHiringConfidence(candidate) {
  return Math.round(Math.min(100, (candidate.authenticityScore || 70) * 0.32 + (candidate.careerConsistency || 70) * 0.24 + (candidate.behavioralScore || 70) * 0.20 + (candidate.technicalScore || 70) * 0.16 + ((candidate.skills || []).length >= 5 ? 8 : 2)));
}

function getConfidenceLevel(score) {
  if (score >= 85) return 'High';
  if (score >= 70) return 'Medium';
  return 'Low';
}

function getRecruiterDecision(candidate) {
  const confidence = getHiringConfidence(candidate);
  if ((candidate.finalScore || 0) >= 88 && confidence >= 82) return 'Shortlist';
  if ((candidate.finalScore || 0) >= 76) return 'Strong Consideration';
  if ((candidate.finalScore || 0) >= 62) return 'Hold';
  return 'Reject';
}

function getHiddenGemReason(candidate) {
  if (candidate.hiddenGem) {
    return `High-growth candidate with ${(candidate.skills || []).slice(0, 3).join(', ')} evidence, strong learning velocity, and more upside than traditional seniority-first screening may reveal.`;
  }
  return 'Not currently flagged as a hidden gem because the profile is already visible through seniority, score strength, or conventional experience signals.';
}

function getExecutiveSummary(candidate) {
  const decision = getRecruiterDecision(candidate).toLowerCase();
  const confidence = getConfidenceLevel(getHiringConfidence(candidate)).toLowerCase();
  const concern = (candidate.weaknesses || [])[0] || 'limited additional verification detail';
  return `${candidate.name} is a ${confidence}-confidence ${candidate.role} profile with strong evidence across technical fit, authenticity, and recruiter reasoning. Recommended for ${decision}. Minor concern is ${concern.toLowerCase()}.`;
}

function normalizeUrl(value) {
  return String(value || '').toLowerCase().replace(/^https?:\/\//, '').replace(/^www\./, '').replace(/\/$/, '');
}

function getNameSimilarity(a, b) {
  const left = String(a || '').toLowerCase().replace(/[^a-z\s]/g, '').split(/\s+/).filter(Boolean);
  const right = String(b || '').toLowerCase().replace(/[^a-z\s]/g, '').split(/\s+/).filter(Boolean);
  if (!left.length || !right.length) return 0;
  const shared = left.filter(token => right.includes(token)).length;
  return (shared * 2) / (left.length + right.length);
}

async function parseCandidateWithBackend(file) {
  try {
    const formData = new FormData();
    formData.append('file', file, file.name);
    const response = await fetch(BACKEND_UPLOAD_ENDPOINT, {
      method: 'POST',
      body: formData
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.detail || payload.message || 'Unable to parse uploaded document.');
    return payload && payload.candidate_profile ? payload.candidate_profile : null;
  } catch (error) {
    if (error instanceof TypeError) return null;
    throw error;
  }
}

async function extractTextFromUpload(file, buffer) {
  const name = file.name.toLowerCase();
  if (name.endsWith('.json')) return new TextDecoder('utf-8').decode(buffer);
  if (/\.(png|jpg|jpeg|webp)$/i.test(name)) throw new Error('Image parsing requires OCR support.');
  if (name.endsWith('.docx')) {
    const docxText = await extractDocxText(buffer);
    if (docxText.trim()) return docxText;
    throw new Error('Could not extract text from DOCX.');
  }
  if (name.endsWith('.pdf')) {
    const pdfText = extractPdfText(buffer);
    if (pdfText.trim()) return pdfText;
    throw new Error('Could not extract text from PDF.');
  }
  const decoded = new TextDecoder('utf-8', { fatal: false }).decode(buffer);
  if (normalizeResumeText(decoded)) return decoded;
  throw new Error('Unsupported file type. Use PDF, DOCX, image, or JSON.');
}

function extractPdfText(buffer) {
  const raw = new TextDecoder('latin1').decode(buffer);
  const pieces = [];
  const literalMatches = raw.matchAll(/\((?:\\.|[^\\)]){2,}\)\s*Tj/g);
  for (const match of literalMatches) pieces.push(decodePdfLiteral(match[0].replace(/\)\s*Tj$/, '').slice(1)));
  const arrayMatches = raw.matchAll(/\[((?:\s*\((?:\\.|[^\\)])+\)\s*)+)\]\s*TJ/g);
  for (const match of arrayMatches) {
    const inner = [...match[1].matchAll(/\((?:\\.|[^\\)])+\)/g)].map(item => decodePdfLiteral(item[0].slice(1, -1))).join('');
    pieces.push(inner);
  }
  const fallback = raw
    .replace(/[^\x09\x0A\x0D\x20-\x7E]/g, ' ')
    .replace(/\s+/g, ' ')
    .match(/[A-Z][A-Za-z .]{2,80}|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|(?:Python|Java|SQL|Machine Learning|B\.?Tech|University|Institute)[A-Za-z .,+#-]*/gi);
  return normalizeResumeText((pieces.join('\n') || '') + '\n' + (fallback || []).join('\n'));
}

function decodePdfLiteral(value) {
  return value
    .replace(/\\n/g, '\n')
    .replace(/\\r/g, '\n')
    .replace(/\\t/g, ' ')
    .replace(/\\([()\\])/g, '$1')
    .replace(/\\(\d{3})/g, (_, oct) => String.fromCharCode(parseInt(oct, 8)));
}

async function extractDocxText(buffer) {
  const bytes = new Uint8Array(buffer);
  const entries = [];
  for (let i = 0; i < bytes.length - 30; i++) {
    if (bytes[i] !== 0x50 || bytes[i+1] !== 0x4b || bytes[i+2] !== 0x03 || bytes[i+3] !== 0x04) continue;
    const method = readU16(bytes, i + 8);
    const compressedSize = readU32(bytes, i + 18);
    const uncompressedSize = readU32(bytes, i + 22);
    const nameLength = readU16(bytes, i + 26);
    const extraLength = readU16(bytes, i + 28);
    const filename = new TextDecoder().decode(bytes.slice(i + 30, i + 30 + nameLength));
    const dataStart = i + 30 + nameLength + extraLength;
    const dataEnd = dataStart + compressedSize;
    if (filename === 'word/document.xml') {
      let data = bytes.slice(dataStart, dataEnd);
      if (method === 8 && typeof DecompressionStream !== 'undefined') {
        try {
          const stream = new Blob([data]).stream().pipeThrough(new DecompressionStream('deflate-raw'));
          data = new Uint8Array(await new Response(stream).arrayBuffer());
        } catch (error) {
          return '';
        }
      }
      if (method === 0 || method === 8) {
        const xml = new TextDecoder('utf-8').decode(data.slice(0, uncompressedSize || data.length));
        return normalizeResumeText(xml.replace(/<w:tab\/>/g, ' ').replace(/<\/w:p>/g, '\n').replace(/<[^>]+>/g, ' '));
      }
    }
    entries.push(filename);
  }
  return '';
}

function readU16(bytes, offset) {
  return bytes[offset] | (bytes[offset + 1] << 8);
}

function readU32(bytes, offset) {
  return (bytes[offset] | (bytes[offset + 1] << 8) | (bytes[offset + 2] << 16) | (bytes[offset + 3] << 24)) >>> 0;
}

function normalizeResumeText(text) {
  return String(text || '')
    .replace(/\r/g, '\n')
    .replace(/[•●▪]/g, '\n')
    .replace(/[ \t]+/g, ' ')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function pickCandidateName(lines, text) {
  const labeled = text.match(/(?:candidate\s+name|full\s+name|name)\s*[:\-]\s*([A-Za-z][A-Za-z .'-]{1,60})/i);
  if (labeled && isMeaningfulDisplayName(labeled[1])) return cleanName(labeled[1]);
  const candidate = lines.slice(0, 5).find(line => {
    const clean = cleanName(line.replace(/\b(email|phone|mobile|linkedin|github)\b.*$/i, ''));
    const words = clean.split(/\s+/).filter(Boolean);
    if (!clean || clean.length > 48 || /\d|@|https?:\/\//i.test(line)) return false;
    if (isLikelySectionHeader(clean)) return false;
    return words.length >= 2 && words.length <= 4 && words.every(isLikelyNameToken);
  });
  return candidate ? cleanName(candidate) : '';
}

function cleanName(value) {
  return String(value || '').replace(/[^A-Za-z .'-]/g, ' ').replace(/\s+/g, ' ').trim();
}

function inferExperienceFromText(text, projects = []) {
  const normalized = String(text || '').replace(/[–—]/g, '-');
  const explicitYears = normalized.match(/(\d+(?:\.\d+)?)\+?\s*(?:years|yrs|year)\b/i);
  if (explicitYears) return Math.max(0, Math.min(20, Math.round(Number(explicitYears[1]))));
  const monthMap = { jan:0, feb:1, mar:2, apr:3, may:4, jun:5, jul:6, aug:7, sep:8, oct:9, nov:10, dec:11 };
  const currentYear = new Date().getFullYear();
  let months = 0;
  const rangePattern = /\b(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*)?(20\d{2}|19\d{2})\s*(?:-|to)\s*(?:(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*)?(present|current|20\d{2}|19\d{2})\b/gi;
  for (const match of normalized.matchAll(rangePattern)) {
    const startMonth = match[1] ? monthMap[match[1].toLowerCase().slice(0,3)] : 0;
    const startYear = Number(match[2]);
    const endYear = /present|current/i.test(match[4]) ? currentYear : Number(match[4]);
    const endMonth = /present|current/i.test(match[4]) ? new Date().getMonth() : (match[3] ? monthMap[match[3].toLowerCase().slice(0,3)] : 11);
    months += Math.max(1, (endYear - startYear) * 12 + (endMonth - startMonth));
  }
  if (months > 0) return Math.max(1, Math.min(15, Math.round(months / 12)));
  const internshipCount = (normalized.match(/\b(intern|internship|trainee|apprentice)\b/gi) || []).length;
  const workSignals = (normalized.match(/\b(experience|worked|developed|built|engineer|developer|analyst|project|freelance|company|startup)\b/gi) || []).length;
  const projectSignals = (String(projects.join(' ')).match(/\b(built|developed|designed|deployed|launched|implemented|led|created)\b/gi) || []).length;
  const dateMatches = [...normalized.matchAll(/\b(20\d{2}|19\d{2})\b/g)].map(match => Number(match[1]));
  if (dateMatches.length >= 2) {
    return Math.max(1, Math.min(12, Math.max(...dateMatches) - Math.min(...dateMatches)));
  }
  if (internshipCount >= 2 || workSignals >= 8 || projectSignals >= 3) return 2;
  if (internshipCount || workSignals >= 3 || projectSignals >= 1) return 1;
  return 0;
}

function inferRoleFromSkills(skills) {
  const set = new Set((skills || []).map(skill => skill.toLowerCase()));
  if (set.has('machine learning') || set.has('deep learning') || set.has('pytorch') || set.has('rag') || set.has('llms')) return 'AI/ML Engineer';
  if (set.has('sql') && (set.has('spark') || set.has('airflow') || set.has('etl'))) return 'Data Engineer';
  if (set.has('react') || set.has('javascript') || set.has('node.js') || set.has('typescript')) return 'Software Engineer';
  if (set.has('sql') || set.has('tableau') || set.has('power bi') || set.has('statistics')) return 'Data Analyst';
  if (set.has('java') || set.has('html') || set.has('css')) return 'Software Developer';
  return 'Candidate Profile';
}

function inferRoleFromResume(text, skills) {
  const lower = String(text || '').toLowerCase();
  const headline = String(text || '').split(/\n/).slice(0, 8).find(line => /\b(engineer|developer|analyst|scientist|designer|intern|consultant|manager)\b/i.test(line));
  if (headline) return cleanRole(headline);
  if (/\b(student|undergraduate|graduate)\b/.test(lower)) return 'Student / Intern Profile';
  if (lower.includes('data scientist')) return 'Data Scientist';
  if (lower.includes('machine learning') || lower.includes('artificial intelligence')) return 'AI/ML Engineer';
  if (lower.includes('frontend') || lower.includes('front end')) return 'Frontend Developer';
  if (lower.includes('backend') || lower.includes('back end')) return 'Backend Developer';
  if (lower.includes('full stack') || lower.includes('fullstack')) return 'Full Stack Developer';
  return inferRoleFromSkills(skills);
}

function cleanRole(value) {
  return String(value || '')
    .replace(/[^A-Za-z /&+-]/g, ' ')
    .replace(/\b(resume|curriculum|vitae|profile|summary|objective)\b/gi, '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 60) || 'Candidate Profile';
}

function extractSectionItems(text, labels) {
  const pattern = new RegExp(`(?:${labels})\\s*[:\\-]?\\s*([\\s\\S]{0,900}?)(?=\\n\\s*(?:education|skills|experience|certifications?|projects?|summary|objective|achievements?|contact)\\b|$)`, 'i');
  const match = text.match(pattern);
  if (!match) return [];
  return match[1]
    .split(/\n|;/)
    .map(item => normalizeTextValue(item.replace(/^[-*]\s*/, '')))
    .filter(item => item.length > 3 && !isLikelySectionHeader(item))
    .slice(0, 6);
}

function extractSkillsFromText(text) {
  return normalizeSkillList(text);
}

function extractProjectsFromText(text) {
  return extractSectionItems(text, 'projects?|project experience').map(item => item.replace(/\s{2,}/g, ' '));
}

function extractEducationDetails(text) {
  const degree = inferDegreeFromEducation(text);
  const college = inferCollegeFromText(text);
  const departmentMatch = text.match(/\b(Computer Science(?: and Engineering)?|Information Technology|Electronics(?: and Communication)?|Artificial Intelligence|Data Science|Mechanical Engineering|Electrical Engineering)\b/i);
  const gpaMatch = text.match(/\b(?:cgpa|gpa|percentage|score)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?(?:\/10(?:\.0+)?|%))/i);
  return {
    degree,
    college,
    department: departmentMatch ? normalizeTextValue(departmentMatch[1]) : '',
    gpa: gpaMatch ? normalizeTextValue(gpaMatch[1]) : '',
    education: formatEducation(degree, college, '')
  };
}

function generateCandidateIntelligence(candidate) {
  const skills = normalizeSkillList(candidate.skills || []);
  const hasContact = Boolean(candidate.email || candidate.phone || candidate.linkedin || candidate.github);
  const hasProjects = (candidate.projects || []).length > 0;
  const hasEducation = Boolean((candidate.degree || candidate.college || candidate.education) && !/uploaded/i.test(String(candidate.education || '')));
  const experience = Number(candidate.experience || 0);
  const technicalScore = Math.min(96, 50 + skills.length * 6 + (hasProjects ? 8 : 0));
  const experienceScore = Math.min(100, 48 + experience * 8 + (hasEducation ? 8 : 0));
  const authenticityScore = Math.min(96, 54 + (candidate.email ? 10 : 0) + (candidate.phone ? 8 : 0) + (candidate.linkedin ? 10 : 0) + (candidate.github ? 8 : 0) + (hasEducation ? 6 : 0));
  const behavioralScore = Math.min(92, 58 + (hasProjects ? 10 : 0) + (candidate.github ? 8 : 0) + skills.length * 2);
  const careerConsistency = Math.min(94, 58 + experience * 5 + Math.min(16, skills.length * 2));
  const learningVelocity = Math.min(95, 62 + skills.length * 3 + (hasProjects ? 8 : 0) + (candidate.github ? 6 : 0));
  const growthPotential = Math.min(96, 65 + skills.length * 3 + (experience <= 3 ? 8 : 0) + (hasProjects ? 8 : 0));
  const cognitiveTwinScore = Math.round(technicalScore * 0.3 + experienceScore * 0.18 + behavioralScore * 0.17 + authenticityScore * 0.18 + careerConsistency * 0.17);
  const finalScore = Math.round(technicalScore * 0.34 + experienceScore * 0.20 + behavioralScore * 0.20 + authenticityScore * 0.15 + careerConsistency * 0.11);
  const hiddenGem = growthPotential >= 84 && experience <= 4;
  const riskLevel = authenticityScore >= 78 ? 'Low' : authenticityScore >= 62 ? 'Medium' : 'High';
  const strengths = [
    skills.length ? `Extracted ${skills.length} resume skills: ${skills.slice(0, 5).join(', ')}` : 'Resume parsed from content',
    hasEducation ? `Education evidence found: ${candidate.education || [candidate.degree, candidate.college].filter(Boolean).join(' · ')}` : '',
    hasProjects ? 'Project evidence supports hands-on capability' : '',
    candidate.github ? 'GitHub signal available for technical validation' : ''
  ].filter(Boolean);
  const weaknesses = [
    !hasContact ? 'Add contact/profile links before final outreach' : '',
    !hasProjects ? 'Project details are light in the parsed resume' : '',
    !candidate.linkedin ? 'LinkedIn link was not present in resume content' : '',
    experience <= 0 ? 'Experience timeline is light and estimated conservatively' : ''
  ].filter(Boolean);
  return {
    finalScore,
    technicalScore,
    experienceScore,
    behavioralScore,
    authenticityScore,
    cognitiveTwinScore,
    careerConsistency,
    growthPotential,
    learningVelocity,
    technicalDepth: technicalScore,
    hiddenGem,
    riskLevel,
    strengths: strengths.length ? strengths : ['Resume parsed from content'],
    weaknesses: weaknesses.length ? weaknesses : ['No major extraction gaps detected'],
    authenticityRisk: `${riskLevel} authenticity risk based on extracted contact, education, profile links, and resume evidence density.`,
    recruiterReasoning: `${candidate.name} has ${skills.slice(0, 4).join(', ') || 'resume-based'} signals with ${experience} year${experience === 1 ? '' : 's'} of estimated experience and ${riskLevel.toLowerCase()} authenticity risk.`,
    whyRanked: `Profile generated from resume content: ${candidate.name}, ${candidate.education || [candidate.degree, candidate.college].filter(Boolean).join(' · ') || 'education evidence available'}, ${skills.slice(0, 6).join(', ') || 'resume skills parsed'}.`,
  };
}

async function importCandidateFile(file, onDone) {
  const reader = new FileReader();
  reader.onload = async () => {
    try {
      const buffer = reader.result;
      let candidate = await parseCandidateWithBackend(file);
      if (!candidate) {
        const text = await extractTextFromUpload(file, buffer);
        candidate = file.name.toLowerCase().endsWith('.json')
          ? parseCandidateJsonUpload(text)
          : { ...extractCandidateProfileFromText(text), resumeText: text };
      }
      if (!hasExtractedCandidateEvidence(candidate)) {
        throw new Error('Could not create a reliable candidate profile from the uploaded document.');
      }
      const result = addCandidateToDatabase(candidate);
      if (onDone) onDone(result);
    } catch (error) {
      if (onDone) onDone({ added: false, error: error.message || 'Unable to parse uploaded document.' });
    }
  };
  reader.readAsArrayBuffer(file);
}

function hasExtractedCandidateEvidence(candidate) {
  if (!candidate) return false;
  return Boolean(
    isMeaningfulDisplayName(candidate.name || candidate.candidate_name)
    || normalizeTextValue(candidate.education)
    || normalizeTextValue(candidate.college)
    || (candidate.skills || []).length
    || (candidate.projects || []).length
    || candidate.email
    || candidate.phone
  );
}

function parseCandidateJsonUpload(text) {
  const parsed = JSON.parse(text);
  const profile = parsed.profile && typeof parsed.profile === 'object' ? parsed.profile : parsed;
  const projects = normalizeTextList(parsed.projects || profile.projects || []);
  const educationLines = Array.isArray(parsed.education)
    ? parsed.education.map(item => stringifyEvidenceItem(item))
    : normalizeTextList(parsed.education || profile.education || []);
  const name = cleanName(profile.name || profile.full_name || parsed.candidate_name || parsed.name || '');
  const skills = normalizeSkillList(parsed.skills || profile.skills || []);
  const role = cleanRole(profile.headline || profile.role || inferRoleFromSkills(skills));
  const experience = Number(profile.years_experience || parsed.years_experience || profile.experience || parsed.experience || 0) || 0;
  const degree = normalizeTextValue(profile.degree || parsed.degree || '');
  const college = normalizeTextValue(profile.college || parsed.college || '');
  const education = formatEducation(degree, college, educationLines.join(' - '));
  const experienceSummary = experience > 0 ? `${experience} year${experience === 1 ? '' : 's'} experience` : buildExperienceSummary('', projects, experience, role, degree);
  const profileLabel = buildProfileLabel(role, degree, experienceSummary);
  const parsingConfidence = getParsingConfidence({
    name: isMeaningfulDisplayName(name) ? name : LOW_CONFIDENCE_LABEL,
    skills,
    projects,
    degree,
    college,
    education,
    email: profile.email || parsed.email || '',
    phone: profile.phone || parsed.phone || '',
    linkedin: profile.linkedin_url || profile.linkedin || parsed.linkedin || '',
    github: profile.github_url || profile.github || parsed.github || '',
    experience,
    experienceSummary,
    resumeText: normalizeResumeText(text)
  });
  return {
    candidate_id: `USER_${Date.now()}`,
    name: isMeaningfulDisplayName(name) ? name : LOW_CONFIDENCE_LABEL,
    candidate_name: isMeaningfulDisplayName(name) ? name : LOW_CONFIDENCE_LABEL,
    profileLabel,
    profile_label: profileLabel,
    role: profileLabel || role || 'Candidate Profile',
    degree,
    college,
    education,
    email: profile.email || parsed.email || '',
    phone: profile.phone || parsed.phone || '',
    linkedin: profile.linkedin_url || profile.linkedin || parsed.linkedin || '',
    github: profile.github_url || profile.github || parsed.github || '',
    experience,
    experienceSummary,
    skills,
    projects,
    certifications: normalizeTextList(parsed.certifications || profile.certifications || []),
    parsing_confidence: parsingConfidence,
    resumeText: normalizeResumeText(text),
    source: 'User Added'
  };
}

function extractCandidateProfileFromText(text) {
  const cleanedText = normalizeResumeText(text);
  const lines = cleanedText.split(/\r?\n/).map(line => line.trim()).filter(Boolean);
  const findLabel = label => {
    const match = cleanedText.match(new RegExp(`${label}\\s*[:\\-]\\s*(.+)`, 'i'));
    return match ? match[1].split(/\r?\n/)[0].trim() : '';
  };
  const name = pickCandidateName(lines, cleanedText);
  const email = (cleanedText.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i) || [''])[0];
  const phone = (cleanedText.match(/(?:\+?91[-\s]?)?[6-9]\d{9}/) || cleanedText.match(/(?:\+\d{1,3}[-\s]?)?(?:\d[-\s]?){8,14}\d/) || [''])[0].trim();
  const linkedin = (cleanedText.match(/(?:https?:\/\/)?(?:www\.)?linkedin\.com\/[^\s)]+/i) || [''])[0];
  const github = (cleanedText.match(/(?:https?:\/\/)?(?:www\.)?github\.com\/[^\s)]+/i) || [''])[0];
  const skills = extractSkillsFromText(findLabel('skills') || cleanedText);
  const projects = extractProjectsFromText(cleanedText);
  const experience = inferExperienceFromText(cleanedText, projects);
  const educationDetails = extractEducationDetails(cleanedText);
  const degree = findLabel('degree') || educationDetails.degree;
  const college = findLabel('college') || findLabel('university') || educationDetails.college;
  const education = formatEducation(degree, college, findLabel('education') || educationDetails.education);
  const certifications = extractSectionItems(cleanedText, 'certifications|certificates');
  const inferredRole = findLabel('role') || findLabel('headline') || inferRoleFromResume(cleanedText, skills);
  const experienceSummary = buildExperienceSummary(cleanedText, projects, experience, inferredRole, degree);
  const profileLabel = buildProfileLabel(inferredRole, degree, experienceSummary);
  const resolvedName = name || buildNameFromResumeIdentity(email, linkedin, github, lines);
  const parsingConfidence = getParsingConfidence({
    name: resolvedName,
    skills,
    projects,
    certifications,
    degree,
    college,
    education,
    email,
    phone,
    linkedin,
    github,
    experience,
    experienceSummary,
    resumeText: cleanedText
  });
  return {
    candidate_id: `USER_${Date.now()}`,
    name: resolvedName,
    candidate_name: resolvedName,
    profileLabel,
    profile_label: profileLabel,
    degree,
    email,
    phone,
    linkedin,
    github,
    role: profileLabel || inferredRole,
    experience,
    experienceSummary,
    skills,
    education: education || LOW_CONFIDENCE_LABEL,
    college,
    projects,
    certifications,
    parsing_confidence: parsingConfidence,
    resumeText: cleanedText
  };
}

function buildNameFromResumeIdentity(email, linkedin, github, lines) {
  const line = lines.slice(0, 5).find(item => {
    const clean = cleanName(item);
    const tokens = clean.split(/\s+/).filter(Boolean);
    return tokens.length >= 2 && tokens.length <= 4 && tokens.every(isLikelyNameToken);
  });
  return line ? toTitleCase(cleanName(line)) : LOW_CONFIDENCE_LABEL;
}

function inferCollegeFromText(text) {
  const lines = String(text || '').split(/\r?\n/).map(line => line.trim()).filter(Boolean);
  const labelled = lines.find(line => /(university|college|institute|school|iit|nit|iiit|bits|karunya)/i.test(line) && !isLikelySectionHeader(line));
  if (labelled) return cleanRole(labelled);
  const match = String(text || '').match(/(?:at|from|of)\s+([A-Z][A-Za-z&.,'() -]{2,80}(?:University|College|Institute|School|Campus)?)/);
  return match ? cleanRole(match[1]) : '';
}

function toTitleCase(value) {
  return String(value || '').toLowerCase().replace(/\b[a-z]/g, char => char.toUpperCase());
}

function buildFooter() {
  return `<footer class="footer"><div class="container">
    <p>© 2026 <a href="index.html">TalentLens AI</a><br/>India's Recruiter Cognitive Twin</p>
  </div></footer>`;
}

// ── CANVAS NETWORK BACKGROUND ───────────────────────────────────────────────
function initNetworkCanvas(canvasId = 'bgCanvas') {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, nodes = [], raf;

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', () => { resize(); init(); });

  function init() {
    nodes = [];
    const count = Math.floor(W * H / 18000);
    for (let i = 0; i < count; i++) {
      nodes.push({
        x: Math.random() * W, y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.4, vy: (Math.random() - 0.5) * 0.4,
        r: Math.random() * 2 + 1, pulse: Math.random() * Math.PI * 2
      });
    }
  }
  init();

  const COLORS = ['#8b5cf6','#6366f1','#3b82f6','#06b6d4'];

  function draw() {
    ctx.clearRect(0, 0, W, H);
    const t = Date.now() * 0.001;
    nodes.forEach((n, i) => {
      n.x += n.vx; n.y += n.vy;
      if (n.x < 0 || n.x > W) n.vx *= -1;
      if (n.y < 0 || n.y > H) n.vy *= -1;
      const alpha = 0.5 + 0.5 * Math.sin(t + n.pulse);
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fillStyle = COLORS[i % COLORS.length];
      ctx.globalAlpha = alpha;
      ctx.fill();
      ctx.globalAlpha = 1;
    });
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[i].x - nodes[j].x, dy = nodes[i].y - nodes[j].y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < 160) {
          ctx.beginPath();
          ctx.moveTo(nodes[i].x, nodes[i].y);
          ctx.lineTo(nodes[j].x, nodes[j].y);
          ctx.strokeStyle = '#6366f1';
          ctx.globalAlpha = (1 - dist/160) * 0.25;
          ctx.lineWidth = 0.8;
          ctx.stroke();
          ctx.globalAlpha = 1;
        }
      }
    }
    raf = requestAnimationFrame(draw);
  }
  draw();
}

