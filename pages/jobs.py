import sys, os
import streamlit as st
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import require_auth, render_sidebar, current_user, get_history, get_linkedin

require_auth()
st.set_page_config(page_title="Job Board - Vision", page_icon="&#128188;", layout="wide", initial_sidebar_state="expanded")
render_sidebar("jobs")

JOB_LINKS = {
    "Data Scientist": [
        {"title":"Data Scientist","company":"Google","location":"Remote/US","tag":"ML","url":"https://www.linkedin.com/jobs/search/?keywords=data+scientist+google"},
        {"title":"Data Scientist","company":"Meta","location":"Menlo Park, CA","tag":"NLP","url":"https://www.linkedin.com/jobs/search/?keywords=data+scientist+meta"},
        {"title":"Data Scientist","company":"Netflix","location":"Los Gatos, CA","tag":"Analytics","url":"https://www.linkedin.com/jobs/search/?keywords=data+scientist+netflix"},
        {"title":"Applied Scientist","company":"Amazon","location":"Seattle, WA","tag":"ML","url":"https://www.linkedin.com/jobs/search/?keywords=applied+scientist+amazon"},
        {"title":"Data Scientist","company":"Any Company","location":"Remote","tag":"Open","url":"https://www.linkedin.com/jobs/search/?keywords=data+scientist&f_WT=2"},
    ],
    "Data Analyst": [
        {"title":"Data Analyst","company":"Airbnb","location":"Remote","tag":"SQL","url":"https://www.linkedin.com/jobs/search/?keywords=data+analyst+airbnb"},
        {"title":"Business Analyst","company":"Microsoft","location":"Redmond, WA","tag":"BI","url":"https://www.linkedin.com/jobs/search/?keywords=business+analyst+microsoft"},
        {"title":"Analytics Engineer","company":"Stripe","location":"Remote","tag":"dbt","url":"https://www.linkedin.com/jobs/search/?keywords=analytics+engineer+stripe"},
        {"title":"Data Analyst","company":"Spotify","location":"Remote","tag":"Python","url":"https://www.linkedin.com/jobs/search/?keywords=data+analyst+spotify"},
        {"title":"Data Analyst","company":"Any Company","location":"Remote","tag":"Open","url":"https://www.linkedin.com/jobs/search/?keywords=data+analyst&f_WT=2"},
    ],
    "Backend Engineer": [
        {"title":"Backend Engineer","company":"Stripe","location":"Remote","tag":"Python","url":"https://www.linkedin.com/jobs/search/?keywords=backend+engineer+stripe"},
        {"title":"Software Engineer - Backend","company":"Shopify","location":"Remote","tag":"Ruby/Go","url":"https://www.linkedin.com/jobs/search/?keywords=backend+engineer+shopify"},
        {"title":"Backend Engineer","company":"Uber","location":"San Francisco","tag":"Java","url":"https://www.linkedin.com/jobs/search/?keywords=backend+engineer+uber"},
        {"title":"API Engineer","company":"Twilio","location":"Remote","tag":"Node.js","url":"https://www.linkedin.com/jobs/search/?keywords=api+engineer+twilio"},
        {"title":"Backend Engineer","company":"Any Company","location":"Remote","tag":"Open","url":"https://www.linkedin.com/jobs/search/?keywords=backend+engineer&f_WT=2"},
    ],
    "Frontend Engineer": [
        {"title":"Frontend Engineer","company":"Figma","location":"San Francisco","tag":"React","url":"https://www.linkedin.com/jobs/search/?keywords=frontend+engineer+figma"},
        {"title":"UI Engineer","company":"Vercel","location":"Remote","tag":"Next.js","url":"https://www.linkedin.com/jobs/search/?keywords=frontend+engineer+vercel"},
        {"title":"Frontend Developer","company":"Atlassian","location":"Remote","tag":"TypeScript","url":"https://www.linkedin.com/jobs/search/?keywords=frontend+developer+atlassian"},
        {"title":"Frontend Engineer","company":"GitHub","location":"Remote","tag":"Vue","url":"https://www.linkedin.com/jobs/search/?keywords=frontend+engineer+github"},
        {"title":"Frontend Engineer","company":"Any Company","location":"Remote","tag":"Open","url":"https://www.linkedin.com/jobs/search/?keywords=frontend+engineer&f_WT=2"},
    ],
    "Full Stack Developer": [
        {"title":"Full Stack Developer","company":"GitLab","location":"Remote","tag":"Ruby+Vue","url":"https://www.linkedin.com/jobs/search/?keywords=full+stack+developer+gitlab"},
        {"title":"Full Stack Engineer","company":"Notion","location":"San Francisco","tag":"React+Node","url":"https://www.linkedin.com/jobs/search/?keywords=full+stack+engineer+notion"},
        {"title":"Software Engineer","company":"Linear","location":"Remote","tag":"TS+GraphQL","url":"https://www.linkedin.com/jobs/search/?keywords=full+stack+engineer+linear"},
        {"title":"Full Stack Engineer","company":"Retool","location":"San Francisco","tag":"React+Python","url":"https://www.linkedin.com/jobs/search/?keywords=full+stack+engineer+retool"},
        {"title":"Full Stack Developer","company":"Any Company","location":"Remote","tag":"Open","url":"https://www.linkedin.com/jobs/search/?keywords=full+stack+developer&f_WT=2"},
    ],
    "DevOps Engineer": [
        {"title":"DevOps Engineer","company":"HashiCorp","location":"Remote","tag":"Terraform","url":"https://www.linkedin.com/jobs/search/?keywords=devops+engineer+hashicorp"},
        {"title":"Site Reliability Engineer","company":"Cloudflare","location":"Remote","tag":"Kubernetes","url":"https://www.linkedin.com/jobs/search/?keywords=sre+cloudflare"},
        {"title":"Platform Engineer","company":"Datadog","location":"New York","tag":"AWS","url":"https://www.linkedin.com/jobs/search/?keywords=platform+engineer+datadog"},
        {"title":"DevOps Engineer","company":"PagerDuty","location":"Remote","tag":"CI/CD","url":"https://www.linkedin.com/jobs/search/?keywords=devops+engineer+pagerduty"},
        {"title":"DevOps Engineer","company":"Any Company","location":"Remote","tag":"Open","url":"https://www.linkedin.com/jobs/search/?keywords=devops+engineer&f_WT=2"},
    ],
    "Cloud Architect": [
        {"title":"Cloud Architect","company":"AWS","location":"Seattle, WA","tag":"AWS","url":"https://www.linkedin.com/jobs/search/?keywords=cloud+architect+aws"},
        {"title":"Solutions Architect","company":"Google Cloud","location":"Remote","tag":"GCP","url":"https://www.linkedin.com/jobs/search/?keywords=solutions+architect+google"},
        {"title":"Cloud Solutions Architect","company":"Microsoft Azure","location":"Remote","tag":"Azure","url":"https://www.linkedin.com/jobs/search/?keywords=cloud+architect+microsoft"},
        {"title":"Principal Cloud Architect","company":"IBM","location":"Remote","tag":"Multi-cloud","url":"https://www.linkedin.com/jobs/search/?keywords=cloud+architect+ibm"},
        {"title":"Cloud Architect","company":"Any Company","location":"Remote","tag":"Open","url":"https://www.linkedin.com/jobs/search/?keywords=cloud+architect&f_WT=2"},
    ],
    "Machine Learning Engineer": [
        {"title":"ML Engineer","company":"OpenAI","location":"San Francisco","tag":"PyTorch","url":"https://www.linkedin.com/jobs/search/?keywords=ml+engineer+openai"},
        {"title":"ML Engineer","company":"DeepMind","location":"London/Remote","tag":"Research","url":"https://www.linkedin.com/jobs/search/?keywords=ml+engineer+deepmind"},
        {"title":"ML Platform Engineer","company":"Hugging Face","location":"Remote","tag":"Transformers","url":"https://www.linkedin.com/jobs/search/?keywords=ml+engineer+hugging+face"},
        {"title":"ML Engineer","company":"Cohere","location":"Remote","tag":"NLP","url":"https://www.linkedin.com/jobs/search/?keywords=ml+engineer+cohere"},
        {"title":"ML Engineer","company":"Any Company","location":"Remote","tag":"Open","url":"https://www.linkedin.com/jobs/search/?keywords=machine+learning+engineer&f_WT=2"},
    ],
    "Data Engineer": [
        {"title":"Data Engineer","company":"Databricks","location":"Remote","tag":"Spark","url":"https://www.linkedin.com/jobs/search/?keywords=data+engineer+databricks"},
        {"title":"Data Engineer","company":"Snowflake","location":"Remote","tag":"SQL","url":"https://www.linkedin.com/jobs/search/?keywords=data+engineer+snowflake"},
        {"title":"Analytics Engineer","company":"dbt Labs","location":"Remote","tag":"dbt","url":"https://www.linkedin.com/jobs/search/?keywords=analytics+engineer+dbt"},
        {"title":"Data Engineer","company":"Fivetran","location":"Remote","tag":"ETL","url":"https://www.linkedin.com/jobs/search/?keywords=data+engineer+fivetran"},
        {"title":"Data Engineer","company":"Any Company","location":"Remote","tag":"Open","url":"https://www.linkedin.com/jobs/search/?keywords=data+engineer&f_WT=2"},
    ],
    "Cybersecurity Analyst": [
        {"title":"Security Analyst","company":"CrowdStrike","location":"Remote","tag":"Threat Intel","url":"https://www.linkedin.com/jobs/search/?keywords=security+analyst+crowdstrike"},
        {"title":"SOC Analyst","company":"Palo Alto Networks","location":"Santa Clara","tag":"SIEM","url":"https://www.linkedin.com/jobs/search/?keywords=soc+analyst+palo+alto"},
        {"title":"Penetration Tester","company":"HackerOne","location":"Remote","tag":"Bug Bounty","url":"https://www.linkedin.com/jobs/search/?keywords=penetration+tester"},
        {"title":"Security Engineer","company":"Cloudflare","location":"Remote","tag":"Network Sec","url":"https://www.linkedin.com/jobs/search/?keywords=security+engineer+cloudflare"},
        {"title":"Cybersecurity Analyst","company":"Any Company","location":"Remote","tag":"Open","url":"https://www.linkedin.com/jobs/search/?keywords=cybersecurity+analyst&f_WT=2"},
    ],
    "iOS Developer": [
        {"title":"iOS Engineer","company":"Apple","location":"Cupertino, CA","tag":"Swift","url":"https://www.linkedin.com/jobs/search/?keywords=ios+engineer+apple"},
        {"title":"iOS Developer","company":"Airbnb","location":"San Francisco","tag":"SwiftUI","url":"https://www.linkedin.com/jobs/search/?keywords=ios+developer+airbnb"},
        {"title":"iOS Engineer","company":"Lyft","location":"San Francisco","tag":"Swift","url":"https://www.linkedin.com/jobs/search/?keywords=ios+engineer+lyft"},
        {"title":"Mobile Engineer iOS","company":"Duolingo","location":"Pittsburgh","tag":"Swift","url":"https://www.linkedin.com/jobs/search/?keywords=ios+mobile+engineer+duolingo"},
        {"title":"iOS Developer","company":"Any Company","location":"Remote","tag":"Open","url":"https://www.linkedin.com/jobs/search/?keywords=ios+developer&f_WT=2"},
    ],
    "Android Developer": [
        {"title":"Android Engineer","company":"Google","location":"Mountain View","tag":"Kotlin","url":"https://www.linkedin.com/jobs/search/?keywords=android+engineer+google"},
        {"title":"Android Developer","company":"Spotify","location":"Remote","tag":"Compose","url":"https://www.linkedin.com/jobs/search/?keywords=android+developer+spotify"},
        {"title":"Android Engineer","company":"Grab","location":"Singapore","tag":"Kotlin","url":"https://www.linkedin.com/jobs/search/?keywords=android+engineer+grab"},
        {"title":"Mobile Engineer","company":"Revolut","location":"Remote","tag":"MVVM","url":"https://www.linkedin.com/jobs/search/?keywords=android+mobile+engineer+revolut"},
        {"title":"Android Developer","company":"Any Company","location":"Remote","tag":"Open","url":"https://www.linkedin.com/jobs/search/?keywords=android+developer&f_WT=2"},
    ],
    "UI/UX Designer": [
        {"title":"Product Designer","company":"Figma","location":"San Francisco","tag":"Figma","url":"https://www.linkedin.com/jobs/search/?keywords=product+designer+figma"},
        {"title":"UX Designer","company":"Google","location":"Mountain View","tag":"Research","url":"https://www.linkedin.com/jobs/search/?keywords=ux+designer+google"},
        {"title":"UI/UX Designer","company":"Canva","location":"Remote","tag":"Design Sys","url":"https://www.linkedin.com/jobs/search/?keywords=ui+ux+designer+canva"},
        {"title":"Product Designer","company":"Notion","location":"San Francisco","tag":"Prototyping","url":"https://www.linkedin.com/jobs/search/?keywords=product+designer+notion"},
        {"title":"UI/UX Designer","company":"Any Company","location":"Remote","tag":"Open","url":"https://www.linkedin.com/jobs/search/?keywords=ui+ux+designer&f_WT=2"},
    ],
    "QA Automation Engineer": [
        {"title":"QA Engineer","company":"Atlassian","location":"Remote","tag":"Cypress","url":"https://www.linkedin.com/jobs/search/?keywords=qa+engineer+atlassian"},
        {"title":"Automation Engineer","company":"Testlio","location":"Remote","tag":"Selenium","url":"https://www.linkedin.com/jobs/search/?keywords=automation+engineer+testlio"},
        {"title":"SDET","company":"Microsoft","location":"Redmond","tag":"Azure DevOps","url":"https://www.linkedin.com/jobs/search/?keywords=sdet+microsoft"},
        {"title":"QA Automation","company":"Postman","location":"San Francisco","tag":"API Testing","url":"https://www.linkedin.com/jobs/search/?keywords=qa+automation+postman"},
        {"title":"QA Engineer","company":"Any Company","location":"Remote","tag":"Open","url":"https://www.linkedin.com/jobs/search/?keywords=qa+automation+engineer&f_WT=2"},
    ],
    "Product Manager": [
        {"title":"Product Manager","company":"Google","location":"Mountain View","tag":"Growth","url":"https://www.linkedin.com/jobs/search/?keywords=product+manager+google"},
        {"title":"Senior PM","company":"Stripe","location":"Remote","tag":"Fintech","url":"https://www.linkedin.com/jobs/search/?keywords=product+manager+stripe"},
        {"title":"Product Manager","company":"Linear","location":"Remote","tag":"B2B SaaS","url":"https://www.linkedin.com/jobs/search/?keywords=product+manager+linear"},
        {"title":"Growth PM","company":"Duolingo","location":"Pittsburgh","tag":"Consumer","url":"https://www.linkedin.com/jobs/search/?keywords=growth+product+manager+duolingo"},
        {"title":"Product Manager","company":"Any Company","location":"Remote","tag":"Open","url":"https://www.linkedin.com/jobs/search/?keywords=product+manager&f_WT=2"},
    ],
}

TAG_COLORS = {
    "ML":"#a78bfa","NLP":"#a78bfa","Analytics":"#60a5fa","SQL":"#34d399","BI":"#60a5fa",
    "Python":"#fbbf24","React":"#60a5fa","TypeScript":"#60a5fa","Go":"#34d399","Node.js":"#34d399",
    "AWS":"#f97316","GCP":"#f97316","Azure":"#f97316","Terraform":"#f59e0b","Kubernetes":"#f59e0b",
    "Docker":"#38bdf8","CI/CD":"#38bdf8","dbt":"#a78bfa","Spark":"#f97316","Swift":"#f97316",
    "Kotlin":"#a78bfa","Figma":"#ec4899","UX":"#ec4899","Testing":"#34d399","Cypress":"#34d399",
    "Selenium":"#34d399","PyTorch":"#f97316","MLOps":"#a78bfa","ETL":"#60a5fa","SIEM":"#f87171",
    "Security":"#f87171","Bug Bounty":"#f87171","Research":"#a78bfa","Transformers":"#a78bfa",
    "MERN":"#60a5fa","Next.js":"#60a5fa","Vue":"#34d399","TS+GraphQL":"#a78bfa","Ruby+Vue":"#f97316",
    "Ruby/Go":"#34d399","Java":"#f59e0b","Multi-cloud":"#60a5fa","SwiftUI":"#f97316",
    "Compose":"#a78bfa","MVVM":"#a78bfa","Prototyping":"#ec4899","Design Sys":"#ec4899",
    "API Testing":"#34d399","Azure DevOps":"#38bdf8","B2B SaaS":"#60a5fa","Consumer":"#60a5fa",
    "Fintech":"#34d399","Growth":"#fbbf24","B2B":"#60a5fa","Network Sec":"#f87171",
    "Threat Intel":"#f87171","Airflow":"#f97316","Tableau":"#60a5fa","Open":"#6b7280",
}

# ── platform helpers ──────────────────────────────────────────────────────────
def _build_platform_urls(title, company):
    """Build search URLs for multiple job platforms based on job title + company."""
    q = f"{title}+{company}".replace(" ", "+")
    q_title = title.replace(" ", "+")
    slug = title.lower().replace(" ", "-")
    return {
        "LinkedIn":    f"https://www.linkedin.com/jobs/search/?keywords={q}",
        "Internshala":  f"https://internshala.com/jobs/{slug}-jobs",
        "Naukri":       f"https://www.naukri.com/{slug}-jobs",
        "Indeed":       f"https://www.indeed.com/jobs?q={q}",
        "Glassdoor":    f"https://www.glassdoor.co.in/Job/{slug}-jobs-SRCH_KO0,{len(title)}.htm",
        "Foundit":      f"https://www.foundit.in/srp/results?searchType=personalizedSearch&query={q_title}",
        "Google":       f"https://www.google.com/search?q={q}+careers+jobs",
    }

PLATFORM_BTN = {
    "LinkedIn":   {"icon":"&#128101;","bg":"linear-gradient(135deg,#0077B5,#005885)"},
    "Internshala":{"icon":"&#128218;","bg":"linear-gradient(135deg,#00A5EC,#0078B5)"},
    "Naukri":     {"icon":"&#128196;","bg":"linear-gradient(135deg,#4A67FF,#304FFE)"},
    "Indeed":     {"icon":"&#128313;","bg":"linear-gradient(135deg,#2164f3,#003A9B)"},
    "Glassdoor":  {"icon":"&#128994;","bg":"linear-gradient(135deg,#0CAA41,#088F35)"},
    "Foundit":    {"icon":"&#128270;","bg":"linear-gradient(135deg,#E9432D,#C62828)"},
    "Google":     {"icon":"&#127759;","bg":"linear-gradient(135deg,#4285F4,#2b5dac)"},
}

# ── page ──────────────────────────────────────────────────────────────────────
st.markdown("<div class='page-title'>&#128188; Job Board</div>", unsafe_allow_html=True)

# ── LinkedIn banner ───────────────────────────────────────────────────────────
email          = current_user()
linkedin_saved = get_linkedin(email)
history        = get_history(email)
last_role      = st.session_state.get("last_top_career") or (history[-1]["top_career"] if history else None)

if linkedin_saved:
    li_search_role = last_role or "software engineer"
    li_url = f"https://www.linkedin.com/jobs/search/?keywords={li_search_role.replace(' ', '+')}"
    st.markdown(
        f"<div class='card' style='background:linear-gradient(135deg,rgba(0,119,181,0.2),rgba(10,102,194,0.15));"
        f"border:1px solid rgba(0,119,181,0.35);padding:18px 24px;margin-bottom:20px;'>"
        f"<div style='display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;'>"
        f"<div>"
        f"<div style='font-size:15px;font-weight:700;color:#fff;'>&#128101; LinkedIn Profile Connected</div>"
        f"<div style='font-size:13px;color:rgba(255,255,255,0.5);margin-top:3px;'>{linkedin_saved}</div>"
        f"</div>"
        f"<a href='{li_url}' target='_blank' style='background:linear-gradient(135deg,#0077b5,#0a66c2);"
        f"color:#fff;text-decoration:none;border-radius:10px;padding:9px 18px;font-size:13px;font-weight:700;"
        f"white-space:nowrap;'>Apply for {last_role or 'Jobs'} on LinkedIn &#8594;</a>"
        f"</div></div>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<div class='card' style='border:1px solid rgba(0,119,181,0.25);padding:14px 20px;margin-bottom:16px;'>"
        "<div style='font-size:13px;color:rgba(255,255,255,0.5);'>"
        "&#128101; <b style='color:rgba(255,255,255,0.7);'>Tip:</b> Save your LinkedIn profile in the "
        "<b style='color:#a78bfa;'>Analyzer</b> page to get one-click LinkedIn job application links here."
        "</div></div>",
        unsafe_allow_html=True
    )

st.markdown("<div class='page-sub'>Curated job openings at top tech companies — apply via LinkedIn, Internshala, Naukri, Indeed, Glassdoor &amp; more!</div>", unsafe_allow_html=True)

# ── filter ────────────────────────────────────────────────────────────────────
roles_available = sorted(JOB_LINKS.keys())

# auto-select last analyzed role
default_role_idx = 0
if last_role and last_role in roles_available:
    default_role_idx = roles_available.index(last_role) + 1  # +1 for "All Roles" offset

filter_col, search_col = st.columns([2, 3])
with filter_col:
    selected_role = st.selectbox(
        "Filter by Role",
        ["All Roles"] + roles_available,
        index=default_role_idx,
        key="job_role_filter"
    )
with search_col:
    search_query = st.text_input("Search jobs", placeholder="e.g. Remote, Python, Senior...", label_visibility="collapsed")

if last_role and selected_role == "All Roles":
    st.markdown(
        f"<div style='font-size:12px;color:rgba(255,255,255,0.35);margin-bottom:8px;'>"
        f"Showing all roles. Your last analyzed role was <b style='color:#a78bfa;'>{last_role}</b>.</div>",
        unsafe_allow_html=True
    )

# ── job cards ─────────────────────────────────────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

display     = {r: JOB_LINKS[r] for r in roles_available} if selected_role == "All Roles" else {selected_role: JOB_LINKS[selected_role]}
total_shown = 0

for role, jobs in display.items():
    filtered = jobs
    if search_query:
        q        = search_query.lower()
        filtered = [j for j in jobs if q in j["title"].lower() or q in j["company"].lower()
                    or q in j["location"].lower() or q in j["tag"].lower()]
    if not filtered:
        continue

    if selected_role == "All Roles":
        st.markdown(
            f"<div style='font-size:17px;font-weight:700;color:#a78bfa;margin:16px 0 10px 0;'>{role}</div>",
            unsafe_allow_html=True
        )

    cols = st.columns(min(3, len(filtered)))
    for idx, job in enumerate(filtered):
        tag_color = TAG_COLORS.get(job["tag"], "#6b7280")
        # Build platform buttons for this job
        plat_urls = _build_platform_urls(job["title"], job["company"])
        btns_html = ""
        for pname, purl in plat_urls.items():
            ps = PLATFORM_BTN[pname]
            btns_html += (
                f"<a href='{purl}' target='_blank' title='Apply on {pname}' "
                f"style='display:inline-flex;align-items:center;gap:4px;margin-right:5px;margin-bottom:5px;"
                f"background:{ps['bg']};color:#fff;text-decoration:none;border-radius:6px;"
                f"padding:4px 10px;font-size:11px;font-weight:600;'>"
                f"{ps['icon']} {pname}</a>"
            )
        with cols[idx % 3]:
            st.markdown(
                f"<div class='card' style='min-height:180px;'>"
                f"<div style='display:flex;justify-content:space-between;align-items:flex-start;'>"
                f"<div style='font-size:15px;font-weight:700;color:#fff;flex:1;'>{job['title']}</div>"
                f"<span style='background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.13);"
                f"border-radius:12px;padding:2px 10px;font-size:11px;color:{tag_color};"
                f"white-space:nowrap;margin-left:8px;'>{job['tag']}</span>"
                f"</div>"
                f"<div style='font-size:13px;color:rgba(255,255,255,0.55);margin-top:4px;'>&#127970; {job['company']}</div>"
                f"<div style='font-size:12px;color:rgba(255,255,255,0.35);margin-top:2px;'>&#128205; {job['location']}</div>"
                f"<div style='font-size:11px;color:rgba(255,255,255,0.3);margin-top:10px;margin-bottom:4px;"
                f"font-weight:600;letter-spacing:0.5px;'>APPLY VIA</div>"
                f"<div style='display:flex;flex-wrap:wrap;gap:2px;'>{btns_html}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        total_shown += 1

if total_shown == 0:
    st.markdown(
        "<div class='card' style='text-align:center;padding:40px;'>"
        "<div style='font-size:36px;'>&#128270;</div>"
        "<div style='font-size:16px;font-weight:600;color:#fff;margin-top:12px;'>No jobs found</div>"
        "<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-top:6px;'>Try a different search term or role filter.</div>"
        "</div>",
        unsafe_allow_html=True
    )

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;font-size:12px;color:rgba(255,255,255,0.2);'>"
    "Apply links redirect to external job platforms. Vision AI is not affiliated with any employer or portal.</div>",
    unsafe_allow_html=True
)
