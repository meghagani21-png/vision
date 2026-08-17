import sys, os, joblib
import streamlit as st
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import require_auth, inject_theme, current_user, logout_session, get_history

st.set_page_config(page_title="Job Board · Vision", page_icon="💼", layout="wide", initial_sidebar_state="expanded")
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

# ── helper: build platform URLs for a job search query ────────────────────────
def _platforms(query):
    """Return a dict of platform → search URL for a given job query string."""
    q = query.replace(" ", "+")
    return {
        "LinkedIn":    f"https://www.linkedin.com/jobs/search/?keywords={q}",
        "Internshala":  f"https://internshala.com/jobs/{query.lower().replace(' ', '-')}-jobs",
        "Naukri":       f"https://www.naukri.com/{query.lower().replace(' ', '-')}-jobs",
        "Indeed":       f"https://www.indeed.com/jobs?q={q}",
        "Glassdoor":    f"https://www.glassdoor.co.in/Job/{query.lower().replace(' ', '-')}-jobs-SRCH_KO0,{len(query)}.htm",
        "Foundit":      f"https://www.foundit.in/srp/results?searchType=personalizedSearch&query={q}",
    }

# Platform button styles
PLATFORM_STYLES = {
    "LinkedIn":   {"icon":"🔗","bg":"linear-gradient(135deg,#0077B5,#005885)"},
    "Internshala":{"icon":"📘","bg":"linear-gradient(135deg,#00A5EC,#0078B5)"},
    "Naukri":     {"icon":"📄","bg":"linear-gradient(135deg,#4A67FF,#304FFE)"},
    "Indeed":     {"icon":"🟦","bg":"linear-gradient(135deg,#2164f3,#003A9B)"},
    "Glassdoor":  {"icon":"🟢","bg":"linear-gradient(135deg,#0CAA41,#088F35)"},
    "Foundit":    {"icon":"🔍","bg":"linear-gradient(135deg,#E9432D,#C62828)"},
}

# ── job data ───────────────────────────────────────────────────────────────────
JOB_LINKS = {
    "Data Scientist": [
        {"title":"Data Scientist","company":"Google","location":"Remote/US","tag":"ML",
         "url":"https://careers.google.com/jobs/results/?q=data+scientist","platforms":_platforms("Data Scientist")},
        {"title":"Data Scientist","company":"Meta","location":"Menlo Park, CA","tag":"NLP",
         "url":"https://www.metacareers.com/jobs?q=data+scientist","platforms":_platforms("Data Scientist")},
        {"title":"Data Scientist","company":"Netflix","location":"Los Gatos, CA","tag":"Analytics",
         "url":"https://jobs.netflix.com/search?q=data+scientist","platforms":_platforms("Data Scientist")},
        {"title":"Applied Scientist","company":"Amazon","location":"Seattle, WA","tag":"ML",
         "url":"https://www.amazon.jobs/en/search?base_query=data+scientist","platforms":_platforms("Data Scientist")},
        {"title":"Data Scientist","company":"LinkedIn","location":"Sunnyvale, CA","tag":"Analytics",
         "url":"https://www.linkedin.com/jobs/search/?keywords=data+scientist","platforms":_platforms("Data Scientist")},
    ],
    "Data Analyst": [
        {"title":"Data Analyst","company":"Airbnb","location":"Remote","tag":"SQL",
         "url":"https://careers.airbnb.com/positions/?department=data-science","platforms":_platforms("Data Analyst")},
        {"title":"Business Analyst","company":"Microsoft","location":"Redmond, WA","tag":"BI",
         "url":"https://careers.microsoft.com/us/en/search-results?keywords=data+analyst","platforms":_platforms("Data Analyst")},
        {"title":"Analytics Engineer","company":"Stripe","location":"Remote","tag":"dbt",
         "url":"https://stripe.com/jobs/search?q=data+analyst","platforms":_platforms("Data Analyst")},
        {"title":"Data Analyst","company":"Spotify","location":"Stockholm/Remote","tag":"Python",
         "url":"https://www.lifeatspotify.com/jobs?q=data+analyst","platforms":_platforms("Data Analyst")},
        {"title":"Data Analyst","company":"LinkedIn","location":"San Francisco","tag":"Tableau",
         "url":"https://www.linkedin.com/jobs/search/?keywords=data+analyst","platforms":_platforms("Data Analyst")},
    ],
    "Backend Engineer": [
        {"title":"Backend Engineer","company":"Stripe","location":"Remote","tag":"Python",
         "url":"https://stripe.com/jobs/search?q=backend+engineer","platforms":_platforms("Backend Engineer")},
        {"title":"Software Engineer – Backend","company":"Shopify","location":"Remote","tag":"Ruby/Go",
         "url":"https://www.shopify.com/careers/search?q=backend","platforms":_platforms("Backend Engineer")},
        {"title":"Backend Engineer","company":"Uber","location":"San Francisco","tag":"Java",
         "url":"https://www.uber.com/global/en/careers/list/?q=backend+engineer","platforms":_platforms("Backend Engineer")},
        {"title":"API Engineer","company":"Twilio","location":"Remote","tag":"Node.js",
         "url":"https://careers.twilio.com/jobs?q=backend","platforms":_platforms("Backend Engineer")},
        {"title":"Backend Engineer","company":"LinkedIn","location":"Various","tag":"Go",
         "url":"https://www.linkedin.com/jobs/search/?keywords=backend+engineer","platforms":_platforms("Backend Engineer")},
    ],
    "Frontend Engineer": [
        {"title":"Frontend Engineer","company":"Figma","location":"San Francisco","tag":"React",
         "url":"https://www.figma.com/careers/#job-openings","platforms":_platforms("Frontend Engineer")},
        {"title":"UI Engineer","company":"Vercel","location":"Remote","tag":"Next.js",
         "url":"https://vercel.com/careers","platforms":_platforms("Frontend Engineer")},
        {"title":"Frontend Developer","company":"Atlassian","location":"Remote","tag":"TypeScript",
         "url":"https://www.atlassian.com/company/careers/all-jobs?team=Engineering&q=frontend","platforms":_platforms("Frontend Engineer")},
        {"title":"Frontend Engineer","company":"GitHub","location":"Remote","tag":"Vue",
         "url":"https://github.com/about/careers","platforms":_platforms("Frontend Engineer")},
        {"title":"Frontend Engineer","company":"LinkedIn","location":"Various","tag":"React",
         "url":"https://www.linkedin.com/jobs/search/?keywords=frontend+engineer","platforms":_platforms("Frontend Engineer")},
    ],
    "Full Stack Developer": [
        {"title":"Full Stack Developer","company":"GitLab","location":"Remote","tag":"Ruby+Vue",
         "url":"https://about.gitlab.com/jobs/","platforms":_platforms("Full Stack Developer")},
        {"title":"Full Stack Engineer","company":"Notion","location":"San Francisco","tag":"React+Node",
         "url":"https://www.notion.so/careers","platforms":_platforms("Full Stack Developer")},
        {"title":"Software Engineer","company":"Linear","location":"Remote","tag":"TS+GraphQL",
         "url":"https://linear.app/careers","platforms":_platforms("Full Stack Developer")},
        {"title":"Full Stack Engineer","company":"Retool","location":"San Francisco","tag":"React+Python",
         "url":"https://retool.com/careers","platforms":_platforms("Full Stack Developer")},
        {"title":"Full Stack Developer","company":"LinkedIn","location":"Various","tag":"MERN",
         "url":"https://www.linkedin.com/jobs/search/?keywords=full+stack+developer","platforms":_platforms("Full Stack Developer")},
    ],
    "DevOps Engineer": [
        {"title":"DevOps Engineer","company":"HashiCorp","location":"Remote","tag":"Terraform",
         "url":"https://www.hashicorp.com/careers","platforms":_platforms("DevOps Engineer")},
        {"title":"Site Reliability Engineer","company":"Cloudflare","location":"Remote","tag":"Kubernetes",
         "url":"https://www.cloudflare.com/careers/jobs/?q=devops","platforms":_platforms("DevOps Engineer")},
        {"title":"Platform Engineer","company":"Datadog","location":"New York","tag":"AWS",
         "url":"https://careers.datadoghq.com/?q=devops","platforms":_platforms("DevOps Engineer")},
        {"title":"DevOps Engineer","company":"PagerDuty","location":"Remote","tag":"CI/CD",
         "url":"https://www.pagerduty.com/careers/?q=devops","platforms":_platforms("DevOps Engineer")},
        {"title":"DevOps Engineer","company":"LinkedIn","location":"Various","tag":"Docker",
         "url":"https://www.linkedin.com/jobs/search/?keywords=devops+engineer","platforms":_platforms("DevOps Engineer")},
    ],
    "Cloud Architect": [
        {"title":"Cloud Architect","company":"AWS","location":"Seattle, WA","tag":"AWS",
         "url":"https://www.amazon.jobs/en/search?base_query=cloud+architect","platforms":_platforms("Cloud Architect")},
        {"title":"Solutions Architect","company":"Google Cloud","location":"Remote","tag":"GCP",
         "url":"https://careers.google.com/jobs/results/?q=cloud+architect","platforms":_platforms("Cloud Architect")},
        {"title":"Cloud Solutions Architect","company":"Microsoft Azure","location":"Remote","tag":"Azure",
         "url":"https://careers.microsoft.com/us/en/search-results?keywords=cloud+architect","platforms":_platforms("Cloud Architect")},
        {"title":"Principal Cloud Architect","company":"IBM","location":"Remote","tag":"Multi-cloud",
         "url":"https://www.ibm.com/employment/us-en/?q=cloud+architect","platforms":_platforms("Cloud Architect")},
        {"title":"Cloud Architect","company":"LinkedIn","location":"Various","tag":"AWS/GCP",
         "url":"https://www.linkedin.com/jobs/search/?keywords=cloud+architect","platforms":_platforms("Cloud Architect")},
    ],
    "Machine Learning Engineer": [
        {"title":"ML Engineer","company":"OpenAI","location":"San Francisco","tag":"PyTorch",
         "url":"https://openai.com/careers","platforms":_platforms("Machine Learning Engineer")},
        {"title":"ML Engineer","company":"DeepMind","location":"London/Remote","tag":"Research",
         "url":"https://www.deepmind.com/careers","platforms":_platforms("Machine Learning Engineer")},
        {"title":"ML Platform Engineer","company":"Hugging Face","location":"Remote","tag":"Transformers",
         "url":"https://apply.workable.com/huggingface/","platforms":_platforms("Machine Learning Engineer")},
        {"title":"ML Engineer","company":"Cohere","location":"Remote","tag":"NLP",
         "url":"https://cohere.com/careers","platforms":_platforms("Machine Learning Engineer")},
        {"title":"Machine Learning Engineer","company":"LinkedIn","location":"Various","tag":"MLOps",
         "url":"https://www.linkedin.com/jobs/search/?keywords=machine+learning+engineer","platforms":_platforms("Machine Learning Engineer")},
    ],
    "Data Engineer": [
        {"title":"Data Engineer","company":"Databricks","location":"Remote","tag":"Spark",
         "url":"https://www.databricks.com/company/careers/open-positions?q=data+engineer","platforms":_platforms("Data Engineer")},
        {"title":"Data Engineer","company":"Snowflake","location":"Remote","tag":"SQL",
         "url":"https://careers.snowflake.com/jobs?q=data+engineer","platforms":_platforms("Data Engineer")},
        {"title":"Analytics Engineer","company":"dbt Labs","location":"Remote","tag":"dbt",
         "url":"https://www.getdbt.com/dbt-labs/open-roles","platforms":_platforms("Data Engineer")},
        {"title":"Data Engineer","company":"Fivetran","location":"Remote","tag":"ETL",
         "url":"https://www.fivetran.com/careers?q=data+engineer","platforms":_platforms("Data Engineer")},
        {"title":"Data Engineer","company":"LinkedIn","location":"Various","tag":"Airflow",
         "url":"https://www.linkedin.com/jobs/search/?keywords=data+engineer","platforms":_platforms("Data Engineer")},
    ],
    "Cybersecurity Analyst": [
        {"title":"Security Analyst","company":"CrowdStrike","location":"Remote","tag":"Threat Intel",
         "url":"https://www.crowdstrike.com/careers/","platforms":_platforms("Cybersecurity Analyst")},
        {"title":"SOC Analyst","company":"Palo Alto Networks","location":"Santa Clara","tag":"SIEM",
         "url":"https://www.paloaltonetworks.com/company/careers","platforms":_platforms("Cybersecurity Analyst")},
        {"title":"Penetration Tester","company":"HackerOne","location":"Remote","tag":"Bug Bounty",
         "url":"https://www.hackerone.com/careers","platforms":_platforms("Cybersecurity Analyst")},
        {"title":"Security Engineer","company":"Cloudflare","location":"Remote","tag":"Network Sec",
         "url":"https://www.cloudflare.com/careers/jobs/?q=security","platforms":_platforms("Cybersecurity Analyst")},
        {"title":"Cybersecurity Analyst","company":"LinkedIn","location":"Various","tag":"Security",
         "url":"https://www.linkedin.com/jobs/search/?keywords=cybersecurity+analyst","platforms":_platforms("Cybersecurity Analyst")},
    ],
    "iOS Developer": [
        {"title":"iOS Engineer","company":"Apple","location":"Cupertino, CA","tag":"Swift",
         "url":"https://jobs.apple.com/en-us/search?search=ios+engineer","platforms":_platforms("iOS Developer")},
        {"title":"iOS Developer","company":"Airbnb","location":"San Francisco","tag":"SwiftUI",
         "url":"https://careers.airbnb.com/positions/?department=engineering","platforms":_platforms("iOS Developer")},
        {"title":"iOS Engineer","company":"Lyft","location":"San Francisco","tag":"Swift",
         "url":"https://www.lyft.com/careers?q=ios","platforms":_platforms("iOS Developer")},
        {"title":"Mobile Engineer – iOS","company":"Duolingo","location":"Pittsburgh","tag":"Swift",
         "url":"https://careers.duolingo.com/?q=ios","platforms":_platforms("iOS Developer")},
        {"title":"iOS Developer","company":"LinkedIn","location":"Various","tag":"Swift",
         "url":"https://www.linkedin.com/jobs/search/?keywords=ios+developer","platforms":_platforms("iOS Developer")},
    ],
    "Android Developer": [
        {"title":"Android Engineer","company":"Google","location":"Mountain View","tag":"Kotlin",
         "url":"https://careers.google.com/jobs/results/?q=android+engineer","platforms":_platforms("Android Developer")},
        {"title":"Android Developer","company":"Spotify","location":"Stockholm/Remote","tag":"Compose",
         "url":"https://www.lifeatspotify.com/jobs?q=android","platforms":_platforms("Android Developer")},
        {"title":"Android Engineer","company":"Grab","location":"Singapore","tag":"Kotlin",
         "url":"https://grab.careers/job-listing/?q=android","platforms":_platforms("Android Developer")},
        {"title":"Mobile Engineer","company":"Revolut","location":"Remote","tag":"MVVM",
         "url":"https://www.revolut.com/en-US/careers?q=android","platforms":_platforms("Android Developer")},
        {"title":"Android Developer","company":"LinkedIn","location":"Various","tag":"Kotlin",
         "url":"https://www.linkedin.com/jobs/search/?keywords=android+developer","platforms":_platforms("Android Developer")},
    ],
    "UI/UX Designer": [
        {"title":"Product Designer","company":"Figma","location":"San Francisco","tag":"Figma",
         "url":"https://www.figma.com/careers/#job-openings","platforms":_platforms("UI UX Designer")},
        {"title":"UX Designer","company":"Google","location":"Mountain View","tag":"Research",
         "url":"https://careers.google.com/jobs/results/?q=ux+designer","platforms":_platforms("UI UX Designer")},
        {"title":"UI/UX Designer","company":"Canva","location":"Sydney/Remote","tag":"Design Sys",
         "url":"https://www.canva.com/careers/?q=designer","platforms":_platforms("UI UX Designer")},
        {"title":"Product Designer","company":"Notion","location":"San Francisco","tag":"Prototyping",
         "url":"https://www.notion.so/careers","platforms":_platforms("UI UX Designer")},
        {"title":"UI/UX Designer","company":"LinkedIn","location":"Various","tag":"UX",
         "url":"https://www.linkedin.com/jobs/search/?keywords=ui+ux+designer","platforms":_platforms("UI UX Designer")},
    ],
    "QA Automation Engineer": [
        {"title":"QA Engineer","company":"Atlassian","location":"Remote","tag":"Cypress",
         "url":"https://www.atlassian.com/company/careers/all-jobs?q=qa","platforms":_platforms("QA Automation Engineer")},
        {"title":"Automation Engineer","company":"Testlio","location":"Remote","tag":"Selenium",
         "url":"https://testlio.com/careers/","platforms":_platforms("QA Automation Engineer")},
        {"title":"SDET","company":"Microsoft","location":"Redmond","tag":"Azure DevOps",
         "url":"https://careers.microsoft.com/us/en/search-results?keywords=sdet","platforms":_platforms("QA Automation Engineer")},
        {"title":"QA Automation","company":"Postman","location":"San Francisco","tag":"API Testing",
         "url":"https://www.postman.com/company/careers/?q=qa","platforms":_platforms("QA Automation Engineer")},
        {"title":"QA Automation Engineer","company":"LinkedIn","location":"Various","tag":"Testing",
         "url":"https://www.linkedin.com/jobs/search/?keywords=qa+automation+engineer","platforms":_platforms("QA Automation Engineer")},
    ],
    "Product Manager": [
        {"title":"Product Manager","company":"Google","location":"Mountain View","tag":"Growth",
         "url":"https://careers.google.com/jobs/results/?q=product+manager","platforms":_platforms("Product Manager")},
        {"title":"Senior PM","company":"Stripe","location":"Remote","tag":"Fintech",
         "url":"https://stripe.com/jobs/search?q=product+manager","platforms":_platforms("Product Manager")},
        {"title":"Product Manager","company":"Linear","location":"Remote","tag":"B2B SaaS",
         "url":"https://linear.app/careers","platforms":_platforms("Product Manager")},
        {"title":"Growth PM","company":"Duolingo","location":"Pittsburgh","tag":"Consumer",
         "url":"https://careers.duolingo.com/?q=product","platforms":_platforms("Product Manager")},
        {"title":"Product Manager","company":"LinkedIn","location":"Various","tag":"B2B",
         "url":"https://www.linkedin.com/jobs/search/?keywords=product+manager","platforms":_platforms("Product Manager")},
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
    "Threat Intel":"#f87171","Airflow":"#f97316","Tableau":"#60a5fa","A/B Testing":"#fbbf24",
    "GraphQL":"#a78bfa","Redis":"#f87171","Microservices":"#60a5fa","Serverless":"#f97316",
    "SwiftPM":"#f97316","CoreData":"#f97316","Hilt/Dagger":"#a78bfa","Penetration Testing":"#f87171",
}

# ── page ──────────────────────────────────────────────────────────────────────
st.markdown("<div class='page-title'>💼 Job Board</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Curated job openings at top tech companies — apply via your favourite platform</div>", unsafe_allow_html=True)

# ── filter ────────────────────────────────────────────────────────────────────
roles_available = sorted(JOB_LINKS.keys())
selected_role = st.selectbox("Filter by Role", ["All Roles"] + roles_available, index=0)

search_query = st.text_input("🔍 Search jobs", placeholder="e.g. Remote, Python, Senior…")

# ── render cards ──────────────────────────────────────────────────────────────
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

if selected_role == "All Roles":
    display = {r: JOB_LINKS[r] for r in roles_available}
else:
    display = {selected_role: JOB_LINKS[selected_role]}

total_shown = 0
for role, jobs in display.items():
    filtered = jobs
    if search_query:
        q = search_query.lower()
        filtered = [j for j in jobs if q in j["title"].lower() or q in j["company"].lower()
                    or q in j["location"].lower() or q in j["tag"].lower()]
    if not filtered:
        continue

    if selected_role == "All Roles":
        st.markdown(f"<div style='font-size:17px;font-weight:700;color:#a78bfa;margin-bottom:10px;margin-top:16px;'>{role}</div>", unsafe_allow_html=True)

    cols = st.columns(min(3, len(filtered)))
    for idx, job in enumerate(filtered):
        tag_color = TAG_COLORS.get(job["tag"], "#aaa")
        platforms = job.get("platforms", {})
        # Build the platform button row
        platform_buttons = ""
        for pname, purl in platforms.items():
            ps = PLATFORM_STYLES.get(pname, {"icon":"🌐","bg":"linear-gradient(135deg,#555,#333)"})
            platform_buttons += (
                f"<a href='{purl}' target='_blank' title='Apply on {pname}' "
                f"style='display:inline-flex;align-items:center;gap:4px;margin-right:6px;margin-bottom:5px;"
                f"background:{ps['bg']};color:#fff;text-decoration:none;border-radius:6px;"
                f"padding:4px 10px;font-size:11px;font-weight:600;transition:opacity 0.2s,transform 0.15s;"
                f"opacity:0.92;' "
                f"onmouseover=\"this.style.opacity='1';this.style.transform='translateY(-1px)'\" "
                f"onmouseout=\"this.style.opacity='0.92';this.style.transform='none'\">"
                f"{ps['icon']} {pname}</a>"
            )
        # Also add the company careers link
        platform_buttons += (
            f"<a href='{job['url']}' target='_blank' title='Company Careers Page' "
            f"style='display:inline-flex;align-items:center;gap:4px;margin-right:6px;margin-bottom:5px;"
            f"background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;text-decoration:none;"
            f"border-radius:6px;padding:4px 10px;font-size:11px;font-weight:600;transition:opacity 0.2s,transform 0.15s;"
            f"opacity:0.92;' "
            f"onmouseover=\"this.style.opacity='1';this.style.transform='translateY(-1px)'\" "
            f"onmouseout=\"this.style.opacity='0.92';this.style.transform='none'\">"
            f"🏢 Careers Page</a>"
        )
        with cols[idx % 3]:
            st.markdown(f"""
            <div class='card' style='min-height:170px;'>
                <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                    <div style='font-size:15px;font-weight:700;color:#fff;flex:1;'>{job['title']}</div>
                    <span style='background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.13);
                                 border-radius:12px;padding:2px 10px;font-size:11px;color:{tag_color};
                                 white-space:nowrap;margin-left:8px;'>{job['tag']}</span>
                </div>
                <div style='font-size:13px;color:rgba(255,255,255,0.55);margin-top:4px;'>🏢 {job['company']}</div>
                <div style='font-size:12px;color:rgba(255,255,255,0.35);margin-top:2px;'>📍 {job['location']}</div>
                <div style='font-size:11px;color:rgba(255,255,255,0.3);margin-top:10px;margin-bottom:4px;font-weight:600;letter-spacing:0.5px;'>APPLY VIA</div>
                <div style='display:flex;flex-wrap:wrap;gap:2px;'>
                    {platform_buttons}
                </div>
            </div>""", unsafe_allow_html=True)
        total_shown += 1

if total_shown == 0:
    st.markdown("""
    <div class='card' style='text-align:center;padding:40px;'>
        <div style='font-size:36px;'>🔍</div>
        <div style='font-size:16px;font-weight:600;color:#fff;margin-top:12px;'>No jobs found</div>
        <div style='font-size:13px;color:rgba(255,255,255,0.4);margin-top:6px;'>Try a different search term or role filter.</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;font-size:12px;color:rgba(255,255,255,0.25);'>Job links redirect to external platforms. Vision AI is not affiliated with any employer or job portal.</div>", unsafe_allow_html=True)
