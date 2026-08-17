import streamlit as st
import sys, os, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import require_auth, render_sidebar, current_name, current_user, get_history

require_auth()
st.set_page_config(page_title="Dashboard - Vision", page_icon="&#127968;", layout="wide", initial_sidebar_state="expanded")
render_sidebar("dashboard")

name    = current_name()
email   = current_user()
history = get_history(email)

st.markdown(f"<div class='page-title'>Welcome back, {name.split('@')[0].title()} &#128075;</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Here's your career intelligence overview</div>", unsafe_allow_html=True)

# ── stats ─────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
count      = len(history)
top_role   = history[-1]["top_career"] if history else "-"
top_score  = f"{history[-1]['top_score']:.0f}%" if history else "-"
unique     = len(set(h["top_career"] for h in history)) if history else 0

c1.metric("Analyses Run",    count)
c2.metric("Last Match Role", top_role)
c3.metric("Last Score",      top_score)
c4.metric("Roles Explored",  unique)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── quick actions ─────────────────────────────────────────────────────────────
st.markdown("<div style='font-size:20px;font-weight:700;color:#fff;margin-bottom:12px;'>Quick Actions</div>", unsafe_allow_html=True)
qa1, qa2, qa3, qa4 = st.columns(4)

with qa1:
    st.markdown("<div class='card' style='text-align:center;'><div style='font-size:32px;'>&#128302;</div><div style='font-weight:700;color:#fff;margin-top:8px;'>Analyze Resume</div><div style='font-size:12px;color:rgba(255,255,255,0.4);margin-top:4px;'>Upload PDF, LinkedIn or paste text</div></div>", unsafe_allow_html=True)
    if st.button("Open Analyzer", key="qa1", use_container_width=True):
        st.switch_page("pages/analyzer.py")

with qa2:
    st.markdown("<div class='card' style='text-align:center;'><div style='font-size:32px;'>&#9878;</div><div style='font-weight:700;color:#fff;margin-top:8px;'>Compare Roles</div><div style='font-size:12px;color:rgba(255,255,255,0.4);margin-top:4px;'>Side-by-side comparison</div></div>", unsafe_allow_html=True)
    if st.button("Open Compare", key="qa2", use_container_width=True):
        st.switch_page("pages/compare.py")

with qa3:
    st.markdown("<div class='card' style='text-align:center;'><div style='font-size:32px;'>&#128188;</div><div style='font-weight:700;color:#fff;margin-top:8px;'>Job Board</div><div style='font-size:12px;color:rgba(255,255,255,0.4);margin-top:4px;'>Curated openings by role</div></div>", unsafe_allow_html=True)
    if st.button("Open Job Board", key="qa3", use_container_width=True):
        st.switch_page("pages/jobs.py")

with qa4:
    st.markdown("<div class='card' style='text-align:center;'><div style='font-size:32px;'>&#128203;</div><div style='font-weight:700;color:#fff;margin-top:8px;'>View History</div><div style='font-size:12px;color:rgba(255,255,255,0.4);margin-top:4px;'>Past analyses and roadmaps</div></div>", unsafe_allow_html=True)
    if st.button("Open History", key="qa4", use_container_width=True):
        st.switch_page("pages/history.py")

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── recent activity ───────────────────────────────────────────────────────────
st.markdown("<div style='font-size:20px;font-weight:700;color:#fff;margin-bottom:12px;'>Recent Activity</div>", unsafe_allow_html=True)

if not history:
    st.markdown(
        "<div class='card' style='text-align:center;padding:40px;'>"
        "<div style='font-size:40px;'>&#128640;</div>"
        "<div style='font-size:16px;font-weight:600;color:#fff;margin-top:12px;'>No analyses yet</div>"
        "<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-top:6px;'>Run your first analysis to see results here.</div>"
        "</div>", unsafe_allow_html=True
    )
else:
    recent = list(reversed(history[-5:]))
    rows = [{"Date": h.get("date","?"), "Top Career Match": h.get("top_career","?"),
             "Match Score": f"{h.get('top_score',0):.1f}%", "Input Type": h.get("input_type","?")}
            for h in recent]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── platform features ─────────────────────────────────────────────────────────
st.markdown("<div style='font-size:20px;font-weight:700;color:#fff;margin-bottom:12px;'>Platform Features</div>", unsafe_allow_html=True)
f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("<div class='card'><div style='font-size:24px;'>&#129302;</div><div style='font-weight:700;color:#a78bfa;margin-top:8px;'>ML-Powered Matching</div><div style='font-size:13px;color:rgba(255,255,255,0.5);margin-top:6px;line-height:1.6;'>TF-IDF + Logistic Regression trained on 15 tech roles with probability scores.</div></div>", unsafe_allow_html=True)
with f2:
    st.markdown("<div class='card'><div style='font-size:24px;'>&#128202;</div><div style='font-weight:700;color:#60a5fa;margin-top:8px;'>Skill Gap Analysis</div><div style='font-size:13px;color:rgba(255,255,255,0.5);margin-top:6px;line-height:1.6;'>See exactly which core and bonus skills you have vs what employers want.</div></div>", unsafe_allow_html=True)
with f3:
    st.markdown("<div class='card'><div style='font-size:24px;'>&#128506;</div><div style='font-weight:700;color:#34d399;margin-top:8px;'>Custom Roadmaps</div><div style='font-size:13px;color:rgba(255,255,255,0.5);margin-top:6px;line-height:1.6;'>3-phase learning roadmaps tailored to your target role. Download as Markdown.</div></div>", unsafe_allow_html=True)
