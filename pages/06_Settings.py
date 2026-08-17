import sys, os, json
import streamlit as st
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import (require_auth, inject_theme, current_user, current_name,
                  logout_session, update_password, verify_user, get_history,
                  _load_users, _save_users, _hash)

st.set_page_config(page_title="Settings · Vision", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")
require_auth()
inject_theme()

# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 8px 0;'>
        <div style='font-size:20px;font-weight:800;color:#fff;'>🔭 Vision</div>
        <div style='font-size:12px;color:rgba(255,255,255,0.35);margin-top:2px;'>Careers AI Platform</div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.08);margin:8px 0 16px 0;'/>
    """, unsafe_allow_html=True)
    st.page_link("pages/01_Dashboard.py",  label="🏠  Dashboard")
    st.page_link("pages/02_Analyzer.py",   label="🔬  Analyzer")
    st.page_link("pages/03_History.py",    label="📋  History")
    st.page_link("pages/04_Compare.py",    label="⚖️  Compare Roles")
    st.page_link("pages/05_Job_Board.py",  label="💼  Job Board")
    st.page_link("pages/06_Settings.py",   label="⚙️  Settings")
    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:16px 0 8px 0;'/>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:12px;color:rgba(255,255,255,0.35);padding-bottom:4px;'>Signed in as</div><div style='font-size:13px;color:rgba(255,255,255,0.7);font-weight:600;'>{current_user()}</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("🚪  Sign Out", use_container_width=True):
        logout_session(); st.switch_page("app.py")

# ── page ──────────────────────────────────────────────────────────────────────
st.markdown("<div class='page-title'>⚙️ Settings</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Manage your account, password, and data</div>", unsafe_allow_html=True)

email = current_user()
name  = current_name()
history = get_history(email)

tab_profile, tab_password, tab_data = st.tabs(["👤 Profile", "🔑 Change Password", "🗄️ My Data"])

# ── PROFILE ───────────────────────────────────────────────────────────────────
with tab_profile:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='card'>
        <div style='display:flex;align-items:center;gap:20px;flex-wrap:wrap;'>
            <div style='width:64px;height:64px;border-radius:50%;
                        background:linear-gradient(135deg,#7c3aed,#4f46e5);
                        display:flex;align-items:center;justify-content:center;
                        font-size:26px;font-weight:800;color:#fff;flex-shrink:0;'>
                {name[0].upper()}
            </div>
            <div>
                <div style='font-size:20px;font-weight:800;color:#fff;'>{name}</div>
                <div style='font-size:14px;color:rgba(255,255,255,0.45);margin-top:2px;'>{email}</div>
                <div style='margin-top:8px;'>
                    <span style='background:rgba(124,58,237,0.2);border:1px solid rgba(124,58,237,0.4);
                                 color:#a78bfa;border-radius:20px;padding:3px 12px;font-size:12px;font-weight:600;'>
                        Free Plan
                    </span>
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # edit display name
    st.markdown("<div style='font-size:15px;font-weight:700;color:#fff;margin-bottom:10px;'>Update Display Name</div>", unsafe_allow_html=True)
    with st.form("form_name"):
        new_name = st.text_input("Display name", value=name, placeholder="Your name")
        if st.form_submit_button("Save Name", type="primary"):
            users = _load_users()
            if email in users and isinstance(users[email], dict):
                users[email]["name"] = new_name.strip()
                _save_users(users)
                st.session_state.user_name = new_name.strip()
                st.success("✅ Name updated!")
            else:
                st.warning("Cannot update name for legacy accounts. Please re-register.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Analyses Run",    len(history))
    c2.metric("Roles Explored",  len(set(h["top_career"] for h in history)) if history else 0)
    best_score = max((h.get("top_score",0) for h in history), default=0)
    c3.metric("Best Match Score", f"{best_score:.0f}%" if history else "—")

# ── CHANGE PASSWORD ────────────────────────────────────────────────────────────
with tab_password:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='card' style='max-width:480px;'>
        <div style='font-size:15px;font-weight:700;color:#fff;margin-bottom:16px;'>Change Your Password</div>
    """, unsafe_allow_html=True)

    with st.form("form_pw"):
        current_pw = st.text_input("Current password", type="password", placeholder="Enter current password")
        new_pw     = st.text_input("New password",     type="password", placeholder="At least 6 characters")
        confirm_pw = st.text_input("Confirm new password", type="password", placeholder="Repeat new password")
        submitted  = st.form_submit_button("Update Password", type="primary")

    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if not current_pw:
            st.error("⚠️ Please enter your current password.")
        elif not verify_user(email, current_pw):
            st.error("❌ Current password is incorrect.")
        elif len(new_pw) < 6:
            st.error("⚠️ New password must be at least 6 characters.")
        elif new_pw != confirm_pw:
            st.error("❌ New passwords do not match.")
        else:
            update_password(email, new_pw)
            st.success("✅ Password updated successfully!")

# ── MY DATA ───────────────────────────────────────────────────────────────────
with tab_data:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # export data
    st.markdown("<div style='font-size:15px;font-weight:700;color:#fff;margin-bottom:10px;'>📥 Export My Data</div>", unsafe_allow_html=True)

    export_data = {
        "email":   email,
        "name":    name,
        "history": history,
    }
    st.download_button(
        label="Download my data (JSON)",
        data=json.dumps(export_data, indent=2),
        file_name="vision_my_data.json",
        mime="application/json",
    )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # clear history
    st.markdown("<div style='font-size:15px;font-weight:700;color:#fff;margin-bottom:10px;'>🗑️ Clear Analysis History</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-bottom:12px;'>This will permanently delete all your past analysis records. This cannot be undone.</div>", unsafe_allow_html=True)

    if st.button("Clear All History", type="secondary"):
        users = _load_users()
        if email in users and isinstance(users[email], dict):
            users[email]["history"] = []
            _save_users(users)
            st.success("✅ History cleared.")
        else:
            st.info("No history to clear.")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # danger zone
    st.markdown("""
    <div style='border:1px solid rgba(239,68,68,0.3);border-radius:14px;padding:20px;background:rgba(239,68,68,0.05);'>
        <div style='font-size:15px;font-weight:700;color:#f87171;margin-bottom:6px;'>⚠️ Danger Zone</div>
        <div style='font-size:13px;color:rgba(255,255,255,0.4);margin-bottom:12px;'>
            Deleting your account is permanent. All your data will be erased and cannot be recovered.
        </div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    confirm_delete = st.text_input("Type your email to confirm deletion", placeholder=email, key="del_confirm")
    if st.button("Delete My Account", type="secondary"):
        if confirm_delete.strip().lower() != email:
            st.error("Email does not match. Account not deleted.")
        else:
            users = _load_users()
            users.pop(email, None)
            _save_users(users)
            logout_session()
            st.switch_page("app.py")
