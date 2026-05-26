"""
Page 3 — Geographic & Customer Insights
Mirrors Power BI page: US bubble map (profit by state), bar charts
(top/bottom customers, state revenue), donut (region split).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.charts import (
    PALETTE, BASE_LAYOUT, GRID_CLR, format_currency, kpi_card_html
)
from utils.data_loader import (
    state_performance, customer_performance, region_performance
)


def render(df: pd.DataFrame):
    st.markdown('<div class="page-title">🗺️ Geographic & Customer Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">US Map · State Rankings · Top/Bottom Customers · Region Breakdown</div>', unsafe_allow_html=True)

    state_df  = state_performance(df)
    cust_df   = customer_performance(df)
    region_df = region_performance(df)

    # ── Region KPI Strip ──────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Region KPIs</div>', unsafe_allow_html=True)
    reg_cols = st.columns(len(region_df))
    for col, (_, row) in zip(reg_cols, region_df.iterrows()):
        with col:
            st.markdown(f"""
<div class="kpi-card">
  <div class="kpi-label">{row['us_region']}</div>
  <div class="kpi-value">{format_currency(row['revenue'])}</div>
  <div class="kpi-delta-pos">Margin: {row['avg_margin']:.1f}%</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── US Map + Region Donuts ────────────────────────────────────────────────
    st.markdown('<div class="section-header">US Geographic Distribution</div>', unsafe_allow_html=True)
    map_col, pie_col = st.columns([3, 2])

    with map_col:
        map_metric = st.selectbox("Map Metric", ["profit", "revenue", "avg_margin"],
                                  format_func=lambda x: {"profit":"Total Profit","revenue":"Total Revenue","avg_margin":"Avg Margin %"}[x],
                                  key="geo_map_metric")
        fig_map = px.scatter_geo(
            state_df, lat="lat", lon="lon",
            size=map_metric, hover_name="state_name",
            color=map_metric,
            color_continuous_scale="Blues",
            scope="usa",
            size_max=55,
            hover_data={"revenue": ":$,.0f", "profit": ":$,.0f", "avg_margin": ":.1f"},
            labels={map_metric: {"profit":"Total Profit","revenue":"Total Revenue","avg_margin":"Avg Margin %"}[map_metric]},
        )
        fig_map.update_layout(
            geo=dict(
                bgcolor="rgba(0,0,0,0)",
                lakecolor="rgba(0,0,0,0)",
                landcolor="rgba(20,30,50,0.85)",
                showlakes=True, showland=True,
                countrycolor="rgba(255,255,255,0.1)",
            ),
            title=dict(text=f"US States — {map_metric.replace('_',' ').title()}",
                       font=dict(size=14, color="#e2e8f0")),
            **BASE_LAYOUT,
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with pie_col:
        fig_r1 = px.pie(region_df, names="us_region", values="revenue",
                         hole=0.52, title="Region Revenue Split",
                         color_discrete_sequence=PALETTE)
        fig_r1.update_traces(textinfo="label+percent", textposition="outside",
                              marker=dict(line=dict(color="rgba(0,0,0,0.3)", width=2)))
        fig_r1.update_layout(**BASE_LAYOUT)
        st.plotly_chart(fig_r1, use_container_width=True)

        fig_r2 = px.pie(region_df, names="us_region", values="profit",
                         hole=0.52, title="Region Profit Split",
                         color_discrete_sequence=PALETTE)
        fig_r2.update_traces(textinfo="label+percent", textposition="outside",
                              marker=dict(line=dict(color="rgba(0,0,0,0.3)", width=2)))
        fig_r2.update_layout(**BASE_LAYOUT)
        st.plotly_chart(fig_r2, use_container_width=True)

    # ── State Rankings ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">State Revenue Rankings</div>', unsafe_allow_html=True)
    sr1, sr2 = st.columns(2)

    with sr1:
        top_states = state_df.nlargest(15, "revenue")
        fig_st = go.Figure(go.Bar(
            x=top_states["revenue"],
            y=top_states["state_name"],
            orientation="h",
            marker=dict(color=top_states["revenue"],
                        colorscale=[[0,"#1e3a5f"],[1,"#4F8EF7"]],
                        line_width=0),
            hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>",
        ))
        fig_st.update_layout(
            title=dict(text="Top 15 States by Revenue", font=dict(size=14, color="#e2e8f0")),
            **BASE_LAYOUT, yaxis=dict(autorange="reversed"),
        )
        fig_st.update_xaxes(tickformat="$,.0f", gridcolor=GRID_CLR)
        st.plotly_chart(fig_st, use_container_width=True)

    with sr2:
        bot_states = state_df.nsmallest(15, "revenue")
        fig_st2 = go.Figure(go.Bar(
            x=bot_states["revenue"],
            y=bot_states["state_name"],
            orientation="h",
            marker=dict(color=bot_states["revenue"],
                        colorscale=[[0,"#3f0000"],[1,"#EF4444"]],
                        line_width=0),
        ))
        fig_st2.update_layout(
            title=dict(text="Bottom 15 States by Revenue", font=dict(size=14, color="#e2e8f0")),
            **BASE_LAYOUT, yaxis=dict(autorange="reversed"),
        )
        fig_st2.update_xaxes(tickformat="$,.0f", gridcolor=GRID_CLR)
        st.plotly_chart(fig_st2, use_container_width=True)

    # ── Customer Analysis ──────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Customer Performance</div>', unsafe_allow_html=True)

    cust_tab1, cust_tab2, cust_tab3 = st.tabs(["🏆 Top Customers", "📉 Bottom Customers", "📊 All Customers"])

    with cust_tab1:
        cc1, cc2 = st.columns(2)
        with cc1:
            top_cust = cust_df.head(15)
            fig_tc = go.Figure(go.Bar(
                x=top_cust["revenue"], y=top_cust["customer_name"],
                orientation="h",
                marker=dict(color=top_cust["revenue"],
                            colorscale=[[0,"#1e3a5f"],[1,"#4F8EF7"]],
                            line_width=0),
            ))
            fig_tc.update_layout(
                title=dict(text="Top 15 Customers by Revenue", font=dict(size=14, color="#e2e8f0")),
                **BASE_LAYOUT, yaxis=dict(autorange="reversed"),
            )
            fig_tc.update_xaxes(tickformat="$,.0f", gridcolor=GRID_CLR)
            st.plotly_chart(fig_tc, use_container_width=True)

        with cc2:
            top_cust_m = cust_df.nlargest(15, "avg_margin")
            fig_tm = go.Figure(go.Bar(
                x=top_cust_m["avg_margin"], y=top_cust_m["customer_name"],
                orientation="h",
                marker=dict(color=top_cust_m["avg_margin"],
                            colorscale=[[0,"#14532d"],[1,"#22C55E"]],
                            line_width=0),
            ))
            fig_tm.update_layout(
                title=dict(text="Top 15 Customers by Profit Margin %", font=dict(size=14, color="#e2e8f0")),
                **BASE_LAYOUT, yaxis=dict(autorange="reversed"),
            )
            fig_tm.update_xaxes(tickformat=".1f", gridcolor=GRID_CLR)
            st.plotly_chart(fig_tm, use_container_width=True)

    with cust_tab2:
        cc3, cc4 = st.columns(2)
        with cc3:
            bot_cust = cust_df.tail(15)
            fig_bc = go.Figure(go.Bar(
                x=bot_cust["revenue"], y=bot_cust["customer_name"],
                orientation="h",
                marker=dict(color=bot_cust["revenue"],
                            colorscale=[[0,"#3f0000"],[1,"#EF4444"]],
                            line_width=0),
            ))
            fig_bc.update_layout(
                title=dict(text="Bottom 15 Customers by Revenue", font=dict(size=14, color="#e2e8f0")),
                **BASE_LAYOUT, yaxis=dict(autorange="reversed"),
            )
            fig_bc.update_xaxes(tickformat="$,.0f", gridcolor=GRID_CLR)
            st.plotly_chart(fig_bc, use_container_width=True)

        with cc4:
            bot_cust_m = cust_df.nsmallest(15, "avg_margin")
            fig_bm = go.Figure(go.Bar(
                x=bot_cust_m["avg_margin"], y=bot_cust_m["customer_name"],
                orientation="h",
                marker=dict(color=bot_cust_m["avg_margin"],
                            colorscale=[[0,"#3f0000"],[1,"#F59E0B"]],
                            line_width=0),
            ))
            fig_bm.update_layout(
                title=dict(text="Bottom 15 Customers by Profit Margin %", font=dict(size=14, color="#e2e8f0")),
                **BASE_LAYOUT, yaxis=dict(autorange="reversed"),
            )
            fig_bm.update_xaxes(tickformat=".1f", gridcolor=GRID_CLR)
            st.plotly_chart(fig_bm, use_container_width=True)

    with cust_tab3:
        tbl = cust_df.copy()
        tbl["revenue"]    = tbl["revenue"].apply(lambda x: f"${x:,.0f}")
        tbl["profit"]     = tbl["profit"].apply(lambda x: f"${x:,.0f}")
        tbl["avg_margin"] = tbl["avg_margin"].apply(lambda x: f"{x:.1f}%")
        tbl.columns       = ["Customer", "Revenue", "Profit", "Orders", "Avg Margin %"]
        st.dataframe(tbl, use_container_width=True, hide_index=True, height=500)

    # ── Customer Scatter ──────────────────────────────────────────────────────
    with st.expander("🔍 Customer Revenue vs Margin Scatter"):
        fig_csc = px.scatter(
            cust_df.head(60), x="revenue", y="avg_margin",
            size="orders", hover_name="customer_name",
            color="avg_margin",
            color_continuous_scale="Blues",
            size_max=30,
            labels={"revenue": "Total Revenue ($)", "avg_margin": "Avg Margin (%)", "orders": "Orders"},
        )
        fig_csc.update_layout(
            title=dict(text="Customer Scatter: Revenue vs Avg Profit Margin",
                       font=dict(size=14, color="#e2e8f0")),
            **BASE_LAYOUT,
        )
        fig_csc.update_xaxes(tickformat="$,.0f", gridcolor=GRID_CLR)
        fig_csc.update_yaxes(tickformat=".1f", gridcolor=GRID_CLR)
        st.plotly_chart(fig_csc, use_container_width=True)
