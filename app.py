"""
app.py
AI Resume Analyzer - Streamlit app.

Run with:
    streamlit run app.py
"""

import os
import streamlit as st
import plotly.graph_objects as go

from resume_parser import extract_resume_text
from analyzer import analyze_resume
from offline_analyzer import analyze_resume_offline

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:

    st.markdown(
        """
        ## How it works

        **1.** Upload your resume (PDF, DOCX, or TXT)

        **2.** (Optional) Paste a job description to match against

        **3.** Click **Analyze Resume**

        **4.** Review your score, gaps, and suggestions
        """
    )

# Offline analysis is used by default
use_ai_mode = False
effective_api_key = ""

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("📄 AI Resume Analyzer")
st.write(
    "Upload your resume to get an AI-powered score, skill gap analysis, "
    "and concrete suggestions for improvement — optionally matched against a specific job description."
)

# ---------------------------------------------------------------------------
# Input section
# ---------------------------------------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a PDF, DOCX, or TXT file",
        type=["pdf", "docx", "txt"],
    )

with col2:
    st.subheader("2. Job Description (optional)")
    job_description = st.text_area(
        "Paste the job description here for a tailored match score",
        height=220,
        placeholder="Paste the job posting text here...",
    )

analyze_clicked = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Helper display functions
# ---------------------------------------------------------------------------
def render_score_gauge(score: int, title: str):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": title},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#2E86AB"},
                "steps": [
                    {"range": [0, 40], "color": "#f8d7da"},
                    {"range": [40, 70], "color": "#fff3cd"},
                    {"range": [70, 100], "color": "#d4edda"},
                ],
            },
        )
    )
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)


def render_list_section(title: str, items: list, icon: str):
    st.markdown(f"**{icon} {title}**")
    if items:
        for item in items:
            st.markdown(f"- {item}")
    else:
        st.caption("None identified.")


# ---------------------------------------------------------------------------
# Analysis flow
# ---------------------------------------------------------------------------
if analyze_clicked:
    if not uploaded_file:
        st.error("Please upload a resume file first.")
    elif use_ai_mode and not effective_api_key:
        st.error("Please enter your Anthropic API key in the sidebar, or switch to Offline mode.")
    else:
        try:
            with st.spinner("Extracting text from resume..."):
                file_bytes = uploaded_file.read()
                resume_text = extract_resume_text(uploaded_file.name, file_bytes)

            if use_ai_mode:
                with st.spinner("Analyzing with Claude... this can take 10-20 seconds"):
                    result = analyze_resume(
                        resume_text=resume_text,
                        job_description=job_description,
                        api_key=effective_api_key,
                    )
            else:
                with st.spinner("Running offline keyword analysis..."):
                    result = analyze_resume_offline(
                        resume_text=resume_text,
                        job_description=job_description,
                    )

            st.session_state["last_result"] = result
            st.session_state["last_resume_text"] = resume_text

        except ValueError as e:
            st.error(f"Could not read resume: {e}")
        except RuntimeError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Unexpected error: {e}")

# ---------------------------------------------------------------------------
# Results display
# ---------------------------------------------------------------------------
if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    st.markdown("---")
    st.header("📊 Analysis Results")
    st.caption(
        "🤖 Generated by Claude (AI-powered mode)" if use_ai_mode
        else "🆓 Generated by offline keyword/heuristic scan — a rough first pass, not a full AI review."
    )

    top_col1, top_col2, top_col3 = st.columns([1, 1, 1.4])
    with top_col1:
        render_score_gauge(
            result.get("overall_match_score", 0),
            "Overall Score" if not job_description.strip() else "Job Match Score",
        )
    with top_col2:
        render_score_gauge(result.get("ats_score", 0), "ATS Compatibility")
    with top_col3:
        st.markdown("**📝 Summary**")
        st.info(result.get("summary", "No summary available."))
        st.markdown(f"**Estimated experience level:** {result.get('estimated_experience_level', 'N/A')}")

    st.markdown("### 🎯 Top Priority Fix")
    st.warning(result.get("top_priority_fix", "No specific priority identified."))

    st.markdown("### Skills Analysis")
    skill_col1, skill_col2 = st.columns(2)
    with skill_col1:
        render_list_section("Matched Skills", result.get("matched_skills", []), "✅")
    with skill_col2:
        render_list_section("Missing Skills", result.get("missing_skills", []), "❌")

    st.markdown("### Strengths & Weaknesses")
    sw_col1, sw_col2 = st.columns(2)
    with sw_col1:
        render_list_section("Strengths", result.get("strengths", []), "💪")
    with sw_col2:
        render_list_section("Weaknesses", result.get("weaknesses", []), "⚠️")

    st.markdown("### 💡 Actionable Suggestions")
    for i, suggestion in enumerate(result.get("suggestions", []), start=1):
        st.markdown(f"{i}. {suggestion}")

    st.markdown("### 🔑 Keywords to Add")
    keywords = result.get("keyword_suggestions", [])
    if keywords:
        st.write(" ".join([f"`{kw}`" for kw in keywords]))
    else:
        st.caption("None identified.")

    with st.expander("View extracted resume text"):
        st.text(st.session_state.get("last_resume_text", ""))

    st.markdown("---")
    st.download_button(
        "⬇️ Download analysis as JSON",
        data=str(result),
        file_name="resume_analysis.json",
        mime="application/json",
    )
