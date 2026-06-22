# TalentLens Ranking Evaluation Report

Generated from `output/results.csv` using the sample Senior Data Scientist job description and `data/sample_candidates.json`.

## Executive Summary

The ranking engine selected Asha Rao (`TL-001`) as the top candidate because she combines strong direct technical fit, senior-level experience, strong career consistency, strong behavioral signals, low authenticity risk, and the full skill-cluster bonus.

The top three candidates are all low-risk profiles with full experience credit and full skill-cluster bonus. The final ordering is therefore mainly decided by technical fit and behavioral signal strength.

| Rank | Candidate | Headline | Final Score | Risk |
|---:|---|---|---:|---|
| 1 | Asha Rao (`TL-001`) | Senior Data Scientist | 96.34 | LOW |
| 2 | Nisha Iyer (`TL-003`) | Analytics Lead | 90.72 | LOW |
| 3 | Ishan Verma (`TL-011`) | Cloud Data Scientist | 88.28 | LOW |

## 1. Why Candidate #1 Ranked Above #2

Candidate #1, Asha Rao, ranked above candidate #2, Nisha Iyer, by **5.62 points**.

| Dimension | Asha Rao | Nisha Iyer | Difference | Weighted Impact |
|---|---:|---:|---:|---:|
| Technical fit | 76.50 | 61.50 | +15.00 | +5.10 |
| Experience | 100.00 | 100.00 | 0.00 | 0.00 |
| Career consistency | 93.81 | 92.57 | +1.24 | +0.14 |
| Skill cluster bonus | 8.00 | 8.00 | 0.00 | 0.00 |
| Behavioral | 85.06 | 83.16 | +1.90 | +0.38 |
| Authenticity | 100.00 | 100.00 | 0.00 | 0.00 |

The deciding factor is **technical fit**. Asha matched Python, SQL, machine learning, statistics, and data analysis, while Nisha missed Python and machine learning. Both candidates received full experience credit, full authenticity credit, low risk, and the same skill-cluster bonus.

Asha's profile is closer to the target Senior Data Scientist role because her career history explicitly includes senior data science, Python, machine learning, statistics, and ranking models. Nisha is very strong, but her profile is more analytics and BI-oriented.

## 2. Why Candidate #2 Ranked Above #3

Candidate #2, Nisha Iyer, ranked above candidate #3, Ishan Verma, by **2.44 points**.

| Dimension | Nisha Iyer | Ishan Verma | Difference | Weighted Impact |
|---|---:|---:|---:|---:|
| Technical fit | 61.50 | 61.50 | 0.00 | 0.00 |
| Experience | 100.00 | 100.00 | 0.00 | 0.00 |
| Career consistency | 92.57 | 90.78 | +1.79 | +0.20 |
| Skill cluster bonus | 8.00 | 8.00 | 0.00 | 0.00 |
| Behavioral | 83.16 | 72.60 | +10.56 | +2.11 |
| Authenticity | 100.00 | 99.08 | +0.92 | +0.14 |

The deciding factor is **behavioral signal strength**. Both candidates have the same technical score, full experience score, and full skill-cluster bonus. Nisha ranks higher because her recruiter response rate, interview completion rate, recruiter saves, search visibility, and completeness signals are stronger overall.

Ishan is more directly aligned to AI/ML and cloud data science, but he loses ground on behavioral strength and has slightly lower authenticity scoring.

## 3. Score Dimensions That Contribute Most

The engine uses these default weighted dimensions:

| Dimension | Weight / Role |
|---|---:|
| Technical fit | 34% |
| Experience | 20% |
| Behavioral signals | 20% |
| Authenticity | 15% |
| Career consistency | 11% |
| Skill cluster bonus | Additive bonus up to 8 points |

For the top three candidates, the largest score contributors are:

| Candidate | Technical Contribution | Experience | Behavioral | Authenticity | Career | Cluster Bonus |
|---|---:|---:|---:|---:|---:|---:|
| Asha Rao | 26.01 | 20.00 | 17.01 | 15.00 | 10.32 | 8.00 |
| Nisha Iyer | 20.91 | 20.00 | 16.63 | 15.00 | 10.18 | 8.00 |
| Ishan Verma | 20.91 | 20.00 | 14.52 | 14.86 | 9.99 | 8.00 |

Because the top three all maxed experience and cluster bonus, the practical differentiators were:

1. Technical fit
2. Behavioral score
3. Career consistency
4. Authenticity, only when candidates are close

## 4. Feature Importance Summary

**Technical fit is the strongest ranking driver.** It has the highest weight and directly decides the #1 vs #2 gap. Missing Python and machine learning materially lowered Nisha's score for a Senior Data Scientist role.

**Behavioral signals are the second strongest differentiator.** They explain most of the #2 vs #3 ranking. Nisha's stronger recruiter engagement and platform activity outweighed Ishan's slightly stronger target-role alignment.

**Experience creates a qualification floor.** All top three candidates scored 100 on experience, so it did not separate them. It still matters because candidates below the 5-year requirement would be penalized.

**Career consistency supports trust and tie-breaking.** Asha and Ishan show stronger direct data science alignment, while Nisha shows strong analytics progression. Career consistency had smaller weight but improves recruiter confidence.

**Authenticity protects ranking quality.** All top three candidates were LOW risk, so authenticity did not heavily reorder them. It remains important for flagging profiles with weak verification, unsupported skill claims, or sparse evidence.

**Skill clusters reward coherent ecosystems.** All top three received the full 8-point bonus, showing strong skill ecosystems. Asha and Ishan earned AI/ML cluster evidence; Nisha earned analytics and data-oriented cluster evidence.

## 5. Recruiter-Facing Explanation Report

### Rank 1: Asha Rao (`TL-001`)

Asha is the strongest overall fit for the Senior Data Scientist role. She matches five of six required skills, including Python, SQL, machine learning, statistics, and data analysis. Her six years of experience meets the senior requirement, and her career path from Data Analyst to Senior Data Scientist is coherent and aligned with the target role.

Strengths:
- Strong technical match for the JD
- Senior-level experience
- Clear data science career progression
- Strong AI/ML skill cluster
- Strong behavioral and verification signals

Concerns:
- Missing communication as an explicitly matched required skill
- Profile text appears sparse or generic

Recruiter note: Best first shortlist candidate. Strong role alignment and low authenticity risk.

### Rank 2: Nisha Iyer (`TL-003`)

Nisha is a strong analytics leader with excellent experience, strong behavioral signals, and low authenticity risk. She ranks below Asha because she misses Python and machine learning, which are central to the Senior Data Scientist JD.

Strengths:
- Eight years of experience
- Strong analytics progression
- Excellent recruiter engagement and profile completeness
- Strong analytics skill cluster
- Low authenticity risk

Concerns:
- Missing Python
- Missing machine learning
- Profile text appears sparse or generic

Recruiter note: Strong candidate for analytics-heavy data science or BI leadership roles. For a machine-learning-heavy Senior Data Scientist role, validate hands-on ML depth.

### Rank 3: Ishan Verma (`TL-011`)

Ishan is a strong cloud data scientist with good AI/ML alignment. He matches Python, SQL, machine learning, and statistics, and his career path aligns well with the target role. He ranks below Nisha mostly because his behavioral score is lower.

Strengths:
- Strong AI/ML and cloud-adjacent profile
- Meets the 5-year experience requirement
- Career history aligns with data science work
- Low authenticity risk
- Full skill-cluster bonus

Concerns:
- Missing data analysis as an explicitly matched required skill
- Missing communication as an explicitly matched required skill
- Profile text appears sparse or generic

Recruiter note: Strong technical shortlist candidate. Worth interviewing if the role values ML/cloud depth more than platform engagement signals.

## Overall Recommendation

Shortlist Asha Rao first. Keep Nisha Iyer as a strong analytics-oriented backup and Ishan Verma as a strong ML/cloud-oriented backup. If the hiring manager prioritizes hands-on machine learning depth, Ishan may deserve closer review against Nisha despite ranking third. If stakeholder analytics and recruiter engagement matter more, Nisha's #2 position is well supported.

## 6. Recruiter Decision, Confidence, and Executive Summary

The demo-ready recruiter decision layer converts ranking evidence into four action buckets: Shortlist, Strong Consideration, Hold, and Reject. Hiring confidence is scored from evidence quality, profile completeness, career consistency, behavioral strength, and authenticity strength.

| Rank | Candidate | Decision | Hiring Confidence | Level |
|---:|---|---|---:|---|
| 1 | TL-001 | Shortlist | 95.20 | High |
| 2 | TL-003 | Shortlist | 95.03 | High |
| 3 | TL-011 | Shortlist | 91.62 | High |
| 4 | TL-002 | Strong Consideration | 91.03 | High |
| 5 | TL-010 | Strong Consideration | 89.95 | High |
| 6 | TL-004 | Strong Consideration | 88.79 | High |
| 7 | TL-006 | Hold | 75.59 | Medium |
| 8 | TL-007 | Hold | 79.21 | Medium |
| 9 | TL-008 | Hold | 77.29 | Medium |
| 10 | TL-005 | Hold | 74.26 | Medium |

### Executive Recruiter Summaries

**TL-001:** Strong technically aligned candidate with a 96.34 final score, 100 experience score, 94 career consistency, and LOW authenticity risk. Recommended decision: Shortlist based on matched 5 of 6 required skills and strong Redrob behavioral signals with high engagement and recruiter confidence. Primary concern: Missing required skill: communication.

**TL-003:** Strong career-consistent candidate with a 90.72 final score, 100 experience score, 93 career consistency, and LOW authenticity risk. Recommended decision: Shortlist based on matched 4 of 6 required skills and strong Redrob behavioral signals with high engagement and recruiter confidence. Primary concern: Missing required skill: python.

**TL-011:** Strong career-consistent candidate with an 88.28 final score, 100 experience score, 91 career consistency, and LOW authenticity risk. Recommended decision: Shortlist based on matched 4 of 6 required skills and healthy Redrob behavioral signals with some areas that can be stronger. Primary concern: Missing required skill: data analysis.

**Strong Consideration Note:** TL-002, TL-010, and TL-004 do not cross the immediate shortlist threshold, but their high confidence scores and strong experience profiles make them credible backup or role-adjacent candidates.

**TL-007 Hidden Gem Note:** TL-007 remains a Hold for this senior role because core JD gaps remain, but the hidden-gem layer flags upside from project quality, AI/NLP skills, and GitHub activity. This is useful for judging because it shows TalentLens can distinguish immediate hiring decisions from longer-term high-growth talent discovery.
