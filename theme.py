# ─────────────────────────────────────────────────────────────────────────────
# theme.py
# All look-and-feel lives here, separate from app logic (app.py).
# Two palettes ("light" / "dark") + a CSS builder + a Plotly figure themer.
# ─────────────────────────────────────────────────────────────────────────────

THEMES = {
    "light": {
        "bg":            "#F8F9FB",
        "card_bg":       "#FFFFFF",
        "sidebar_bg":    "#FFFFFF",
        "text":          "#1E293B",
        "muted":         "#64748B",
        "border":        "#E2E8F0",
        "grid":          "#E2E8F0",
        "plot_bg":       "#FAFAFA",
        "paper_bg":      "#FAFAFA",
        "primary":       "#2563EB",
        # pipeline stage cards (Section 2 summary)
        "stage1_bg": "#F1F5F9", "stage1_accent": "#1D4ED8",
        "stage2_bg": "#F5F3FF", "stage2_accent": "#7C3AED",
        "stage3_bg": "#F0FDF4", "stage3_accent": "#16A34A",
        # alert boxes
        "red_bg": "#FEF2F2",  "red_border": "#DC2626",  "red_text": "#7F1D1D",
        "green_bg": "#F0FDF4","green_border": "#16A34A","green_text": "#14532D",
        "amber_bg": "#FFFBEB","amber_border": "#D97706","amber_text": "#78350F",
        "blue_bg": "#EFF6FF", "blue_border": "#2563EB", "blue_text": "#1E3A5F",
    },
    "dark": {
        "bg":            "#0E1117",
        "card_bg":       "#1A1D29",
        "sidebar_bg":    "#12141C",
        "text":          "#FFFFFF",
        "muted":         "#94A3B8",
        "border":        "#2A2D3A",
        "grid":          "#2A2D3A",
        "plot_bg":       "#161923",
        "paper_bg":      "#161923",
        "primary":       "#60A5FA",
        "stage1_bg": "#131C2E", "stage1_accent": "#60A5FA",
        "stage2_bg": "#1E1730", "stage2_accent": "#A78BFA",
        "stage3_bg": "#122019", "stage3_accent": "#4ADE80",
        "red_bg": "#2A1414",  "red_border": "#F87171",  "red_text": "#FCA5A5",
        "green_bg": "#132018","green_border": "#4ADE80","green_text": "#86EFAC",
        "amber_bg": "#241D0E","amber_border": "#FBBF24","amber_text": "#FCD34D",
        "blue_bg": "#101B2E", "blue_border": "#60A5FA", "blue_text": "#93C5FD",
    },
}


def build_css(theme_name: str) -> str:
    """Return a <style> block that themes the whole app for the given palette."""
    t = THEMES[theme_name]
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

    /* app background + text */
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}

    /* Streamlit renders a separate fixed header bar above .stApp that is
       NOT covered by the rule above — this is what causes the persistent
       white/light strip at the top of the page in dark mode. Must be
       targeted explicitly and made transparent so the app background
       shows through with no seam. */
    header[data-testid="stHeader"] {{
        background-color: transparent;
        background: {t['bg']};
    }}
    div[data-testid="stDecoration"] {{ display: none; }}
    div[data-testid="stToolbar"] {{ background-color: transparent; }}

    /* remove Streamlit's large default top padding so content sits closer
       to the header instead of leaving a tall empty band */
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }}

    /* sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {t['sidebar_bg']};
        border-right: 1px solid {t['border']};
    }}
    section[data-testid="stSidebar"] * {{ color: {t['text']}; }}
    section[data-testid="stSidebar"] .block-container {{ padding-top: 1.25rem; }}

    /* metric cards */
    div[data-testid="stMetric"] {{
        background-color: {t['card_bg']};
        border: 1px solid {t['border']};
        border-radius: 10px;
        padding: 12px 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        min-width: 0; /* allow flex children to shrink instead of overflowing */
        overflow: hidden;
    }}
    div[data-testid="stMetricLabel"] {{
        text-transform: uppercase;
        letter-spacing: .03em;
        font-size: 0.68rem !important;
        opacity: 0.75;
        white-space: normal;
        line-height: 1.25;
    }}
    /* fluid metric-value sizing so numbers never get clipped ("0...", "2...")
       on narrow / mobile viewports — scales smoothly between a min and max
       instead of a single fixed size that overflows its column. */
    div[data-testid="stMetricValue"] {{
        font-size: clamp(1.05rem, 4vw, 1.6rem) !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        line-height: 1.2;
    }}
    div[data-testid="stMetricDelta"] {{
        font-size: 0.75rem !important;
        white-space: normal;
        line-height: 1.3;
    }}

    /* on narrow screens, let KPI metric rows wrap to 2-3 per line instead
       of forcing 5 columns into ~70px each */
    @media (max-width: 640px) {{
        div[data-testid="stHorizontalBlock"] {{
            flex-wrap: wrap;
            row-gap: 10px;
        }}
        div[data-testid="stHorizontalBlock"] > div {{
            min-width: 47%;
            flex: 1 1 47%;
        }}
        div[data-testid="stMetricValue"] {{
            font-size: 1.35rem !important;
        }}
    }}

    /* section headers */
    .section-title {{
        font-size: 17px;
        font-weight: 600;
        color: {t['text']};
        margin: 4px 0 10px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid {t['border']};
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.01em;
    }}
    .section-title svg {{ flex-shrink: 0; }}

    /* generic bordered card container (st.container(border=True)) —
       shadow + hover lift, matching the reference dashboard's card feel */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {t['card_bg']};
        border-color: {t['border']} !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        transition: box-shadow 0.2s ease;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        box-shadow: 0 2px 12px rgba(0,0,0,0.20);
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] > div {{ gap: 0.6rem; }}

    /* alert boxes — line-height + max-width keep long sentences from
       looking like a dense wall of text on narrow columns, and font-weight
       500 on the body text keeps contrast readable in both themes */
    .alert-red, .alert-green, .alert-amber, .alert-blue {{
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
        font-size: 13.5px;
        line-height: 1.55;
        display: flex;
        gap: 8px;
        align-items: flex-start;
        font-weight: 450;
    }}
    .alert-red svg, .alert-green svg, .alert-amber svg, .alert-blue svg {{
        flex-shrink: 0;
        margin-top: 2px;
    }}
    .alert-red {{
        background-color: {t['red_bg']}; border-left: 4px solid {t['red_border']};
        color: {t['red_text']};
    }}
    .alert-green {{
        background-color: {t['green_bg']}; border-left: 4px solid {t['green_border']};
        color: {t['green_text']};
    }}
    .alert-amber {{
        background-color: {t['amber_bg']}; border-left: 4px solid {t['amber_border']};
        color: {t['amber_text']};
    }}
    .alert-blue {{
        background-color: {t['blue_bg']}; border-left: 4px solid {t['blue_border']};
        color: {t['blue_text']};
    }}

    /* pipeline stage summary cards (Section 2) */
    .stage-card {{
        border-radius: 8px; padding: 14px; margin: 8px 0;
    }}
    .stage-card .stage-label {{
        font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: {t['muted']};
    }}
    .stage-card .stage-value {{ font-size: 22px; font-weight: 600; }}
    .stage-card .stage-sub {{ font-size: 12px; color: {t['muted']}; }}
    .stage-arrow {{ text-align: center; color: {t['muted']}; margin: 4px 0; }}

    /* plain HTML result tables (used instead of pandas Styler, which needs jinja2) */
    .themed-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    .themed-table th {{
        text-align: left; padding: 8px 10px; border-bottom: 2px solid {t['border']};
        color: {t['muted']}; text-transform: uppercase; font-size: 11px; letter-spacing: .04em;
    }}
    .themed-table td {{
        padding: 8px 10px; border-bottom: 1px solid {t['border']}; color: {t['text']};
    }}

    /* hide default streamlit chrome */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* top-level tab navigation (replaces the old single-page mega-scroll) */
    div[data-testid="stTabs"] button[data-baseweb="tab"] {{
        color: {t['muted']};
        font-weight: 500;
        font-size: 14px;
        padding: 8px 4px;
    }}
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {{
        color: {t['primary']};
        font-weight: 600;
    }}
    div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {{
        background-color: {t['primary']};
        height: 2.5px;
    }}
    div[data-testid="stTabs"] div[data-baseweb="tab-border"] {{
        background-color: {t['border']};
    }}
    </style>
    """


def plotly_colors(theme_name: str) -> dict:
    """Colors to reuse when theming individual Plotly figures."""
    t = THEMES[theme_name]
    return {
        "plot_bg": t["plot_bg"],
        "paper_bg": t["paper_bg"],
        "text": t["text"],
        "grid": t["grid"],
    }


def apply_fig_theme(fig, theme_name: str):
    """Apply the current theme's colors to a Plotly figure in place.

    Call this right before st.plotly_chart(), after any chart-specific
    update_layout()/update_xaxes() calls — it only touches background,
    font, and gridline colors, leaving titles/legends/etc. untouched.
    """
    c = plotly_colors(theme_name)
    fig.update_layout(
        plot_bgcolor=c["plot_bg"],
        paper_bgcolor=c["paper_bg"],
        font=dict(color=c["text"]),
    )
    fig.update_xaxes(gridcolor=c["grid"])
    fig.update_yaxes(gridcolor=c["grid"])
    return fig


def render_stage_card(theme_name, label, value, sub, accent_key, bg_key):
    """Build one themed 'pipeline stage' summary card (replaces inline hex HTML)."""
    t = THEMES[theme_name]
    return f"""
    <div class='stage-card' style='background:{t[bg_key]};'>
        <div class='stage-label'>{label}</div>
        <div class='stage-value' style='color:{t[accent_key]};'>{value}</div>
        <div class='stage-sub'>{sub}</div>
    </div>
    """


def render_colored_table(df, color_col, negative="red", positive="green", theme_name="light"):
    """
    Render a small DataFrame as a themed HTML table, coloring `color_col`
    red/green based on the sign of a leading '+'/'-' in the text (or of the
    numeric value). Avoids pandas' Styler, which requires jinja2.
    """
    t = THEMES[theme_name]
    neg_color = t["red_border"] if negative == "red" else t["green_border"]
    pos_color = t["green_border"] if positive == "green" else t["red_border"]

    def cell_color(val):
        s = str(val)
        if s.strip().startswith("-") or s.strip().startswith("−"):
            return neg_color
        if s.strip().startswith("+"):
            return pos_color
        return t["text"]

    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    rows_html = []
    for _, row in df.iterrows():
        cells = []
        for c in df.columns:
            val = row[c]
            if c == color_col:
                cells.append(f"<td style='color:{cell_color(val)}; font-weight:600;'>{val}</td>")
            else:
                cells.append(f"<td>{val}</td>")
        rows_html.append(f"<tr>{''.join(cells)}</tr>")

    return f"""
    <table class='themed-table'>
        <thead><tr>{headers}</tr></thead>
        <tbody>{''.join(rows_html)}</tbody>
    </table>
    """