"""
Sales Intelligence Dashboard
Streamlit-powered replica and enhancement of the Power BI Sales Report.
Covers: Executive Overview & Trends | Product & Channel Performance | Geographic & Customer Insights
"""

import streamlit as st
from utils.data_loader import load_data
from utils.styles import inject_css


APP_URL = "http://127.0.0.1:8501/"

if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"

st.set_page_config(
    page_title="Sales Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

PAGES = {
    "home":       ("\U0001F3E0", "Home"),
    "executive":  ("\U0001F4C8", "Executive Overview & Trends"),
    "product":    ("\U0001F4E6", "Product & Channel Performance"),
    "geo":        ("\U0001F5FA\ufe0f", "Geographic & Customer Insights"),
    "ai":         ("\U0001F916", "AI Insights & Analytics"),
}


def set_active_page(page_key: str):
    st.session_state.active_page = page_key


df = load_data()

if "active_page" not in st.session_state or st.session_state.active_page not in PAGES:
    query_page = st.query_params.get("page", "home")
    if isinstance(query_page, list):
        query_page = query_page[0] if query_page else "home"
    if query_page not in PAGES:
        query_page = "home"
    st.session_state.active_page = query_page

with st.sidebar:
    st.markdown('<div class="sidebar-logo">📊 Sales Intelligence</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### Navigation")
    for key, (icon, label) in PAGES.items():
        is_active = (st.session_state.active_page == key)
        if st.button(
            f"{icon}  {label}",
            key=f"nav_{key}",
            type="primary" if is_active else "secondary",
            width="stretch"
        ):
            set_active_page(key)
            st.rerun()

    st.markdown("---")
    st.markdown("### Global Filters")

    years = sorted(df["year"].dropna().unique().tolist())
    sel_years = st.multiselect("Year", years, default=years, key="g_year")

    channels = sorted(df["channel"].dropna().unique().tolist())
    sel_channels = st.multiselect("Channel", channels, default=channels, key="g_channel")

    regions = sorted(df["us_region"].dropna().unique().tolist())
    sel_regions = st.multiselect("Region", regions, default=regions, key="g_region")

    st.markdown("---")
    st.caption("Power BI -> Streamlit Conversion\nData: 2014-2018 US Sales")

fdf = df.copy()
if sel_years:
    fdf = fdf[fdf["year"].isin(sel_years)]
if sel_channels:
    fdf = fdf[fdf["channel"].isin(sel_channels)]
if sel_regions:
    fdf = fdf[fdf["us_region"].isin(sel_regions)]

page = st.session_state.active_page

if page == "home":
    from pages.home import render
    render(fdf)
elif page == "executive":
    from pages.executive import render
    render(fdf)
elif page == "product":
    from pages.product import render
    render(fdf)
elif page == "geo":
    from pages.geo import render
    render(fdf)
elif page == "ai":
    from pages.ai_insights import render
    render(fdf)
