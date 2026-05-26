"""
Data loading, cleaning, and KPI computation layer.
Converts Power BI DAX measures to Python/pandas equivalents.
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "sales_data.csv"


@st.cache_data(show_spinner="Loading sales data…")
def load_data() -> pd.DataFrame:
    """Load and preprocess the sales dataset."""
    df = pd.read_csv(DATA_PATH, parse_dates=["order_date"])

    # ── Date fields ─────────────────────────────────────────────────────────
    df["year"]    = df["order_date"].dt.year
    df["quarter"] = df["order_date"].dt.quarter
    df["month"]   = df["order_date"].dt.month

    # ── Derived / cleaned fields ─────────────────────────────────────────────
    df["profit_margin_pct"] = df["profit_margin_pct"].clip(-200, 200)
    df["revenue_per_order"] = df["revenue"] / df.groupby("order_number")["revenue"].transform("count")

    # ── Order-level aggregation helper ───────────────────────────────────────
    df["order_value"] = df.groupby("order_number")["revenue"].transform("sum")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# KPI Calculations  (DAX → Python conversions)
# ─────────────────────────────────────────────────────────────────────────────

def kpi_total_revenue(df: pd.DataFrame) -> float:
    """DAX: Total Revenue = SUM(sales[revenue])"""
    return df["revenue"].sum()


def kpi_total_profit(df: pd.DataFrame) -> float:
    """DAX: Total Profit = SUM(sales[profit])"""
    return df["profit"].sum()


def kpi_profit_margin(df: pd.DataFrame) -> float:
    """DAX: Profit Margin % = DIVIDE(Total Profit, Total Revenue) * 100"""
    rev = kpi_total_revenue(df)
    return (kpi_total_profit(df) / rev * 100) if rev else 0.0


def kpi_total_orders(df: pd.DataFrame) -> int:
    """DAX: Total Orders = DISTINCTCOUNT(sales[order_number])"""
    return df["order_number"].nunique()


def kpi_revenue_per_order(df: pd.DataFrame) -> float:
    """DAX: Revenue per order = DIVIDE(Total Revenue, Total Orders)"""
    orders = kpi_total_orders(df)
    return (kpi_total_revenue(df) / orders) if orders else 0.0


def kpi_avg_profit_margin(df: pd.DataFrame) -> float:
    """DAX: Avg Profit Margin % = AVERAGE(sales[profit_margin_pct])"""
    return df["profit_margin_pct"].mean()


def compute_all_kpis(df: pd.DataFrame) -> dict:
    """Return dict of all top-level KPIs."""
    return {
        "Total Revenue":      kpi_total_revenue(df),
        "Total Profit":       kpi_total_profit(df),
        "Profit Margin %":    kpi_profit_margin(df),
        "Total Orders":       kpi_total_orders(df),
        "Revenue per Order":  kpi_revenue_per_order(df),
        "Avg Profit Margin %": kpi_avg_profit_margin(df),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Time-series aggregation helpers
# ─────────────────────────────────────────────────────────────────────────────

def monthly_revenue_profit(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly aggregated revenue and profit."""
    g = (df.groupby(["year", "month", "order_month_name"])
           .agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
           .reset_index()
           .sort_values(["year", "month"]))
    g["period"] = g["year"].astype(str) + "-" + g["month"].astype(str).str.zfill(2)
    return g


def product_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Product-level aggregation."""
    return (df.groupby("product_name")
              .agg(
                  revenue=("revenue", "sum"),
                  profit=("profit", "sum"),
                  orders=("order_number", "nunique"),
                  avg_margin=("profit_margin_pct", "mean"),
              )
              .reset_index()
              .sort_values("revenue", ascending=False))


def channel_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Channel-level aggregation."""
    return (df.groupby("channel")
              .agg(
                  revenue=("revenue", "sum"),
                  profit=("profit", "sum"),
                  orders=("order_number", "nunique"),
                  avg_margin=("profit_margin_pct", "mean"),
              )
              .reset_index())


def state_performance(df: pd.DataFrame) -> pd.DataFrame:
    """State-level aggregation with lat/lon."""
    return (df.groupby(["state", "state_name", "us_region"])
              .agg(
                  revenue=("revenue", "sum"),
                  profit=("profit", "sum"),
                  orders=("order_number", "nunique"),
                  avg_margin=("profit_margin_pct", "mean"),
                  lat=("lat", "mean"),
                  lon=("lon", "mean"),
              )
              .reset_index())


def customer_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Customer-level aggregation."""
    return (df.groupby("customer_name")
              .agg(
                  revenue=("revenue", "sum"),
                  profit=("profit", "sum"),
                  orders=("order_number", "nunique"),
                  avg_margin=("profit_margin_pct", "mean"),
              )
              .reset_index()
              .sort_values("revenue", ascending=False))


def region_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Region-level aggregation."""
    return (df.groupby("us_region")
              .agg(
                  revenue=("revenue", "sum"),
                  profit=("profit", "sum"),
                  avg_margin=("profit_margin_pct", "mean"),
              )
              .reset_index())


def order_value_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Bin order values for histogram (replicates Power BI OrderValue bins)."""
    ov = df.groupby("order_number")["revenue"].sum()
    bins = [0, 5000, 10000, 25000, 50000, 100000, 250000, 500000, float("inf")]
    labels = ["<5K", "5-10K", "10-25K", "25-50K", "50-100K", "100-250K", "250-500K", ">500K"]
    ov_binned = pd.cut(ov, bins=bins, labels=labels)
    return ov_binned.value_counts().sort_index().reset_index().rename(
        columns={"index": "order_value_bin", "count": "order_count", "revenue": "order_count"}
    )
