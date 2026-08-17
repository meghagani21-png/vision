import sys, os, json
import streamlit as st
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import (require_auth, render_sidebar, current_user, current_name,
                  update_password, verify_user, get_history, get_linkedin, save_linkedin,
                  _load_users, _save_users, _hash)

require_auth()
st.set_page_config(page_title="Settings - Vision", page_icon="&#9881;", layout="wide", initial_sidebar_state="expanded")
render_sidebar("settings")

st.markdown("<div class='page-title'>&#9881; Settings</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Manage your account, LinkedIn profile, password and data</div>", unsafe_allow_html=True)

email   = current_user()
name    = current_name()
history = get_history(email)

tab_profile, tab_linkedin, tab_password, tab_data = st.tabs(
    ["&#128100; Profile", "&#128101; LinkedIn", "&#128273; Change Password", "&#128452; My Data"]
)

# ── PROFILE ───────────────────────────────────────────────────────────────────
with tab_profile:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='card'><div style='display:flex;align-items:center;gap:20px;flex-wrap:wrap;'>"
        f"<div style='width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,#7c3aed,#4f46e5);"
        f"display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:800;color:#fff;flex-shrink:0;'>"
        f"{name[0].upper()}</div>"
        f"<div><div style='font-size:20px;font-weight:800;color:#fff;'>{name}</div>"
        f"<div style='font-size:14px;color:rgba(255,255,255,0.45);margin-top:2px;'>{email}</div>"
        f"<div style='margin-top:8px;'><span style='background:rgba(124,58,237,0.2);border:1px solid rgba(124,58,237,0.4);"
        f"color:#a78bfa;border-radius:20px;padding:3px 12px;font-size:12px;font-weight:600;'>Free Plan</span>"
        f"</div></div></div></div>",
        unsafe_allow_html=True
    )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    with st.form("form_name"):
        new_name = st.text_input("Display name", value=name, placeholder="Your name")
        if st.form_submit_button("Save Name", type="primary"):
            users = _load_users()
            if email in users and isinstance(users[email], dict):
                users[email]["name"] = new_name.strip()
                _save_users(users)
                st.session_state.user_name = new_name.strip()
                st.success("Name updated!")
            else:
                st.warning("Cannot update name for this account type.")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Analyses Run",    len(history))
    c2.metric("Roles Explored",  len(set(h["top_career"] for h in history)) if history else 0)
    best = max((h.get("top_score", 0) for h in history), default=0)
    c3.metric("Best Match Score", f"{best:.0f}%" if history else "-")

# ── LINKEDIN ──────────────────────────────────────────────────────────────────
with tab_linkedin:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    saved_li = get_linkedin(email)

    st.markdown(
        "<div class='card' style='background:linear-gradient(135deg,rgba(0,119,181,0.15),rgba(10,102,194,0.1));"
        "border:1px solid rgba(0,119,181,0.3);'>"
        "<div style='font-size:16px;font-weight:700;color:#fff;margin-bottom:6px;'>&#128101; LinkedIn Profile</div>"
        "<div style='font-size:13px;color:rgba(255,255,255,0.5);line-height:1.6;'>"
        "Adding your LinkedIn profile URL enables one-click job applications directly on LinkedIn "
        "for your matched career roles. Your URL is saved locally and never shared.</div>"
        "</div>",
        unsafe_allow_html=True
    )

    with st.form("form_linkedin"):
        li_url = st.text_input(
            "LinkedIn Profile URL",
            value=saved_li,
            placeholder="https://www.linkedin.com/in/yourname/"
        )
        if st.form_submit_button("Save LinkedIn Profile", type="primary"):
            if li_url.strip() and "linkedin.com" in li_url.lower():
                save_linkedin(email, li_url.strip())
                st.success("LinkedIn profile saved!")
                st.rerun()
            elif li_url.strip() == "":
                save_linkedin(email, "")
                st.info("LinkedIn profile removed.")
                st.rerun()
            else:
                st.error("Please enter a valid LinkedIn URL (must contain linkedin.com)")

    if saved_li:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:13px;color:rgba(255,255,255,0.5);'>"
            f"&#10003; Current profile: <a href='{saved_li}' target='_blank' style='color:#60a5fa;'>{saved_li}</a></div>",
            unsafe_allow_html=True
        )
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        history_roles = list(set(h["top_career"] for h in history)) if history else []
        if history_roles:
            st.markdown(
                "<div style='font-size:14px;font-weight:700;color:#fff;margin-bottom:10px;'>Quick Apply Links for Your Matched Roles</div>",
                unsafe_allow_html=True
            )
            for role in history_roles[:6]:
                li_job_url = f"https://www.linkedin.com/jobs/search/?keywords={role.replace(' ', '+')}"
                st.markdown(
                    f"<a href='{li_job_url}' target='_blank' style='display:inline-flex;align-items:center;"
                    f"gap:8px;margin:4px;background:rgba(0,119,181,0.2);border:1px solid rgba(0,119,181,0.3);"
                    f"color:#60a5fa;text-decoration:none;border-radius:10px;padding:6px 14px;font-size:13px;font-weight:600;'>"
                    f"&#128101; {role}</a>",
                    unsafe_allow_html=True
                )

# ── CHANGE PASSWORD ────────────────────────────────────────────────────────────
with tab_password:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    with st.form("form_pw"):
        current_pw = st.text_input("Current password",     type="password", placeholder="Enter current password")
        new_pw     = st.text_input("New password",         type="password", placeholder="At least 6 characters")
        confirm_pw = st.text_input("Confirm new password", type="password", placeholder="Repeat new password")
        submitted  = st.form_submit_button("Update Password", type="primary")

    if submitted:
        if not current_pw:
            st.error("Please enter your current password.")
        elif not verify_user(email, current_pw):
            st.error("Current password is incorrect.")
        elif len(new_pw) < 6:
            st.error("New password must be at least 6 characters.")
        elif new_pw != confirm_pw:
            st.error("New passwords do not match.")
        else:
            update_password(email, new_pw)
            st.success("Password updated successfully!")

# ── MY DATA ───────────────────────────────────────────────────────────────────
with tab_data:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    st.markdown("<div style='font-size:15px;font-weight:700;color:#fff;margin-bottom:10px;'>&#128229; Export My Data</div>", unsafe_allow_html=True)
    export_data = {"email": email, "name": name, "linkedin": get_linkedin(email), "history": history}
    st.download_button(
        label="Download my data (JSON)",
        data=json.dumps(export_data, indent=2),
        file_name="vision_my_data.json",
        mime="application/json",
    )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:15px;font-weight:700;color:#fff;margin-bottom:8px;'>&#128465; Clear Analysis History</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-bottom:10px;'>Permanently deletes all past analysis records.</div>", unsafe_allow_html=True)
    if st.button("Clear All History", type="secondary"):
        users = _load_users()
        if email in users and isinstance(users[email], dict):
            users[email]["history"] = []
            _save_users(users)
            st.success("History cleared.")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='border:1px solid rgba(239,68,68,0.3);border-radius:14px;padding:18px;"
        "background:rgba(239,68,68,0.05);'>"
        "<div style='font-size:15px;font-weight:700;color:#f87171;margin-bottom:6px;'>&#9888; Danger Zone</div>"
        "<div style='font-size:13px;color:rgba(255,255,255,0.4);'>Deleting your account is permanent and cannot be undone.</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    confirm_del = st.text_input("Type your email to confirm deletion", placeholder=email, key="del_confirm")
    if st.button("Delete My Account", type="secondary"):
        if confirm_del.strip().lower() != email:
            st.error("Email does not match. Account not deleted.")
        else:
            from auth import logout_session
            users = _load_users()
            users.pop(email, None)
            _save_users(users)
            logout_session()
            st.rerun()
