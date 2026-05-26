"""
Page 2 — Product & Channel Performance
Mirrors Power BI page: bar charts (products by revenue/margin),
donut charts (channel splits), scatter (revenue vs margin by product).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.charts import (
    bar_chart, donut_chart, scatter_chart, PALETTE, BASE_LAYOUT, GRID_CLR, format_currency
)
from utils.data_loader import product_performance, channel_performance


def render(df: pd.DataFrame):
    st.markdown('<div class="page-title">📦 Product & Channel Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Top Products · Channel Revenue & Profit Splits · Margin Analysis</div>', unsafe_allow_html=True)

    # ── Page Filters ──────────────────────────────────────────────────────────
    with st.expander("🔧 Page Filters", expanded=False):
        top_n = st.slider("Top N Products", 5, 30, 15, key="prod_topn")
        metric = st.radio("Primary Metric", ["Revenue", "Profit", "Profit Margin %"],
                          horizontal=True, key="prod_metric")

    prod_df = product_performance(df)
    chan_df  = channel_performance(df)

    metric_col = {"Revenue": "revenue", "Profit": "profit", "Profit Margin %": "avg_margin"}[metric]

    # ── Channel KPIs ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Channel Overview</div>', unsafe_allow_html=True)
    ck = st.columns(len(chan_df))
    for col, (_, row) in zip(ck, chan_df.iterrows()):
        with col:
            st.markdown(f"""
<div class="kpi-card">
  <div class="kpi-label">{row['channel']}</div>
  <div class="kpi-value">{format_currency(row['revenue'])}</div>
  <div class="kpi-delta-pos">Margin: {row['avg_margin']:.1f}%</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Product Bar Charts ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Product Performance</div>', unsafe_allow_html=True)
    pr1, pr2 = st.columns(2)

    with pr1:
        top_rev = prod_df.nlargest(top_n, "revenue")
        fig = go.Figure(go.Bar(
            x=top_rev["revenue"],
            y=top_rev["product_name"],
            orientation="h",
            marker=dict(
                color=top_rev["revenue"],
                colorscale=[[0, "#1e3a5f"], [1, "#4F8EF7"]],
                line_width=0,
            ),
            hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            title=dict(text=f"Top {top_n} Products by Revenue", font=dict(size=14, color="#e2e8f0")),
            **BASE_LAYOUT,
            yaxis=dict(autorange="reversed"),
        )
        fig.update_xaxes(tickformat="$,.0f", gridcolor=GRID_CLR)
        fig.update_yaxes(gridcolor=GRID_CLR)
        st.plotly_chart(fig, use_container_width=True)

    with pr2:
        top_margin = prod_df.nlargest(top_n, "avg_margin")
        fig2 = go.Figure(go.Bar(
            x=top_margin["avg_margin"],
            y=top_margin["product_name"],
            orientation="h",
            marker=dict(
                color=top_margin["avg_margin"],
                colorscale=[[0, "#14532d"], [1, "#22C55E"]],
                line_width=0,
            ),
            hovertemplate="<b>%{y}</b><br>Margin: %{x:.1f}%<extra></extra>",
        ))
        fig2.update_layout(
            title=dict(text=f"Top {top_n} Products by Profit Margin %", font=dict(size=14, color="#e2e8f0")),
            **BASE_LAYOUT,
            yaxis=dict(autorange="reversed"),
        )
        fig2.update_xaxes(tickformat=".1f", gridcolor=GRID_CLR)
        fig2.update_yaxes(gridcolor=GRID_CLR)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Channel Donut Charts ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">Channel Revenue, Profit & Margin Split</div>', unsafe_allow_html=True)
    dc1, dc2, dc3 = st.columns(3)

    donut_configs = [
        (dc1, "revenue",    "Channel Revenue Split",     "$,.0f"),
        (dc2, "profit",     "Channel Profit Split",      "$,.0f"),
        (dc3, "avg_margin", "Channel Avg Margin %",      ".1f"),
    ]
    for col, val_col, title, fmt in donut_configs:
        with col:
            fig_d = px.pie(
                chan_df, names="channel", values=val_col,
                hole=0.55, title=title,
                color_discrete_sequence=PALETTE,
            )
            fig_d.update_traces(
                textposition="outside",
                textinfo="label+percent",
                hovertemplate=f"<b>%{{label}}</b><br>%{{value:{fmt}}}<extra></extra>",
                marker=dict(line=dict(color="rgba(0,0,0,0.3)", width=2)),
            )
            fig_d.update_layout(**BASE_LAYOUT)
            st.plotly_chart(fig_d, use_container_width=True)

    # ── Product Revenue vs Margin Scatter ─────────────────────────────────────
    st.markdown('<div class="section-header">Product Revenue vs Profit Margin</div>', unsafe_allow_html=True)
    fig_sc = px.scatter(
        prod_df.head(40), x="revenue", y="avg_margin",
        size="orders", hover_name="product_name",
        color="avg_margin",
        color_continuous_scale="Blues",
        labels={"revenue": "Total Revenue ($)", "avg_margin": "Avg Profit Margin (%)", "orders": "# Orders"},
        size_max=35,
    )
    fig_sc.update_traces(
        marker=dict(opacity=0.8, line=dict(width=1, color="rgba(255,255,255,0.2)")),
    )
    fig_sc.update_layout(
        title=dict(text="Product Bubble Chart: Revenue vs Margin (bubble size = # Orders)",
                   font=dict(size=14, color="#e2e8f0")),
        **BASE_LAYOUT,
    )
    fig_sc.update_xaxes(tickformat="$,.0f", gridcolor=GRID_CLR)
    fig_sc.update_yaxes(tickformat=".1f", gridcolor=GRID_CLR)
    st.plotly_chart(fig_sc, use_container_width=True)

    # ── Product Detail Table ──────────────────────────────────────────────────
    with st.expander("📋 Full Product Performance Table"):
        tbl = prod_df.copy()
        tbl["revenue"]    = tbl["revenue"].apply(lambda x: f"${x:,.0f}")
        tbl["profit"]     = tbl["profit"].apply(lambda x: f"${x:,.0f}")
        tbl["avg_margin"] = tbl["avg_margin"].apply(lambda x: f"{x:.1f}%")
        tbl.columns       = ["Product", "Revenue", "Profit", "Orders", "Avg Margin %"]
        st.dataframe(tbl, use_container_width=True, hide_index=True, height=400)

    # ── Channel x Product Heatmap ─────────────────────────────────────────────
    with st.expander("🔥 Channel × Product Revenue Heatmap"):
        pivot = df.groupby(["channel", "product_name"])["revenue"].sum().unstack(fill_value=0)
        pivot = pivot[pivot.sum().nlargest(20).index]
        fig_hm = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale="Blues",
            hovertemplate="Channel: %{y}<br>Product: %{x}<br>Revenue: $%{z:,.0f}<extra></extra>",
        ))
        fig_hm.update_layout(
            title=dict(text="Revenue Heatmap: Channel × Top 20 Products",
                       font=dict(size=14, color="#e2e8f0")),
            **BASE_LAYOUT,
        )
        st.plotly_chart(fig_hm, use_container_width=True)
