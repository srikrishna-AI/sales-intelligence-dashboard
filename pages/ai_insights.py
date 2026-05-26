"""
Page 4 — AI Insights & Analytics
Powered by Gemini via the Google Gen AI SDK.
Features: auto-generated executive summary, trend explanations,
anomaly detection, and a natural language Q&A chatbot.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from utils.data_loader import compute_all_kpis, monthly_revenue_profit
from components.charts import format_currency, PALETTE, BASE_LAYOUT, GRID_CLR
import plotly.graph_objects as go


# ─────────────────────────────────────────────────────────────────────────────
# Gemini API Helper
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_SYSTEM_PROMPT = (
    "You are an expert sales analyst and business intelligence consultant. "
    "Analyze the provided sales data and give concise, actionable insights. "
    "Use numbers from the context. Keep responses focused and professional. "
    "Format with bullet points where helpful."
)


def call_gemini(prompt: str, system: str = "", max_tokens: int = 800) -> str:
    """
    Call Gemini via the Google Gen AI SDK.
    Requires GEMINI_API_KEY in environment variables or the API key input.
    """
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("API_KEY")
        or ""
    )
    if not api_key:
        return _fallback_insight(prompt)

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
            config={
                "system_instruction": system or DEFAULT_SYSTEM_PROMPT,
                "max_output_tokens": max_tokens,
            },
        )
        return (resp.text or "").strip() or "Gemini returned an empty response."
    except ImportError:
        return _fallback_insight(prompt)
    except Exception as e:
        if "api_key" in str(e).lower() or "auth" in str(e).lower():
            return "**API Key Required** - Set your `GEMINI_API_KEY` environment variable to enable AI insights."
        return f"API Error: {str(e)}"

def _fallback_insight(prompt: str) -> str:
    """Rule-based fallback when no API key is configured."""
    return (
        "📝 **AI Insights (Demo Mode)**\n\n"
        "Install the `google-genai` package and set `GEMINI_API_KEY` to enable full AI analysis. "
        "In the meantime, here are the key signals from the data visible in the charts:\n\n"
        "- **Revenue trend**: Check the Executive Overview page for monthly patterns.\n"
        "- **Top performers**: Visit Product & Channel page for ranking details.\n"
        "- **Geographic spread**: The map page highlights regional concentration.\n\n"
        "_To enable real AI: `pip install google-genai` and set `GEMINI_API_KEY`._"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Build data context string for Gemini
# ─────────────────────────────────────────────────────────────────────────────

def build_context(df: pd.DataFrame) -> str:
    kpis = compute_all_kpis(df)
    top_products = (df.groupby("product_name")["revenue"].sum()
                      .nlargest(5).reset_index()
                      .apply(lambda r: f"{r['product_name']}: ${r['revenue']:,.0f}", axis=1)
                      .tolist())
    top_states   = (df.groupby("state_name")["revenue"].sum()
                      .nlargest(5).reset_index()
                      .apply(lambda r: f"{r['state_name']}: ${r['revenue']:,.0f}", axis=1)
                      .tolist())
    top_cust     = (df.groupby("customer_name")["revenue"].sum()
                      .nlargest(5).reset_index()
                      .apply(lambda r: f"{r['customer_name']}: ${r['revenue']:,.0f}", axis=1)
                      .tolist())
    chan_rev      = (df.groupby("channel")["revenue"].sum()
                      .reset_index()
                      .apply(lambda r: f"{r['channel']}: ${r['revenue']:,.0f}", axis=1)
                      .tolist())
    monthly = monthly_revenue_profit(df)
    rev_by_yr = df.groupby("year")["revenue"].sum().to_dict()

    return f"""
SALES DATA CONTEXT
==================
Date Range: {df['order_date'].min().date()} to {df['order_date'].max().date()}
Total Records: {len(df):,}

KEY KPIs:
- Total Revenue: {format_currency(kpis['Total Revenue'])}
- Total Profit: {format_currency(kpis['Total Profit'])}
- Profit Margin: {kpis['Profit Margin %']:.1f}%
- Total Orders: {kpis['Total Orders']:,}
- Revenue per Order: {format_currency(kpis['Revenue per Order'])}

CHANNELS: {', '.join(df['channel'].unique().tolist())}
REGIONS: {', '.join(df['us_region'].unique().tolist())}
Products: {df['product_name'].nunique()} unique | Customers: {df['customer_name'].nunique()} | States: {df['state_name'].nunique()}

TOP 5 PRODUCTS BY REVENUE:
{chr(10).join(top_products)}

TOP 5 STATES BY REVENUE:
{chr(10).join(top_states)}

TOP 5 CUSTOMERS:
{chr(10).join(top_cust)}

CHANNEL REVENUE:
{chr(10).join(chan_rev)}

ANNUAL REVENUE:
{chr(10).join([f'{yr}: ${rev:,.0f}' for yr, rev in sorted(rev_by_yr.items())])}
"""


# ─────────────────────────────────────────────────────────────────────────────
# Anomaly Detection (rule-based + statistical)
# ─────────────────────────────────────────────────────────────────────────────

def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Detect revenue anomaly months using z-score."""
    monthly = df.groupby(["year", "month"])["revenue"].sum().reset_index()
    monthly["z_score"] = (
        (monthly["revenue"] - monthly["revenue"].mean()) / monthly["revenue"].std()
    )
    monthly["anomaly"] = monthly["z_score"].abs() > 2.0
    monthly["period"]  = monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)
    return monthly


# ─────────────────────────────────────────────────────────────────────────────
# Main Render
# ─────────────────────────────────────────────────────────────────────────────

def render(df: pd.DataFrame):
    st.markdown('<div class="page-title">🤖 AI Insights & Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Gemini-Powered Executive Summary · Auto Insights · Anomaly Detection · Natural Language Q&A</div>', unsafe_allow_html=True)

    context = build_context(df)

    # ── API Key Configuration ─────────────────────────────────────────────────
    with st.expander("🔑 API Configuration", expanded=False):
        api_key = st.text_input("Gemini API Key (optional - overrides env var)",
                                 type="password", key="ai_api_key",
                                 help="Set GEMINI_API_KEY env var for persistent configuration")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            st.success("API key set for this session")
        st.caption("Without a key, the dashboard runs in demo mode with pre-computed insights.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Executive Summary", "💡 Auto Insights", "⚠️ Anomaly Detection", "💬 Q&A Chatbot"
    ])

    # ── Tab 1: Executive Summary ───────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-header">AI-Generated Executive Summary</div>', unsafe_allow_html=True)

        if st.button("🔄 Generate Executive Summary", key="gen_summary", type="primary"):
            with st.spinner("Gemini is analyzing your data..."):
                prompt = f"""
Based on this sales data, write a concise executive summary (5-7 bullet points) covering:
1. Overall business health and revenue performance
2. Profitability analysis
3. Top performing segments (products, channels, regions)
4. Areas of concern or underperformance
5. 2-3 strategic recommendations

{context}
"""
                summary = call_gemini(prompt, max_tokens=600)
                st.session_state["exec_summary"] = summary

        if "exec_summary" in st.session_state:
            st.markdown(f"""
<div class="insight-card">
<span class="insight-icon">📋</span><strong>Executive Summary</strong><br><br>
{st.session_state['exec_summary'].replace(chr(10), '<br>')}
</div>
""", unsafe_allow_html=True)
        else:
            # Show data context preview
            kpis = compute_all_kpis(df)
            cols = st.columns(3)
            cols[0].metric("Total Revenue",   format_currency(kpis["Total Revenue"]))
            cols[1].metric("Total Profit",    format_currency(kpis["Total Profit"]))
            cols[2].metric("Profit Margin %", f"{kpis['Profit Margin %']:.1f}%")
            st.info("👆 Click **Generate Executive Summary** to get an AI-powered analysis of your filtered data.")

    # ── Tab 2: Auto Insights ───────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-header">Automated Business Insights</div>', unsafe_allow_html=True)

        insight_types = {
            "📈 Revenue Trend Analysis":     "Analyze the revenue trends, seasonality patterns, and year-over-year growth.",
            "🌍 Geographic Analysis":         "Identify geographic concentration risks, underperforming regions, and expansion opportunities.",
            "📦 Product Portfolio Analysis":  "Analyze product mix, identify stars vs laggards, and recommend portfolio adjustments.",
            "👥 Customer Segmentation":        "Segment customers by value, identify at-risk high-value customers, and suggest retention strategies.",
            "🔮 Growth Forecast":             "Based on historical trends, provide a growth forecast and key assumptions.",
        }

        sel_insight = st.selectbox("Select Insight Type", list(insight_types.keys()), key="insight_type")

        if st.button("💡 Generate Insight", key="gen_insight", type="primary"):
            with st.spinner(f"Analyzing…"):
                prompt = f"{insight_types[sel_insight]}\n\n{context}"
                insight = call_gemini(prompt, max_tokens=500)
                st.session_state[f"insight_{sel_insight}"] = insight

        cache_key = f"insight_{sel_insight}"
        if cache_key in st.session_state:
            st.markdown(f"""
<div class="insight-card">
<span class="insight-icon">💡</span><strong>{sel_insight}</strong><br><br>
{st.session_state[cache_key].replace(chr(10), '<br>')}
</div>
""", unsafe_allow_html=True)

        # Static auto-computed insights
        st.markdown('<div class="section-header">Auto-Computed Statistical Insights</div>', unsafe_allow_html=True)
        kpis = compute_all_kpis(df)

        # Revenue concentration
        top5_cust_rev = df.groupby("customer_name")["revenue"].sum().nlargest(5).sum()
        conc_pct = (top5_cust_rev / kpis["Total Revenue"] * 100)

        # Best month
        monthly = monthly_revenue_profit(df)
        best_month = monthly.loc[monthly["revenue"].idxmax()]
        worst_month = monthly.loc[monthly["revenue"].idxmin()]

        # Margin leaders
        top_margin_product = (df.groupby("product_name")["profit_margin_pct"]
                                .mean().nlargest(1).reset_index().iloc[0])

        auto_insights = [
            ("📊", "Revenue Concentration Risk",
             f"Top 5 customers account for **{conc_pct:.1f}%** of total revenue "
             f"(${top5_cust_rev:,.0f}). {'High concentration — consider diversification.' if conc_pct > 40 else 'Healthy diversification.'}"),
            ("📅", "Peak Revenue Month",
             f"Best month: **{best_month['period']}** with ${best_month['revenue']:,.0f}. "
             f"Worst month: **{worst_month['period']}** with ${worst_month['revenue']:,.0f}. "
             f"Peak/trough ratio: {best_month['revenue']/worst_month['revenue']:.1f}x"),
            ("🏆", "Margin Leader",
             f"**{top_margin_product['product_name']}** leads with an average margin of "
             f"{top_margin_product['profit_margin_pct']:.1f}% — significantly above the portfolio average of {kpis['Profit Margin %']:.1f}%."),
            ("📦", "Order Efficiency",
             f"Average revenue per order: **{format_currency(kpis['Revenue per Order'])}**. "
             f"Total of {kpis['Total Orders']:,} unique orders across {df['customer_name'].nunique()} customers."),
        ]

        for icon, title, text in auto_insights:
            st.markdown(f"""
<div class="insight-card">
<span class="insight-icon">{icon}</span><strong>{title}</strong><br>
{text}
</div>
""", unsafe_allow_html=True)

    # ── Tab 3: Anomaly Detection ───────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-header">Statistical Anomaly Detection</div>', unsafe_allow_html=True)
        st.caption("Anomalies detected using z-score > 2.0 standard deviations from the monthly mean.")

        anomaly_df = detect_anomalies(df)
        anomalies  = anomaly_df[anomaly_df["anomaly"]]

        if len(anomalies) == 0:
            st.success("✅ No significant anomalies detected in the filtered dataset.")
        else:
            st.warning(f"⚠️ {len(anomalies)} anomalous months detected")
            for _, row in anomalies.iterrows():
                direction = "📈 Positive spike" if row["z_score"] > 0 else "📉 Negative dip"
                st.markdown(f"""
<div class="insight-card">
<span class="insight-icon">⚠️</span><strong>{row['period']}</strong> — {direction}<br>
Revenue: ${row['revenue']:,.0f} | Z-Score: {row['z_score']:.2f}σ
</div>
""", unsafe_allow_html=True)

        # Anomaly chart
        fig_anom = go.Figure()
        fig_anom.add_trace(go.Scatter(
            x=anomaly_df["period"], y=anomaly_df["revenue"],
            mode="lines+markers", name="Revenue",
            line=dict(color=PALETTE[0], width=2),
            marker=dict(size=5),
        ))
        if len(anomalies) > 0:
            fig_anom.add_trace(go.Scatter(
                x=anomalies["period"], y=anomalies["revenue"],
                mode="markers", name="Anomaly",
                marker=dict(color="#EF4444", size=12, symbol="x-open", line=dict(width=2)),
            ))
        # Mean bands
        mean = anomaly_df["revenue"].mean()
        std  = anomaly_df["revenue"].std()
        fig_anom.add_hline(y=mean + 2*std, line_dash="dash", line_color="#F59E0B", annotation_text="+2σ")
        fig_anom.add_hline(y=mean - 2*std, line_dash="dash", line_color="#F59E0B", annotation_text="-2σ")
        fig_anom.update_layout(
            title=dict(text="Monthly Revenue with Anomaly Bands", font=dict(size=14, color="#e2e8f0")),
            **BASE_LAYOUT,
        )
        fig_anom.update_yaxes(tickformat="$,.0f", gridcolor=GRID_CLR)
        fig_anom.update_xaxes(gridcolor=GRID_CLR, tickangle=45)
        st.plotly_chart(fig_anom, use_container_width=True)

        if len(anomalies) > 0 and st.button("🤖 Explain Anomalies with AI", key="explain_anom"):
            anomaly_list = "\n".join([
                f"- {r['period']}: ${r['revenue']:,.0f} (z={r['z_score']:.2f})"
                for _, r in anomalies.iterrows()
            ])
            prompt = f"""
These monthly revenue figures were flagged as statistical anomalies (z-score > 2):
{anomaly_list}

Based on the full data context below, suggest possible business reasons for each anomaly and recommended follow-up actions.

{context}
"""
            with st.spinner("Analyzing anomalies…"):
                explanation = call_gemini(prompt, max_tokens=500)
            st.markdown(f"""
<div class="insight-card">
{explanation.replace(chr(10), '<br>')}
</div>
""", unsafe_allow_html=True)

    # ── Tab 4: Q&A Chatbot ────────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-header">Natural Language Sales Q&A</div>', unsafe_allow_html=True)
        st.caption("Ask any question about your sales data in plain English.")

        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Render chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="ai-message-user">🧑 {msg["content"]}</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-message-bot">🤖 {msg["content"]}</div>',
                            unsafe_allow_html=True)

        # Example questions
        example_qs = [
            "Which region has the highest profit margin?",
            "What is the revenue growth trend year-over-year?",
            "Which products should we discontinue based on profitability?",
            "Who are our top 3 strategic customers and why?",
            "What channel is most profitable?",
        ]

        st.markdown("**💡 Example Questions:**")
        eq_cols = st.columns(len(example_qs))
        for col, q in zip(eq_cols, example_qs):
            with col:
                if st.button(q[:35] + ("…" if len(q) > 35 else ""), key=f"eq_{q[:10]}",
                             use_container_width=True):
                    st.session_state["chat_input_val"] = q

        # Chat input
        user_input = st.text_input(
            "Ask a question about your sales data…",
            value=st.session_state.get("chat_input_val", ""),
            key="chat_input",
            placeholder="e.g. What is driving profit margin decline in the Midwest?",
        )
        st.session_state["chat_input_val"] = ""

        send_col, clear_col = st.columns([4, 1])
        with send_col:
            send = st.button("Send ▶", type="primary", use_container_width=True)
        with clear_col:
            if st.button("Clear 🗑️", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        if send and user_input.strip():
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            sys_prompt = (
                "You are an expert sales data analyst. Answer questions about the provided "
                "sales data concisely and with specific numbers. If the answer can be found "
                "in the context, use those exact figures. If not, say so clearly."
            )
            history_text = "\n".join([
                f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}"
                for m in st.session_state.chat_history[-6:]
            ])
            prompt = f"{context}\n\nConversation history:\n{history_text}\n\nAnswer the latest question."

            with st.spinner("Thinking…"):
                answer = call_gemini(prompt, system=sys_prompt, max_tokens=400)

            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()
