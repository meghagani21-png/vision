import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import inject_theme, login_session, register_user, verify_user, user_exists, is_logged_in

inject_theme()

# hide sidebar on login page
st.markdown("<style>[data-testid='stSidebar']{display:none!important;}</style>", unsafe_allow_html=True)

# if already logged in rerun so app.py sends to dashboard
if is_logged_in():
    st.rerun()

if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "signin"

left_col, right_col = st.columns([1.15, 0.95])

# ── LEFT HERO ─────────────────────────────────────────────────────────────────
with left_col:
    st.markdown(
        "<div style='padding:40px 32px 40px 8px;'>"
        "<div style='font-size:44px;margin-bottom:14px;'>&#128301;</div>"
        "<div style='font-size:40px;font-weight:900;color:#fff;line-height:1.15;letter-spacing:-1px;margin-bottom:16px;'>"
        "Your AI-Powered<br>"
        "<span style='background:linear-gradient(90deg,#a78bfa,#60a5fa,#34d399);"
        "-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;'>"
        "Career Accelerator</span></div>"
        "<div style='font-size:15px;color:rgba(255,255,255,0.5);line-height:1.75;max-width:420px;margin-bottom:40px;'>"
        "Upload your resume or LinkedIn profile, get an instant career match score, "
        "uncover your skill gaps, and download a custom 3-phase learning roadmap.</div>"

        "<div style='display:flex;align-items:flex-start;gap:14px;margin-bottom:18px;'>"
        "<div style='width:40px;height:40px;border-radius:10px;flex-shrink:0;background:rgba(167,139,250,0.12);"
        "border:1px solid rgba(167,139,250,0.25);display:flex;align-items:center;justify-content:center;font-size:18px;'>&#129302;</div>"
        "<div><div style='color:#fff;font-weight:700;font-size:14px;'>ML Career Matching</div>"
        "<div style='color:rgba(255,255,255,0.4);font-size:13px;'>TF-IDF + Logistic Regression across 15 tech roles</div></div></div>"

        "<div style='display:flex;align-items:flex-start;gap:14px;margin-bottom:18px;'>"
        "<div style='width:40px;height:40px;border-radius:10px;flex-shrink:0;background:rgba(96,165,250,0.12);"
        "border:1px solid rgba(96,165,250,0.25);display:flex;align-items:center;justify-content:center;font-size:18px;'>&#128202;</div>"
        "<div><div style='color:#fff;font-weight:700;font-size:14px;'>Skill Gap Analysis</div>"
        "<div style='color:rgba(255,255,255,0.4);font-size:13px;'>See exactly which skills to learn next</div></div></div>"

        "<div style='display:flex;align-items:flex-start;gap:14px;margin-bottom:18px;'>"
        "<div style='width:40px;height:40px;border-radius:10px;flex-shrink:0;background:rgba(52,211,153,0.12);"
        "border:1px solid rgba(52,211,153,0.25);display:flex;align-items:center;justify-content:center;font-size:18px;'>&#128506;</div>"
        "<div><div style='color:#fff;font-weight:700;font-size:14px;'>Custom Roadmaps</div>"
        "<div style='color:rgba(255,255,255,0.4);font-size:13px;'>3-phase plan, downloadable as Markdown</div></div></div>"

        "<div style='display:flex;align-items:flex-start;gap:14px;margin-bottom:18px;'>"
        "<div style='width:40px;height:40px;border-radius:10px;flex-shrink:0;background:rgba(14,165,233,0.12);"
        "border:1px solid rgba(14,165,233,0.25);display:flex;align-items:center;justify-content:center;font-size:18px;'>&#128101;</div>"
        "<div><div style='color:#fff;font-weight:700;font-size:14px;'>LinkedIn Profile Import</div>"
        "<div style='color:rgba(255,255,255,0.4);font-size:13px;'>Paste your LinkedIn URL to find matched jobs</div></div></div>"

        "<div style='display:flex;align-items:flex-start;gap:14px;margin-bottom:18px;'>"
        "<div style='width:40px;height:40px;border-radius:10px;flex-shrink:0;background:rgba(249,115,22,0.12);"
        "border:1px solid rgba(249,115,22,0.25);display:flex;align-items:center;justify-content:center;font-size:18px;'>&#128188;</div>"
        "<div><div style='color:#fff;font-weight:700;font-size:14px;'>Curated Job Board</div>"
        "<div style='color:rgba(255,255,255,0.4);font-size:13px;'>Top openings at Google, Meta, Stripe and more</div></div></div>"

        "<div style='display:flex;align-items:flex-start;gap:14px;margin-bottom:0;'>"
        "<div style='width:40px;height:40px;border-radius:10px;flex-shrink:0;background:rgba(251,191,36,0.12);"
        "border:1px solid rgba(251,191,36,0.25);display:flex;align-items:center;justify-content:center;font-size:18px;'>&#9878;</div>"
        "<div><div style='color:#fff;font-weight:700;font-size:14px;'>Role Comparison</div>"
        "<div style='color:rgba(255,255,255,0.4);font-size:13px;'>Compare any two careers side by side</div></div></div>"

        "<div style='display:flex;gap:32px;margin-top:40px;padding-top:24px;"
        "border-top:1px solid rgba(255,255,255,0.08);flex-wrap:wrap;'>"
        "<div><div style='color:#fff;font-size:22px;font-weight:800;'>15+</div><div style='color:rgba(255,255,255,0.35);font-size:12px;'>Career Roles</div></div>"
        "<div><div style='color:#fff;font-size:22px;font-weight:800;'>75+</div><div style='color:rgba(255,255,255,0.35);font-size:12px;'>Job Listings</div></div>"
        "<div><div style='color:#fff;font-size:22px;font-weight:800;'>100%</div><div style='color:rgba(255,255,255,0.35);font-size:12px;'>Free to Use</div></div>"
        "<div><div style='color:#fff;font-size:22px;font-weight:800;'>Local</div><div style='color:rgba(255,255,255,0.35);font-size:12px;'>ML Model</div></div>"
        "</div></div>",
        unsafe_allow_html=True
    )

# ── RIGHT AUTH PANEL ──────────────────────────────────────────────────────────
with right_col:
    st.markdown(
        "<style>"
        ".tab-row{display:flex;border-radius:14px;background:rgba(255,255,255,0.05);"
        "border:1px solid rgba(255,255,255,0.09);padding:4px;gap:4px;margin-bottom:24px;}"
        ".tab-btn{flex:1;text-align:center;padding:10px 0;border-radius:10px;"
        "font-size:14px;font-weight:600;color:rgba(255,255,255,0.4);}"
        ".tab-btn.active{background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;"
        "box-shadow:0 4px 14px rgba(124,58,237,0.35);}"
        "</style>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='margin-bottom:24px;'>"
        "<div style='font-size:18px;font-weight:800;color:#fff;letter-spacing:-0.3px;'>"
        "Vision <span style='color:rgba(255,255,255,0.3);font-weight:400;'>Careers AI</span>"
        "</div></div>",
        unsafe_allow_html=True
    )

    tab    = st.session_state.auth_tab
    si_cls = "tab-btn active" if tab == "signin" else "tab-btn"
    su_cls = "tab-btn active" if tab == "signup" else "tab-btn"
    st.markdown(
        f"<div class='tab-row'><div class='{si_cls}'>Sign In</div><div class='{su_cls}'>Sign Up</div></div>",
        unsafe_allow_html=True
    )

    tc1, tc2 = st.columns(2)
    with tc1:
        if st.button("Sign In", key="btn_si", use_container_width=True):
            st.session_state.auth_tab = "signin"; st.rerun()
    with tc2:
        if st.button("Sign Up", key="btn_su", use_container_width=True):
            st.session_state.auth_tab = "signup"; st.rerun()

    # ── SIGN IN ───────────────────────────────────────────────────────────────
    if st.session_state.auth_tab == "signin":
        st.markdown(
            "<div style='font-size:22px;font-weight:800;color:#fff;margin-bottom:4px;'>Welcome back</div>"
            "<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-bottom:20px;'>Sign in to your Vision account</div>",
            unsafe_allow_html=True
        )
        with st.form("form_signin", clear_on_submit=False):
            si_email = st.text_input("Email address", placeholder="you@example.com")
            si_pw    = st.text_input("Password", type="password", placeholder="Your password")
            si_btn   = st.form_submit_button("Sign In", type="primary", use_container_width=True)

        if si_btn:
            e = si_email.strip().lower()
            if not e:
                st.error("Please enter your email.")
            elif not si_pw:
                st.error("Please enter your password.")
            elif verify_user(e, si_pw):
                login_session(e)
                st.rerun()
            else:
                st.error("Incorrect email or password.")

        st.markdown(
            "<div style='text-align:center;margin-top:14px;font-size:13px;color:rgba(255,255,255,0.35);'>"
            "No account? Click <b style='color:#a78bfa;'>Sign Up</b> above.</div>",
            unsafe_allow_html=True
        )

    # ── SIGN UP ───────────────────────────────────────────────────────────────
    else:
        st.markdown(
            "<div style='font-size:22px;font-weight:800;color:#fff;margin-bottom:4px;'>Create account</div>"
            "<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-bottom:20px;'>Free forever. No credit card needed.</div>",
            unsafe_allow_html=True
        )
        with st.form("form_signup", clear_on_submit=True):
            su_name    = st.text_input("Full name",        placeholder="Jane Doe")
            su_email   = st.text_input("Email address",    placeholder="you@example.com")
            su_pw      = st.text_input("Password",         type="password", placeholder="At least 6 characters")
            su_confirm = st.text_input("Confirm password", type="password", placeholder="Repeat password")
            su_btn     = st.form_submit_button("Create Account", type="primary", use_container_width=True)

        if su_btn:
            e = su_email.strip().lower()
            if not su_name.strip():
                st.error("Please enter your name.")
            elif not e or "@" not in e:
                st.error("Please enter a valid email.")
            elif len(su_pw) < 6:
                st.error("Password must be at least 6 characters.")
            elif su_pw != su_confirm:
                st.error("Passwords do not match.")
            elif user_exists(e):
                st.error("An account with this email already exists.")
            else:
                register_user(e, su_pw, su_name.strip())
                login_session(e)
                st.rerun()

        st.markdown(
            "<div style='text-align:center;margin-top:14px;font-size:13px;color:rgba(255,255,255,0.35);'>"
            "Already have an account? Click <b style='color:#a78bfa;'>Sign In</b> above.</div>",
            unsafe_allow_html=True
        )

    # OR divider + Google
    st.markdown(
        "<div style='display:flex;align-items:center;gap:12px;margin:18px 0;'>"
        "<div style='flex:1;height:1px;background:rgba(255,255,255,0.09);'></div>"
        "<span style='color:rgba(255,255,255,0.25);font-size:12px;'>OR</span>"
        "<div style='flex:1;height:1px;background:rgba(255,255,255,0.09);'></div></div>",
        unsafe_allow_html=True
    )
    if st.button("Continue with Google", use_container_width=True, key="google_btn"):
        try:
            st.login("google")
        except Exception as e:
            st.warning(f"Google login error: {e}")

    st.markdown(
        "<div style='margin-top:24px;padding-top:18px;border-top:1px solid rgba(255,255,255,0.07);"
        "text-align:center;font-size:11px;color:rgba(255,255,255,0.2);line-height:1.6;'>"
        "By signing up you agree to our Terms of Service and Privacy Policy.<br>"
        "2026 Vision Careers AI</div>",
        unsafe_allow_html=True
    )
