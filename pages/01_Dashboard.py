import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import require_auth, inject_theme, current_name, current_user, get_history

st.set_page_config(page_title="Dashboard · Vision", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")
require_auth()
inject_theme()

# ── sidebar ──────────────────────────────────────────────────────────────────
from auth import logout_session
with st.sidebar:
    st.markdown(f"""
    <div style='padding:16px 0 8px 0;'>
        <div style='font-size:20px;font-weight:800;color:#fff;'>🔭 Vision</div>
        <div style='font-size:12px;color:rgba(255,255,255,0.35);margin-top:2px;'>Careers AI Platform</div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.08);margin:8px 0 16px 0;'/>
    """, unsafe_allow_html=True)
    st.page_link("pages/01_Dashboard.py",   label="🏠  Dashboard",     )
    st.page_link("pages/02_Analyzer.py",    label="🔬  Analyzer",      )
    st.page_link("pages/03_History.py",     label="📋  History",       )
    st.page_link("pages/04_Compare.py",     label="⚖️  Compare Roles", )
    st.page_link("pages/05_Job_Board.py",   label="💼  Job Board",     )
    st.page_link("pages/06_Settings.py",    label="⚙️  Settings",      )
    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:16px 0 8px 0;'/>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:12px;color:rgba(255,255,255,0.35);padding-bottom:4px;'>Signed in as</div><div style='font-size:13px;color:rgba(255,255,255,0.7);font-weight:600;'>{current_user()}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("🚪  Sign Out", use_container_width=True):
        logout_session()
        st.switch_page("app.py")

# ── page content ─────────────────────────────────────────────────────────────
name = current_name()
history = get_history(current_user())

st.markdown(f"<div class='page-title'>Welcome back, {name.split('@')[0].title()} 👋</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Here's your career intelligence overview</div>", unsafe_allow_html=True)

# ── stats row ────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
analyses_count = len(history)
top_role = history[-1]["top_career"] if history else "—"
top_score = f"{history[-1]['top_score']:.0f}%" if history else "—"
roles_explored = len(set(h["top_career"] for h in history)) if history else 0

c1.metric("Analyses Run", analyses_count, delta="+1" if analyses_count > 0 else None)
c2.metric("Best Match Role", top_role)
c3.metric("Best Match Score", top_score)
c4.metric("Roles Explored", roles_explored)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── quick actions ─────────────────────────────────────────────────────────────
st.markdown("<div class='page-title' style='font-size:20px;'>Quick Actions</div>", unsafe_allow_html=True)
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

qa1, qa2, qa3, qa4 = st.columns(4)
with qa1:
    st.markdown("""
    <div class='card' style='text-align:center;cursor:pointer;'>
        <div style='font-size:32px;'>🔬</div>
        <div style='font-weight:700;font-size:15px;color:#fff;margin-top:8px;'>Analyze Resume</div>
        <div style='font-size:12px;color:rgba(255,255,255,0.4);margin-top:4px;'>Upload PDF or paste text</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Go to Analyzer", key="qa_analyzer", use_container_width=True):
        st.switch_page("pages/02_Analyzer.py")

with qa2:
    st.markdown("""
    <div class='card' style='text-align:center;cursor:pointer;'>
        <div style='font-size:32px;'>⚖️</div>
        <div style='font-weight:700;font-size:15px;color:#fff;margin-top:8px;'>Compare Roles</div>
        <div style='font-size:12px;color:rgba(255,255,255,0.4);margin-top:4px;'>Side-by-side comparison</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Go to Compare", key="qa_compare", use_container_width=True):
        st.switch_page("pages/04_Compare.py")

with qa3:
    st.markdown("""
    <div class='card' style='text-align:center;cursor:pointer;'>
        <div style='font-size:32px;'>💼</div>
        <div style='font-weight:700;font-size:15px;color:#fff;margin-top:8px;'>Browse Jobs</div>
        <div style='font-size:12px;color:rgba(255,255,255,0.4);margin-top:4px;'>Curated openings by role</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Go to Job Board", key="qa_jobs", use_container_width=True):
        st.switch_page("pages/05_Job_Board.py")

with qa4:
    st.markdown("""
    <div class='card' style='text-align:center;cursor:pointer;'>
        <div style='font-size:32px;'>📋</div>
        <div style='font-weight:700;font-size:15px;color:#fff;margin-top:8px;'>View History</div>
        <div style='font-size:12px;color:rgba(255,255,255,0.4);margin-top:4px;'>Past analyses & roadmaps</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Go to History", key="qa_history", use_container_width=True):
        st.switch_page("pages/03_History.py")

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── recent activity ───────────────────────────────────────────────────────────
st.markdown("<div class='page-title' style='font-size:20px;'>Recent Activity</div>", unsafe_allow_html=True)
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

if not history:
    st.markdown("""
    <div class='card' style='text-align:center;padding:40px;'>
        <div style='font-size:40px;'>🚀</div>
        <div style='font-size:16px;font-weight:600;color:#fff;margin-top:12px;'>No analyses yet</div>
        <div style='font-size:13px;color:rgba(255,255,255,0.4);margin-top:6px;'>Run your first analysis to see your career match results here.</div>
    </div>""", unsafe_allow_html=True)
else:
    import pandas as pd
    recent = list(reversed(history[-5:]))
    rows = []
    for h in recent:
        rows.append({
            "Date": h.get("date", "—"),
            "Top Career Match": h.get("top_career", "—"),
            "Match Score": f"{h.get('top_score', 0):.1f}%",
            "Input Type": h.get("input_type", "—"),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── platform features ────────────────────────────────────────────────────────
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.markdown("<div class='page-title' style='font-size:20px;'>Platform Features</div>", unsafe_allow_html=True)
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("""<div class='card'>
        <div style='font-size:24px;'>🤖</div>
        <div style='font-weight:700;color:#a78bfa;margin-top:8px;'>ML-Powered Matching</div>
        <div style='font-size:13px;color:rgba(255,255,255,0.5);margin-top:6px;line-height:1.6;'>
        TF-IDF + Logistic Regression trained on 15 tech roles. Predicts your best-fit career path with probability scores.
        </div></div>""", unsafe_allow_html=True)
with f2:
    st.markdown("""<div class='card'>
        <div style='font-size:24px;'>📊</div>
        <div style='font-weight:700;color:#60a5fa;margin-top:8px;'>Skill Gap Analysis</div>
        <div style='font-size:13px;color:rgba(255,255,255,0.5);margin-top:6px;line-height:1.6;'>
        See exactly which core and bonus skills you have vs. what employers want. Green = you have it. Red = learn it next.
        </div></div>""", unsafe_allow_html=True)
with f3:
    st.markdown("""<div class='card'>
        <div style='font-size:24px;'>🗺️</div>
        <div style='font-weight:700;color:#34d399;margin-top:8px;'>Custom Roadmaps</div>
        <div style='font-size:13px;color:rgba(255,255,255,0.5);margin-top:6px;line-height:1.6;'>
        3-phase learning roadmaps tailored to your target role. Download as Markdown and track your progress offline.
        </div></div>""", unsafe_allow_html=True)
