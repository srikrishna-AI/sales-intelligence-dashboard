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


def call_groq(prompt: str, system: str = "", max_tokens: int = 1500) -> str:
    """
    Call Groq via the Groq SDK.
    Requires GROQ_API_KEY in environment variables.
    """
    api_key = os.getenv("GROQ_API_KEY") or ""
    if not api_key:
        return _fallback_insight(prompt)

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        else:
            messages.append({"role": "system", "content": DEFAULT_SYSTEM_PROMPT})
        messages.append({"role": "user", "content": prompt})

        chat_completion = client.chat.completions.create(
            messages=messages,
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return chat_completion.choices[0].message.content.strip() or "Groq returned an empty response."

    except ImportError:
        return _fallback_insight(prompt)
    except Exception as e:
        if "api_key" in str(e).lower() or "auth" in str(e).lower() or "unauthorized" in str(e).lower():
            return "**Groq API Key Required** - Set your `GROQ_API_KEY` environment variable in the `.env` file."
        return f"Groq API Error: {str(e)}"

def _fallback_insight(prompt: str) -> str:
    """Rule-based fallback when no API key is configured."""
    return (
        "📝 **AI Insights (Demo Mode)**\n\n"
        "Configure your `GROQ_API_KEY` in the `.env` file to enable live AI analysis. "
        "In the meantime, here are the key signals from the data visible in the charts:\n\n"
        "- **Revenue trend**: Check the Executive Overview page for monthly patterns.\n"
        "- **Top performers**: Visit Product & Channel page for ranking details.\n"
        "- **Geographic spread**: The map page highlights regional concentration.\n\n"
        "_To enable live AI: Provide your Groq API key to the assistant to store in the `.env` file._"
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
    
    # Regional performance
    region_perf = (df.groupby("us_region")
                    .agg(revenue=("revenue", "sum"), profit=("profit", "sum"), margin=("profit_margin_pct", "mean"))
                    .reset_index()
                    .apply(lambda r: f"- {r['us_region']}: Revenue ${r['revenue']:,.0f} | Profit ${r['profit']:,.0f} | Avg Margin {r['margin']:.1f}%", axis=1)
                    .tolist())

    # Top/Bottom products by profit margin
    top_margin_prods = (df.groupby("product_name")["profit_margin_pct"].mean()
                          .nlargest(5).reset_index()
                          .apply(lambda r: f"- {r['product_name']}: {r['profit_margin_pct']:.1f}%", axis=1)
                          .tolist())
    bot_margin_prods = (df.groupby("product_name")["profit_margin_pct"].mean()
                          .nsmallest(5).reset_index()
                          .apply(lambda r: f"- {r['product_name']}: {r['profit_margin_pct']:.1f}%", axis=1)
                          .tolist())

    monthly = monthly_revenue_profit(df)
    rev_by_yr = df.groupby("year")["revenue"].sum().to_dict()

    # Anomaly detection summary
    anom_df = detect_anomalies(df)
    anoms = anom_df[anom_df["anomaly"]]
    if len(anoms) > 0:
        anom_list = [f"- {r['period']}: Revenue ${r['revenue']:,.0f} (Z-Score: {r['z_score']:.2f} std dev)" for _, r in anoms.iterrows()]
    else:
        anom_list = ["- No statistical revenue anomalies detected."]

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

REVENUE ANOMALIES (Z-Score > 2.0 std dev):
{chr(10).join(anom_list)}

REGIONAL PERFORMANCE (REVENUE, PROFIT, MARGIN):
{chr(10).join(region_perf)}

TOP 5 PRODUCTS BY REVENUE:
{chr(10).join(top_products)}

TOP 5 PRODUCTS BY PROFIT MARGIN %:
{chr(10).join(top_margin_prods)}

BOTTOM 5 PRODUCTS BY PROFIT MARGIN %:
{chr(10).join(bot_margin_prods)}

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
    st.markdown('<div class="page-subtitle">Unified AI Analytics Hub · Ask questions about summaries, trends, anomalies, and details</div>', unsafe_allow_html=True)

    context = build_context(df)

    # Check for API key in environment
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.warning(
            "⚠️ **Groq API Key Not Found**: Running in Demo Mode with pre-computed insights. "
            "To enable live AI features, add your `GROQ_API_KEY` to the project's `.env` file."
        )

    # Render Q&A Chatbot Directly
    st.markdown('<div class="section-header">Natural Language Sales Q&A</div>', unsafe_allow_html=True)
    st.caption("Ask any question about your sales data (e.g., summaries, regional details, anomalies, trends, categories).")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Render chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="ai-message-user">🧑 {msg["content"].replace("$", r"\$")}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-message-bot">🤖 {msg["content"].replace("$", r"\$")}</div>',
                        unsafe_allow_html=True)

    # Example questions
    example_qs = [
        "Give me a detailed executive summary of the sales data.",
        "Which region has the highest profit margin?",
        "Are there any statistical anomalies in our monthly revenue?",
        "Which products should we discontinue based on profitability?",
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
            "sales data context concisely, with specific numbers. If the answer can be found "
            "in the context, use those exact figures. If not, say so clearly."
        )
        history_text = "\n".join([
            f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}"
            for m in st.session_state.chat_history[-6:]
        ])
        prompt = f"{context}\n\nConversation history:\n{history_text}\n\nAnswer the latest question."

        with st.spinner("Thinking…"):
            answer = call_groq(prompt, system=sys_prompt, max_tokens=1500)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()
