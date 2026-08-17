import sys, os
import pandas as pd
import streamlit as st
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import require_auth, render_sidebar, current_user, get_history

require_auth()
st.set_page_config(page_title="History - Vision", page_icon="&#128203;", layout="wide", initial_sidebar_state="expanded")
render_sidebar("history")

st.markdown("<div class='page-title'>&#128203; Analysis History</div>", unsafe_allow_html=True)
st.markdown("<div class='page-sub'>Every career analysis you have run, saved automatically</div>", unsafe_allow_html=True)

history = get_history(current_user())

if not history:
    st.markdown(
        "<div class='card' style='text-align:center;padding:48px;'>"
        "<div style='font-size:48px;'>&#128237;</div>"
        "<div style='font-size:18px;font-weight:700;color:#fff;margin-top:14px;'>No history yet</div>"
        "<div style='font-size:13px;color:rgba(255,255,255,0.4);margin-top:6px;'>Your analyses will appear here after you run them.</div>"
        "</div>",
        unsafe_allow_html=True
    )
    if st.button("Go to Analyzer", type="primary"):
        st.switch_page("pages/analyzer.py")
else:
    all_records = list(reversed(history))

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Analyses",  len(all_records))
    best = max(all_records, key=lambda h: h.get("top_score", 0))
    c2.metric("Best Match Ever", best["top_career"], f"{best['top_score']:.0f}%")
    c3.metric("Unique Roles Found", len(set(h["top_career"] for h in all_records)))

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    rows = [{"Date": h.get("date","?"), "Top Career Match": h.get("top_career","?"),
             "Match Score": f"{h.get('top_score',0):.1f}%", "Input Type": h.get("input_type","?")}
            for h in all_records]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:18px;font-weight:700;color:#fff;margin-bottom:12px;'>Detailed Breakdown</div>", unsafe_allow_html=True)

    for i, h in enumerate(all_records[:10]):
        with st.expander(
            f"&#128197; {h.get('date','?')}  -  {h.get('top_career','?')}  ({h.get('top_score',0):.1f}%)",
            expanded=(i == 0)
        ):
            all_roles = h.get("all_roles", [])
            if all_roles:
                import altair as alt
                df_r = pd.DataFrame(all_roles)
                chart = (
                    alt.Chart(df_r)
                    .mark_bar(cornerRadiusEnd=6)
                    .encode(
                        x=alt.X("Match Score:Q", scale=alt.Scale(domain=[0, 100])),
                        y=alt.Y("Career:N", sort="-x"),
                        color=alt.Color("Match Score:Q", scale=alt.Scale(scheme="purples"), legend=None),
                        tooltip=["Career", alt.Tooltip("Match Score:Q", format=".1f")]
                    )
                    .properties(height=220)
                    .configure_view(strokeWidth=0)
                    .configure_axis(labelColor="#aaa", titleColor="#aaa", gridColor="rgba(255,255,255,0.05)")
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.write("No breakdown data for this entry.")
