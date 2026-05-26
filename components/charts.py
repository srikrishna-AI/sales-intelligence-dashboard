"""
Reusable Plotly chart components for the Sales Intelligence Dashboard.
All charts use a consistent dark theme matching the CSS design system.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional

# ── Theme ────────────────────────────────────────────────────────────────────
PALETTE   = ["#4F8EF7", "#a78bfa", "#22C55E", "#F59E0B", "#EF4444", "#06b6d4", "#f97316", "#ec4899"]
BG_COLOR  = "rgba(0,0,0,0)"
GRID_CLR  = "rgba(255,255,255,0.06)"
TEXT_CLR  = "#94a3b8"
FONT      = "Inter, system-ui, sans-serif"

BASE_LAYOUT = dict(
    paper_bgcolor=BG_COLOR,
    plot_bgcolor=BG_COLOR,
    font=dict(family=FONT, color=TEXT_CLR, size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1),
    colorway=PALETTE,
)

def _apply_base(fig):
    fig.update_layout(**BASE_LAYOUT)
    fig.update_xaxes(gridcolor=GRID_CLR, zeroline=False)
    fig.update_yaxes(gridcolor=GRID_CLR, zeroline=False)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Line Charts
# ─────────────────────────────────────────────────────────────────────────────

def line_chart(df: pd.DataFrame, x: str, y: str | list,
               title: str = "", color: Optional[str] = None,
               y_format: str = "$,.0f") -> go.Figure:
    """Monthly trend line chart."""
    y_cols = [y] if isinstance(y, str) else y
    fig = go.Figure()
    for i, col in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=df[x], y=df[col],
            mode="lines+markers",
            name=col,
            line=dict(color=PALETTE[i], width=2.5),
            marker=dict(size=5),
            hovertemplate=f"<b>%{{x}}</b><br>{col}: %{{y:{y_format.replace('$','$')}}}<extra></extra>",
        ))
    fig.update_layout(title=dict(text=title, font=dict(size=14, color="#e2e8f0")), **BASE_LAYOUT)
    fig.update_xaxes(gridcolor=GRID_CLR, zeroline=False)
    fig.update_yaxes(gridcolor=GRID_CLR, zeroline=False, tickformat=y_format)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Bar / Column Charts
# ─────────────────────────────────────────────────────────────────────────────

def bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "",
              orientation: str = "v", color_col: Optional[str] = None,
              top_n: int = 20, y_format: str = "$,.0f") -> go.Figure:
    """Vertical or horizontal bar chart."""
    plot_df = df.head(top_n)
    if orientation == "h":
        plot_df = plot_df.sort_values(y, ascending=True)

    color_map = dict(zip(plot_df[color_col].unique(), PALETTE)) if color_col else None

    fig = px.bar(
        plot_df, x=x if orientation == "v" else y,
        y=y if orientation == "v" else x,
        orientation=orientation,
        color=color_col,
        color_discrete_map=color_map,
        title=title,
    )
    fig.update_traces(marker_line_width=0)
    if orientation == "v":
        fig.update_yaxes(tickformat=y_format)
    else:
        fig.update_xaxes(tickformat=y_format)
    return _apply_base(fig)


def grouped_bar(df: pd.DataFrame, x: str, y_cols: list,
                title: str = "", y_format: str = "$,.0f") -> go.Figure:
    """Grouped bar chart for multiple metrics."""
    fig = go.Figure()
    for i, col in enumerate(y_cols):
        fig.add_trace(go.Bar(
            x=df[x], y=df[col],
            name=col,
            marker_color=PALETTE[i],
        ))
    fig.update_layout(barmode="group", title=dict(text=title, font=dict(size=14, color="#e2e8f0")), **BASE_LAYOUT)
    fig.update_xaxes(gridcolor=GRID_CLR)
    fig.update_yaxes(gridcolor=GRID_CLR, tickformat=y_format)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Donut Chart
# ─────────────────────────────────────────────────────────────────────────────

def donut_chart(df: pd.DataFrame, names: str, values: str,
                title: str = "", hole: float = 0.55) -> go.Figure:
    """Donut chart for channel / region splits."""
    fig = px.pie(df, names=names, values=values, title=title, hole=hole,
                 color_discrete_sequence=PALETTE)
    fig.update_traces(
        textposition="outside",
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>%{value:$,.0f}<br>%{percent}<extra></extra>",
        marker=dict(line=dict(color="rgba(0,0,0,0.2)", width=2)),
    )
    fig.update_layout(**BASE_LAYOUT)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Scatter Chart
# ─────────────────────────────────────────────────────────────────────────────

def scatter_chart(df: pd.DataFrame, x: str, y: str, size: Optional[str] = None,
                  color: Optional[str] = None, title: str = "",
                  hover_name: Optional[str] = None) -> go.Figure:
    """Scatter / bubble chart."""
    fig = px.scatter(
        df, x=x, y=y,
        size=size, color=color,
        hover_name=hover_name,
        title=title,
        color_discrete_sequence=PALETTE,
        size_max=40,
    )
    fig.update_traces(marker=dict(opacity=0.75, line=dict(width=1, color="rgba(255,255,255,0.2)")))
    return _apply_base(fig)


# ─────────────────────────────────────────────────────────────────────────────
# Map
# ─────────────────────────────────────────────────────────────────────────────

def bubble_map(df: pd.DataFrame, lat: str, lon: str, size: str,
               hover: str, color: str, title: str = "") -> go.Figure:
    """US bubble map by state."""
    fig = px.scatter_geo(
        df, lat=lat, lon=lon,
        size=size, hover_name=hover,
        color=color,
        color_continuous_scale="Blues",
        scope="usa",
        title=title,
        size_max=50,
    )
    fig.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)",
                 landcolor="rgba(20,30,50,0.8)", showlakes=True,
                 showland=True, countrycolor="rgba(255,255,255,0.1)"),
        **BASE_LAYOUT,
    )
    return fig


def choropleth_map(df: pd.DataFrame, locations: str, color: str, title: str = "") -> go.Figure:
    """US choropleth map by state abbreviation."""
    fig = px.choropleth(
        df, locations=locations,
        color=color,
        locationmode="USA-states",
        scope="usa",
        color_continuous_scale="Blues",
        title=title,
        hover_data={"revenue": ":$,.0f", "profit": ":$,.0f"},
    )
    fig.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        **BASE_LAYOUT,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# KPI Card HTML
# ─────────────────────────────────────────────────────────────────────────────

def kpi_card_html(label: str, value: str, delta: Optional[str] = None,
                  icon: str = "📊", delta_positive: bool = True) -> str:
    """Render a KPI card as HTML."""
    delta_class = "kpi-delta-pos" if delta_positive else "kpi-delta-neg"
    delta_arrow = "▲" if delta_positive else "▼"
    delta_html = f'<div class="{delta_class}">{delta_arrow} {delta}</div>' if delta else ""
    return f"""
<div class="kpi-card">
  <span class="kpi-icon">{icon}</span>
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{value}</div>
  {delta_html}
</div>
"""


def format_currency(v: float) -> str:
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"${v/1_000:.1f}K"
    return f"${v:.2f}"


def format_number(v: float) -> str:
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"{v/1_000:.1f}K"
    return f"{v:.0f}"
