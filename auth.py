"""
auth.py  -  Shared authentication helpers for Vision Careers AI SaaS
"""
import os, json, hashlib, hmac
import streamlit as st

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

# ── user-db helpers ───────────────────────────────────────────────────────────

def _load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_users(users: dict) -> None:
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def user_exists(email: str) -> bool:
    return email in _load_users()

def get_user(email: str) -> dict:
    return _load_users().get(email, {})

def register_user(email: str, password: str, name: str) -> bool:
    users = _load_users()
    if email in users:
        return False
    users[email] = {"pw": _hash(password), "name": name, "history": [], "linkedin": ""}
    _save_users(users)
    return True

def verify_user(email: str, password: str) -> bool:
    users = _load_users()
    if email not in users:
        try:
            su = st.secrets["users"]
            if email in su:
                return hmac.compare_digest(password, str(su[email]))
        except Exception:
            pass
        return False
    stored  = users[email]
    pw_hash = stored if isinstance(stored, str) else stored.get("pw", "")
    return hmac.compare_digest(_hash(password), pw_hash)

def _ensure_user_record(email: str, name: str = "") -> None:
    """Create a users.json record for Google/OAuth users on first login."""
    users = _load_users()
    if email not in users:
        users[email] = {"pw": "", "name": name or email, "history": [], "linkedin": ""}
        _save_users(users)
    elif isinstance(users[email], str):
        # migrate legacy plain-text password entry
        old_pw = users[email]
        users[email] = {"pw": old_pw, "name": name or email, "history": [], "linkedin": ""}
        _save_users(users)

def save_analysis(email: str, record: dict) -> None:
    """Append one analysis record to user history. Creates record if missing."""
    _ensure_user_record(email)
    users = _load_users()
    users[email].setdefault("history", []).append(record)
    users[email]["history"] = users[email]["history"][-20:]
    _save_users(users)

def get_history(email: str) -> list:
    users = _load_users()
    entry = users.get(email, {})
    if isinstance(entry, str):
        return []
    return entry.get("history", [])

def get_linkedin(email: str) -> str:
    users = _load_users()
    entry = users.get(email, {})
    if isinstance(entry, dict):
        return entry.get("linkedin", "")
    return ""

def save_linkedin(email: str, url: str) -> None:
    _ensure_user_record(email)
    users = _load_users()
    users[email]["linkedin"] = url.strip()
    _save_users(users)

def update_password(email: str, new_password: str) -> bool:
    users = _load_users()
    if email not in users:
        return False
    if isinstance(users[email], str):
        users[email] = {"pw": _hash(new_password), "name": email, "history": [], "linkedin": ""}
    else:
        users[email]["pw"] = _hash(new_password)
    _save_users(users)
    return True

# ── session helpers ───────────────────────────────────────────────────────────

def _google_active() -> bool:
    try:
        return bool(st.user and st.user.is_logged_in)
    except Exception:
        return False

def is_logged_in() -> bool:
    if st.session_state.get("logged_in"):
        return True
    if _google_active():
        try:
            email = st.user.email or ""
            name  = st.user.name  or email
            if email and not st.session_state.get("logged_in"):
                st.session_state.logged_in  = True
                st.session_state.user_email = email
                st.session_state.user_name  = name
                _ensure_user_record(email, name)
        except Exception:
            pass
        return True
    return False

def current_user() -> str:
    return st.session_state.get("user_email", "")

def current_name() -> str:
    return st.session_state.get("user_name", current_user())

def login_session(email: str) -> None:
    st.session_state.logged_in  = True
    st.session_state.user_email = email
    u = get_user(email)
    st.session_state.user_name  = u.get("name", email) if isinstance(u, dict) else email

def logout_session() -> None:
    for k in ["logged_in", "user_email", "user_name"]:
        st.session_state.pop(k, None)
    try:
        if _google_active():
            st.logout()
    except Exception:
        pass

# ── shared dark theme CSS ─────────────────────────────────────────────────────

DARK_THEME = """
<style>
/* ── backgrounds ── */
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main > div { background: #0e0e1a !important; }

[data-testid="stSidebar"] {
    background: #13131f !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}

/* ── hide Streamlit auto-generated page nav ── */
[data-testid="stSidebarNav"] { display: none !important; }
#MainMenu, footer, header    { visibility: hidden; }

/* ── typography ── */
html, body, [class*="css"] { color: #e2e2f0 !important; }

/* ── metric cards ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px; padding: 18px 20px !important;
}
[data-testid="stMetricLabel"] { color: rgba(255,255,255,0.5) !important; font-size:13px !important; }
[data-testid="stMetricValue"] { color: #ffffff !important; font-size:26px !important; }

/* ── tabs ── */
button[data-baseweb="tab"] { color: rgba(255,255,255,0.45) !important; font-weight:600 !important; }
button[data-baseweb="tab"][aria-selected="true"] {
    color:#a78bfa !important; border-bottom:2px solid #a78bfa !important;
}

/* ── inputs ── */
div[data-testid="stTextInput"] label  { color:rgba(255,255,255,0.6) !important; font-size:13px !important; }
div[data-testid="stTextInput"] input  {
    background:rgba(255,255,255,0.06) !important;
    border:1px solid rgba(255,255,255,0.13) !important;
    border-radius:12px !important; color:#fff !important; font-size:15px !important;
}
div[data-testid="stTextInput"] input:focus {
    border:1px solid #a78bfa !important;
    box-shadow:0 0 0 3px rgba(167,139,250,0.15) !important;
}
div[data-testid="stTextArea"] textarea {
    background:rgba(255,255,255,0.06) !important;
    border:1px solid rgba(255,255,255,0.13) !important;
    border-radius:12px !important; color:#fff !important;
}
div[data-testid="stSelectbox"] > div > div {
    background:rgba(255,255,255,0.06) !important;
    border:1px solid rgba(255,255,255,0.13) !important;
    border-radius:12px !important; color:#fff !important;
}
[data-testid="stFileUploader"] {
    background:rgba(255,255,255,0.04) !important;
    border:1px dashed rgba(255,255,255,0.15) !important;
    border-radius:14px !important;
}

/* ── buttons ── */
div[data-testid="stFormSubmitButton"] button,
button[kind="primary"] {
    background: linear-gradient(135deg,#7c3aed,#4f46e5) !important;
    color:#fff !important; border:none !important;
    border-radius:12px !important; font-weight:700 !important;
    box-shadow:0 4px 18px rgba(124,58,237,0.35) !important;
}
button[kind="secondary"] {
    background:rgba(255,255,255,0.07) !important;
    color:rgba(255,255,255,0.85) !important;
    border:1px solid rgba(255,255,255,0.15) !important;
    border-radius:12px !important; font-weight:600 !important;
}

/* ── expanders ── */
[data-testid="stExpander"] {
    background:rgba(255,255,255,0.04) !important;
    border:1px solid rgba(255,255,255,0.08) !important;
    border-radius:14px !important;
}
details summary { color:#e2e2f0 !important; }

/* ── misc ── */
div[data-testid="stAlert"] { border-radius:12px !important; }
[data-testid="stDataFrame"] { border-radius:14px !important; overflow:hidden; }
hr { border-color: rgba(255,255,255,0.08) !important; }
.stProgress > div > div > div > div {
    background: linear-gradient(90deg,#7c3aed,#06b6d4) !important;
}

/* ── skill chips ── */
.chip-pass {
    background:rgba(52,211,153,0.15); color:#34d399;
    padding:5px 14px; border-radius:20px; margin:3px;
    display:inline-block; font-size:.85rem; font-weight:600;
    border:1px solid rgba(52,211,153,0.3);
}
.chip-fail {
    background:rgba(239,68,68,0.12); color:#f87171;
    padding:5px 14px; border-radius:20px; margin:3px;
    display:inline-block; font-size:.85rem; font-weight:600;
    border:1px solid rgba(239,68,68,0.25);
}

/* ── layout helpers ── */
.page-title { font-size:28px; font-weight:800; color:#fff; margin-bottom:4px; letter-spacing:-0.5px; }
.page-sub   { font-size:14px; color:rgba(255,255,255,0.4); margin-bottom:24px; }
.card {
    background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:18px; padding:24px; margin-bottom:16px;
    transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.2s ease;
}
.card:hover {
    border-color: rgba(167,139,250,0.2);
    box-shadow: 0 4px 24px rgba(124,58,237,0.1);
    transform: translateY(-1px);
}

/* ── animated gradient text ── */
.gradient-text {
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399, #a78bfa);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradientShift 4s ease infinite;
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ── glow card ── */
.glow-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px; padding: 24px; margin-bottom: 16px;
    position: relative; overflow: hidden;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.glow-card:hover {
    border-color: rgba(167,139,250,0.3);
    box-shadow: 0 0 30px rgba(124,58,237,0.15);
}
.glow-card::before {
    content: '';
    position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(167,139,250,0.04) 0%, transparent 60%);
    animation: glowPulse 4s ease-in-out infinite;
}
@keyframes glowPulse {
    0%, 100% { opacity: 0.3; transform: scale(0.8); }
    50%      { opacity: 0.8; transform: scale(1.2); }
}

/* ── achievement badge ── */
.badge-unlocked {
    background: linear-gradient(135deg, rgba(167,139,250,0.15), rgba(96,165,250,0.1));
    border: 1px solid rgba(167,139,250,0.3);
    border-radius: 18px; padding: 20px; text-align: center;
    transition: transform 0.2s ease, box-shadow 0.3s ease;
}
.badge-unlocked:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(124,58,237,0.25);
}
.badge-locked {
    background: rgba(255,255,255,0.02);
    border: 1px dashed rgba(255,255,255,0.1);
    border-radius: 18px; padding: 20px; text-align: center;
    opacity: 0.5;
}

/* ── pulse dot ── */
.pulse-dot {
    width: 8px; height: 8px; border-radius: 50%; display: inline-block;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.5; transform: scale(1.5); }
}

/* ── score ring ── */
.score-ring {
    width: 120px; height: 120px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    position: relative; margin: 0 auto;
}
</style>
"""

def inject_theme():
    st.markdown(DARK_THEME, unsafe_allow_html=True)

# ── sidebar renderer (called from every page) ─────────────────────────────────

def render_sidebar(active: str = ""):
    inject_theme()

    # extra sidebar button styles
    st.markdown("""
    <style>
    div[data-testid="stSidebar"] button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid transparent !important;
        color: rgba(255,255,255,0.6) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 9px 14px !important;
        border-radius: 10px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin-bottom: 2px !important;
    }
    div[data-testid="stSidebar"] button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.07) !important;
        color: #fff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(
            "<div style='padding:16px 0 8px 0;'>"
            "<div style='font-size:20px;font-weight:800;color:#fff;'>&#128301; Vision</div>"
            "<div style='font-size:12px;color:rgba(255,255,255,0.35);margin-top:2px;'>Careers AI Platform</div>"
            "</div>"
            "<hr style='border-color:rgba(255,255,255,0.08);margin:8px 0 8px 0;'/>",
            unsafe_allow_html=True
        )

        nav_items = [
            ("dashboard",    "&#127968;  Dashboard"),
            ("analyzer",     "&#128302;  Analyzer"),
            ("history",      "&#128203;  History"),
            ("compare",      "&#9878;&#65039;   Compare Roles"),
            ("jobs",         "&#128188;  Job Board"),
            ("interview",    "&#129504;  Interview Coach"),
            ("skill_radar",  "&#128202;  Skill Radar"),
            ("achievements", "&#127942;  Achievements"),
            ("resume_tips",  "&#128221;  Resume Tips"),
            ("market_pulse", "&#127758;  Market Pulse"),
            ("settings",     "&#9881;&#65039;   Settings"),
        ]

        for key, label in nav_items:
            is_active = key == active
            # highlight active page
            if is_active:
                st.markdown(
                    f"<div style='background:rgba(167,139,250,0.12);border:1px solid rgba(167,139,250,0.3);"
                    f"border-radius:10px;padding:9px 14px;margin-bottom:2px;"
                    f"color:#a78bfa;font-weight:700;font-size:14px;'>{label}</div>",
                    unsafe_allow_html=True
                )
            else:
                if st.button(label, key=f"nav_{key}", use_container_width=True):
                    st.switch_page(f"pages/{key}.py")

        st.markdown(
            "<hr style='border-color:rgba(255,255,255,0.08);margin:10px 0 8px 0;'/>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='font-size:11px;color:rgba(255,255,255,0.3);padding-bottom:2px;'>Signed in as</div>"
            f"<div style='font-size:13px;color:rgba(255,255,255,0.7);font-weight:600;"
            f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{current_user()}</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("&#128682;  Sign Out", key="sidebar_signout", use_container_width=True):
            logout_session()
            st.rerun()

def require_auth():
    """Stop page execution if not logged in — navigation handles redirect via app.py."""
    if not is_logged_in():
        st.stop()
