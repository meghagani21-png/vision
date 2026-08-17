import os, re, sys, datetime
import joblib
import pandas as pd
import streamlit as st
import altair as alt
import PyPDF2

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import require_auth, render_sidebar, current_user, save_analysis, get_linkedin, save_linkedin
from roadmap import get_roadmap

require_auth()
st.set_page_config(page_title="Analyzer - Vision", page_icon="🔬", layout="wide", initial_sidebar_state="expanded")
render_sidebar("analyzer")

# ── helpers ───────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model.pkl")
    return joblib.load(path) if os.path.exists(path) else None

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text   = ""
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
    cls = "chip-pass" if matched else "chip-fail"
    icon = "✅" if matched else "➤"
    return f'<span class="{cls}">{icon} {skill}</span>'

# ── load model ────────────────────────────────────────────────────────────────
model_payload = load_model()
if model_payload is None:
    st.error("model.pkl not found. Run `python train_model.py` first.")
    st.stop()

pipeline = model_payload["pipeline"]
metadata = model_payload["career_metadata"]
classes  = pipeline.classes_

# ── page header ───────────────────────────────────────────────────────────────
st.markdown("<div class='page-title'>🔬 Career Analyzer</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Upload your resume, paste your LinkedIn profile URL, or type your skills to get your career match</div>", unsafe_allow_html=True)

# ── LinkedIn profile section ──────────────────────────────────────────────────
email          = current_user()
saved_linkedin = get_linkedin(email)

with st.expander("👥 LinkedIn Profile (optional — helps match jobs to your profile)", expanded=bool(saved_linkedin)):
    li_col1, li_col2 = st.columns([4, 1])
    with li_col1:
        linkedin_url = st.text_input(
            "Your LinkedIn Profile URL",
            value=saved_linkedin,
            placeholder="https://www.linkedin.com/in/yourname/",
            key="linkedin_input",
            label_visibility="collapsed"
        )
    with li_col2:
        if st.button("Save Profile", key="save_linkedin", use_container_width=True):
            if linkedin_url.strip() and "linkedin.com" in linkedin_url.lower():
                save_linkedin(email, linkedin_url.strip())
                st.session_state["linkedin_saved"] = linkedin_url.strip()
                st.success("LinkedIn profile saved!")
            else:
                st.error("Please enter a valid LinkedIn URL.")

    if saved_linkedin:
        st.markdown(
            f"<div style='font-size:12px;color:rgba(255,255,255,0.4);margin-top:6px;'>"
            f"✅ Saved: <a href='{saved_linkedin}' target='_blank' style='color:#60a5fa;'>{saved_linkedin}</a>"
            f"</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div style='font-size:12px;color:rgba(255,255,255,0.35);margin-top:4px;'>"
            "💡 After analyzing your profile, go to Job Board to see roles matched to your top career."
            "</div>",
            unsafe_allow_html=True
        )

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── input tabs ────────────────────────────────────────────────────────────────
user_text  = ""
input_type = "text"

upload_tab, text_tab = st.tabs(["📄 Upload Resume (PDF)", "✏️ Paste Skills / Experience"])

with upload_tab:
    uploaded_file = st.file_uploader("Drop your resume PDF here", type=["pdf"])
    if uploaded_file is not None:
        with st.spinner("Parsing PDF..."):
            user_text  = extract_text_from_pdf(uploaded_file)
            input_type = "PDF"
        st.success(f"Parsed {len(user_text.split())} words from your resume.")

with text_tab:
    pasted = st.text_area(
        "Paste your skills, experience, or bio:",
        height=140,
        placeholder="e.g. Python, React, Docker, SQL, AWS, machine learning, 3 years backend experience..."
    )
    if pasted:
        user_text  = pasted
        input_type = "text"

analyze_btn = st.button("🚀 Analyze My Profile", type="primary", use_container_width=True)

# ── results ───────────────────────────────────────────────────────────────────
if analyze_btn:
    if len(user_text.strip()) < 15:
        st.warning("Please provide more detail - at least a few skills or sentences.")
    else:
        st.toast("Analyzing profile against industry standards...", icon="🔍")

        probs   = pipeline.predict_proba([user_text])[0]
        prob_df = pd.DataFrame({"Career": classes, "Match Score": probs * 100}).sort_values("Match Score", ascending=False)
        top_roles  = prob_df.head(5)
        top_career = top_roles.iloc[0]["Career"]
        top_score  = top_roles.iloc[0]["Match Score"]

        # ── SAVE to history (works for all users including Google) ─────────────
        record = {
            "date":       datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "top_career": top_career,
            "top_score":  top_score,
            "input_type": input_type,
            "all_roles":  top_roles.to_dict("records"),
        }
        save_analysis(email, record)

        # ── store last result in session so Compare/Job Board can read it ──────
        st.session_state["last_top_career"] = top_career
        st.session_state["last_top_score"]  = top_score
        st.session_state["last_all_roles"]  = top_roles.to_dict("records")

        # ── hero result card ───────────────────────────────────────────────────
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='card' style='background:linear-gradient(135deg,rgba(124,58,237,0.2),rgba(79,70,229,0.15));"
            f"border:1px solid rgba(124,58,237,0.3);text-align:center;padding:32px;'>"
            f"<div style='font-size:13px;color:rgba(255,255,255,0.5);letter-spacing:1px;text-transform:uppercase;'>Top Career Match</div>"
            f"<div style='font-size:36px;font-weight:900;color:#fff;margin:8px 0 4px 0;'>{top_career}</div>"
            f"<div style='font-size:22px;font-weight:700;color:#a78bfa;'>{top_score:.1f}% Match</div>"
            f"</div>",
            unsafe_allow_html=True
        )
        st.progress(int(top_score))

        # quick link to job board filtered for this role
        linkedin_saved = get_linkedin(email)
        if linkedin_saved:
            st.markdown(
                f"<div style='text-align:center;margin:12px 0 0 0;'>"
                f"<a href='https://www.linkedin.com/jobs/search/?keywords={top_career.replace(' ','+')}' "
                f"target='_blank' style='display:inline-block;background:linear-gradient(135deg,#0077b5,#0a66c2);"
                f"color:#fff;text-decoration:none;border-radius:10px;padding:8px 20px;font-size:13px;font-weight:700;margin-right:10px;'>"
                f"👥 Apply on LinkedIn for {top_career}</a>"
                f"</div>",
                unsafe_allow_html=True
            )
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📊 Probability Chart", "🔍 Skill Gap and Market Data", "🗺️ Actionable Roadmap"])

        with tab1:
            chart = (
                alt.Chart(top_roles)
                .mark_bar(cornerRadiusEnd=8)
                .encode(
                    x=alt.X("Match Score:Q", title="Match Probability (%)", scale=alt.Scale(domain=[0, 100])),
                    y=alt.Y("Career:N", sort="-x", title=""),
                    color=alt.Color("Match Score:Q", scale=alt.Scale(scheme="purples"), legend=None),
                    tooltip=["Career", alt.Tooltip("Match Score:Q", format=".1f")]
                )
                .properties(height=300)
                .configure_view(strokeWidth=0)
                .configure_axis(labelColor="#aaa", titleColor="#aaa", gridColor="rgba(255,255,255,0.05)")
            )
            st.altair_chart(chart, use_container_width=True)

        with tab2:
            role_data = metadata[top_career]
            ca, cb    = st.columns([1, 2])
            with ca:
                st.markdown(
                    f"<div class='card'>"
                    f"<div style='font-size:12px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;'>Expected Salary</div>"
                    f"<div style='font-size:22px;font-weight:800;color:#34d399;margin-top:4px;'>{role_data['salary_range']}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div class='card'>"
                    f"<div style='font-size:12px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;'>Market Difficulty</div>"
                    f"<div style='font-size:22px;font-weight:800;color:#f59e0b;margin-top:4px;'>{role_data['difficulty']}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with cb:
                st.markdown("**Core Competencies**")
                core_html = "".join([create_badge(s, check_skill_match(s, user_text)) for s in role_data["core_skills"]])
                st.markdown(core_html, unsafe_allow_html=True)
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                st.markdown("**Bonus / Stand-Out Skills**")
                bonus_html = "".join([create_badge(s, check_skill_match(s, user_text)) for s in role_data["bonus_skills"]])
                st.markdown(bonus_html, unsafe_allow_html=True)

        with tab3:
            phases     = get_roadmap(top_career, metadata)
            roadmap_md = f"# Your Custom Roadmap: {top_career}\n\n"
            for title, desc in phases:
                with st.expander(title, expanded=True):
                    st.markdown(desc)
                roadmap_md += f"### {title}\n{desc}\n\n"
            st.divider()
            dl_col1, dl_col2 = st.columns([1, 1])
            with dl_col1:
                st.download_button(
                    label="📥 Download Roadmap (.md)",
                    data=roadmap_md,
                    file_name=f"{top_career.replace(' ', '_')}_Roadmap.md",
                    mime="text/markdown",
                    type="primary",
                    use_container_width=True
                )
            with dl_col2:
                li = get_linkedin(email)
                li_url = f"https://www.linkedin.com/jobs/search/?keywords={top_career.replace(' ', '+')}"
                st.markdown(
                    f"<a href='{li_url}' target='_blank' style='display:block;text-align:center;"
                    f"background:linear-gradient(135deg,#0077b5,#0a66c2);color:#fff;text-decoration:none;"
                    f"border-radius:12px;padding:10px 0;font-size:14px;font-weight:700;margin-top:0px;'>"
                    f"👥 Find {top_career} Jobs on LinkedIn</a>",
                    unsafe_allow_html=True
                )
