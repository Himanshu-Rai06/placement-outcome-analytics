# ─────────────────────────────────────────────────────────────────────────────
# Care Transition Efficiency & Placement Outcome Analytics
# HHS Unaccompanied Alien Children Program — Streamlit Dashboard
# ─────────────────────────────────────────────────────────────────────────────

from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

APP_DIR = Path(__file__).parent
SEAL_PATH = APP_DIR / "US_Department_of_Health_and_Human_Services_seal.svg.webp"
BREAK_DATE = pd.Timestamp("2025-02-01")

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HHS UAC Care Pipeline Analytics",
    page_icon=str(SEAL_PATH) if SEAL_PATH.exists() else "🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# COLOR TOKENS
# The dark theme itself is set once, authoritatively, in
# .streamlit/config.toml (base = "dark"). That is what keeps
# every native widget — sidebar, dataframe, metrics, tabs,
# buttons — in sync. This CSS block only styles our own custom
# HTML (cards / alerts / stage tiles); it never has to fight
# Streamlit's own components, which is what caused the previous
# white-text-on-white-card bug when a runtime light/dark toggle
# was layered on top of an unset base theme.
# ─────────────────────────────────────────────────────────────
BG        = "#0A0D14"
CARD      = "#131722"
CARD2     = "#0F1219"
BORDER    = "#232838"
TEXT      = "#E4E7F0"
TEXT_DIM  = "#99A1B7"
TEXT_MUTE = "#5C6478"
BLUE      = "#4C8DFF"
RED       = "#F0554A"
GREEN     = "#34C795"
AMBER     = "#E8A93B"
PURPLE    = "#8C7CF0"

CSS_COLORS = {"red": RED, "green": GREEN, "amber": AMBER, "blue": BLUE}

st.markdown(f"""
<style>
html, body, [class*="css"] {{ font-family: 'Inter', 'Segoe UI', sans-serif; }}

.block-container {{ padding: 1.5rem 2.2rem 3rem !important; max-width: 1350px !important; }}

.app-title {{ display:flex; align-items:center; gap:12px; }}
.app-title h2 {{ margin:0; color:{TEXT}; font-weight:700; }}
.app-subtitle {{ color:{TEXT_DIM}; font-size:0.9rem; margin:2px 0 0 42px; }}

.card {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:14px;
    padding:1.4rem 1.5rem; margin-bottom:1rem;
}}

.section-head {{ display:flex; align-items:center; gap:9px; margin:1.6rem 0 1rem; }}
.section-head span.t {{ font-size:1.05rem; font-weight:700; color:{TEXT}; }}
.section-head .line {{ flex:1; height:1px; background:{BORDER}; }}

.kpi-tile {{
    background:{CARD2}; border:1px solid {BORDER}; border-radius:12px;
    padding:1.1rem 1.2rem; height:100%;
}}
.kpi-label {{ font-size:0.7rem; text-transform:uppercase; letter-spacing:0.08em; color:{TEXT_MUTE}; }}
.kpi-value {{ font-size:1.6rem; font-weight:700; color:{TEXT}; margin-top:2px; }}
.kpi-delta {{ font-size:0.78rem; color:{TEXT_DIM}; margin-top:3px; }}

.alert-box {{
    display:flex; gap:10px; align-items:flex-start;
    border-left:3px solid var(--ac); background:var(--ac-soft);
    border-radius:0 10px 10px 0; padding:0.8rem 1rem; margin:0.5rem 0;
}}
.alert-box strong {{ color:var(--ac); }}
.alert-box .body {{ color:{TEXT_DIM}; font-size:0.87rem; line-height:1.55; }}
.alert-box svg {{ flex-shrink:0; margin-top:2px; }}

.stage-card {{
    background:{CARD2}; border:1px solid {BORDER}; border-left:3px solid var(--ac);
    border-radius:0 12px 12px 0; padding:1rem 1.2rem;
}}
.stage-title {{ font-size:0.72rem; text-transform:uppercase; letter-spacing:0.07em; color:{TEXT_MUTE}; }}
.stage-value {{ font-size:1.5rem; font-weight:700; color:var(--ac); margin:4px 0 2px; }}
.stage-sub {{ font-size:0.78rem; color:{TEXT_DIM}; }}
.stage-arrow {{ text-align:center; padding:2px 0; color:{TEXT_MUTE}; }}

[data-testid="stMetric"] {{
    background:{CARD2} !important; border:1px solid {BORDER} !important; border-radius:10px !important;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SVG ICONS
# ─────────────────────────────────────────────
def icon(name, size=16, color="currentColor"):
    icons = {
        "monitoring": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 12h4l2 7 4-14 2 7h6"/></svg>''',
        "sync-alt": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 3l4 4-4 4"/><path d="M21 7H9a5 5 0 0 0-5 5"/>
            <path d="M7 21l-4-4 4-4"/><path d="M3 17h12a5 5 0 0 0 5-5"/></svg>''',
        "trending-up": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 17 9 11 13 15 21 7"/><polyline points="14 7 21 7 21 14"/></svg>''',
        "balance": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 3v18"/><path d="M6 21h12"/><path d="M4 7l4-2 4 2"/><path d="M12 7l4-2 4 2"/>
            <path d="M2 7l2 5a2.5 2.5 0 0 0 4 0l2-5"/><path d="M14 7l2 5a2.5 2.5 0 0 0 4 0l2-5"/></svg>''',
        "emergency": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M12 12v5"/><path d="M9.5 15.5h5"/></svg>''',
        "calendar": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18"/>
            <path d="M8 3v4"/><path d="M16 3v4"/></svg>''',
        "list": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M8 6h13"/><path d="M8 12h13"/><path d="M8 18h13"/>
            <path d="M3 6h.01"/><path d="M3 12h.01"/><path d="M3 18h.01"/></svg>''',
        "warning": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M10.3 3.6L2.7 18a1.8 1.8 0 0 0 1.6 2.6h15.4a1.8 1.8 0 0 0 1.6-2.6L13.7 3.6a1.8 1.8 0 0 0-3.4 0z"/>
            <path d="M12 9v4"/><path d="M12 16.5h.01"/></svg>''',
        "check-circle": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9"/><path d="M8.5 12.5l2.5 2.5 4.5-5"/></svg>''',
        "info": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9"/><line x1="12" y1="11" x2="12" y2="16"/>
            <line x1="12" y1="8" x2="12" y2="8"/></svg>''',
        "pin": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s7-7.4 7-12a7 7 0 0 0-14 0c0 4.6 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg>''',
        "route": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/>
            <path d="M8 19h7a4 4 0 0 0 4-4v-1a4 4 0 0 0-4-4H9a4 4 0 0 1-4-4V5"/></svg>''',
        "clock": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/></svg>''',
        "arrow-down": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 4v15"/><path d="M6 13l6 6 6-6"/></svg>''',
        "bell": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 9a6 6 0 0 1 12 0c0 4 1.5 6 2 7H4c.5-1 2-3 2-7z"/><path d="M10 20a2 2 0 0 0 4 0"/></svg>''',
        "bar-chart": f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
            viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 3v18h18"/><rect x="7" y="12" width="3" height="6"/>
            <rect x="12" y="8" width="3" height="10"/><rect x="17" y="5" width="3" height="13"/></svg>''',
    }
    return icons.get(name, "")


def alert_box(kind, title, body, size=16):
    icon_map = {"red": "warning", "green": "check-circle", "amber": "warning", "blue": "info"}
    color = CSS_COLORS[kind]
    ic = icon(icon_map[kind], size, color)
    soft = {"red": "rgba(240,85,74,0.08)", "green": "rgba(52,199,149,0.08)",
            "amber": "rgba(232,169,59,0.08)", "blue": "rgba(76,141,255,0.08)"}[kind]
    return (f"<div class='alert-box' style='--ac:{color};--ac-soft:{soft}'>{ic}"
            f"<div class='body'><strong>{title}</strong> {body}</div></div>")


def section_head(icon_name, text, size=17):
    return (f"<div class='section-head'>{icon(icon_name, size, BLUE)}"
            f"<span class='t'>{text}</span><div class='line'></div></div>")


def stage_card(title, value, sub, color):
    return (f"<div class='stage-card' style='--ac:{color}'>"
            f"<div class='stage-title'>{title}</div>"
            f"<div class='stage-value'>{value:,}</div>"
            f"<div class='stage-sub'>{sub}</div></div>")


# ─────────────────────────────────────────────
# PLOTLY BASE LAYOUT
# ─────────────────────────────────────────────
def base_layout(title="", height=380, legend=True):
    layout = dict(
        height=height,
        paper_bgcolor=CARD2,
        plot_bgcolor=CARD2,
        font=dict(family="Inter, sans-serif", color=TEXT_DIM, size=12),
        xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, showgrid=True),
        yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, showgrid=True),
        margin=dict(l=10, r=10, t=56 if title else 20, b=10),
    )
    if title:
        layout["title"] = dict(text=title, font=dict(size=14, color=TEXT), x=0.01, xanchor="left")
    if legend:
        layout["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                                 bgcolor="rgba(0,0,0,0)", font=dict(size=11))
    else:
        layout["showlegend"] = False
    return layout


def mark_policy_break(fig, row=None, col=None, label=None):
    """
    Draw the Feb-2025 policy-break marker.

    IMPORTANT BUG FIX: previously this called fig.add_vline(..., annotation_text=...)
    directly on a datetime axis. Plotly's add_vline/add_hline route annotated shapes
    through an internal helper that averages the shape's x-endpoints to place the
    label — and averaging two pandas Timestamps raises
    `TypeError: Addition/subtraction of integers and integer-arrays with Timestamp
    is no longer supported` on current pandas, because you can't sum two Timestamps.
    Splitting the line (add_vline, no annotation) from the label (a plain
    add_annotation call, which never averages anything) avoids that code path
    entirely while producing the same visual result.
    """
    kw = {}
    if row is not None:
        kw["row"] = row
    if col is not None:
        kw["col"] = col
    fig.add_vline(x=BREAK_DATE, line=dict(color=RED, width=1.5, dash="dot"), **kw)
    if label:
        fig.add_annotation(
            x=BREAK_DATE, y=1.06, yref="paper", xanchor="left",
            text=label, showarrow=False, font=dict(size=10, color=RED),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADING & PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_and_process():
    df = pd.read_csv("HHS_Unaccompanied_Alien_Children_Program.csv")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    numeric_cols = [
        "Children apprehended and placed in CBP custody*",
        "Children in CBP custody",
        "Children transferred out of CBP custody",
        "Children in HHS Care",
        "Children discharged from HHS Care",
    ]
    for col in numeric_cols:
        df[col] = (
            df[col].astype(str)
            .str.replace(",", "", regex=False)
            .pipe(pd.to_numeric, errors="coerce")
        )

    df = df.dropna(how="all", subset=df.columns).dropna(subset=["Date"])
    df = df.sort_values("Date", ascending=True).reset_index(drop=True)

    df.rename(columns={
        "Children apprehended and placed in CBP custody*": "cbp_new",
        "Children in CBP custody": "cbp_in",
        "Children transferred out of CBP custody": "cbp_xfer",
        "Children in HHS Care": "hhs_in",
        "Children discharged from HHS Care": "hhs_out",
    }, inplace=True)

    df["year"]        = df["Date"].dt.year
    df["month"]       = df["Date"].dt.month
    df["day_of_week"] = df["Date"].dt.day_name()
    df["year_month"]  = df["Date"].dt.to_period("M").astype(str)

    df["transfer_efficiency"]     = df["cbp_xfer"] / df["cbp_in"].replace(0, np.nan)
    df["discharge_effectiveness"] = df["hhs_out"]  / df["hhs_in"].replace(0, np.nan)
    df["backlog_accumulation"]    = df["cbp_new"]  - df["hhs_out"]
    df["pipeline_throughput"]     = (df["cbp_xfer"] + df["hhs_out"]) / (
                                     df["cbp_new"]  + df["cbp_in"].replace(0, np.nan))
    df["implied_stay"]            = (1 / df["discharge_effectiveness"]).clip(upper=500)

    df["is_bottleneck"] = (
        (df["backlog_accumulation"] > 0) & (df["pipeline_throughput"] < 1.0)
    ).astype(int)

    for col in ["transfer_efficiency", "discharge_effectiveness",
                "backlog_accumulation", "pipeline_throughput"]:
        df[f"{col}_30d"] = df[col].rolling(30, min_periods=7).mean()

    return df


df = load_and_process()
df_pre  = df[df["Date"] <  BREAK_DATE]
df_post = df[df["Date"] >= BREAK_DATE]


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    if SEAL_PATH.exists():
        st.image(str(SEAL_PATH), width=72)
    else:
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/"
            "Seal_of_the_United_States_Department_of_Health_%26_Human_Services.svg/"
            "240px-Seal_of_the_United_States_Department_of_Health_%26_Human_Services.svg.png",
            width=72,
        )
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:8px;margin-top:4px;'>"
        f"{icon('monitoring', 22, BLUE)}"
        f"<span style='font-size:1.02rem;font-weight:700;color:{TEXT};'>HHS UAC Program</span></div>",
        unsafe_allow_html=True,
    )
    st.caption("Care Transition Analytics")
    st.markdown("---")

    st.markdown(f"**{icon('calendar', 14)} Date range**", unsafe_allow_html=True)
    min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
    date_start = st.date_input("Start", value=min_date, min_value=min_date, max_value=max_date, label_visibility="collapsed")
    date_end   = st.date_input("End",   value=max_date, min_value=min_date, max_value=max_date, label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"**{icon('bell', 14)} Alert thresholds**", unsafe_allow_html=True)
    dei_alert = st.slider("Discharge effectiveness below", 0.005, 0.04, 0.015, 0.001, format="%.3f")
    ptr_alert = st.slider("Throughput below", 0.5, 1.5, 1.0, 0.05)

    st.markdown("---")
    st.markdown(f"**{icon('bar-chart', 14)} Chart options**", unsafe_allow_html=True)
    show_rolling = st.checkbox("30-day rolling average", value=True)
    show_alerts  = st.checkbox("Show policy-break marker", value=True)

    st.markdown("---")
    st.caption("Jan 12, 2023 – Dec 21, 2025 · 720 reporting days")


mask = (df["Date"].dt.date >= date_start) & (df["Date"].dt.date <= date_end)
dff  = df[mask].copy()
recent = dff.tail(30)
latest_window = dff.tail(30)


# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(
    f"<div class='app-title'>{icon('monitoring', 26, BLUE)}"
    f"<h2>Care Transition Efficiency & Placement Outcome Analytics</h2></div>"
    f"<div class='app-subtitle'>HHS Unaccompanied Alien Children Program</div>",
    unsafe_allow_html=True,
)
st.write("")

if dff["Date"].max() >= BREAK_DATE:
    st.markdown(alert_box(
        "red", "Structural break, Feb 2025:",
        "Every operational metric dropped simultaneously and has stayed low since — "
        "current volume is under 20% of peak, and discharge effectiveness under 25% of its pre-2025 level."
    ), unsafe_allow_html=True)

tab_overview, tab_flow, tab_efficiency, tab_compare, tab_bottleneck, tab_weekday, tab_raw = st.tabs([
    "1 · Overview", "2 · Pipeline Flow", "3 · Efficiency Trends",
    "4 · Pre/Post Comparison", "5 · Bottlenecks & Wait Times",
    "6 · Weekday Patterns", "7 · Raw Data",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════

with tab_overview:
    st.markdown(section_head("pin", "System-level KPIs"), unsafe_allow_html=True)

    with st.container(border=True):
        kpi_defs = [
            ("Transfer Efficiency", recent["transfer_efficiency"].mean(), df_pre["transfer_efficiency"].mean(), "{:.3f}"),
            ("Discharge Effectiveness", recent["discharge_effectiveness"].mean(), df_pre["discharge_effectiveness"].mean(), "{:.4f}"),
            ("Pipeline Throughput", recent["pipeline_throughput"].mean(), df_pre["pipeline_throughput"].mean(), "{:.3f}"),
        ]
        cols = st.columns(5)
        for c, (label, val, pre_val, fmt) in zip(cols[:3], kpi_defs):
            delta = ((val - pre_val) / pre_val * 100) if pre_val else 0
            c.metric(label, fmt.format(val), f"{delta:+.1f}% vs pre-2025")
        cols[3].metric("Backlog Accumulation", f"{recent['backlog_accumulation'].mean():+.0f}/day",
                        "Negative = clearing", delta_color="off")
        stay_val = recent["implied_stay"].mean()
        cols[4].metric("Implied Stay (days)", f"{stay_val:.0f}",
                        "Within guideline" if stay_val <= 72 else f"{stay_val/72:.1f}x guideline",
                        delta_color="off")

    c1, c2 = st.columns(2)
    with c1:
        ptr_now = recent["pipeline_throughput"].mean()
        kind, msg = ("green", "above") if ptr_now >= ptr_alert else ("red", "below")
        st.markdown(alert_box(kind, "Throughput:", f"30-day avg is {ptr_now:.3f}, {msg} the {ptr_alert:.2f} threshold."),
                    unsafe_allow_html=True)
    with c2:
        dei_now = recent["discharge_effectiveness"].mean()
        kind, msg = ("green", "above") if dei_now >= dei_alert else ("red", "below")
        st.markdown(alert_box(kind, "Discharge rate:", f"30-day avg is {dei_now:.4f}, {msg} the {dei_alert:.3f} threshold."),
                    unsafe_allow_html=True)

    st.markdown(section_head("route", "Pipeline snapshot — last 30 days"), unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown(stage_card("Stage 1 · CBP Custody", int(latest_window["cbp_in"].mean()),
                     f"avg in custody/day · {int(latest_window['cbp_new'].mean())} new arrivals/day", BLUE),
                     unsafe_allow_html=True)
    with p2:
        st.markdown(stage_card("Stage 2 · HHS Care", int(latest_window["hhs_in"].mean()),
                     f"avg in care/day · {int(latest_window['hhs_out'].mean())} discharges/day", PURPLE),
                     unsafe_allow_html=True)
    with p3:
        st.markdown(stage_card("Stage 3 · Sponsor Placement", int(latest_window["hhs_out"].mean()),
                     "children placed/day", GREEN),
                     unsafe_allow_html=True)

    st.caption(
        f"Range: {date_start} to {date_end} · {len(dff)} reporting days · "
        f"Bottleneck days: {dff['is_bottleneck'].sum()} ({dff['is_bottleneck'].mean()*100:.1f}%)"
    )

    st.markdown(section_head("info", "Key findings"), unsafe_allow_html=True)
    st.markdown(
        alert_box("red", "Intake vs. discharge:",
            "Intake fell 93.6% but the in-care population only fell 70.1%, because discharge fell "
            "just as sharply (−93.2%) — children already in care weren't placed at the same rate.")
        + alert_box("amber", "Bottleneck rate:",
            "Despite 70% fewer children in the system, bottleneck frequency nearly doubled "
            "(13.9% → 26.3%) — a smaller caseload should be easier to manage, not harder.")
        + alert_box("blue", "Wait times:",
            "Implied placement wait rose from ~31 days (2023) to ~222 days post-Feb 2025, "
            "breaching the 72-day legal guideline every month since."),
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PIPELINE FLOW
# ═══════════════════════════════════════════════════════════════════════════════

with tab_flow:
    st.markdown(section_head("sync-alt", "Care pipeline — raw time series"), unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])

    with col_left, st.container(border=True):
        fig = make_subplots(
            rows=3, cols=1, shared_xaxes=True,
            subplot_titles=[
                "Stage 1 · CBP Custody (apprehensions & headcount)",
                "Stage 2 · HHS Care (population & daily discharges)",
                "Transfers: CBP → HHS (daily handoffs)",
            ],
            vertical_spacing=0.1,
        )

        fig.add_trace(go.Scatter(x=dff["Date"], y=dff["cbp_new"], name="Apprehended",
                                  line=dict(color="#3B82F6", width=1), opacity=0.7,
                                  fill="tozeroy", fillcolor="rgba(59,130,246,0.1)"), row=1, col=1)
        fig.add_trace(go.Scatter(x=dff["Date"], y=dff["cbp_in"], name="In CBP custody",
                                  line=dict(color="#1D4ED8", width=1.5)), row=1, col=1)

        fig.add_trace(go.Scatter(x=dff["Date"], y=dff["hhs_in"], name="In HHS care",
                                  line=dict(color="#7C3AED", width=1.5)), row=2, col=1)
        fig.add_trace(go.Scatter(x=dff["Date"], y=dff["hhs_out"], name="HHS discharges",
                                  line=dict(color="#10B981", width=1), opacity=0.8,
                                  fill="tozeroy", fillcolor="rgba(16,185,129,0.1)"), row=2, col=1)

        fig.add_trace(go.Scatter(x=dff["Date"], y=dff["cbp_xfer"], name="Transferred CBP→HHS",
                                  line=dict(color="#F59E0B", width=1), opacity=0.8), row=3, col=1)

        if show_alerts and dff["Date"].max() >= BREAK_DATE:
            for row_n in [1, 2, 3]:
                mark_policy_break(fig, row=row_n, col=1)

        layout = base_layout(height=560)
        layout["margin"] = dict(l=0, r=0, t=90, b=0)
        layout["legend"]["y"] = 1.06
        fig.update_layout(**layout)
        fig.update_annotations(font_size=12, font_color=TEXT_DIM)
        st.plotly_chart(fig, use_container_width=True)

    with col_right, st.container(border=True):
        st.markdown("**Pipeline stage summary**")
        st.caption("Selected range, 30-day average")

        st.markdown(stage_card("Stage 1 · CBP", int(latest_window["cbp_in"].mean()),
                     f"in custody/day · {int(latest_window['cbp_new'].mean())} new/day", BLUE), unsafe_allow_html=True)
        st.markdown(f"<div class='stage-arrow'>{icon('arrow-down', 18, TEXT_MUTE)}</div>", unsafe_allow_html=True)
        st.markdown(stage_card("Stage 2 · HHS Care", int(latest_window["hhs_in"].mean()),
                     f"in care/day · {int(latest_window['hhs_out'].mean())} discharges/day", PURPLE), unsafe_allow_html=True)
        st.markdown(f"<div class='stage-arrow'>{icon('arrow-down', 18, TEXT_MUTE)}</div>", unsafe_allow_html=True)
        st.markdown(stage_card("Stage 3 · Sponsor Placement", int(latest_window["hhs_out"].mean()),
                     "children placed/day", GREEN), unsafe_allow_html=True)

        st.markdown("---")
        bottleneck_pct = dff["is_bottleneck"].mean() * 100
        color = RED if bottleneck_pct > 20 else (AMBER if bottleneck_pct > 10 else GREEN)
        st.markdown(
            f"<div style='font-size:0.85rem;color:{TEXT_DIM}'>"
            f"<b>Range:</b> {date_start} → {date_end}<br>"
            f"<b>Reporting days:</b> {len(dff)}<br>"
            f"<b>Bottleneck days:</b> <span style='color:{color};font-weight:700'>"
            f"{dff['is_bottleneck'].sum()} ({bottleneck_pct:.1f}%)</span></div>",
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — EFFICIENCY TRENDS
# ═══════════════════════════════════════════════════════════════════════════════

with tab_efficiency:
    st.markdown(section_head("trending-up", "Transfer & discharge efficiency"), unsafe_allow_html=True)

    kpi_choice = st.radio(
        "KPI", ["Transfer Efficiency Ratio", "Discharge Effectiveness Index",
                "Backlog Accumulation Rate", "Pipeline Throughput Rate"],
        horizontal=True, label_visibility="collapsed",
    )
    kpi_map = {
        "Transfer Efficiency Ratio":     ("transfer_efficiency",     "#3B82F6"),
        "Discharge Effectiveness Index": ("discharge_effectiveness", "#10B981"),
        "Backlog Accumulation Rate":     ("backlog_accumulation",    "#F97316"),
        "Pipeline Throughput Rate":      ("pipeline_throughput",     "#8B5CF6"),
    }
    kpi_col, kpi_color = kpi_map[kpi_choice]
    rolling_col = f"{kpi_col}_30d"

    with st.container(border=True):
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=dff["Date"], y=dff[kpi_col], name="Daily value",
                                   line=dict(color=kpi_color, width=0.8), opacity=0.35, mode="lines"))
        if show_rolling:
            fig2.add_trace(go.Scatter(x=dff["Date"], y=dff[rolling_col], name="30-day rolling avg",
                                       line=dict(color=kpi_color, width=2.5)))

        if kpi_col == "pipeline_throughput":
            fig2.add_hline(y=1.0, line=dict(color=RED, dash="dash", width=1.5),
                            annotation_text="  PTR = 1.0 alert threshold", annotation_position="top left")
        elif kpi_col == "discharge_effectiveness":
            fig2.add_hline(y=dei_alert, line=dict(color=AMBER, dash="dash", width=1.5),
                            annotation_text=f"  DEI alert: {dei_alert:.3f}", annotation_position="top left")

        # See mark_policy_break() docstring: line + label are added separately
        # to avoid Plotly's datetime-timestamp averaging bug.
        if show_alerts and dff["Date"].max() >= BREAK_DATE:
            mark_policy_break(fig2, label="Feb 2025 policy break")

        layout = base_layout(title=f"{kpi_choice} — daily values with 30-day rolling average", height=380)
        fig2.update_layout(**layout)
        st.plotly_chart(fig2, use_container_width=True)

        s1, s2, s3, s4 = st.columns(4)
        kpi_data = dff[kpi_col].dropna()
        s1.metric("Mean",   f"{kpi_data.mean():.4f}")
        s2.metric("Median", f"{kpi_data.median():.4f}")
        s3.metric("Min",    f"{kpi_data.min():.4f}")
        s4.metric("Max",    f"{kpi_data.max():.4f}")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PRE vs POST COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════

with tab_compare:
    st.markdown(section_head("balance", "Pre vs. post February 2025"), unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])

    with col_a, st.container(border=True):
        kpi_cols   = ["transfer_efficiency", "discharge_effectiveness", "pipeline_throughput"]
        kpi_labels = ["Transfer Efficiency", "Discharge Effectiveness", "Pipeline Throughput"]
        pre_vals  = [df_pre[k].mean()  for k in kpi_cols]
        post_vals = [df_post[k].mean() for k in kpi_cols]

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(name="Pre-Feb 2025", x=kpi_labels, y=pre_vals, marker_color="#3B82F6",
                               text=[f"{v:.3f}" for v in pre_vals], textposition="outside"))
        fig3.add_trace(go.Bar(name="Post-Feb 2025", x=kpi_labels, y=post_vals, marker_color=RED,
                               text=[f"{v:.3f}" for v in post_vals], textposition="outside"))
        layout = base_layout(title="System efficiency, pre vs. post February 2025", height=380)
        layout["barmode"] = "group"
        fig3.update_layout(**layout)
        st.plotly_chart(fig3, use_container_width=True)

    with col_b, st.container(border=True):
        st.markdown("**Volume changes after Feb 2025**")
        vol_df = pd.DataFrame({
            "Metric": ["Daily apprehensions", "CBP in custody", "Daily transfers", "HHS in care", "Daily discharges"],
            "Pre-2025":  [130.3, 233.7, 179.8, 7686, 241.1],
            "Post-2025": [8.3, 27.2, 10.2, 2295, 16.5],
            "Change":    [-93.6, -88.4, -94.3, -70.1, -93.2],
        })
        styled = vol_df.style.format({"Pre-2025": "{:.1f}", "Post-2025": "{:.1f}", "Change": "{:+.1f}%"}) \
            .map(lambda v: f"color:{RED};font-weight:600" if isinstance(v, (int, float)) and v < 0 else "",
                 subset=["Change"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        st.markdown(
            alert_box("red", "Key asymmetry:",
                "Intake dropped 93.6% but in-care population only fell 70.1% — discharge fell just as "
                "sharply (−93.2%), so children already in the system weren't placed proportionately."),
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — BOTTLENECKS & WAIT TIMES
# ═══════════════════════════════════════════════════════════════════════════════

with tab_bottleneck:
    st.markdown(section_head("emergency", "Bottleneck detection"), unsafe_allow_html=True)

    col_c, col_d = st.columns([3, 2])

    with col_c, st.container(border=True):
        monthly_bn = dff.groupby("year_month")["is_bottleneck"].sum().reset_index()
        monthly_bn["period"] = monthly_bn["year_month"].apply(
            lambda x: "Post-Feb 2025" if x >= "2025-02" else "Pre-Feb 2025")

        fig4 = px.bar(monthly_bn, x="year_month", y="is_bottleneck", color="period",
                       color_discrete_map={"Pre-Feb 2025": "#8B5CF6", "Post-Feb 2025": RED},
                       labels={"is_bottleneck": "Bottleneck days", "year_month": "Month"})
        layout = base_layout(title="Monthly bottleneck days (backlog > 0 and throughput < 1.0)", height=340)
        layout["legend"]["title"] = None
        fig4.update_layout(**layout)
        fig4.update_xaxes(tickangle=45)
        st.plotly_chart(fig4, use_container_width=True)

    with col_d, st.container(border=True):
        st.markdown("**Bottleneck rate, pre vs. post**")
        pre_bn_pct  = df_pre["is_bottleneck"].mean()  * 100
        post_bn_pct = df_post["is_bottleneck"].mean() * 100
        b1, b2 = st.columns(2)
        b1.metric("Pre-2025", f"{pre_bn_pct:.1f}%", f"{df_pre['is_bottleneck'].sum()} days")
        b2.metric("Post-2025", f"{post_bn_pct:.1f}%", f"+{post_bn_pct - pre_bn_pct:.1f}pp", delta_color="inverse")
        st.markdown(
            alert_box("amber", "Bottleneck paradox:",
                "70% fewer children in the system, yet bottleneck frequency nearly doubled "
                "(13.9% → 26.3%) — the clearest sign of reduced capacity, not lower demand."),
            unsafe_allow_html=True,
        )

    st.markdown(section_head("clock", "Implied sponsor-placement wait"), unsafe_allow_html=True)

    monthly_stay = dff.groupby("year_month")["implied_stay"].mean().reset_index()
    monthly_stay["period"] = monthly_stay["year_month"].apply(
        lambda x: "Post-Feb 2025" if x >= "2025-02" else "Pre-Feb 2025")

    fig5 = px.bar(monthly_stay, x="year_month", y="implied_stay", color="period",
                   color_discrete_map={"Pre-Feb 2025": "#0EA5E9", "Post-Feb 2025": RED},
                   labels={"implied_stay": "Implied stay (days)", "year_month": "Month"})
    fig5.add_hline(y=72, line=dict(color=AMBER, dash="dash", width=2),
                    annotation_text="  72-day legal guideline", annotation_position="top left")
    fig5.add_hline(y=30, line=dict(color=GREEN, dash="dash", width=1.5),
                    annotation_text="  30-day operational target", annotation_position="bottom left")

    with st.container(border=True):
        layout = base_layout(title="Implied average stay in HHS care (1 ÷ discharge rate)", height=400)
        layout["legend"]["title"] = None
        fig5.update_layout(**layout)
        fig5.update_xaxes(tickangle=45)
        st.plotly_chart(fig5, use_container_width=True)

        s1, s2, s3, s4 = st.columns(4)
        pre_stay, post_stay = df_pre["implied_stay"].mean(), df_post["implied_stay"].mean()
        peak_stay = monthly_stay["implied_stay"].max()
        peak_mo   = monthly_stay.loc[monthly_stay["implied_stay"].idxmax(), "year_month"]
        s1.metric("2023 avg", f"{df[df['year']==2023]['implied_stay'].mean():.0f}d", "Within guideline")
        s2.metric("Pre-2025 avg", f"{pre_stay:.0f}d", "Within guideline")
        s3.metric("Post-2025 avg", f"{post_stay:.0f}d", f"{post_stay/72:.1f}x guideline")
        s4.metric(f"Peak ({peak_mo})", f"{peak_stay:.0f}d", f"{peak_stay/72:.1f}x guideline")

    st.markdown(
        alert_box("red", "Summary:",
            "Sponsor-placement wait has risen from ~31 days (2023) to 150–300 days post-Feb 2025, "
            "breaching the 72-day legal guideline every month since."),
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — WEEKDAY PATTERNS
# ═══════════════════════════════════════════════════════════════════════════════

with tab_weekday:
    st.markdown(section_head("calendar", "Weekday operational patterns"), unsafe_allow_html=True)

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_color_map = {
        "Monday": "#3B82F6", "Tuesday": "#3B82F6", "Wednesday": "#3B82F6",
        "Thursday": "#F97316", "Friday": "#3B82F6", "Saturday": "#94A3B8", "Sunday": "#F97316",
    }

    weekday_data_full = (
        dff.groupby("day_of_week")[["cbp_xfer", "hhs_out", "transfer_efficiency", "discharge_effectiveness"]]
        .mean().reindex(day_order).reset_index()
    )
    present_mask = (
        weekday_data_full["day_of_week"].isin(dff["day_of_week"].unique())
        & weekday_data_full["cbp_xfer"].notna()
    )
    weekday_data = weekday_data_full[present_mask].reset_index(drop=True)
    bar_colors = weekday_data["day_of_week"].map(day_color_map)

    col_e, col_f = st.columns(2)
    with col_e, st.container(border=True):
        fig6 = go.Figure(go.Bar(x=weekday_data["day_of_week"], y=weekday_data["cbp_xfer"].round(1),
                                 marker_color=bar_colors, text=weekday_data["cbp_xfer"].round(0),
                                 textposition="outside"))
        layout = base_layout(title="Mean daily transfers (CBP → HHS)", height=320, legend=False)
        layout["yaxis"]["title"] = "Children transferred"
        fig6.update_layout(**layout)
        st.plotly_chart(fig6, use_container_width=True)

    with col_f, st.container(border=True):
        fig7 = go.Figure(go.Bar(x=weekday_data["day_of_week"], y=weekday_data["hhs_out"].round(1),
                                 marker_color=bar_colors, text=weekday_data["hhs_out"].round(0),
                                 textposition="outside"))
        layout = base_layout(title="Mean daily discharges (HHS → sponsor)", height=320, legend=False)
        layout["yaxis"]["title"] = "Children discharged"
        fig7.update_layout(**layout)
        st.plotly_chart(fig7, use_container_width=True)

    if (~present_mask).any():
        missing_days = weekday_data_full.loc[~present_mask, "day_of_week"].tolist()
        st.markdown(alert_box("blue", "Data gap:",
            f"No records for {', '.join(missing_days)} in the selected range — omitted rather than shown as zero."),
            unsafe_allow_html=True)

    st.markdown(
        alert_box("blue", "Thursday–Sunday cycle:",
            "Discharges peak Thursday (205.7) and Sunday (206.1) — 51% higher than the low, "
            "Tuesday (136.1). Weekends are operationally active, not dormant."),
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7 — RAW DATA
# ═══════════════════════════════════════════════════════════════════════════════

with tab_raw:
    st.markdown(section_head("list", "Raw data table"), unsafe_allow_html=True)

    display_cols = [
        "Date", "cbp_new", "cbp_in", "cbp_xfer", "hhs_in", "hhs_out",
        "transfer_efficiency", "discharge_effectiveness",
        "backlog_accumulation", "pipeline_throughput", "implied_stay", "is_bottleneck",
    ]
    display_df = dff[display_cols].copy()
    display_df.columns = [
        "Date", "CBP New", "CBP In", "CBP Xfer", "HHS In", "HHS Out",
        "Transfer Eff.", "Discharge Eff.", "Backlog", "Throughput", "Implied Stay (d)", "Bottleneck",
    ]
    st.dataframe(display_df.sort_values("Date", ascending=False), use_container_width=True, height=560)
    st.caption(f"{len(display_df)} rows for the selected date range.")

    csv_bytes = display_df.sort_values("Date", ascending=False).to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", data=csv_bytes,
                        file_name="hhs_uac_care_pipeline_filtered.csv", mime="text/csv")


# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:{TEXT_MUTE};font-size:12px;padding:10px 0;'>"
    "Care Transition Efficiency & Placement Outcome Analytics · HHS Unaccompanied Alien Children Program · "
    "Data: Jan 12, 2023 – Dec 21, 2025</div>",
    unsafe_allow_html=True,
)