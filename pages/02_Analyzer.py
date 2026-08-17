import os, re, sys
import joblib, requests
import pandas as pd
import streamlit as st
import altair as alt
import PyPDF2

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import require_auth, inject_theme, current_name, current_user, logout_session, save_analysis
from roadmap import get_roadmap

st.set_page_config(page_title="Analyzer · Vision", page_icon="🔬", layout="wide", initial_sidebar_state="expanded")
require_auth()
inject_theme()

# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 8px 0;'>
        <div style='font-size:20px;font-weight:800;color:#fff;'>🔭 Vision</div>
        <div style='font-size:12px;color:rgba(255,255,255,0.35);margin-top:2px;'>Careers AI Platform</div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.08);margin:8px 0 16px 0;'/>
    """, unsafe_allow_html=True)
    st.page_link("pages/01_Dashboard.py",  label="🏠  Dashboard")
    st.page_link("pages/02_Analyzer.py",   label="🔬  Analyzer")
    st.page_link("pages/03_History.py",    label="📋  History")
    st.page_link("pages/04_Compare.py",    label="⚖️  Compare Roles")
    st.page_link("pages/05_Job_Board.py",  label="💼  Job Board")
    st.page_link("pages/06_Settings.py",   label="⚙️  Settings")
    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:16px 0 8px 0;'/>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:12px;color:rgba(255,255,255,0.35);padding-bottom:4px;'>Signed in as</div><div style='font-size:13px;color:rgba(255,255,255,0.7);font-weight:600;'>{current_user()}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("🚪  Sign Out", use_container_width=True):
        logout_session()
        st.switch_page("app.py")

# ── helpers ───────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model.pkl")
    if not os.path.exists(path):
        return None
    return joblib.load(path)

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + " "
    return text

def check_skill_match(skill, user_text):
    s = skill.lower().replace(".", "").replace("+", "")
    t = user_text.lower().replace(".", "").replace("+", "")
    return bool(re.search(r'\b' + re.escape(s) + r'\b', t))

def create_badge(skill, matched):
    cls  = "chip-pass" if matched else "chip-fail"
    icon = "✅" if matched else "🎯"
    return f'<span class="{cls}">{icon} {skill}</span>'

# ── load model ────────────────────────────────────────────────────────────────
model_payload = load_model()
if model_payload is None:
    st.error("⚠️ `model.pkl` not found. Run `python train_model.py` first.")
    st.stop()

pipeline = model_payload["pipeline"]
metadata = model_payload["career_metadata"]
classes  = pipeline.classes_

# ── page header ───────────────────────────────────────────────────────────────
st.markdown("<div class='page-title'>🔬 Career Analyzer</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Upload your resume or paste your skills — our ML engine will find your best-fit career path</div>", unsafe_allow_html=True)

# ── input ─────────────────────────────────────────────────────────────────────
user_text   = ""
input_type  = "text"

upload_tab, text_tab = st.tabs(["📄 Upload Resume (PDF)", "✍️ Paste Skills / Text"])

with upload_tab:
    uploaded_file = st.file_uploader("Drop your resume PDF here", type=["pdf"])
    if uploaded_file is not None:
        with st.spinner("Parsing PDF…"):
            user_text  = extract_text_from_pdf(uploaded_file)
            input_type = "PDF"
        st.success(f"✅ Parsed {len(user_text.split())} words from your resume.")

with text_tab:
    pasted = st.text_area("Paste your skills, experience, or bio:", height=140,
                          placeholder="e.g. Python, React, Docker, SQL, AWS, machine learning...")
    if pasted:
        user_text  = pasted
        input_type = "text"

analyze_btn = st.button("🚀 Analyze My Profile", type="primary", use_container_width=True)

# ── results ───────────────────────────────────────────────────────────────────
if analyze_btn:
    if len(user_text.strip()) < 15:
        st.warning("Please provide more detail — at least a few skills or a sentence.")
    else:
        st.toast("Analyzing profile against industry standards…", icon="🔍")

        probs    = pipeline.predict_proba([user_text])[0]
        prob_df  = pd.DataFrame({"Career": classes, "Match Score": probs * 100}).sort_values("Match Score", ascending=False)
        top_roles   = prob_df.head(5)
        top_career  = top_roles.iloc[0]["Career"]
        top_score   = top_roles.iloc[0]["Match Score"]

        # save to history
        import datetime
        save_analysis(current_user(), {
            "date":       datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "top_career": top_career,
            "top_score":  top_score,
            "input_type": input_type,
            "all_roles":  top_roles.to_dict("records"),
        })

        # ── hero result ───────────────────────────────────────────────────────
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='card' style='background:linear-gradient(135deg,rgba(124,58,237,0.2),rgba(79,70,229,0.15));
             border:1px solid rgba(124,58,237,0.3);text-align:center;padding:32px;'>
            <div style='font-size:13px;color:rgba(255,255,255,0.5);letter-spacing:1px;text-transform:uppercase;'>Top Career Match</div>
            <div style='font-size:36px;font-weight:900;color:#fff;margin:8px 0 4px 0;'>{top_career}</div>
            <div style='font-size:22px;font-weight:700;color:#a78bfa;'>{top_score:.1f}% Match</div>
        </div>""", unsafe_allow_html=True)
        st.progress(int(top_score))
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── tabs ──────────────────────────────────────────────────────────────
        tab1, tab2, tab3 = st.tabs(["📊 Probability Chart", "🔍 Skill Gap & Market Data", "🗺️ Actionable Roadmap"])

        with tab1:
            chart = (alt.Chart(top_roles)
                .mark_bar(cornerRadiusEnd=8)
                .encode(
                    x=alt.X("Match Score:Q", title="Match Probability (%)", scale=alt.Scale(domain=[0,100])),
                    y=alt.Y("Career:N", sort="-x", title=""),
                    color=alt.Color("Match Score:Q", scale=alt.Scale(scheme="purples"), legend=None),
                    tooltip=["Career", alt.Tooltip("Match Score:Q", format=".1f")]
                )
                .properties(height=300)
                .configure_view(strokeWidth=0)
                .configure_axis(labelColor="#aaa", titleColor="#aaa", gridColor="rgba(255,255,255,0.05)")
                .configure_bar(color="#7c3aed")
            )
            st.altair_chart(chart, use_container_width=True)

        with tab2:
            role_data = metadata[top_career]
            ca, cb = st.columns([1, 2])
            with ca:
                st.markdown(f"""<div class='card'>
                    <div style='font-size:12px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;'>Expected Salary</div>
                    <div style='font-size:22px;font-weight:800;color:#34d399;margin-top:4px;'>{role_data['salary_range']}</div>
                </div>""", unsafe_allow_html=True)
                diff_color = {"High":"#f59e0b","Very High":"#ef4444","Medium":"#60a5fa","Low":"#34d399"}.get(role_data['difficulty'],"#aaa")
                st.markdown(f"""<div class='card'>
                    <div style='font-size:12px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;'>Market Difficulty</div>
                    <div style='font-size:22px;font-weight:800;margin-top:4px;' style='color:{diff_color};'>{role_data['difficulty']}</div>
                </div>""", unsafe_allow_html=True)
            with cb:
                st.markdown("**Core Competencies**")
                core_html = "".join([create_badge(s, check_skill_match(s, user_text)) for s in role_data["core_skills"]])
                st.markdown(core_html, unsafe_allow_html=True)
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                st.markdown("**Bonus / Stand-Out Skills**")
                bonus_html = "".join([create_badge(s, check_skill_match(s, user_text)) for s in role_data["bonus_skills"]])
                st.markdown(bonus_html, unsafe_allow_html=True)

        with tab3:
            phases = get_roadmap(top_career, metadata)
            roadmap_md = f"# Your Custom Roadmap: {top_career}\n\n"
            for title, desc in phases:
                with st.expander(title, expanded=True):
                    st.markdown(desc)
                roadmap_md += f"### {title}\n{desc}\n\n"
            st.divider()
            st.download_button(
                label="📥 Download Roadmap (.md)",
                data=roadmap_md,
                file_name=f"{top_career.replace(' ','_')}_Roadmap.md",
                mime="text/markdown",
                type="primary"
            )
