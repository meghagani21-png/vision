import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from auth import is_logged_in

# hide the default Streamlit nav bar with CSS — we use our own sidebar buttons
st.markdown("""
<style>
[data-testid="stSidebarNav"]          { display: none !important; }
[data-testid="stSidebarNavItems"]     { display: none !important; }
[data-testid="stSidebarNavSeparator"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── page definitions ──────────────────────────────────────────────────────────
pg_login        = st.Page("pages/login.py",        title="Login",           icon="🔑", default=True)
pg_dashboard    = st.Page("pages/dashboard.py",    title="Dashboard",       icon="🏠")
pg_analyzer     = st.Page("pages/analyzer.py",     title="Analyzer",        icon="🔬")
pg_history      = st.Page("pages/history.py",      title="History",         icon="📋")
pg_compare      = st.Page("pages/compare.py",      title="Compare Roles",   icon="⚖️")
pg_jobs         = st.Page("pages/jobs.py",          title="Job Board",       icon="💼")
pg_interview    = st.Page("pages/interview.py",     title="Interview Coach", icon="🧠")
pg_skill_radar  = st.Page("pages/skill_radar.py",   title="Skill Radar",     icon="📊")
pg_achievements = st.Page("pages/achievements.py",  title="Achievements",    icon="🏆")
pg_resume_tips  = st.Page("pages/resume_tips.py",   title="Resume Tips",     icon="📝")
pg_market_pulse = st.Page("pages/market_pulse.py",  title="Market Pulse",    icon="🌐")
pg_settings     = st.Page("pages/settings.py",      title="Settings",        icon="⚙️")

if is_logged_in():
    nav = st.navigation(
        [pg_dashboard, pg_analyzer, pg_history, pg_compare, pg_jobs,
         pg_interview, pg_skill_radar, pg_achievements, pg_resume_tips, pg_market_pulse,
         pg_settings],
        position="sidebar"
    )
else:
    nav = st.navigation([pg_login], position="sidebar")

nav.run()
