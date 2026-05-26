"""
Page 1 — Executive Overview & Trends
Mirrors Power BI page: KPI cards, line charts (revenue/profit by month),
column chart (order value distribution), scatter (unit price vs margin).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from components.charts import (
    line_chart, bar_chart, scatter_chart, kpi_card_html,
    format_currency, format_number, PALETTE, BASE_LAYOUT, GRID_CLR
)
from utils.data_loader import (
    compute_all_kpis, monthly_revenue_profit, order_value_distribution
)


def render(df: pd.DataFrame):
    st.markdown('<div class="page-title">📈 Executive Overview & Trends</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Core KPIs · Monthly Trends · Order Analysis · Profitability Scatter</div>', unsafe_allow_html=True)

    kpis = compute_all_kpis(df)

    # ── Page-level filter: Month ───────────────────────────────────────────────
    all_months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    month_map  = {m: i+1 for i, m in enumerate(all_months)}

    with st.expander("🔧 Page Filters", expanded=False):
        sel_months = st.multiselect("Month", all_months, default=all_months, key="exec_months")

    if sel_months:
        df = df[df["order_month_num"].isin([month_map[m] for m in sel_months])]
        kpis = compute_all_kpis(df)

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)

    card_data = [
        (k1, "Total Revenue",    format_currency(kpis["Total Revenue"]),    "💰"),
        (k2, "Total Profit",     format_currency(kpis["Total Profit"]),     "📈"),
        (k3, "Profit Margin %",  f"{kpis['Profit Margin %']:.1f}%",         "🎯"),
        (k4, "Total Orders",     format_number(kpis["Total Orders"]),        "🛒"),
        (k5, "Rev / Order",      format_currency(kpis["Revenue per Order"]), "📦"),
    ]
    for col, label, val, icon in card_data:
        with col:
            st.markdown(kpi_card_html(label, val, icon=icon), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Monthly Trend Lines ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Revenue & Profit Trends by Month</div>', unsafe_allow_html=True)
    mdf = monthly_revenue_profit(df)

    tc1, tc2 = st.columns(2)

    with tc1:
        fig_rev = go.Figure()
        fig_rev.add_trace(go.Scatter(
            x=mdf["period"], y=mdf["revenue"],
            mode="lines+markers",
            name="Revenue",
            line=dict(color=PALETTE[0], width=2.5),
            fill="tozeroy",
            fillcolor="rgba(79,142,247,0.1)",
            hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
        ))
        fig_rev.update_layout(
            title=dict(text="Monthly Revenue", font=dict(size=14, color="#e2e8f0")),
            **BASE_LAYOUT,
        )
        fig_rev.update_yaxes(tickformat="$,.0f", gridcolor=GRID_CLR)
        fig_rev.update_xaxes(gridcolor=GRID_CLR, tickangle=45)
        st.plotly_chart(fig_rev, use_container_width=True)

    with tc2:
        fig_prof = go.Figure()
        fig_prof.add_trace(go.Scatter(
            x=mdf["period"], y=mdf["profit"],
            mode="lines+markers",
            name="Profit",
            line=dict(color=PALETTE[2], width=2.5),
            fill="tozeroy",
            fillcolor="rgba(34,197,94,0.1)",
            hovertemplate="<b>%{x}</b><br>Profit: $%{y:,.0f}<extra></extra>",
        ))
        fig_prof.update_layout(
            title=dict(text="Monthly Profit", font=dict(size=14, color="#e2e8f0")),
            **BASE_LAYOUT,
        )
        fig_prof.update_yaxes(tickformat="$,.0f", gridcolor=GRID_CLR)
        fig_prof.update_xaxes(gridcolor=GRID_CLR, tickangle=45)
        st.plotly_chart(fig_prof, use_container_width=True)

    # ── Revenue vs Profit Dual-axis ────────────────────────────────────────────
    with st.expander("📊 Revenue vs Profit — Side by Side Comparison"):
        fig_dual = go.Figure()
        fig_dual.add_trace(go.Bar(x=mdf["period"], y=mdf["revenue"], name="Revenue",
                                  marker_color=PALETTE[0], opacity=0.8))
        fig_dual.add_trace(go.Bar(x=mdf["period"], y=mdf["profit"], name="Profit",
                                  marker_color=PALETTE[2], opacity=0.8))
        fig_dual.update_layout(barmode="group", **BASE_LAYOUT,
            title=dict(text="Revenue vs Profit (Monthly)", font=dict(size=14, color="#e2e8f0")))
        fig_dual.update_yaxes(tickformat="$,.0f", gridcolor=GRID_CLR)
        fig_dual.update_xaxes(gridcolor=GRID_CLR, tickangle=45)
        st.plotly_chart(fig_dual, use_container_width=True)

    # ── Order Value Distribution + Scatter ────────────────────────────────────
    bc1, bc2 = st.columns(2)

    with bc1:
        st.markdown('<div class="section-header">Order Value Distribution</div>', unsafe_allow_html=True)
        order_vals = df.groupby("order_number")["revenue"].sum()
        bins   = [0, 5000, 10000, 25000, 50000, 100000, 250000, 500000, float("inf")]
        labels = ["<5K", "5-10K", "10-25K", "25-50K", "50-100K", "100-250K", "250-500K", ">500K"]
        binned = pd.cut(order_vals, bins=bins, labels=labels).value_counts().sort_index().reset_index()
        binned.columns = ["bin", "count"]

        fig_hist = go.Figure(go.Bar(
            x=binned["bin"], y=binned["count"],
            marker_color=PALETTE[0],
            marker_line_width=0,
        ))
        fig_hist.update_layout(
            title=dict(text="Order Value Bins", font=dict(size=14, color="#e2e8f0")),
            **BASE_LAYOUT,
        )
        fig_hist.update_yaxes(gridcolor=GRID_CLR)
        fig_hist.update_xaxes(gridcolor=GRID_CLR)
        st.plotly_chart(fig_hist, use_container_width=True)

    with bc2:
        st.markdown('<div class="section-header">Unit Price vs Profit Margin</div>', unsafe_allow_html=True)
        scatter_df = df[["unit_price", "profit_margin_pct", "channel", "product_name"]].dropna()
        fig_sc = px.scatter(
            scatter_df, x="unit_price", y="profit_margin_pct",
            color="channel", hover_name="product_name",
            color_discrete_sequence=PALETTE,
            opacity=0.55,
            labels={"unit_price": "Unit Price ($)", "profit_margin_pct": "Profit Margin (%)"},
        )
        fig_sc.update_traces(marker=dict(size=5))
        fig_sc.update_layout(
            title=dict(text="Unit Price vs Profit Margin %", font=dict(size=14, color="#e2e8f0")),
            **BASE_LAYOUT,
        )
        fig_sc.update_xaxes(tickformat="$,.0f", gridcolor=GRID_CLR)
        fig_sc.update_yaxes(tickformat=".1f", gridcolor=GRID_CLR)
        st.plotly_chart(fig_sc, use_container_width=True)

    # ── YoY Comparison ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Year-over-Year Revenue Comparison</div>', unsafe_allow_html=True)
    yoy = df.groupby(["year", "month"]).agg(revenue=("revenue", "sum")).reset_index()
    fig_yoy = go.Figure()
    for i, yr in enumerate(sorted(yoy["year"].unique())):
        yr_df = yoy[yoy["year"] == yr].sort_values("month")
        fig_yoy.add_trace(go.Scatter(
            x=yr_df["month"], y=yr_df["revenue"],
            mode="lines+markers", name=str(yr),
            line=dict(color=PALETTE[i], width=2),
        ))
    fig_yoy.update_layout(
        title=dict(text="YoY Monthly Revenue", font=dict(size=14, color="#e2e8f0")),
        **BASE_LAYOUT,
    )
    fig_yoy.update_xaxes(
        tickvals=list(range(1, 13)),
        ticktext=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        gridcolor=GRID_CLR,
    )
    fig_yoy.update_yaxes(tickformat="$,.0f", gridcolor=GRID_CLR)
    st.plotly_chart(fig_yoy, use_container_width=True)
