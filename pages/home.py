"""
Home Page — Welcome screen and summary navigation cards.
Mirrors the Power BI 'Home Page' with quick-access navigation.
"""

import streamlit as st
import pandas as pd
from components.charts import format_currency, format_number
from utils.data_loader import compute_all_kpis

APP_URL = "http://127.0.0.1:8501/"


def _set_active_page(page_key: str):
    st.session_state.active_page = page_key


def render(df: pd.DataFrame):
    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown('<div class="page-title">📊 Sales Intelligence Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Powered by AI · Replicated & Enhanced from Power BI · 2014–2018 US Sales Data</div>', unsafe_allow_html=True)

    kpis = compute_all_kpis(df)

    # ── Top KPI Strip ─────────────────────────────────────────────────────────
    cols = st.columns(5)
    kpi_items = [
        ("Total Revenue",    format_currency(kpis["Total Revenue"]),    "💰"),
        ("Total Profit",     format_currency(kpis["Total Profit"]),     "📈"),
        ("Profit Margin",    f"{kpis['Profit Margin %']:.1f}%",        "🎯"),
        ("Total Orders",     format_number(kpis["Total Orders"]),       "🛒"),
        ("Rev / Order",      format_currency(kpis["Revenue per Order"]), "📦"),
    ]
    for col, (label, val, icon) in zip(cols, kpi_items):
        with col:
            st.markdown(
                f"""<div class="kpi-card">
  <span class="kpi-icon">{icon}</span>
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{val}</div>
</div>""",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Navigate to a Dashboard Section</div>', unsafe_allow_html=True)

    # ── Navigation Cards ──────────────────────────────────────────────────────
    nav_cols = st.columns(3)
    nav_items = [
        ("executive",  "📈", "Executive Overview & Trends",
         "KPI cards, revenue & profit trends, scatter analysis, order value distribution"),
        ("product",    "📦", "Product & Channel Performance",
         "Top products by revenue & margin, channel donut charts, product scatter"),
        ("geo",        "🗺️", "Geographic & Customer Insights",
         "US bubble map, state rankings, top customers, region breakdown"),
    ]
    for col, (page_key, icon, title, desc) in zip(nav_cols, nav_items):
        with col:
            if st.button(
                f"{icon}  {title}",
                key=f"home_nav_{page_key}",
                width="stretch"
            ):
                _set_active_page(page_key)
                st.rerun()
            st.caption(desc)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── AI Insights teaser ────────────────────────────────────────────────────
    if st.button(
        "🤖  AI Insights & Analytics — Natural Language Q&A + Auto Insights",
        key="home_nav_ai",
        width="stretch"
    ):
        _set_active_page("ai")
        st.rerun()

    st.markdown("---")

    # ── Dataset overview ──────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Dataset Overview</div>', unsafe_allow_html=True)
    oc1, oc2, oc3, oc4 = st.columns(4)
    oc1.metric("Total Records", f"{len(df):,}")
    oc2.metric("Unique Customers", f"{df['customer_name'].nunique():,}")
    oc3.metric("Products", f"{df['product_name'].nunique():,}")
    oc4.metric("States Covered", f"{df['state_name'].nunique():,}")

    with st.expander("📋 Raw Data Preview"):
        st.dataframe(
            df[["order_date","order_number","customer_name","product_name","channel",
                "us_region","quantity","unit_price","revenue","profit","profit_margin_pct"]]
            .head(500),
            use_container_width=True,
            height=350,
        )
