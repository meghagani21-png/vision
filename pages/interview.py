import sys, os, random, hashlib
import streamlit as st
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import require_auth, render_sidebar, current_user, get_history
import joblib

require_auth()
st.set_page_config(page_title="Interview Coach - Vision", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
render_sidebar("interview")

@st.cache_resource
def load_model():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model.pkl")
    return joblib.load(path) if os.path.exists(path) else None

model_payload = load_model()
if model_payload is None:
    st.error("model.pkl not found."); st.stop()
metadata = model_payload["career_metadata"]

# ── Interview question bank (generated from metadata) ────────────────────────
QUESTION_TEMPLATES = {
    "Technical": [
        "Explain the difference between {s1} and {s2}. When would you use each?",
        "How would you design a system using {s1}? Walk us through your architecture.",
        "Describe a challenging bug you encountered while working with {s1}. How did you resolve it?",
        "What are the best practices for implementing {s1} in a production environment?",
        "How do you ensure code quality and testing when working with {s1}?",
        "Explain the internal workings of {s1}. What happens under the hood?",
        "Compare {s1} with its alternatives. Why would you choose it over others?",
        "How would you optimize a slow {s1} pipeline? What metrics would you track?",
        "Describe how {s1} integrates with {s2} in a real-world project.",
        "What security considerations should you keep in mind when using {s1}?",
    ],
    "Behavioral": [
        "Tell me about a time you had to learn {s1} quickly for a project. How did you approach it?",
        "Describe a situation where you disagreed with a team member about using {s1} vs another approach.",
        "How do you stay updated with the latest developments in {s1} and related technologies?",
        "Tell me about a project where you had to work with {s1} under a tight deadline.",
        "Describe a time when you mentored someone on {s1}. What was your approach?",
        "How do you handle feedback when your {s1} implementation needs significant changes?",
        "Tell me about a failure involving {s1}. What did you learn?",
        "Describe how you've contributed to your team's knowledge of {s1}.",
    ],
    "System Design": [
        "Design a scalable system that leverages {s1} and {s2} for a startup with 1M users.",
        "How would you architect a real-time data pipeline using {s1}?",
        "Design a microservices architecture where {s1} is a critical component.",
        "How would you handle failover and disaster recovery for a {s1}-based system?",
        "Design an API gateway that integrates {s1} with third-party services.",
        "How would you scale a {s1} system from 1K to 1M requests per second?",
    ],
    "Situational": [
        "Your {s1} production deployment just crashed at 2 AM. Walk me through your incident response.",
        "A client wants a feature built with {s1} in 2 weeks. Your team estimates 6 weeks. How do you handle it?",
        "You discover a critical security vulnerability in your {s1} implementation. What steps do you take?",
        "Your team wants to migrate from {s1} to {s2}. How would you plan and execute this?",
        "A new junior developer joined and struggles with {s1}. How would you onboard them?",
        "The stakeholders want you to choose between {s1} and {s2}. How do you make the decision?",
    ],
}

DIFFICULTY_MAP = {
    "Technical": ["Medium", "Hard", "Hard", "Medium", "Medium", "Hard", "Medium", "Hard", "Medium", "Hard"],
    "Behavioral": ["Easy", "Medium", "Easy", "Medium", "Medium", "Easy", "Medium", "Easy"],
    "System Design": ["Hard", "Hard", "Hard", "Hard", "Hard", "Hard"],
    "Situational": ["Medium", "Hard", "Hard", "Hard", "Medium", "Medium"],
}

DIFFICULTY_COLORS = {"Easy": "#34d399", "Medium": "#fbbf24", "Hard": "#f87171"}

TIPS = {
    "Technical": "Use the **STAR method** adapted for technical questions: **S**ituation → **T**echnology → **A**pproach → **R**esult. Always mention trade-offs.",
    "Behavioral": "Structure your answer with **STAR**: **S**ituation → **T**ask → **A**ction → **R**esult. Be specific with numbers and outcomes.",
    "System Design": "Start with **requirements** (functional + non-functional), then **high-level design**, then **deep dive** into components. Always discuss **trade-offs**.",
    "Situational": "Show your **thought process**, not just the answer. Demonstrate leadership, empathy, and structured problem-solving.",
}

def generate_questions(role, seed):
    """Generate role-specific interview questions from metadata."""
    rng = random.Random(seed)
    role_data = metadata.get(role, {})
    all_skills = role_data.get("core_skills", []) + role_data.get("bonus_skills", [])
    if len(all_skills) < 2:
        all_skills = ["Python", "SQL"]

    questions = {}
    for category, templates in QUESTION_TEMPLATES.items():
        cat_questions = []
        selected = rng.sample(templates, min(4, len(templates)))
        difficulties = DIFFICULTY_MAP[category]
        for i, tmpl in enumerate(selected):
            s1, s2 = rng.sample(all_skills, min(2, len(all_skills)))
            q_text = tmpl.format(s1=s1, s2=s2)
            diff = difficulties[i % len(difficulties)]
            cat_questions.append({"question": q_text, "difficulty": diff})
        questions[category] = cat_questions
    return questions

# ── page ──────────────────────────────────────────────────────────────────────
st.markdown("<div class='page-title'>🧠 AI Interview Coach</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Practice role-specific interview questions tailored to your career match</div>", unsafe_allow_html=True)

# Role selection
history = get_history(current_user())
last_role = st.session_state.get("last_top_career") or (history[-1]["top_career"] if history else None)
all_roles = sorted(metadata.keys())
default_idx = all_roles.index(last_role) if last_role and last_role in all_roles else 0

col_role, col_gen = st.columns([3, 1])
with col_role:
    selected_role = st.selectbox("Select Role to Practice", all_roles, index=default_idx)
with col_gen:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    if st.button("🔄 New Questions", type="primary", use_container_width=True):
        st.session_state["interview_seed"] = random.randint(0, 999999)

if "interview_seed" not in st.session_state:
    st.session_state["interview_seed"] = 42

# Info banner
role_data = metadata.get(selected_role, {})
core_count = len(role_data.get("core_skills", []))
bonus_count = len(role_data.get("bonus_skills", []))
st.markdown(
    f"<div class='glow-card' style='padding:16px 20px;'>"
    f"<div style='display:flex;align-items:center;gap:16px;flex-wrap:wrap;'>"
    f"<div style='font-size:32px;'>🎯</div>"
    f"<div>"
    f"<div style='font-size:16px;font-weight:700;color:#fff;'>Practicing for: "
    f"<span class='gradient-text'>{selected_role}</span></div>"
    f"<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-top:2px;'>"
    f"Questions cover {core_count} core skills and {bonus_count} bonus skills</div>"
    f"</div></div></div>",
    unsafe_allow_html=True
)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# Fix expander label text wrapping (prevents letter overlap)
st.markdown("""
<style>
[data-testid="stExpander"] summary {
    white-space: normal !important;
    word-break: break-word !important;
    overflow-wrap: break-word !important;
    line-height: 1.5 !important;
    align-items: flex-start !important;
}
[data-testid="stExpander"] summary p {
    white-space: normal !important;
    word-break: break-word !important;
}
[data-testid="stExpander"] details summary {
    white-space: normal !important;
}
</style>
""", unsafe_allow_html=True)

# Generate and display questions
questions = generate_questions(selected_role, st.session_state["interview_seed"])

for category, cat_questions in questions.items():
    cat_icon = {"Technical": "💻", "Behavioral": "🤝", "System Design": "🏗️", "Situational": "🎭"}
    icon = cat_icon.get(category, "❓")

    st.markdown(
        f"<div style='display:flex;align-items:center;gap:10px;margin:20px 0 8px 0;'>"
        f"<span style='font-size:22px;'>{icon}</span>"
        f"<span style='font-size:18px;font-weight:700;color:#fff;'>{category}</span>"
        f"<span style='font-size:12px;color:rgba(255,255,255,0.3);margin-left:4px;'>"
        f"{len(cat_questions)} questions</span></div>",
        unsafe_allow_html=True
    )

    # Tip card
    st.markdown(
        f"<div style='background:rgba(167,139,250,0.08);border:1px solid rgba(167,139,250,0.15);"
        f"border-radius:12px;padding:10px 16px;margin-bottom:12px;font-size:13px;color:rgba(255,255,255,0.6);'>"
        f"💡 <b style='color:#a78bfa;'>Tip:</b> {TIPS[category]}</div>",
        unsafe_allow_html=True
    )

    for i, q in enumerate(cat_questions):
        diff_color = DIFFICULTY_COLORS[q["difficulty"]]
        label = f"Question {i+1}  ·  {q['difficulty']}"
        with st.expander(label, expanded=False):
            # Full question text displayed clearly inside
            st.markdown(
                f"<div style='font-size:15px;font-weight:700;color:#fff;line-height:1.6;"
                f"word-break:break-word;white-space:normal;margin-bottom:14px;'>"
                f"{q['question']}"
                f"</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='display:inline-flex;align-items:center;gap:8px;margin-bottom:12px;'"
                f">"
                f"<span style='width:8px;height:8px;border-radius:50%;background:{diff_color};"
                f"display:inline-block;'></span>"
                f"<span style='font-size:12px;font-weight:600;color:{diff_color};'>Difficulty: {q['difficulty']}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

            # Answer guidance
            answer_key = f"show_answer_{category}_{i}"
            if st.button("💡 Reveal Answer Guide", key=answer_key):
                st.markdown(
                    f"<div style='background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.2);"
                    f"border-radius:12px;padding:14px;margin-top:8px;'>"
                    f"<div style='font-size:13px;font-weight:700;color:#34d399;margin-bottom:8px;'>Answer Framework</div>"
                    f"<div style='font-size:13px;color:rgba(255,255,255,0.6);line-height:1.7;'>"
                    f"1. <b>Context:</b> Set the scene — what project, team, or scenario?<br>"
                    f"2. <b>Your Approach:</b> What specific technology/method did you use and why?<br>"
                    f"3. <b>Implementation:</b> Walk through the key steps you took.<br>"
                    f"4. <b>Trade-offs:</b> What alternatives did you consider? Why this approach?<br>"
                    f"5. <b>Result:</b> Quantifiable outcome — performance gains, time saved, etc."
                    f"</div></div>",
                    unsafe_allow_html=True
                )

# ── Stats ─────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
total_q = sum(len(v) for v in questions.values())
st.markdown(
    f"<div class='card' style='text-align:center;padding:20px;'>"
    f"<div style='display:flex;justify-content:center;gap:40px;flex-wrap:wrap;'>"
    f"<div><div style='font-size:28px;font-weight:800;color:#a78bfa;'>{total_q}</div>"
    f"<div style='font-size:12px;color:rgba(255,255,255,0.4);'>Questions Generated</div></div>"
    f"<div><div style='font-size:28px;font-weight:800;color:#60a5fa;'>{len(questions)}</div>"
    f"<div style='font-size:12px;color:rgba(255,255,255,0.4);'>Categories</div></div>"
    f"<div><div style='font-size:28px;font-weight:800;color:#34d399;'>{core_count + bonus_count}</div>"
    f"<div style='font-size:12px;color:rgba(255,255,255,0.4);'>Skills Covered</div></div>"
    f"</div></div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div style='text-align:center;font-size:12px;color:rgba(255,255,255,0.2);margin-top:16px;'>"
    "Questions are dynamically generated based on role metadata. Click 'New Questions' for a fresh set.</div>",
    unsafe_allow_html=True
)
