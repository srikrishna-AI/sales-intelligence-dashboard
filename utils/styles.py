"""
Custom CSS injection for professional enterprise dashboard styling.
Supports dark/light theme compatibility via CSS variables.
"""

import streamlit as st


def inject_css():
    st.markdown(
        """
<style>
/* ── Root Variables ─────────────────────────────────────────────── */
:root {
    --accent:      #4F8EF7;
    --accent-dark: #2563EB;
    --positive:    #22C55E;
    --negative:    #EF4444;
    --warning:     #F59E0B;
    --card-bg:     rgba(30, 41, 59, 0.7);
    --card-border: rgba(79, 142, 247, 0.25);
    --radius:      12px;
    --shadow:      0 4px 24px rgba(0,0,0,0.18);
}

/* ── Hide default Streamlit chrome ─────────────────────────────── */
footer {visibility: hidden;}
header[data-testid="stHeader"] {
    background: transparent !important;
}
div[data-testid="stAppDeployButton"], 
button[id="MainMenu"] {
    display: none !important;
}
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}

/* ── Sidebar ────────────────────────────────────────────────────── */
.sidebar-logo {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--accent);
    padding: 0.5rem 0;
    letter-spacing: 0.5px;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid rgba(79,142,247,0.15);
    display: block !important;
    visibility: visible !important;
}

/* ── Navigation Buttons ─────────────────────────────────────────── */
div[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    color: #cbd5e1 !important;
    border-radius: 8px !important;
    justify-content: flex-start !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
    margin-bottom: 2px !important;
    width: 100% !important;
}
div[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover {
    background: rgba(79,142,247,0.12) !important;
    border-color: rgba(79, 142, 247, 0.4) !important;
    color: #fff !important;
}
div[data-testid="stSidebar"] button[data-testid="baseButton-primary"] {
    background: rgba(79,142,247,0.2) !important;
    border: 1px solid var(--accent) !important;
    color: #fff !important;
    border-radius: 8px !important;
    justify-content: flex-start !important;
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
    margin-bottom: 2px !important;
    width: 100% !important;
}
div[data-testid="stSidebar"] button[data-testid="baseButton-primary"]:hover {
    background: rgba(79,142,247,0.28) !important;
    border-color: var(--accent) !important;
}

.sidebar-nav-icon {
    width: 1.35rem;
    flex: 0 0 auto;
}

/* ── KPI Cards ──────────────────────────────────────────────────── */
.kpi-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow);
    backdrop-filter: blur(8px);
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(79,142,247,0.18);
}
.kpi-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #94a3b8;
    margin-bottom: 0.35rem;
}
.kpi-value {
    font-size: 1.95rem;
    font-weight: 800;
    color: #f1f5f9;
    line-height: 1.1;
}
.kpi-delta-pos { color: var(--positive); font-size: 0.8rem; font-weight: 600; margin-top: 0.3rem; }
.kpi-delta-neg { color: var(--negative); font-size: 0.8rem; font-weight: 600; margin-top: 0.3rem; }
.kpi-icon { font-size: 1.5rem; float: right; opacity: 0.6; }

/* ── Section Headers ────────────────────────────────────────────── */
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e2e8f0;
    border-left: 4px solid var(--accent);
    padding-left: 0.75rem;
    margin: 1.5rem 0 1rem 0;
}

/* ── Chart Containers ───────────────────────────────────────────── */
.chart-container {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: var(--radius);
    padding: 1rem;
    box-shadow: var(--shadow);
}

/* ── Page Title ─────────────────────────────────────────────────── */
.page-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #4F8EF7, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.25rem;
}
.page-subtitle {
    color: #64748b;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

/* ── AI Chat ─────────────────────────────────────────────────────── */
.ai-message-user {
    background: rgba(79,142,247,0.15);
    border: 1px solid rgba(79,142,247,0.3);
    border-radius: 12px 12px 2px 12px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    color: #e2e8f0;
}
.ai-message-bot {
    background: rgba(30,41,59,0.8);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px 12px 12px 2px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    color: #cbd5e1;
}

/* ── Insight Cards ──────────────────────────────────────────────── */
.insight-card {
    background: linear-gradient(135deg, rgba(79,142,247,0.1), rgba(167,139,250,0.1));
    border: 1px solid rgba(79,142,247,0.2);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    margin: 0.5rem 0;
}
.insight-icon { font-size: 1.2rem; margin-right: 0.5rem; }

/* ── Home Page Cards ─────────────────────────────────────────────── */
.nav-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    padding: 1.75rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.25s;
    box-shadow: var(--shadow);
}
.nav-card:hover {
    border-color: var(--accent);
    transform: translateY(-3px);
    box-shadow: 0 12px 36px rgba(79,142,247,0.2);
}
.nav-card-icon { font-size: 2.5rem; margin-bottom: 0.75rem; }
.nav-card-title { font-size: 1rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.4rem; }
.nav-card-desc  { font-size: 0.8rem; color: #64748b; }
.home-nav-link {
    display: block;
    width: 100%;
    padding: 0.62rem 0.85rem;
    border: 1px solid rgba(79, 142, 247, 0.25);
    border-radius: 8px;
    background: rgba(30, 41, 59, 0.7);
    color: #e2e8f0 !important;
    text-align: center;
    text-decoration: none !important;
    font-weight: 700;
    transition: all 0.2s;
}
.home-nav-link:hover {
    border-color: var(--accent);
    background: rgba(79,142,247,0.15);
    color: #fff !important;
}
.home-nav-link-wide {
    margin-top: 0.5rem;
}

/* ── Dataframe styling ──────────────────────────────────────────── */
div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

/* ── Metric delta override ──────────────────────────────────────── */
div[data-testid="metric-container"] {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    box-shadow: var(--shadow);
}

/* ── Home Page Navigation Buttons ───────────────────────────────── */
.st-key-home_nav_executive button,
.st-key-home_nav_product button,
.st-key-home_nav_geo button,
.st-key-home_nav_ai button {
    display: block !important;
    width: 100% !important;
    padding: 0.62rem 0.85rem !important;
    border: 1px solid rgba(79, 142, 247, 0.25) !important;
    border-radius: 8px !important;
    background: rgba(30, 41, 59, 0.7) !important;
    color: #e2e8f0 !important;
    font-weight: 700 !important;
    transition: all 0.2s !important;
}
.st-key-home_nav_executive button:hover,
.st-key-home_nav_product button:hover,
.st-key-home_nav_geo button:hover,
.st-key-home_nav_ai button:hover {
    border-color: var(--accent) !important;
    background: rgba(79,142,247,0.15) !important;
    color: #fff !important;
    box-shadow: 0 0 12px rgba(79, 142, 247, 0.2) !important;
}

/* ── Scrollbar ──────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(79,142,247,0.4); border-radius: 3px; }
</style>
        """,
        unsafe_allow_html=True,
    )
