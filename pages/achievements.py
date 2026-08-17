import sys, os, datetime
import streamlit as st
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import require_auth, render_sidebar, current_user, get_history

require_auth()
st.set_page_config(page_title="Achievements - Vision", page_icon="🏆", layout="wide", initial_sidebar_state="expanded")
render_sidebar("achievements")

# ── Achievement definitions ──────────────────────────────────────────────────
ACHIEVEMENTS = [
    {
        "id": "first_analysis", "icon": "🚀", "title": "First Launch",
        "desc": "Complete your first career analysis",
        "check": lambda h, **kw: len(h) >= 1, "tier": "bronze",
    },
    {
        "id": "three_analyses", "icon": "🔬", "title": "Researcher",
        "desc": "Complete 3 career analyses",
        "check": lambda h, **kw: len(h) >= 3, "tier": "bronze",
    },
    {
        "id": "five_analyses", "icon": "🧪", "title": "Lab Expert",
        "desc": "Complete 5 career analyses",
        "check": lambda h, **kw: len(h) >= 5, "tier": "silver",
    },
    {
        "id": "ten_analyses", "icon": "⚡", "title": "Power User",
        "desc": "Complete 10 career analyses",
        "check": lambda h, **kw: len(h) >= 10, "tier": "gold",
    },
    {
        "id": "twenty_analyses", "icon": "💎", "title": "Diamond Analyst",
        "desc": "Complete 20 career analyses",
        "check": lambda h, **kw: len(h) >= 20, "tier": "platinum",
    },
    {
        "id": "high_score", "icon": "🎯", "title": "Sharpshooter",
        "desc": "Get a match score above 80%",
        "check": lambda h, **kw: any(x.get("top_score", 0) > 80 for x in h), "tier": "silver",
    },
    {
        "id": "perfect_score", "icon": "💯", "title": "Perfect Match",
        "desc": "Get a match score above 95%",
        "check": lambda h, **kw: any(x.get("top_score", 0) > 95 for x in h), "tier": "gold",
    },
    {
        "id": "three_roles", "icon": "🔀", "title": "Explorer",
        "desc": "Get matched to 3 different roles",
        "check": lambda h, **kw: len(set(x.get("top_career", "") for x in h)) >= 3, "tier": "bronze",
    },
    {
        "id": "five_roles", "icon": "🌍", "title": "World Traveler",
        "desc": "Get matched to 5 different roles",
        "check": lambda h, **kw: len(set(x.get("top_career", "") for x in h)) >= 5, "tier": "silver",
    },
    {
        "id": "all_roles", "icon": "👑", "title": "Renaissance",
        "desc": "Get matched to 10+ different roles",
        "check": lambda h, **kw: len(set(x.get("top_career", "") for x in h)) >= 10, "tier": "platinum",
    },
    {
        "id": "pdf_upload", "icon": "📄", "title": "Resume Ready",
        "desc": "Upload a PDF resume for analysis",
        "check": lambda h, **kw: any(x.get("input_type", "") == "PDF" for x in h), "tier": "bronze",
    },
    {
        "id": "consistent", "icon": "📊", "title": "Consistent",
        "desc": "Maintain 70%+ score across 3 analyses",
        "check": lambda h, **kw: len([x for x in h if x.get("top_score", 0) >= 70]) >= 3, "tier": "silver",
    },
    {
        "id": "improving", "icon": "📈", "title": "On the Rise",
        "desc": "Improve your score in consecutive analyses",
        "check": lambda h, **kw: len(h) >= 2 and h[-1].get("top_score", 0) > h[-2].get("top_score", 0), "tier": "bronze",
    },
    {
        "id": "multi_input", "icon": "🔄", "title": "Multi-Modal",
        "desc": "Use both PDF upload and text input",
        "check": lambda h, **kw: len(set(x.get("input_type", "") for x in h)) >= 2, "tier": "silver",
    },
    {
        "id": "streak_3", "icon": "🔥", "title": "Hot Streak",
        "desc": "Analyze on 3 different days",
        "check": lambda h, **kw: len(set(x.get("date", "")[:10] for x in h)) >= 3, "tier": "gold",
    },
]

TIER_STYLES = {
    "bronze":   {"bg": "linear-gradient(135deg, rgba(205,127,50,0.15), rgba(205,127,50,0.05))",
                 "border": "rgba(205,127,50,0.4)", "color": "#cd7f32", "label": "Bronze"},
    "silver":   {"bg": "linear-gradient(135deg, rgba(192,192,192,0.15), rgba(192,192,192,0.05))",
                 "border": "rgba(192,192,192,0.4)", "color": "#c0c0c0", "label": "Silver"},
    "gold":     {"bg": "linear-gradient(135deg, rgba(255,215,0,0.15), rgba(255,215,0,0.05))",
                 "border": "rgba(255,215,0,0.4)", "color": "#ffd700", "label": "Gold"},
    "platinum": {"bg": "linear-gradient(135deg, rgba(167,139,250,0.15), rgba(96,165,250,0.05))",
                 "border": "rgba(167,139,250,0.4)", "color": "#a78bfa", "label": "Platinum"},
}

# ── page ──────────────────────────────────────────────────────────────────────
st.markdown("<div class='page-title'>🏆 Achievements</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Level up your career journey — unlock badges as you explore, analyze, and grow</div>", unsafe_allow_html=True)

email = current_user()
history = get_history(email)

# Calculate achievements
unlocked = []
locked = []
for ach in ACHIEVEMENTS:
    is_unlocked = ach["check"](history)
    if is_unlocked:
        unlocked.append(ach)
    else:
        locked.append(ach)

total = len(ACHIEVEMENTS)
unlocked_count = len(unlocked)
progress_pct = (unlocked_count / total * 100) if total > 0 else 0

# ── Progress banner ──────────────────────────────────────────────────────────
level = "Beginner" if unlocked_count < 4 else ("Intermediate" if unlocked_count < 8 else ("Advanced" if unlocked_count < 12 else "Legend"))
level_icon = "🌱" if unlocked_count < 4 else ("⚡" if unlocked_count < 8 else ("🌟" if unlocked_count < 12 else "👑"))

st.markdown(
    f"<div class='glow-card' style='padding:28px;'>"
    f"<div style='display:flex;align-items:center;gap:24px;flex-wrap:wrap;'>"
    f"<div style='font-size:48px;'>{level_icon}</div>"
    f"<div style='flex:1;min-width:200px;'>"
    f"<div style='font-size:13px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;'>Your Level</div>"
    f"<div style='font-size:24px;font-weight:800;color:#fff;margin-top:2px;'>{level}</div>"
    f"<div style='margin-top:12px;background:rgba(255,255,255,0.06);border-radius:10px;height:12px;overflow:hidden;'>"
    f"<div style='width:{progress_pct}%;height:100%;background:linear-gradient(90deg,#7c3aed,#60a5fa);border-radius:10px;"
    f"transition:width 0.5s ease;'></div></div>"
    f"<div style='font-size:12px;color:rgba(255,255,255,0.4);margin-top:6px;'>"
    f"{unlocked_count}/{total} achievements unlocked</div>"
    f"</div>"
    f"<div style='display:flex;gap:20px;'>"
    f"<div style='text-align:center;'>"
    f"<div style='font-size:28px;font-weight:800;color:#a78bfa;'>{unlocked_count}</div>"
    f"<div style='font-size:11px;color:rgba(255,255,255,0.35);'>Unlocked</div></div>"
    f"<div style='text-align:center;'>"
    f"<div style='font-size:28px;font-weight:800;color:rgba(255,255,255,0.2);'>{len(locked)}</div>"
    f"<div style='font-size:11px;color:rgba(255,255,255,0.35);'>Locked</div></div>"
    f"</div></div></div>",
    unsafe_allow_html=True
)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── Unlocked achievements ────────────────────────────────────────────────────
if unlocked:
    st.markdown("<div style='font-size:18px;font-weight:700;color:#fff;margin-bottom:14px;'>✨ Unlocked</div>", unsafe_allow_html=True)
    cols = st.columns(min(4, len(unlocked)))
    for i, ach in enumerate(unlocked):
        ts = TIER_STYLES[ach["tier"]]
        with cols[i % min(4, len(unlocked))]:
            st.markdown(
                f"<div class='badge-unlocked' style='background:{ts['bg']};border-color:{ts['border']};'>"
                f"<div style='font-size:36px;margin-bottom:8px;'>{ach['icon']}</div>"
                f"<div style='font-size:14px;font-weight:700;color:#fff;'>{ach['title']}</div>"
                f"<div style='font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px;'>{ach['desc']}</div>"
                f"<div style='margin-top:8px;'>"
                f"<span style='background:rgba(255,255,255,0.1);border:1px solid {ts['border']};"
                f"color:{ts['color']};border-radius:12px;padding:2px 10px;font-size:10px;font-weight:700;'>"
                f"{ts['label']}</span></div>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ── Locked achievements ──────────────────────────────────────────────────────
if locked:
    st.markdown("<div style='font-size:18px;font-weight:700;color:rgba(255,255,255,0.5);margin-bottom:14px;'>🔒 Locked</div>", unsafe_allow_html=True)
    cols = st.columns(min(4, len(locked)))
    for i, ach in enumerate(locked):
        ts = TIER_STYLES[ach["tier"]]
        with cols[i % min(4, len(locked))]:
            st.markdown(
                f"<div class='badge-locked'>"
                f"<div style='font-size:36px;margin-bottom:8px;filter:grayscale(1);'>🔒</div>"
                f"<div style='font-size:14px;font-weight:700;color:rgba(255,255,255,0.4);'>{ach['title']}</div>"
                f"<div style='font-size:12px;color:rgba(255,255,255,0.25);margin-top:4px;'>{ach['desc']}</div>"
                f"<div style='margin-top:8px;'>"
                f"<span style='background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);"
                f"color:rgba(255,255,255,0.3);border-radius:12px;padding:2px 10px;font-size:10px;font-weight:700;'>"
                f"{ts['label']}</span></div>"
                f"</div>",
                unsafe_allow_html=True
            )

# ── Achievement stats ─────────────────────────────────────────────────────────
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
tiers_unlocked = {}
for ach in unlocked:
    tiers_unlocked[ach["tier"]] = tiers_unlocked.get(ach["tier"], 0) + 1

st.markdown(
    "<div class='card' style='padding:20px;'>"
    "<div style='font-size:16px;font-weight:700;color:#fff;margin-bottom:14px;'>Achievement Breakdown</div>"
    "<div style='display:flex;gap:24px;flex-wrap:wrap;'>"
    + "".join([
        f"<div style='text-align:center;min-width:80px;'>"
        f"<div style='font-size:22px;font-weight:800;color:{TIER_STYLES[tier]['color']};'>{tiers_unlocked.get(tier, 0)}</div>"
        f"<div style='font-size:12px;color:rgba(255,255,255,0.4);'>{TIER_STYLES[tier]['label']}</div></div>"
        for tier in ["bronze", "silver", "gold", "platinum"]
    ])
    + "</div></div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div style='text-align:center;font-size:12px;color:rgba(255,255,255,0.2);margin-top:16px;'>"
    "Achievements are based on your analysis history. Keep exploring to unlock more!</div>",
    unsafe_allow_html=True
)
