import os
import re
import joblib
import requests
import pandas as pd
import streamlit as st
import altair as alt
import PyPDF2
from streamlit_lottie import st_lottie
from roadmap import get_roadmap

# --- PAGE CONFIG ---
st.set_page_config(page_title="Vision Careers AI", page_icon="🔭", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM CSS ---
# This CSS centers our layout, removes standard Streamlit padding, and styles our skill chips
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .big-font { font-size: 24px !important; font-weight: 700; color: #1f77b4; }
    .stProgress > div > div > div > div { background-color: #00C896; }
    .skill-chip-pass { background-color: #d4edda; color: #155724; padding: 6px 14px; border-radius: 20px; margin: 4px; display: inline-block; font-size: 0.9rem; font-weight: 600; border: 1px solid #c3e6cb; }
    .skill-chip-fail { background-color: #f8d7da; color: #721c24; padding: 6px 14px; border-radius: 20px; margin: 4px; display: inline-block; font-size: 0.9rem; font-weight: 600; border: 1px solid #f5c6cb; }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
@st.cache_resource
def load_model():
    if not os.path.exists("model.pkl"):
        return None
    return joblib.load("model.pkl")

def load_lottieurl(url):
    """Fetches a Lottie animation from a URL."""
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def extract_text_from_pdf(file):
    """Extracts text content from an uploaded PDF file."""
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + " "
    return text

def check_skill_match(skill, user_text):
    skill_lower = skill.lower().replace(".", "").replace("+", "")
    text_lower = user_text.lower().replace(".", "").replace("+", "")
    pattern = r'\b' + re.escape(skill_lower) + r'\b'
    return bool(re.search(pattern, text_lower))

def create_badge(skill, matched):
    class_name = "skill-chip-pass" if matched else "skill-chip-fail"
    icon = "✅" if matched else "🎯"
    return f'<span class="{class_name}">{icon} {skill}</span>'

# --- LOAD RESOURCES ---
model_payload = load_model()
lottie_coding = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json")

if model_payload is None:
    st.error("⚠️ `model.pkl` not found! Run `python train_model.py` in your terminal.")
    st.stop()

pipeline = model_payload["pipeline"]
metadata = model_payload["career_metadata"]
classes = pipeline.classes_

# --- HERO SECTION ---
col1, col2 = st.columns([2, 1])
with col1:
    st.title("🔭 Vision Careers AI")
    st.markdown("### Accelerate your tech career with Machine Learning.")
    st.write("Upload your resume or paste your technical background below. Our local AI will analyze your skills, predict your optimal career path, and generate a customized skill-gap roadmap.")
with col2:
    if lottie_coding:
        st_lottie(lottie_coding, height=180, key="coding")

st.divider()

# --- INPUT SECTION (TEXT OR PDF) ---
user_text = ""
upload_tab, text_tab = st.tabs(["📄 Upload Resume (PDF)", "✍️ Paste Text"])

with upload_tab:
    uploaded_file = st.file_uploader("Upload your resume to instantly extract your skills.", type=["pdf"])
    if uploaded_file is not None:
        with st.spinner("Parsing PDF..."):
            user_text = extract_text_from_pdf(uploaded_file)
            st.success("Resume successfully parsed! Ready for analysis.")

with text_tab:
    pasted_text = st.text_area("Or paste your skills/experience here:", height=120)
    if pasted_text:
        user_text = pasted_text

analyze_btn = st.button("🚀 Analyze My Profile", type="primary", use_container_width=True)

# --- RESULTS SECTION ---
if analyze_btn:
    if len(user_text.strip()) < 15:
        st.warning("Please upload a valid resume or type more detailed skills for an accurate prediction.")
    else:
        st.toast("Analyzing profile against industry standards...", icon="🔍")
        
        # ML Prediction
        probs = pipeline.predict_proba([user_text])[0]
        prob_df = pd.DataFrame({"Career": classes, "Match Score": probs * 100}).sort_values(by="Match Score", ascending=False)
        top_roles = prob_df.head(5)
        
        top_career = top_roles.iloc[0]["Career"]
        top_score = top_roles.iloc[0]["Match Score"]

        st.markdown(f'<p class="big-font">🏆 Optimal Role: {top_career} ({top_score:.1f}% Match)</p>', unsafe_allow_html=True)
        st.progress(int(top_score))
        
        st.write("") # Spacer
        
        # --- UI TABS ---
        tab1, tab2, tab3 = st.tabs(["📊 Probability Chart", "🔍 Skill Gap & Market Data", "🗺️ Actionable Roadmap"])
        
        # TAB 1: CHART
        with tab1:
            chart = alt.Chart(top_roles).mark_bar(cornerRadiusEnd=6).encode(
                x=alt.X("Match Score:Q", title="Match Probability (%)", scale=alt.Scale(domain=[0, 100])),
                y=alt.Y("Career:N", sort="-x", title=""),
                color=alt.Color("Match Score:Q", scale=alt.Scale(scheme="viridis"), legend=None),
                tooltip=["Career", alt.Tooltip("Match Score:Q", format=".1f")]
            ).properties(height=320)
            st.altair_chart(chart, use_container_width=True)

        # TAB 2: SKILL GAP
        with tab2:
            col_a, col_b = st.columns([1, 2])
            role_data = metadata[top_career]
            
            with col_a:
                st.info(f"**Expected Salary:**\n\n{role_data['salary_range']}")
                st.warning(f"**Market Difficulty:**\n\n{role_data['difficulty']}")
            
            with col_b:
                st.write("**Core Competencies:**")
                core_html = "".join([create_badge(s, check_skill_match(s, user_text)) for s in role_data["core_skills"]])
                st.markdown(core_html, unsafe_allow_html=True)
                
                st.write("**Bonus / Stand-Out Skills:**")
                bonus_html = "".join([create_badge(s, check_skill_match(s, user_text)) for s in role_data["bonus_skills"]])
                st.markdown(bonus_html, unsafe_allow_html=True)

        # TAB 3: ROADMAP & EXPORT
        with tab3:
            phases = get_roadmap(top_career, metadata)
            roadmap_md = f"# Your Custom Roadmap: {top_career}\n\n"
            
            for title, desc in phases:
                with st.expander(title, expanded=True):
                    st.markdown(desc)
                # Append to our string for downloading
                roadmap_md += f"### {title}\n{desc}\n\n"
            
            st.divider()
            # File Download Button
            st.download_button(
                label="📥 Download Roadmap (.md)",
                data=roadmap_md,
                file_name=f"{top_career.replace(' ', '_')}_Roadmap.md",
                mime="text/markdown",
                type="primary"
            )