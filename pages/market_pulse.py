import sys, os
import streamlit as st
import pandas as pd
import altair as alt
import joblib
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import require_auth, render_sidebar, current_user, get_history

require_auth()
st.set_page_config(page_title="Market Pulse - Vision", page_icon="🌐", layout="wide", initial_sidebar_state="expanded")
render_sidebar("market_pulse")

@st.cache_resource
def load_model():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model.pkl")
    return joblib.load(path) if os.path.exists(path) else None

model_payload = load_model()
if model_payload is None:
    st.error("model.pkl not found."); st.stop()
metadata = model_payload["career_metadata"]
all_roles = sorted(metadata.keys())

# ── Mock Market Data ─────────────────────────────────────────────────────────
# In a real app, this would come from an API (e.g. Glassdoor, LinkedIn)
MARKET_DATA = {
    role: {
        "demand": "Hot" if metadata[role]["difficulty"] in ["High", "Very High"] else "Stable",
        "remote_friendly": 95 if "Engineer" in role or "Developer" in role else 75,
        "yoy_growth": 15 if "Data" in role or "ML" in role or "Cloud" in role else 5,
        "openings": (all_roles.index(role) + 1) * 1234,
    }
    for role in all_roles
}

# ── page ──────────────────────────────────────────────────────────────────────
st.markdown("<div class='page-title'>🌐 Career Market Pulse</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Real-time industry insights, demand trends, and market intelligence</div>", unsafe_allow_html=True)

# Select role
email = current_user()
history = get_history(email)
last_role = st.session_state.get("last_top_career") or (history[-1]["top_career"] if history else None)
default_idx = all_roles.index(last_role) if last_role and last_role in all_roles else 0

selected_role = st.selectbox("Select a Role to Analyze", all_roles, index=default_idx)
mdata = MARKET_DATA[selected_role]
rmeta = metadata[selected_role]

# ── Top Metrics ──────────────────────────────────────────────────────────────
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"<div class='card' style='text-align:center;padding:24px;'>"
        f"<div style='font-size:32px;'>🔥</div>"
        f"<div style='font-size:12px;color:rgba(255,255,255,0.4);text-transform:uppercase;margin-top:8px;'>Market Demand</div>"
        f"<div style='font-size:24px;font-weight:800;color:#f87171;margin-top:4px;'>{mdata['demand']}</div>"
        f"</div>",
        unsafe_allow_html=True
    )
with c2:
    st.markdown(
        f"<div class='card' style='text-align:center;padding:24px;'>"
        f"<div style='font-size:32px;'>📈</div>"
        f"<div style='font-size:12px;color:rgba(255,255,255,0.4);text-transform:uppercase;margin-top:8px;'>YoY Growth</div>"
        f"<div style='font-size:24px;font-weight:800;color:#34d399;margin-top:4px;'>+{mdata['yoy_growth']}%</div>"
        f"</div>",
        unsafe_allow_html=True
    )
with c3:
    st.markdown(
        f"<div class='card' style='text-align:center;padding:24px;'>"
        f"<div style='font-size:32px;'>🏠</div>"
        f"<div style='font-size:12px;color:rgba(255,255,255,0.4);text-transform:uppercase;margin-top:8px;'>Remote Index</div>"
        f"<div style='font-size:24px;font-weight:800;color:#60a5fa;margin-top:4px;'>{mdata['remote_friendly']}%</div>"
        f"</div>",
        unsafe_allow_html=True
    )
with c4:
    st.markdown(
        f"<div class='card' style='text-align:center;padding:24px;'>"
        f"<div style='font-size:32px;'>💰</div>"
        f"<div style='font-size:12px;color:rgba(255,255,255,0.4);text-transform:uppercase;margin-top:8px;'>Avg Salary</div>"
        f"<div style='font-size:20px;font-weight:800;color:#a78bfa;margin-top:4px;'>{rmeta['salary_range']}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── Trends & Skills ──────────────────────────────────────────────────────────
t1, t2 = st.columns(2)
with t1:
    st.markdown("<div style='font-size:18px;font-weight:700;color:#fff;margin-bottom:12px;'>📊 Salary Distribution</div>", unsafe_allow_html=True)
    # Mock data for distribution
    dist_data = pd.DataFrame({
        "Percentile": ["10th", "25th", "50th (Median)", "75th", "90th"],
        "Salary": [70000, 90000, 120000, 150000, 190000]
    })
    chart = (
        alt.Chart(dist_data)
        .mark_area(
            line={'color':'#60a5fa'},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='#60a5fa', offset=0),
                       alt.GradientStop(color='transparent', offset=1)],
                x1=1, x2=1, y1=1, y2=0
            )
        )
        .encode(
            x=alt.X("Percentile:N", sort=None),
            y=alt.Y("Salary:Q", title="Base Salary ($)"),
            tooltip=["Percentile", "Salary"]
        )
        .properties(height=250)
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, use_container_width=True)

with t2:
    st.markdown("<div style='font-size:18px;font-weight:700;color:#fff;margin-bottom:12px;'>🚀 Trending Tech Stack</div>", unsafe_allow_html=True)
    
    # Combine core/bonus skills and rank them (mock popularity)
    skills = rmeta["core_skills"] + rmeta["bonus_skills"]
    skill_df = pd.DataFrame({
        "Skill": skills,
        "Demand Score": [95 - (i*5) for i in range(len(skills))]
    })
    
    chart2 = (
        alt.Chart(skill_df)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X("Demand Score:Q", scale=alt.Scale(domain=[0,100])),
            y=alt.Y("Skill:N", sort="-x"),
            color=alt.Color("Demand Score:Q", scale=alt.Scale(scheme="purples"), legend=None),
            tooltip=["Skill", "Demand Score"]
        )
        .properties(height=250)
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart2, use_container_width=True)

# ── Job Market Heatmap ───────────────────────────────────────────────────────
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
st.markdown("<div style='font-size:18px;font-weight:700;color:#fff;margin-bottom:12px;'>🗺️ Top Hiring Hubs</div>", unsafe_allow_html=True)

# Mock city data
hubs = pd.DataFrame({
    "City": ["San Francisco", "New York", "Seattle", "Austin", "Remote", "London", "Toronto"],
    "Job Openings": [5400, 4200, 3100, 2800, 12500, 2200, 1800]
}).sort_values("Job Openings", ascending=False)

st.dataframe(
    hubs,
    column_config={
        "City": "Tech Hub",
        "Job Openings": st.column_config.ProgressColumn(
            "Active Roles",
            help="Current job openings",
            format="%f",
            min_value=0,
            max_value=15000,
        ),
    },
    hide_index=True,
    use_container_width=True
)

st.markdown(
    "<div style='text-align:center;font-size:12px;color:rgba(255,255,255,0.2);margin-top:20px;'>"
    "Market data is a simulation for demonstration purposes based on career metadata.</div>",
    unsafe_allow_html=True
)
