import html

import streamlit as st

GLOBAL_BG_COLOR = "#070b14"
GLOBAL_TEXT_COLOR = "#ecf2ff"
GLOBAL_SURFACE_COLOR = "#0f1728"
GLOBAL_SURFACE_ALT_COLOR = "#121f36"
GLOBAL_BORDER_COLOR = "#2b3f63"
GLOBAL_MUTED_TEXT_COLOR = "#8fa7cc"
GLOBAL_ACCENT_COLOR = "#37d0ff"
GLOBAL_FONT_FAMILY = "'SUIT Variable', 'Pretendard Variable', 'Noto Sans KR', 'Apple SD Gothic Neo', 'Segoe UI', sans-serif"


def apply_global_theme() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://cdn.jsdelivr.net/gh/sunn-us/SUIT/fonts/static/woff2/SUIT.css');

        :root,
        [data-theme="light"],
        [data-theme="dark"] {{
            color-scheme: dark !important;
            --app-bg: {GLOBAL_BG_COLOR};
            --app-surface: {GLOBAL_SURFACE_COLOR};
            --app-surface-alt: {GLOBAL_SURFACE_ALT_COLOR};
            --app-border: {GLOBAL_BORDER_COLOR};
            --app-text: {GLOBAL_TEXT_COLOR};
            --app-muted: {GLOBAL_MUTED_TEXT_COLOR};
            --app-accent: {GLOBAL_ACCENT_COLOR};
            --app-font: {GLOBAL_FONT_FAMILY};
            --primary-color: {GLOBAL_ACCENT_COLOR};
            --background-color: {GLOBAL_BG_COLOR};
            --secondary-background-color: {GLOBAL_SURFACE_COLOR};
            --text-color: {GLOBAL_TEXT_COLOR};
            --font: {GLOBAL_FONT_FAMILY};
        }}

        html, body, .stApp, [data-testid="stAppViewContainer"] {{
            background:
                radial-gradient(1000px 360px at 8% -5%, rgba(48, 95, 255, 0.22), transparent 60%),
                radial-gradient(900px 320px at 90% 0%, rgba(55, 208, 255, 0.16), transparent 64%),
                linear-gradient(180deg, #050912 0%, #070b14 100%) !important;
            color: var(--app-text) !important;
            font-family: var(--app-font) !important;
        }}

        header[data-testid="stHeader"],
        [data-testid="stToolbar"] {{
            background: transparent !important;
        }}

        [data-testid="stSidebarNav"],
        [data-testid="stSidebar"],
        [aria-label="Sidebar"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarToggleButton"],
        button[aria-label="Open sidebar"],
        button[aria-label="Close sidebar"] {{
            display: none !important;
        }}

        .block-container {{
            max-width: 1320px;
            padding-top: 2.2rem !important;
            padding-bottom: 2rem !important;
        }}

        h1, h2, h3, h4, p, span, div, label, li, a, summary, input, select, button, table, th, td {{
            font-family: var(--app-font) !important;
        }}

        .material-symbols-rounded,
        .material-symbols-outlined,
        .material-icons,
        [class*="material-symbols"],
        [class*="material-icons"],
        [data-testid="stIconMaterial"] {{
            font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
        }}

        h1 {{
            font-size: clamp(1.8rem, 1.2rem + 1.8vw, 2.7rem) !important;
            font-weight: 780 !important;
            letter-spacing: -0.02em;
        }}

        h2 {{
            font-size: clamp(1.2rem, 1rem + 0.8vw, 1.7rem) !important;
            font-weight: 700 !important;
            letter-spacing: -0.01em;
        }}

        [data-testid="stMetric"] {{
            border: 1px solid var(--app-border);
            border-radius: 16px;
            padding: 10px 12px;
            background: linear-gradient(180deg, rgba(18,31,54,0.88), rgba(9,15,28,0.92));
            box-shadow: 0 10px 20px rgba(2, 6, 23, 0.25);
        }}

        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"] {{
            color: var(--app-text) !important;
        }}

        .stButton > button,
        div[data-testid="stButton"] > button,
        button[data-testid^="stBaseButton-"] {{
            border-radius: 12px !important;
            border: 1px solid var(--app-border) !important;
            min-height: 42px !important;
            background: linear-gradient(180deg, rgba(18,31,54,0.95), rgba(13,23,42,0.95)) !important;
            color: var(--app-text) !important;
            transition: all 0.18s ease;
        }}

        .stButton > button:hover,
        div[data-testid="stButton"] > button:hover {{
            border-color: #4f77b5 !important;
            transform: translateY(-1px);
        }}

        .stButton > button[kind="primary"],
        button[data-testid="stBaseButton-primary"] {{
            background: linear-gradient(135deg, #1f6dff, #10b8ff) !important;
            border-color: #56d8ff !important;
            color: #f8fbff !important;
            box-shadow: 0 0 0 1px rgba(86, 216, 255, 0.25), 0 8px 20px rgba(16, 184, 255, 0.28) !important;
        }}

        .stSelectbox [data-baseweb="select"] > div,
        [data-baseweb="input"],
        [data-testid="stTextInputRootElement"],
        [data-baseweb="input"] > div,
        .stTextArea textarea,
        .stNumberInput input {{
            border-radius: 12px !important;
            border: 1px solid var(--app-border) !important;
            background: rgba(13, 23, 42, 0.92) !important;
            color: var(--app-text) !important;
            box-shadow: none !important;
        }}

        .stTextInput [data-baseweb="input"] > div,
        .stTextInput div[data-baseweb="input"] > div,
        div[data-baseweb="base-input"] > div {{
            border: 1px solid var(--app-border) !important;
            border-radius: 12px !important;
            box-shadow: none !important;
            background: rgba(13, 23, 42, 0.92) !important;
        }}

        .stTextInput input,
        .stTextInput input:focus,
        .stTextInput input:focus-visible {{
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            background: transparent !important;
            color: var(--app-text) !important;
            -webkit-text-fill-color: var(--app-text) !important;
        }}

        [data-baseweb="input"]:focus-within > div,
        [data-baseweb="input"]:focus-within,
        [data-testid="stTextInputRootElement"]:focus-within,
        [data-baseweb="input"] > div:focus-within,
        .stTextInput div[data-baseweb="input"]:focus-within > div {{
            border-color: var(--app-accent) !important;
            box-shadow: 0 0 0 1px rgba(55, 208, 255, 0.35) !important;
            outline: none !important;
        }}

        .stTextInput input:-webkit-autofill,
        .stTextInput input:-webkit-autofill:hover,
        .stTextInput input:-webkit-autofill:focus {{
            -webkit-text-fill-color: var(--app-text) !important;
            -webkit-box-shadow: 0 0 0 1000px rgba(13, 23, 42, 0.92) inset !important;
            transition: background-color 9999s ease-out 0s !important;
        }}

        .stSelectbox svg,
        [data-baseweb="select"] svg {{
            color: var(--app-text) !important;
            fill: var(--app-text) !important;
        }}

        [data-baseweb="popover"],
        [data-baseweb="menu"],
        [role="listbox"] {{
            background: rgba(10, 18, 33, 0.98) !important;
            border: 1px solid var(--app-border) !important;
            border-radius: 12px !important;
            color: var(--app-text) !important;
        }}

        [role="option"]:hover {{
            background: rgba(55, 208, 255, 0.2) !important;
        }}

        [data-testid="stExpander"] > details {{
            border: 1px solid var(--app-border) !important;
            border-radius: 12px !important;
            background: rgba(8, 14, 26, 0.86) !important;
        }}

        [data-testid="stExpander"] > details > summary,
        [data-testid="stExpander"] > details[open] > summary,
        [data-testid="stExpander"] > details > summary:hover,
        [data-testid="stExpander"] > details > summary:focus-visible {{
            background: transparent !important;
            color: var(--app-text) !important;
            -webkit-text-fill-color: var(--app-text) !important;
        }}

        [data-testid="stExpander"] > details > summary * {{
            color: var(--app-text) !important;
            -webkit-text-fill-color: var(--app-text) !important;
            background: transparent !important;
        }}

        [data-testid="stDivider"] {{
            border-color: rgba(66, 88, 126, 0.55) !important;
        }}

        .ow-hero-wrap {{
            border: 1px solid var(--app-border);
            border-radius: 18px;
            padding: 18px 20px;
            background:
                linear-gradient(120deg, rgba(23, 38, 68, 0.92), rgba(10, 16, 30, 0.94));
            box-shadow: 0 18px 28px rgba(2, 8, 22, 0.42);
            margin-bottom: 0.8rem;
        }}

        .ow-hero-badge {{
            display: inline-block;
            border-radius: 999px;
            border: 1px solid rgba(86, 216, 255, 0.45);
            color: #a6f0ff;
            padding: 4px 10px;
            font-size: 0.72rem;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            margin-bottom: 8px;
            font-weight: 700;
        }}

        .ow-hero-title {{
            font-size: clamp(1.45rem, 1.2rem + 1.2vw, 2.2rem);
            font-weight: 800;
            color: #f3f8ff;
            line-height: 1.15;
            margin: 0 0 6px 0;
        }}

        .ow-hero-sub {{
            color: var(--app-muted);
            margin: 0;
            font-size: 0.95rem;
        }}

        @media (max-width: 900px) {{
            .block-container {{
                padding-top: 1.2rem !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_hero(title: str, subtitle: str, badge: str = "Overwatch 2 Meta") -> None:
    st.markdown(
        f"""
        <section class="ow-hero-wrap">
            <div class="ow-hero-badge">{html.escape(badge)}</div>
            <h1 class="ow-hero-title">{html.escape(title)}</h1>
            <p class="ow-hero-sub">{html.escape(subtitle)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_top_navigation(current_page: str) -> None:
    nav_items = [
        ("main", "메인", "main.py"),
        ("pick_win", "픽률·승률", "pages/1_pick_win_distribution.py"),
        ("role_rank", "포지션 비중", "pages/2_role_rank_share.py"),
    ]

    cols = st.columns(len(nav_items))
    for col, (page_key, label, target) in zip(cols, nav_items):
        with col:
            is_current = page_key == current_page
            clicked = st.button(
                label,
                key=f"nav_{current_page}_{page_key}",
                use_container_width=True,
                type="primary" if is_current else "secondary",
                disabled=is_current,
            )
            if clicked and hasattr(st, "switch_page"):
                st.switch_page(target)
