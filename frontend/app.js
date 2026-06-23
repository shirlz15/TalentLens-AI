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

function getCandidateDatabase() {
  const userAdded = JSON.parse(localStorage.getItem(TALENTLENS_DB_KEY) || '[]');
  return [
    ...CANDIDATES.map(c => ({ ...c, source: c.source || 'Built-In' })),
    ...userAdded.map(c => ({ ...c, source: 'User Added' }))
  ];
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
  const existing = JSON.parse(localStorage.getItem(TALENTLENS_DB_KEY) || '[]');
  const duplicate = getCandidateDatabase().find(item => {
    const sameName = item.name && candidate.name && getNameSimilarity(item.name, candidate.name) >= 0.86;
    const sameEmail = item.email && candidate.email && item.email.trim().toLowerCase() === candidate.email.trim().toLowerCase();
    const samePhone = item.phone && candidate.phone && item.phone.replace(/\D/g, '') === candidate.phone.replace(/\D/g, '');
    const sameLinkedin = item.linkedin && candidate.linkedin && normalizeUrl(item.linkedin) === normalizeUrl(candidate.linkedin);
    const sameGithub = item.github && candidate.github && normalizeUrl(item.github) === normalizeUrl(candidate.github);
    return sameName || sameEmail || samePhone || sameLinkedin || sameGithub;
  });
  if (duplicate) return { added: false, candidate: duplicate };
  const nextId = Math.max(100, ...getCandidateDatabase().map(c => Number(c.id) || 0)) + 1;
  const resumeText = candidate.resumeText || '';
  const generated = generateCandidateIntelligence(candidate);
  existing.push({
    id: nextId,
    initials: candidate.initials || candidate.name.split(/\s+/).map(part => part[0]).join('').slice(0, 2).toUpperCase(),
    name: candidate.name,
    candidate_name: candidate.name,
    email: candidate.email || '',
    phone: candidate.phone || '',
    linkedin: candidate.linkedin || '',
    github: candidate.github || '',
    role: candidate.role || inferRoleFromSkills(candidate.skills || []),
    company: candidate.company || candidate.college || 'Resume Profile',
    location: candidate.location || 'India',
    experience: Number(candidate.experience || 0),
    finalScore: Number(candidate.finalScore || generated.finalScore),
    technicalScore: Number(candidate.technicalScore || generated.technicalScore),
    experienceScore: Number(candidate.experienceScore || generated.experienceScore),
    behavioralScore: Number(candidate.behavioralScore || generated.behavioralScore),
    authenticityScore: Number(candidate.authenticityScore || generated.authenticityScore),
    cognitiveTwinScore: Number(candidate.cognitiveTwinScore || generated.cognitiveTwinScore),
    hiddenGem: Boolean(candidate.hiddenGem || generated.hiddenGem),
    riskLevel: candidate.riskLevel || generated.riskLevel,
    skills: candidate.skills || ['Python','SQL'],
    strengths: candidate.strengths || generated.strengths,
    weaknesses: candidate.weaknesses || generated.weaknesses,
    whyRanked: candidate.whyRanked || generated.whyRanked,
    recruiterReasoning: candidate.recruiterReasoning || generated.recruiterReasoning,
    authenticityRisk: candidate.authenticityRisk || generated.authenticityRisk,
    careerConsistency: Number(candidate.careerConsistency || generated.careerConsistency),
    growthPotential: Number(candidate.growthPotential || generated.growthPotential),
    learningVelocity: Number(candidate.learningVelocity || generated.learningVelocity),
    technicalDepth: Number(candidate.technicalDepth || generated.technicalDepth),
    education: candidate.education || candidate.college || 'Resume education profile',
    college: candidate.college || '',
    projects: candidate.projects || [],
    certifications: candidate.certifications || [],
    resumeText,
    gradient: candidate.gradient || 'linear-gradient(135deg,#06b6d4,#8b5cf6)',
    source: 'User Added',
    source_code: 'USER_ADDED'
  });
  localStorage.setItem(TALENTLENS_DB_KEY, JSON.stringify(existing));
  return { added: true, candidate: existing[existing.length - 1] };
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

async function extractTextFromUpload(file, buffer) {
  const name = file.name.toLowerCase();
  if (name.endsWith('.json')) return new TextDecoder('utf-8').decode(buffer);
  if (name.endsWith('.docx')) {
    const docxText = await extractDocxText(buffer);
    if (docxText.trim()) return docxText;
  }
  if (name.endsWith('.pdf')) {
    const pdfText = extractPdfText(buffer);
    if (pdfText.trim()) return pdfText;
  }
  return new TextDecoder('utf-8', { fatal: false }).decode(buffer);
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
  if (labeled) return cleanName(labeled[1]);
  const blocked = /(resume|curriculum|vitae|email|phone|mobile|linkedin|github|education|skills|project|experience|certification|profile|summary|objective|developer|engineer|intern|student)/i;
  const candidate = lines.slice(0, 12).find(line => {
    const clean = cleanName(line);
    const words = clean.split(/\s+/).filter(Boolean);
    return words.length >= 2 && words.length <= 4 && clean.length <= 50 && /^[A-Za-z .'-]+$/.test(clean) && !blocked.test(clean);
  });
  return candidate ? cleanName(candidate) : '';
}

function cleanName(value) {
  return String(value || '').replace(/[^A-Za-z .'-]/g, ' ').replace(/\s+/g, ' ').trim();
}

function inferExperienceFromText(text) {
  const normalized = String(text || '').replace(/[–—]/g, '-');
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
  const dateMatches = [...normalized.matchAll(/\b(20\d{2}|19\d{2})\b/g)].map(match => Number(match[1]));
  if (dateMatches.length >= 2) {
    return Math.max(1, Math.min(12, Math.max(...dateMatches) - Math.min(...dateMatches)));
  }
  if (internshipCount >= 2 || workSignals >= 8) return 2;
  if (internshipCount || workSignals >= 3) return 1;
  return 1;
}

function inferRoleFromSkills(skills) {
  const set = new Set((skills || []).map(skill => skill.toLowerCase()));
  if (set.has('machine learning') || set.has('deep learning') || set.has('pytorch') || set.has('rag') || set.has('llms')) return 'AI/ML Engineer';
  if (set.has('react') || set.has('javascript') || set.has('node.js') || set.has('typescript')) return 'Software Engineer';
  if (set.has('sql') || set.has('tableau') || set.has('power bi') || set.has('statistics')) return 'Data Analyst';
  if (set.has('java') || set.has('html') || set.has('css')) return 'Software Developer';
  return 'Resume-Based Talent Profile';
}

function inferRoleFromResume(text, skills) {
  const lower = String(text || '').toLowerCase();
  const headline = String(text || '').split(/\n/).slice(0, 8).find(line => /\b(engineer|developer|analyst|scientist|designer|intern|consultant|manager)\b/i.test(line));
  if (headline) return cleanRole(headline);
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
    .slice(0, 60) || 'Resume-Based Talent Profile';
}

function extractSectionItems(text, labels) {
  const pattern = new RegExp(`(?:${labels})\\s*[:\\-]?\\s*([\\s\\S]{0,500}?)(?=\\n\\s*(?:education|skills|experience|certifications?|projects?|summary|objective|$))`, 'i');
  const match = text.match(pattern);
  if (!match) return [];
  return match[1].split(/\n|;/).map(item => item.replace(/^[-*]\s*/, '').trim()).filter(item => item.length > 8).slice(0, 4);
}

function generateCandidateIntelligence(candidate) {
  const skills = candidate.skills || [];
  const hasContact = Boolean(candidate.email || candidate.phone || candidate.linkedin || candidate.github);
  const hasProjects = (candidate.projects || []).length > 0;
  const hasEducation = Boolean(candidate.education && !/uploaded/i.test(candidate.education));
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
    skills.length ? `Extracted ${skills.length} resume skills: ${skills.slice(0, 5).join(', ')}` : 'Resume Parsed Successfully',
    hasEducation ? `Education evidence found: ${candidate.education}` : '',
    hasProjects ? 'Project evidence supports hands-on capability' : '',
    candidate.github ? 'GitHub signal available for technical validation' : ''
  ].filter(Boolean);
  const weaknesses = [
    !hasContact ? 'Add contact/profile links before final outreach' : '',
    !hasProjects ? 'Project details are light in the parsed resume' : '',
    !candidate.linkedin ? 'LinkedIn link was not present in resume content' : '',
    experience === 0 ? 'Experience timeline is light and estimated conservatively' : ''
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
    strengths: strengths.length ? strengths : ['Resume Parsed Successfully'],
    weaknesses: weaknesses.length ? weaknesses : ['No major extraction gaps detected'],
    authenticityRisk: `Resume Parsed Successfully. ${riskLevel} authenticity risk based on extracted contact, education, profile links, and resume evidence density.`,
    recruiterReasoning: `${candidate.name} has ${skills.slice(0, 4).join(', ') || 'resume-based'} signals with ${experience} year${experience === 1 ? '' : 's'} of estimated experience and ${riskLevel.toLowerCase()} authenticity risk.`,
    whyRanked: `Profile Generated From Resume: ${candidate.name}, ${candidate.education || candidate.college || 'education profile available'}, ${skills.slice(0, 6).join(', ') || 'resume skills parsed'}.`,
  };
}

async function importCandidateFile(file, onDone) {
  const reader = new FileReader();
  reader.onload = async () => {
    const buffer = reader.result;
    const text = await extractTextFromUpload(file, buffer);
    let candidate;
    if (file.name.toLowerCase().endsWith('.json')) {
      const parsed = JSON.parse(text);
      const profile = parsed.profile || parsed;
      candidate = {
        name: profile.name || profile.full_name || parsed.candidate_name || parsed.name || 'Resume Profile',
        role: profile.headline || profile.role || inferRoleFromSkills(parsed.skills || profile.skills || []),
        email: profile.email || parsed.email || '',
        phone: profile.phone || parsed.phone || '',
        linkedin: profile.linkedin_url || parsed.linkedin || '',
        github: profile.github_url || parsed.github || '',
        experience: profile.years_experience || parsed.years_experience || 0,
        skills: parsed.skills || profile.skills || ['Python','SQL'],
        education: Array.isArray(parsed.education) ? parsed.education.map(e => e.degree || e.school || JSON.stringify(e)).join(', ') : (parsed.education || profile.education || profile.college || 'Resume education profile'),
        college: profile.college || parsed.college || '',
        projects: parsed.projects || [],
        certifications: parsed.certifications || [],
        resumeText: text
      };
    } else {
      candidate = {
        ...extractCandidateProfileFromText(text),
        resumeText: text
      };
    }
    const result = addCandidateToDatabase(candidate);
    if (onDone) onDone(result);
  };
  reader.readAsArrayBuffer(file);
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
  const skillsText = findLabel('skills') || cleanedText;
  const knownSkills = ['Python','SQL','Machine Learning','Deep Learning','PyTorch','TensorFlow','LLMs','RAG','LangChain','Vector DBs','MLOps','Kubernetes','Spark','Airflow','React','FastAPI','Docker','NLP','Tableau','Power BI','Git','AWS','GCP','Java','JavaScript','TypeScript','Node.js','Excel','Statistics','Pandas','NumPy','Scikit-learn','HTML','CSS','MongoDB','MySQL','PostgreSQL'];
  const skills = knownSkills.filter(skill => skillsText.toLowerCase().includes(skill.toLowerCase()) || (skill === 'LLMs' && skillsText.toLowerCase().includes('llm')));
  const experience = Number((cleanedText.match(/(\d+(?:\.\d+)?)\+?\s*(?:years|yrs|year)/i) || [0, 0])[1]) || inferExperienceFromText(cleanedText);
  const education = findLabel('education') || (cleanedText.match(/(B\.?\s?Tech|M\.?\s?Tech|MBA|BSc|MSc|PhD|Bachelor|Master|Computer Science|Information Technology)[^\n]*/i) || ['Education extracted from uploaded resume'])[0];
  const college = findLabel('college') || findLabel('university') || (cleanedText.match(/(?:IIT|NIT|IIIT|University|Institute|College|Karunya)[^\n]*/i) || [''])[0];
  const projects = extractSectionItems(cleanedText, 'projects');
  const certifications = extractSectionItems(cleanedText, 'certifications|certificates');
  return {
    name: name || buildNameFromResumeIdentity(email, linkedin, github, lines),
    candidate_name: name || buildNameFromResumeIdentity(email, linkedin, github, lines),
    email,
    phone,
    linkedin,
    github,
    role: findLabel('role') || findLabel('headline') || inferRoleFromResume(cleanedText, skills),
    experience,
    skills: skills.length ? skills : ['Python','SQL'],
    education,
    college,
    projects,
    certifications,
    resumeText: cleanedText
  };
}

function buildNameFromResumeIdentity(email, linkedin, github, lines) {
  const fromEmail = email ? cleanName(email.split('@')[0].replace(/[._-]+/g, ' ')) : '';
  if (fromEmail && fromEmail.split(/\s+/).length >= 2) return toTitleCase(fromEmail);
  const fromProfile = linkedin || github;
  if (fromProfile) {
    const handle = fromProfile.split('/').filter(Boolean).pop() || '';
    const clean = cleanName(handle.replace(/[._-]+/g, ' '));
    if (clean) return toTitleCase(clean);
  }
  const line = lines.find(item => cleanName(item).split(/\s+/).length >= 2 && !/(resume|education|skills|project|experience|certification|email|phone|linkedin|github)/i.test(item));
  return line ? toTitleCase(cleanName(line)) : 'Resume Parsed Successfully';
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
