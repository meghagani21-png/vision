import sys, os, math
import streamlit as st
import pandas as pd
import altair as alt
import joblib
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import require_auth, render_sidebar, current_user, get_history

require_auth()
st.set_page_config(page_title="Skill Radar - Vision", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
render_sidebar("skill_radar")

@st.cache_resource
def load_model():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model.pkl")
    return joblib.load(path) if os.path.exists(path) else None

model_payload = load_model()
if model_payload is None:
    st.error("model.pkl not found."); st.stop()
metadata = model_payload["career_metadata"]
pipeline = model_payload["pipeline"]

# ── page ──────────────────────────────────────────────────────────────────────
st.markdown("<div class='page-title'>📊 Skill Radar & Analytics</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Visualize your career profile strength and track your growth over time</div>", unsafe_allow_html=True)

email = current_user()
history = get_history(email)

if not history:
    st.markdown(
        "<div class='glow-card' style='text-align:center;padding:48px;'>"
        "<div style='font-size:48px;'>📊</div>"
        "<div style='font-size:18px;font-weight:700;color:#fff;margin-top:14px;'>No data yet</div>"
        "<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-top:6px;'>"
        "Run your first analysis in the Analyzer to see your Skill Radar.</div></div>",
        unsafe_allow_html=True
    )
    if st.button("Go to Analyzer", type="primary"):
        st.switch_page("pages/analyzer.py")
    st.stop()

# ── Job Readiness Score ───────────────────────────────────────────────────────
latest = history[-1]
top_score = latest.get("top_score", 0)
analyses_count = len(history)
roles_explored = len(set(h["top_career"] for h in history))
avg_score = sum(h.get("top_score", 0) for h in history) / len(history)

# Compute readiness as composite of top score, consistency, and breadth
readiness = min(100, (top_score * 0.5) + (min(avg_score, 100) * 0.3) + (min(roles_explored * 5, 100) * 0.2))

readiness_color = "#34d399" if readiness >= 70 else ("#fbbf24" if readiness >= 40 else "#f87171")
readiness_label = "Excellent" if readiness >= 80 else ("Good" if readiness >= 60 else ("Building" if readiness >= 40 else "Getting Started"))

st.markdown(
    f"<div class='glow-card' style='padding:28px;'>"
    f"<div style='display:flex;align-items:center;gap:28px;flex-wrap:wrap;'>"
    f"<div class='score-ring' style='background:conic-gradient({readiness_color} {readiness*3.6}deg, rgba(255,255,255,0.06) 0deg);'>"
    f"<div style='width:96px;height:96px;border-radius:50%;background:#0e0e1a;display:flex;align-items:center;justify-content:center;'>"
    f"<div style='text-align:center;'>"
    f"<div style='font-size:28px;font-weight:900;color:{readiness_color};'>{readiness:.0f}</div>"
    f"<div style='font-size:10px;color:rgba(255,255,255,0.4);'>READINESS</div>"
    f"</div></div></div>"
    f"<div style='flex:1;min-width:200px;'>"
    f"<div style='font-size:20px;font-weight:800;color:#fff;'>Job Readiness Score</div>"
    f"<div style='font-size:14px;color:{readiness_color};font-weight:600;margin-top:4px;'>{readiness_label}</div>"
    f"<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-top:8px;line-height:1.6;'>"
    f"Based on your match scores, consistency across analyses, and breadth of roles explored.</div>"
    f"</div>"
    f"<div style='display:flex;gap:20px;flex-wrap:wrap;'>"
    f"<div style='text-align:center;'><div style='font-size:24px;font-weight:800;color:#a78bfa;'>{analyses_count}</div>"
    f"<div style='font-size:11px;color:rgba(255,255,255,0.35);'>Analyses</div></div>"
    f"<div style='text-align:center;'><div style='font-size:24px;font-weight:800;color:#60a5fa;'>{roles_explored}</div>"
    f"<div style='font-size:11px;color:rgba(255,255,255,0.35);'>Roles</div></div>"
    f"<div style='text-align:center;'><div style='font-size:24px;font-weight:800;color:#34d399;'>{avg_score:.0f}%</div>"
    f"<div style='font-size:11px;color:rgba(255,255,255,0.35);'>Avg Score</div></div>"
    f"</div></div></div>",
    unsafe_allow_html=True
)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_radar, tab_heatmap, tab_growth = st.tabs(["🎯 Skill Radar", "🔥 Role Heatmap", "📈 Growth Tracker"])

# ── Skill Radar Chart ─────────────────────────────────────────────────────────
with tab_radar:
    top_career = latest.get("top_career", list(metadata.keys())[0])
    all_roles_list = sorted(metadata.keys())
    selected = st.selectbox("Select Role for Radar", all_roles_list,
                            index=all_roles_list.index(top_career) if top_career in all_roles_list else 0)
    role_meta = metadata[selected]
    all_skills = role_meta["core_skills"] + role_meta["bonus_skills"]

    # Build radar data using the latest analysis scores
    last_all_roles = latest.get("all_roles", [])
    role_scores = {r["Career"]: r["Match Score"] for r in last_all_roles}
    
    # Create dimensions for radar based on skill categories
    dimensions = ["Core Skills", "Bonus Skills", "Match Score", "Market Readiness", "Versatility", "Growth Potential"]
    core_pct = len(role_meta["core_skills"]) / max(1, len(all_skills)) * 100
    match_pct = role_scores.get(selected, top_score)
    versatility = min(100, roles_explored * 15)
    growth = min(100, analyses_count * 10)
    market = 80 if role_meta.get("difficulty") in ["Medium", "Low"] else (60 if role_meta.get("difficulty") == "High" else 45)

    radar_values = [core_pct, 100 - core_pct, match_pct, market, versatility, growth]
    
    # Create radar as layered Altair chart
    radar_df = pd.DataFrame({
        "Dimension": dimensions,
        "Score": radar_values,
        "angle": [i * (360 / len(dimensions)) for i in range(len(dimensions))]
    })

    # Use Altair radial chart
    base = alt.Chart(radar_df).encode(
        theta=alt.Theta("Dimension:N", sort=dimensions),
        radius=alt.Radius("Score:Q", scale=alt.Scale(domain=[0, 100])),
        color=alt.value("#a78bfa"),
        tooltip=["Dimension:N", alt.Tooltip("Score:Q", format=".0f")]
    )

    chart = base.mark_arc(innerRadius=20, stroke="#a78bfa", strokeWidth=2).encode(
        opacity=alt.value(0.3)
    ).properties(height=350, title=f"Skill Profile: {selected}")

    chart = chart.configure_view(strokeWidth=0).configure_title(color="#fff", fontSize=16)
    st.altair_chart(chart, use_container_width=True)

    # Skill breakdown
    st.markdown("<div style='font-size:16px;font-weight:700;color:#fff;margin:16px 0 10px 0;'>Skill Categories</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            "<div class='card'><div style='font-size:12px;color:rgba(255,255,255,0.4);text-transform:uppercase;"
            "letter-spacing:1px;margin-bottom:10px;'>Core Skills</div>"
            + "".join([f"<span style='display:inline-block;background:rgba(167,139,250,0.15);border:1px solid rgba(167,139,250,0.3);"
                       f"border-radius:20px;padding:4px 12px;margin:3px;font-size:13px;color:#a78bfa;'>{s}</span>"
                       for s in role_meta["core_skills"]])
            + "</div>",
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            "<div class='card'><div style='font-size:12px;color:rgba(255,255,255,0.4);text-transform:uppercase;"
            "letter-spacing:1px;margin-bottom:10px;'>Bonus Skills</div>"
            + "".join([f"<span style='display:inline-block;background:rgba(96,165,250,0.15);border:1px solid rgba(96,165,250,0.3);"
                       f"border-radius:20px;padding:4px 12px;margin:3px;font-size:13px;color:#60a5fa;'>{s}</span>"
                       for s in role_meta["bonus_skills"]])
            + "</div>",
            unsafe_allow_html=True
        )

# ── Role Heatmap ──────────────────────────────────────────────────────────────
with tab_heatmap:
    st.markdown(
        "<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-bottom:16px;'>"
        "Shows how your latest profile maps across all 15 career roles</div>",
        unsafe_allow_html=True
    )
    
    last_all_roles = latest.get("all_roles", [])
    if last_all_roles:
        heatmap_df = pd.DataFrame(last_all_roles).sort_values("Match Score", ascending=False)
        
        chart = (
            alt.Chart(heatmap_df)
            .mark_bar(cornerRadiusEnd=8)
            .encode(
                x=alt.X("Match Score:Q", title="Match Score (%)", scale=alt.Scale(domain=[0, 100])),
                y=alt.Y("Career:N", sort="-x", title=""),
                color=alt.Color("Match Score:Q",
                    scale=alt.Scale(scheme="viridis", domain=[0, 100]),
                    legend=None
                ),
                tooltip=["Career:N", alt.Tooltip("Match Score:Q", format=".1f")]
            )
            .properties(height=400)
            .configure_view(strokeWidth=0)
            .configure_axis(labelColor="#aaa", titleColor="#aaa", gridColor="rgba(255,255,255,0.05)")
        )
        st.altair_chart(chart, use_container_width=True)

        # Top 3 insights
        top3 = heatmap_df.head(3)
        st.markdown("<div style='font-size:16px;font-weight:700;color:#fff;margin:12px 0;'>🎯 Your Top 3 Matches</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        colors = ["#a78bfa", "#60a5fa", "#34d399"]
        medals = ["🥇", "🥈", "🥉"]
        for i, (_, row) in enumerate(top3.iterrows()):
            with cols[i]:
                st.markdown(
                    f"<div class='card' style='text-align:center;border-color:rgba({','.join([str(int(colors[i][j:j+2],16)) for j in (1,3,5)])},0.3);'>"
                    f"<div style='font-size:28px;'>{medals[i]}</div>"
                    f"<div style='font-size:16px;font-weight:700;color:{colors[i]};margin-top:6px;'>{row['Career']}</div>"
                    f"<div style='font-size:24px;font-weight:800;color:#fff;margin-top:4px;'>{row['Match Score']:.1f}%</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
    else:
        st.info("Run an analysis to see your role heatmap.")

# ── Growth Tracker ────────────────────────────────────────────────────────────
with tab_growth:
    st.markdown(
        "<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-bottom:16px;'>"
        "Track how your match scores evolve over time</div>",
        unsafe_allow_html=True
    )
    
    if len(history) >= 2:
        growth_data = []
        for i, h in enumerate(history):
            growth_data.append({
                "Analysis #": i + 1,
                "Date": h.get("date", f"#{i+1}"),
                "Score": h.get("top_score", 0),
                "Role": h.get("top_career", "?"),
            })
        growth_df = pd.DataFrame(growth_data)

        line_chart = (
            alt.Chart(growth_df)
            .mark_line(point=True, strokeWidth=3, color="#a78bfa")
            .encode(
                x=alt.X("Analysis #:Q", title="Analysis Number", axis=alt.Axis(tickMinStep=1)),
                y=alt.Y("Score:Q", title="Match Score (%)", scale=alt.Scale(domain=[0, 100])),
                tooltip=["Date:N", "Role:N", alt.Tooltip("Score:Q", format=".1f")]
            )
            .properties(height=300)
            .configure_view(strokeWidth=0)
            .configure_axis(labelColor="#aaa", titleColor="#aaa", gridColor="rgba(255,255,255,0.05)")
        )
        st.altair_chart(line_chart, use_container_width=True)

        # Trend analysis
        first_score = history[0].get("top_score", 0)
        last_score = history[-1].get("top_score", 0)
        delta = last_score - first_score
        trend_icon = "📈" if delta > 0 else ("📉" if delta < 0 else "➡️")
        trend_color = "#34d399" if delta > 0 else ("#f87171" if delta < 0 else "#fbbf24")

        st.markdown(
            f"<div class='card' style='display:flex;gap:32px;flex-wrap:wrap;align-items:center;'>"
            f"<div><span style='font-size:28px;'>{trend_icon}</span></div>"
            f"<div><div style='font-size:14px;font-weight:700;color:#fff;'>Score Trend</div>"
            f"<div style='font-size:22px;font-weight:800;color:{trend_color};'>{delta:+.1f}%</div>"
            f"<div style='font-size:12px;color:rgba(255,255,255,0.4);'>from first to latest analysis</div></div>"
            f"<div><div style='font-size:14px;font-weight:700;color:#fff;'>Best Score</div>"
            f"<div style='font-size:22px;font-weight:800;color:#a78bfa;'>{max(h.get('top_score',0) for h in history):.1f}%</div></div>"
            f"<div><div style='font-size:14px;font-weight:700;color:#fff;'>Average</div>"
            f"<div style='font-size:22px;font-weight:800;color:#60a5fa;'>{avg_score:.1f}%</div></div>"
            f"</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div class='card' style='text-align:center;padding:40px;'>"
            "<div style='font-size:36px;'>📈</div>"
            "<div style='font-size:16px;font-weight:600;color:#fff;margin-top:12px;'>Need more data</div>"
            "<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-top:6px;'>"
            "Run at least 2 analyses to see your growth trend.</div></div>",
            unsafe_allow_html=True
        )
