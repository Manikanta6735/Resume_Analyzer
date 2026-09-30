"""
analyzer.py
Sends resume (and optionally a job description) to the Claude API
and returns a structured analysis as a Python dict.
"""

import json
import os
import re

MODEL_NAME = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are an expert technical recruiter and resume coach with 15 years \
of experience across tech, finance, and general industries. You give precise, honest, \
actionable feedback. You always respond with ONLY valid JSON, no markdown fences, no \
commentary before or after the JSON.
"""

# Prompt used when the user supplies both a resume and a target job description
JD_MATCH_PROMPT_TEMPLATE = """Analyze the following resume against the given job description.

RESUME:
---
{resume_text}
---

JOB DESCRIPTION:
---
{job_description}
---

Return ONLY a JSON object with exactly this structure (no extra keys, no markdown):

{{
  "overall_match_score": <integer 0-100, how well the resume matches this specific job>,
  "ats_score": <integer 0-100, how well the resume would parse/score in an Applicant Tracking System>,
  "summary": "<2-3 sentence overall assessment>",
  "matched_skills": ["<skill from JD that IS present in resume>", ...],
  "missing_skills": ["<important skill/requirement from JD that is MISSING from resume>", ...],
  "strengths": ["<specific strength of this resume for this role>", ...],
  "weaknesses": ["<specific weakness or gap for this role>", ...],
  "suggestions": ["<concrete, actionable improvement, e.g. rewrite of a bullet point>", ...],
  "keyword_suggestions": ["<important keyword/phrase from JD to add to the resume>", ...],
  "estimated_experience_level": "<Entry-level|Mid-level|Senior|Lead/Principal>",
  "top_priority_fix": "<the single most impactful change the candidate should make>"
}}

Be specific and reference actual content from the resume and job description. \
Aim for 3-6 items in each list where applicable.
"""

# Prompt used when the user only supplies a resume (no target job description)
GENERAL_PROMPT_TEMPLATE = """Analyze the following resume in general (no specific job description was provided).

RESUME:
---
{resume_text}
---

Return ONLY a JSON object with exactly this structure (no extra keys, no markdown):

{{
  "overall_match_score": <integer 0-100, general resume quality/strength score>,
  "ats_score": <integer 0-100, how well this resume would parse/score in an Applicant Tracking System>,
  "summary": "<2-3 sentence overall assessment>",
  "matched_skills": ["<key skill clearly demonstrated in the resume>", ...],
  "missing_skills": ["<common skill/section that seems to be missing or underdeveloped>", ...],
  "strengths": ["<specific strength of this resume>", ...],
  "weaknesses": ["<specific weakness, e.g. vague bullet points, no metrics>", ...],
  "suggestions": ["<concrete, actionable improvement>", ...],
  "keyword_suggestions": ["<industry-standard keyword this resume could benefit from>", ...],
  "estimated_experience_level": "<Entry-level|Mid-level|Senior|Lead/Principal>",
  "top_priority_fix": "<the single most impactful change the candidate should make>"
}}

Be specific and reference actual content from the resume. \
Aim for 3-6 items in each list where applicable.
"""


def _extract_json(raw_text: str) -> dict:
    """
    Robustly extract a JSON object from the model's response,
    in case it wraps it in markdown fences despite instructions.
    """
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned.strip())
    cleaned = re.sub(r"```$", "", cleaned.strip())
    cleaned = cleaned.strip()

    # Fallback: grab the first {...} block if there's stray text around it
    if not cleaned.startswith("{"):
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)

    return json.loads(cleaned)


def analyze_resume(resume_text: str, job_description: str = "", api_key: str = None) -> dict:
    """
    Calls the Claude API to analyze a resume, optionally against a job description.

    Args:
        resume_text: Extracted plain text of the resume.
        job_description: Optional job description text to match against.
        api_key: Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.

    Returns:
        A dict matching the schema described in the prompt templates above.

    Raises:
        RuntimeError if the API call fails or the response can't be parsed.
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError(
            "No Anthropic API key found. Set the ANTHROPIC_API_KEY environment "
            "variable or enter a key in the sidebar."
        )

    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            "The 'anthropic' package isn't installed. Run: pip install anthropic "
            "— or use Offline mode instead, which needs no extra package."
        )

    client = anthropic.Anthropic(api_key=key)

    if job_description and job_description.strip():
        prompt = JD_MATCH_PROMPT_TEMPLATE.format(
            resume_text=resume_text.strip(),
            job_description=job_description.strip(),
        )
    else:
        prompt = GENERAL_PROMPT_TEMPLATE.format(resume_text=resume_text.strip())

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError as e:
        raise RuntimeError(f"Anthropic API error: {e}")

    raw_text = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )

    try:
        result = _extract_json(raw_text)
    except (json.JSONDecodeError, AttributeError) as e:
        raise RuntimeError(
            f"Could not parse the model's response as JSON: {e}\n\nRaw response:\n{raw_text}"
        )

    return result
