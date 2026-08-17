import sys, os, joblib
import streamlit as st
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import require_auth, render_sidebar, current_user, get_history

require_auth()
st.set_page_config(page_title="Compare Roles - Vision", page_icon="&#9878;", layout="wide", initial_sidebar_state="expanded")
render_sidebar("compare")

@st.cache_resource
def load_model():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model.pkl")
    return joblib.load(path) if os.path.exists(path) else None

model_payload = load_model()
if model_payload is None:
    st.error("model.pkl not found."); st.stop()

metadata  = model_payload["career_metadata"]
all_roles = sorted(metadata.keys())

st.markdown("<div class='page-title'>&#9878; Compare Career Roles</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Pick any two roles and compare salary, skills, and difficulty side by side</div>", unsafe_allow_html=True)

# ── auto-select last analyzed role ────────────────────────────────────────────
history       = get_history(current_user())
last_role     = st.session_state.get("last_top_career") or (history[-1]["top_career"] if history else None)
default_idx_a = all_roles.index(last_role) if last_role and last_role in all_roles else 0

if last_role:
    st.markdown(
        f"<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-bottom:12px;'>"
        f"&#128270; Auto-selected your last analyzed role: <b style='color:#a78bfa;'>{last_role}</b>"
        f"</div>",
        unsafe_allow_html=True
    )

col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    role_a = st.selectbox("Role A", all_roles, index=default_idx_a, key="role_a")
with col_sel2:
    default_idx_b = 1 if default_idx_a == 0 else 0
    role_b = st.selectbox("Role B", all_roles, index=default_idx_b, key="role_b")

if role_a == role_b:
    st.warning("Please select two different roles to compare.")
    st.stop()

da = metadata[role_a]
db = metadata[role_b]
DIFF_ORDER = {"Low": 1, "Medium": 2, "High": 3, "Very High": 4}

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── at a glance ───────────────────────────────────────────────────────────────
st.markdown("<div style='font-size:18px;font-weight:700;color:#fff;margin-bottom:12px;'>&#128202; At a Glance</div>", unsafe_allow_html=True)
g1, g2, g3, g4 = st.columns(4)
g1.metric(f"{role_a} Salary",     da["salary_range"])
g2.metric(f"{role_a} Difficulty", da["difficulty"])
g3.metric(f"{role_b} Salary",     db["salary_range"])
g4.metric(f"{role_b} Difficulty", db["difficulty"])

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── skills breakdown ──────────────────────────────────────────────────────────
st.markdown("<div style='font-size:18px;font-weight:700;color:#fff;margin-bottom:12px;'>&#128736; Skills Breakdown</div>", unsafe_allow_html=True)

def skill_pills(skills, color="#a78bfa"):
    return "".join([
        f"<span style='background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.13);"
        f"border-radius:20px;padding:4px 12px;margin:3px;display:inline-block;font-size:13px;color:{color};'>{s}</span>"
        for s in skills
    ])

left, right = st.columns(2)
with left:
    st.markdown(
        f"<div class='card'>"
        f"<div style='font-size:17px;font-weight:800;color:#a78bfa;margin-bottom:14px;'>{role_a}</div>"
        f"<div style='font-size:12px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>Core Skills</div>"
        f"<div style='margin-bottom:14px;'>{skill_pills(da['core_skills'],'#a78bfa')}</div>"
        f"<div style='font-size:12px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>Bonus Skills</div>"
        f"<div>{skill_pills(da['bonus_skills'],'#c4b5fd')}</div>"
        f"</div>",
        unsafe_allow_html=True
    )
with right:
    st.markdown(
        f"<div class='card'>"
        f"<div style='font-size:17px;font-weight:800;color:#60a5fa;margin-bottom:14px;'>{role_b}</div>"
        f"<div style='font-size:12px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>Core Skills</div>"
        f"<div style='margin-bottom:14px;'>{skill_pills(db['core_skills'],'#60a5fa')}</div>"
        f"<div style='font-size:12px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>Bonus Skills</div>"
        f"<div>{skill_pills(db['bonus_skills'],'#93c5fd')}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── shared vs unique ──────────────────────────────────────────────────────────
st.markdown("<div style='font-size:18px;font-weight:700;color:#fff;margin-bottom:12px;'>&#128270; Shared vs Unique Skills</div>", unsafe_allow_html=True)

set_a  = set(s.lower() for s in da["core_skills"] + da["bonus_skills"])
set_b  = set(s.lower() for s in db["core_skills"] + db["bonus_skills"])
shared = set_a & set_b
only_a = set_a - set_b
only_b = set_b - set_a

ov1, ov2, ov3 = st.columns(3)
with ov1:
    st.markdown(f"<div class='card' style='text-align:center;'><div style='font-size:28px;font-weight:800;color:#34d399;'>{len(shared)}</div><div style='font-size:13px;color:rgba(255,255,255,0.5);'>Shared Skills</div><div style='margin-top:10px;'>{skill_pills(list(shared),'#34d399') if shared else '<span style=\"color:rgba(255,255,255,0.3)\">None</span>'}</div></div>", unsafe_allow_html=True)
with ov2:
    st.markdown(f"<div class='card' style='text-align:center;'><div style='font-size:28px;font-weight:800;color:#a78bfa;'>{len(only_a)}</div><div style='font-size:13px;color:rgba(255,255,255,0.5);'>Only in {role_a}</div><div style='margin-top:10px;'>{skill_pills(list(only_a),'#a78bfa') if only_a else '<span style=\"color:rgba(255,255,255,0.3)\">None</span>'}</div></div>", unsafe_allow_html=True)
with ov3:
    st.markdown(f"<div class='card' style='text-align:center;'><div style='font-size:28px;font-weight:800;color:#60a5fa;'>{len(only_b)}</div><div style='font-size:13px;color:rgba(255,255,255,0.5);'>Only in {role_b}</div><div style='margin-top:10px;'>{skill_pills(list(only_b),'#60a5fa') if only_b else '<span style=\"color:rgba(255,255,255,0.3)\">None</span>'}</div></div>", unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── verdict ───────────────────────────────────────────────────────────────────
st.markdown("<div style='font-size:18px;font-weight:700;color:#fff;margin-bottom:12px;'>&#127942; Quick Verdict</div>", unsafe_allow_html=True)

diff_a = DIFF_ORDER.get(da["difficulty"], 2)
diff_b = DIFF_ORDER.get(db["difficulty"], 2)
harder = role_a if diff_a > diff_b else (role_b if diff_b > diff_a else "Both equal")
easier = role_a if diff_a < diff_b else (role_b if diff_b < diff_a else "Both equal")

st.markdown(
    f"<div class='card'><div style='display:flex;gap:32px;flex-wrap:wrap;'>"
    f"<div><span style='color:rgba(255,255,255,0.4);font-size:12px;'>EASIER TO BREAK INTO</span><br>"
    f"<span style='font-size:18px;font-weight:700;color:#34d399;'>{easier}</span></div>"
    f"<div><span style='color:rgba(255,255,255,0.4);font-size:12px;'>MORE COMPETITIVE</span><br>"
    f"<span style='font-size:18px;font-weight:700;color:#f87171;'>{harder}</span></div>"
    f"<div><span style='color:rgba(255,255,255,0.4);font-size:12px;'>SKILLS OVERLAP</span><br>"
    f"<span style='font-size:18px;font-weight:700;color:#a78bfa;'>{len(shared)} shared</span></div>"
    f"<div><span style='color:rgba(255,255,255,0.4);font-size:12px;'>EXTRA SKILLS</span><br>"
    f"<span style='font-size:18px;font-weight:700;color:#60a5fa;'>{len(only_a)} for {role_a} | {len(only_b)} for {role_b}</span></div>"
    f"</div></div>",
    unsafe_allow_html=True
)
