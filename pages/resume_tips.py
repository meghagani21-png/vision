import sys, os, re
import streamlit as st
import joblib
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import require_auth, render_sidebar, current_user, get_history

require_auth()
st.set_page_config(page_title="Resume Tips - Vision", page_icon="📝", layout="wide", initial_sidebar_state="expanded")
render_sidebar("resume_tips")

@st.cache_resource
def load_model():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model.pkl")
    return joblib.load(path) if os.path.exists(path) else None

model_payload = load_model()
if model_payload is None:
    st.error("model.pkl not found."); st.stop()
metadata = model_payload["career_metadata"]

# ── Resume tips data ─────────────────────────────────────────────────────────
ATS_CHECKLIST = [
    {"item": "Use a clean, single-column layout", "icon": "📐", "tip": "ATS parsers struggle with multi-column formats, tables, and graphics. Stick to a simple top-to-bottom layout."},
    {"item": "Include a professional summary (3-4 lines)", "icon": "📝", "tip": "Start with a concise summary highlighting your target role, years of experience, and top 3 skills."},
    {"item": "Use standard section headings", "icon": "📑", "tip": "Use 'Experience', 'Education', 'Skills', 'Projects' — not creative alternatives like 'My Journey' or 'Expertise'."},
    {"item": "List skills as keywords, not just in context", "icon": "🏷️", "tip": "Have a dedicated 'Skills' section with explicit keywords. ATS scans for exact matches."},
    {"item": "Include measurable achievements", "icon": "📊", "tip": "Use numbers: 'Reduced API latency by 40%' beats 'Improved performance'."},
    {"item": "Save as PDF (not .docx or .pages)", "icon": "📄", "tip": "PDF preserves formatting across all systems. Name it 'FirstName_LastName_Resume.pdf'."},
    {"item": "Keep it to 1-2 pages max", "icon": "📏", "tip": "1 page for <5 years experience, 2 pages for senior roles. Every line should earn its space."},
    {"item": "Use standard fonts (Arial, Calibri, Helvetica)", "icon": "🔤", "tip": "Fancy fonts can render as garbled text in some ATS systems."},
    {"item": "No headers/footers for critical info", "icon": "⚠️", "tip": "Many ATS can't read headers/footers. Keep your name and contact info in the main body."},
    {"item": "Tailor keywords to each job posting", "icon": "🎯", "tip": "Mirror the exact terms from the job description. If they say 'React.js', don't write 'ReactJS'."},
]

SECTION_TIPS = {
    "Professional Summary": {
        "icon": "📋",
        "color": "#a78bfa",
        "template": "Results-driven {role} with expertise in {skills}. Proven track record of {achievement}. Seeking to leverage {strength} to drive impact at a forward-thinking organization.",
        "dos": ["Mention your target role explicitly", "Include 2-3 top technical skills", "Add a measurable achievement", "Keep it under 4 lines"],
        "donts": ["Don't use 'I am looking for…'", "Don't list every skill you know", "Don't use buzzwords without substance", "Don't copy-paste a generic summary"],
    },
    "Technical Skills": {
        "icon": "💻",
        "color": "#60a5fa",
        "template": None,
        "dos": ["Group skills by category (Languages, Frameworks, Tools)", "List proficiency levels for key skills", "Include version numbers for frameworks", "Put most relevant skills first"],
        "donts": ["Don't list skills you can't discuss in an interview", "Don't mix unrelated skills together", "Don't use skill bars or graphs", "Don't forget soft skills entirely"],
    },
    "Work Experience": {
        "icon": "💼",
        "color": "#34d399",
        "template": None,
        "dos": ["Use action verbs (Built, Designed, Led, Optimized)", "Quantify impact with numbers", "Show progression in responsibilities", "Include relevant tech stack per role"],
        "donts": ["Don't just list job duties", "Don't include irrelevant positions", "Don't use passive voice", "Don't leave employment gaps unexplained"],
    },
    "Projects": {
        "icon": "🛠️",
        "color": "#fbbf24",
        "template": None,
        "dos": ["Include GitHub/live links", "Describe the problem you solved", "List the tech stack used", "Mention team size and your specific role"],
        "donts": ["Don't list tutorial projects as original work", "Don't include projects without descriptions", "Don't list more than 4-5 projects", "Don't forget to mention results/outcomes"],
    },
}

# ── page ──────────────────────────────────────────────────────────────────────
st.markdown("<div class='page-title'>📝 AI Resume Tips</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Smart, actionable tips to optimize your resume for ATS systems and recruiters</div>", unsafe_allow_html=True)

email = current_user()
history = get_history(email)

# Determine target role
last_role = st.session_state.get("last_top_career") or (history[-1]["top_career"] if history else None)
all_roles = sorted(metadata.keys())
default_idx = all_roles.index(last_role) if last_role and last_role in all_roles else 0
selected_role = st.selectbox("Optimize resume for", all_roles, index=default_idx)

role_data = metadata[selected_role]
core_skills = role_data["core_skills"]
bonus_skills = role_data["bonus_skills"]

# ── Resume Score ─────────────────────────────────────────────────────────────
last_score = history[-1].get("top_score", 0) if history else 0
# Compute a resume optimization score based on multiple factors
has_pdf = any(h.get("input_type") == "PDF" for h in history) if history else False
has_multiple = len(history) >= 3
has_high_score = last_score >= 70

score_factors = [
    ("Profile analyzed", bool(history), 20),
    ("PDF resume uploaded", has_pdf, 20),
    ("Multiple analyses done", has_multiple, 15),
    ("Score above 70%", has_high_score, 25),
    ("Multiple roles explored", len(set(h.get("top_career","") for h in history)) >= 2 if history else False, 20),
]
resume_score = sum(pts for _, done, pts in score_factors if done)
score_color = "#34d399" if resume_score >= 70 else ("#fbbf24" if resume_score >= 40 else "#f87171")

st.markdown(
    f"<div class='glow-card' style='padding:24px;'>"
    f"<div style='display:flex;align-items:center;gap:24px;flex-wrap:wrap;'>"
    f"<div class='score-ring' style='background:conic-gradient({score_color} {resume_score*3.6}deg, rgba(255,255,255,0.06) 0deg);'>"
    f"<div style='width:96px;height:96px;border-radius:50%;background:#0e0e1a;display:flex;align-items:center;justify-content:center;'>"
    f"<div style='text-align:center;'>"
    f"<div style='font-size:28px;font-weight:900;color:{score_color};'>{resume_score}</div>"
    f"<div style='font-size:10px;color:rgba(255,255,255,0.4);'>SCORE</div>"
    f"</div></div></div>"
    f"<div style='flex:1;min-width:200px;'>"
    f"<div style='font-size:18px;font-weight:800;color:#fff;'>Resume Optimization Score</div>"
    f"<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-top:6px;'>Targeting: "
    f"<span style='color:#a78bfa;font-weight:600;'>{selected_role}</span></div>"
    f"<div style='margin-top:10px;'>"
    + "".join([
        f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'>"
        f"<span style='color:{'#34d399' if done else 'rgba(255,255,255,0.2)'};font-size:14px;'>{'✅' if done else '⬜'}</span>"
        f"<span style='font-size:12px;color:rgba(255,255,255,{'0.6' if done else '0.3'});'>{label} (+{pts}pts)</span></div>"
        for label, done, pts in score_factors
    ])
    + "</div></div></div></div>",
    unsafe_allow_html=True
)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_keywords, tab_sections, tab_ats = st.tabs(["🏷️ Missing Keywords", "📋 Section-by-Section", "🎯 ATS Checklist"])

# ── Missing Keywords ─────────────────────────────────────────────────────────
with tab_keywords:
    st.markdown(
        f"<div style='font-size:16px;font-weight:700;color:#fff;margin-bottom:6px;'>Keywords for {selected_role}</div>"
        f"<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-bottom:16px;'>"
        f"Include these keywords in your resume to pass ATS screening</div>",
        unsafe_allow_html=True
    )

    st.markdown("<div style='font-size:14px;font-weight:700;color:#a78bfa;margin-bottom:8px;'>🔑 Must-Have Keywords (Core)</div>", unsafe_allow_html=True)
    core_html = "".join([
        f"<span style='display:inline-block;background:rgba(167,139,250,0.15);border:1px solid rgba(167,139,250,0.3);"
        f"border-radius:20px;padding:6px 14px;margin:4px;font-size:13px;color:#a78bfa;font-weight:600;'>"
        f"✦ {s}</span>"
        for s in core_skills
    ])
    st.markdown(core_html, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:14px;font-weight:700;color:#60a5fa;margin-bottom:8px;'>⭐ Stand-Out Keywords (Bonus)</div>", unsafe_allow_html=True)
    bonus_html = "".join([
        f"<span style='display:inline-block;background:rgba(96,165,250,0.12);border:1px solid rgba(96,165,250,0.25);"
        f"border-radius:20px;padding:6px 14px;margin:4px;font-size:13px;color:#60a5fa;font-weight:600;'>"
        f"✦ {s}</span>"
        for s in bonus_skills
    ])
    st.markdown(bonus_html, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='card' style='background:rgba(52,211,153,0.06);border-color:rgba(52,211,153,0.2);'>"
        f"<div style='font-size:14px;font-weight:700;color:#34d399;margin-bottom:8px;'>💡 Pro Tip: Keyword Placement</div>"
        f"<div style='font-size:13px;color:rgba(255,255,255,0.5);line-height:1.7;'>"
        f"Place core keywords in your <b>Summary</b> and <b>Skills</b> sections. "
        f"Weave bonus keywords naturally into your <b>Experience</b> bullet points. "
        f"Match the exact phrasing from the job description whenever possible.</div></div>",
        unsafe_allow_html=True
    )

    # Salary context
    st.markdown(
        f"<div class='card'>"
        f"<div style='display:flex;gap:24px;flex-wrap:wrap;'>"
        f"<div><div style='font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;'>Expected Salary</div>"
        f"<div style='font-size:20px;font-weight:800;color:#34d399;margin-top:4px;'>{role_data['salary_range']}</div></div>"
        f"<div><div style='font-size:11px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;'>Market Difficulty</div>"
        f"<div style='font-size:20px;font-weight:800;color:#fbbf24;margin-top:4px;'>{role_data['difficulty']}</div></div>"
        f"</div></div>",
        unsafe_allow_html=True
    )

# ── Section Tips ─────────────────────────────────────────────────────────────
with tab_sections:
    for section_name, section_data in SECTION_TIPS.items():
        with st.expander(f"{section_data['icon']} {section_name}", expanded=True):
            # Template
            if section_data["template"]:
                filled = section_data["template"].format(
                    role=selected_role,
                    skills=", ".join(core_skills[:3]),
                    achievement="delivering scalable solutions",
                    strength=", ".join(core_skills[:2])
                )
                st.markdown(
                    f"<div style='background:rgba(167,139,250,0.08);border:1px solid rgba(167,139,250,0.15);"
                    f"border-radius:12px;padding:14px;margin-bottom:14px;'>"
                    f"<div style='font-size:12px;font-weight:700;color:#a78bfa;margin-bottom:6px;'>📋 Template</div>"
                    f"<div style='font-size:13px;color:rgba(255,255,255,0.7);font-style:italic;line-height:1.6;'>"
                    f"\"{filled}\"</div></div>",
                    unsafe_allow_html=True
                )

            col_do, col_dont = st.columns(2)
            with col_do:
                st.markdown(
                    "<div style='font-size:13px;font-weight:700;color:#34d399;margin-bottom:8px;'>✅ Do</div>"
                    + "".join([
                        f"<div style='font-size:13px;color:rgba(255,255,255,0.6);margin-bottom:6px;line-height:1.5;'>"
                        f"• {tip}</div>" for tip in section_data["dos"]
                    ]),
                    unsafe_allow_html=True
                )
            with col_dont:
                st.markdown(
                    "<div style='font-size:13px;font-weight:700;color:#f87171;margin-bottom:8px;'>❌ Don't</div>"
                    + "".join([
                        f"<div style='font-size:13px;color:rgba(255,255,255,0.6);margin-bottom:6px;line-height:1.5;'>"
                        f"• {tip}</div>" for tip in section_data["donts"]
                    ]),
                    unsafe_allow_html=True
                )

# ── ATS Checklist ────────────────────────────────────────────────────────────
with tab_ats:
    st.markdown(
        "<div style='font-size:16px;font-weight:700;color:#fff;margin-bottom:6px;'>ATS Optimization Checklist</div>"
        "<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-bottom:16px;'>"
        "Make sure your resume passes Applicant Tracking Systems before a human ever sees it</div>",
        unsafe_allow_html=True
    )

    for i, item in enumerate(ATS_CHECKLIST):
        st.markdown(
            f"<div class='card' style='padding:16px 20px;'>"
            f"<div style='display:flex;align-items:flex-start;gap:12px;'>"
            f"<div style='font-size:20px;flex-shrink:0;'>{item['icon']}</div>"
            f"<div>"
            f"<div style='font-size:14px;font-weight:700;color:#fff;'>{item['item']}</div>"
            f"<div style='font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px;line-height:1.5;'>{item['tip']}</div>"
            f"</div></div></div>",
            unsafe_allow_html=True
        )

st.markdown(
    "<div style='text-align:center;font-size:12px;color:rgba(255,255,255,0.2);margin-top:20px;'>"
    "Tips are tailored to your selected role. Change the role above for role-specific advice.</div>",
    unsafe_allow_html=True
)
