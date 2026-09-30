"""
offline_analyzer.py
A free, rule-based resume analyzer that needs NO API key.

It uses keyword matching + heuristics (regex-based) instead of an LLM to produce
the same result shape as analyzer.analyze_resume(), so app.py can render either
one identically.
"""

import re
from collections import Counter

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

SKILL_KEYWORDS = [
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql",
    # Web / frameworks
    "react", "angular", "vue", "node.js", "nodejs", "express", "django", "flask",
    "fastapi", "spring", "spring boot", ".net", "next.js", "html", "css",
    "tailwind", "bootstrap",
    # Data / ML
    "machine learning", "deep learning", "nlp", "computer vision", "pandas",
    "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "data analysis",
    "data science", "statistics", "power bi", "tableau", "excel",
    # Cloud / DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
    "ci/cd", "jenkins", "git", "github", "gitlab", "linux", "bash",
    # Databases
    "mysql", "postgresql", "mongodb", "redis", "oracle", "sqlite", "firebase",
    "dynamodb",
    # Project / soft skills
    "agile", "scrum", "jira", "project management", "leadership",
    "communication", "teamwork", "problem solving", "critical thinking",
    "stakeholder management", "cross-functional",
    # Other common
    "rest api", "graphql", "microservices", "testing", "unit testing",
    "system design", "api", "product management", "ui/ux", "figma",
]

SECTION_PATTERNS = {
    "contact_info": r"[\w\.-]+@[\w\.-]+\.\w+",  # email
    "phone": r"(\+?\d[\d\-\s\(\)]{7,}\d)",
    "education": r"\b(education|bachelor|master|b\.?tech|m\.?tech|university|college|degree|b\.?sc|m\.?sc)\b",
    "experience": r"\b(experience|work history|employment|professional experience)\b",
    "skills_section": r"\b(skills|technical skills|core competencies)\b",
    "summary": r"\b(summary|objective|profile|about me)\b",
    "projects": r"\b(projects?|portfolio)\b",
    "certifications": r"\b(certifications?|certified|certificate)\b",
}

ACTION_VERBS = [
    "led", "built", "developed", "designed", "implemented", "managed",
    "created", "improved", "increased", "reduced", "launched", "optimized",
    "architected", "delivered", "drove", "spearheaded", "automated",
    "collaborated", "achieved", "streamlined", "mentored", "executed",
]

SENIOR_WORDS = ["senior", "lead", "principal", "staff", "head of", "director", "manager"]
ENTRY_WORDS = ["intern", "junior", "entry level", "graduate", "trainee"]


def _find_keywords(text: str, keywords: list) -> list:
    """Return which keywords from `keywords` appear in `text` (case-insensitive, word-boundary safe)."""
    text_lower = text.lower()
    found = []
    for kw in keywords:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(kw.lower()) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.append(kw)
    return found


def _count_bullets(text: str) -> int:
    return len(re.findall(r"(?m)^\s*[-•*▪●]\s+", text))


def _count_numbers(text: str) -> int:
    """Rough proxy for quantifiable achievements (%, $, or standalone numbers)."""
    return len(re.findall(r"\b\d+(\.\d+)?\s*(%|percent|\+|x)\b|\$\s?\d+", text.lower()))


def _estimate_experience_level(text: str) -> str:
    text_lower = text.lower()
    years_match = re.findall(r"(\d+)\+?\s*years?", text_lower)
    max_years = max((int(y) for y in years_match), default=0)

    if any(w in text_lower for w in SENIOR_WORDS) or max_years >= 7:
        return "Senior"
    if max_years >= 3:
        return "Mid-level"
    if any(w in text_lower for w in ENTRY_WORDS) or max_years < 2:
        return "Entry-level"
    return "Mid-level"


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def analyze_resume_offline(resume_text: str, job_description: str = "") -> dict:
    """
    Free, offline, keyword/heuristic-based resume analysis.
    Returns the same dict shape as analyzer.analyze_resume() so the UI
    can render either interchangeably.
    """
    resume_skills = _find_keywords(resume_text, SKILL_KEYWORDS)

    strengths = []
    weaknesses = []
    suggestions = []

    # --- Section / structure checks (drive ATS score) ---------------------
    ats_points = 0
    ats_max = 0

    for label, pattern in SECTION_PATTERNS.items():
        ats_max += 1
        if re.search(pattern, resume_text, re.IGNORECASE):
            ats_points += 1
        else:
            if label == "contact_info":
                weaknesses.append("No email address detected — make sure contact info is in plain text, not an image.")
                suggestions.append("Add a clear email address near the top of the resume.")
            elif label == "skills_section":
                weaknesses.append("No dedicated 'Skills' section detected.")
                suggestions.append("Add a 'Skills' section listing your key technical and soft skills.")
            elif label == "experience":
                weaknesses.append("No clear 'Experience' section header detected.")
            elif label == "education":
                weaknesses.append("No clear 'Education' section detected.")

    bullet_count = _count_bullets(resume_text)
    ats_max += 1
    if bullet_count >= 4:
        ats_points += 1
        strengths.append(f"Uses bullet points ({bullet_count} found) — good for ATS parsing and readability.")
    else:
        suggestions.append("Use bullet points (•) for experience entries instead of paragraphs — ATS systems parse these more reliably.")

    action_verbs_found = _find_keywords(resume_text, ACTION_VERBS)
    ats_max += 1
    if len(action_verbs_found) >= 3:
        ats_points += 1
        strengths.append(f"Uses strong action verbs (e.g. {', '.join(action_verbs_found[:5])}).")
    else:
        suggestions.append("Start bullet points with strong action verbs like 'Led', 'Built', 'Improved', or 'Automated' instead of passive phrasing.")

    quant_count = _count_numbers(resume_text)
    ats_max += 1
    if quant_count >= 2:
        ats_points += 1
        strengths.append("Includes quantifiable achievements (numbers/percentages) — this strengthens impact.")
    else:
        weaknesses.append("Few or no quantifiable achievements found (e.g. '%', '$', metrics).")
        suggestions.append("Quantify achievements where possible, e.g. 'Reduced load time by 30%' instead of 'Improved performance'.")

    word_count = _word_count(resume_text)
    ats_max += 1
    if 300 <= word_count <= 900:
        ats_points += 1
        strengths.append(f"Resume length looks appropriate (~{word_count} words).")
    elif word_count < 300:
        weaknesses.append(f"Resume seems short (~{word_count} words) — may be missing detail.")
        suggestions.append("Expand on your experience with more specific accomplishments and responsibilities.")
    else:
        weaknesses.append(f"Resume seems long (~{word_count} words) — consider trimming to 1-2 pages.")
        suggestions.append("Tighten the resume to the most relevant, recent, and impactful experience (aim for 1-2 pages).")

    ats_score = round((ats_points / ats_max) * 100) if ats_max else 0

    # --- Skill / JD matching -----------------------------------------------
    if job_description and job_description.strip():
        jd_skills = _find_keywords(job_description, SKILL_KEYWORDS)
        matched_skills = sorted(set(resume_skills) & set(jd_skills))
        missing_skills = sorted(set(jd_skills) - set(resume_skills))

        match_ratio = (len(matched_skills) / len(jd_skills)) if jd_skills else 0.5
        overall_score = round(0.7 * (match_ratio * 100) + 0.3 * ats_score)

        summary = (
            f"Found {len(matched_skills)} of {len(jd_skills)} keyword skills from the job "
            f"description present in the resume. This is a keyword/heuristic-based check, "
            f"not a full semantic match, so use it as a rough signal alongside your own judgment."
        )
        top_priority_fix = (
            f"Add these missing keywords if genuinely applicable: {', '.join(missing_skills[:5])}."
            if missing_skills else
            "Good keyword coverage — focus on strengthening quantifiable achievements instead."
        )
        keyword_suggestions = missing_skills[:10]

    else:
        matched_skills = resume_skills
        # Generic "commonly expected" skills not found, just as a nudge
        common_expected = ["communication", "teamwork", "problem solving", "leadership", "git"]
        missing_skills = [s for s in common_expected if s not in resume_skills]

        overall_score = ats_score
        summary = (
            f"Detected {len(resume_skills)} recognizable skill keywords in the resume. "
            f"This is a general structural/keyword scan, not a semantic quality review — "
            f"treat it as a first pass."
        )
        top_priority_fix = suggestions[0] if suggestions else "Resume structure looks solid overall."
        keyword_suggestions = missing_skills

    if not strengths:
        strengths.append("Resume was successfully parsed and contains readable text content.")
    if not suggestions:
        suggestions.append("No major structural issues detected by the keyword scan.")

    result = {
        "overall_match_score": max(0, min(100, overall_score)),
        "ats_score": max(0, min(100, ats_score)),
        "summary": summary,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "strengths": strengths[:6],
        "weaknesses": weaknesses[:6] if weaknesses else ["No major issues detected by the keyword scan."],
        "suggestions": suggestions[:6],
        "keyword_suggestions": keyword_suggestions[:10],
        "estimated_experience_level": _estimate_experience_level(resume_text),
        "top_priority_fix": top_priority_fix,
    }
    return result
