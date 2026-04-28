import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="역할별 랭크 비중", layout="wide")

GLOBAL_BG_COLOR = "#0f172a"
GLOBAL_TEXT_COLOR = "#f8fafc"
GLOBAL_SURFACE_COLOR = "#111827"
GLOBAL_BORDER_COLOR = "#334155"
GLOBAL_MUTED_TEXT_COLOR = "#94a3b8"
GLOBAL_ACCENT_COLOR = "#3b82f6"
GLOBAL_FONT_FAMILY = "'Pretendard Variable', 'Pretendard', 'Noto Sans KR', 'Apple SD Gothic Neo', 'Segoe UI', sans-serif"

st.markdown(
    f"""
    <style>
    :root,
    [data-theme="light"],
    [data-theme="dark"] {{
        color-scheme: dark !important;
        --app-bg: {GLOBAL_BG_COLOR};
        --app-surface: {GLOBAL_SURFACE_COLOR};
        --app-border: {GLOBAL_BORDER_COLOR};
        --app-text: {GLOBAL_TEXT_COLOR};
        --app-text-muted: {GLOBAL_MUTED_TEXT_COLOR};
        --app-accent: {GLOBAL_ACCENT_COLOR};
        --app-font: {GLOBAL_FONT_FAMILY};
        --primary-color: {GLOBAL_ACCENT_COLOR};
        --background-color: {GLOBAL_BG_COLOR};
        --secondary-background-color: {GLOBAL_SURFACE_COLOR};
        --text-color: {GLOBAL_TEXT_COLOR};
        --font: {GLOBAL_FONT_FAMILY};
    }}
    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {{
        background-color: var(--app-bg) !important;
        color: var(--app-text) !important;
    }}
    [data-testid="stSidebarNav"],
    [data-testid="stSidebar"],
    .sidebar,
    [aria-label="Sidebar"] {{
        display: none !important;
    }}
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarToggleButton"],
    button[aria-label="Open sidebar"],
    button[aria-label="Close sidebar"] {{
        display: none !important;
    }}
    body, .stApp, [data-testid="stMarkdownContainer"], [data-testid="stText"], p, span, div, label {{
        font-family: var(--app-font) !important;
    }}
    .stButton > button,
    div[data-testid="stButton"] > button,
    button[data-testid^="stBaseButton-"] {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        min-height: 40px !important;
        transition: background-color 0.2s ease, border-color 0.2s ease;
    }}
    .stButton > button[kind="secondary"],
    button[data-testid="stBaseButton-secondary"] {{
        background-color: #0b1220 !important;
        color: var(--app-text) !important;
        border: 1px solid var(--app-border) !important;
        -webkit-text-fill-color: var(--app-text) !important;
    }}
    .stButton > button[kind="secondary"]:hover,
    button[data-testid="stBaseButton-secondary"]:hover {{
        background-color: var(--app-surface) !important;
        border-color: #1e293b !important;
    }}
    .stButton > button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {{
        background-color: var(--app-accent) !important;
        border-color: #60a5fa !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        box-shadow: 0 0 0 1px rgba(96, 165, 250, 0.35), 0 0 0 4px rgba(59, 130, 246, 0.2) !important;
    }}
    .stButton > button[kind="primary"]:disabled,
    button[data-testid="stBaseButton-primary"]:disabled {{
        background-color: var(--app-accent) !important;
        border-color: #60a5fa !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
        filter: none !important;
    }}
    .stSelectbox [data-baseweb="select"] > div,
    div[data-baseweb="select"] > div,
    [data-baseweb="popover"] {{
        background-color: var(--app-surface) !important;
        color: var(--app-text) !important;
        border: 1px solid var(--app-border) !important;
        border-radius: 12px !important;
    }}
    .stSelectbox input,
    [data-baseweb="input"] input {{
        background-color: var(--app-surface) !important;
        color: var(--app-text) !important;
        caret-color: var(--app-accent) !important;
    }}
    .stSelectbox [data-baseweb="input"] input:focus,
    [data-baseweb="input"] input:focus {{
        background-color: var(--app-surface) !important;
        border-color: var(--app-accent) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }}
    [data-baseweb="popover"] [role="listbox"],
    [data-baseweb="popover"] [role="menu"] {{
        background-color: var(--app-surface) !important;
    }}
    [role="option"],
    [role="menuitem"] {{
        color: var(--app-text) !important;
    }}
    [role="option"]:hover,
    [role="menuitem"]:hover {{
        background-color: rgba(59, 130, 246, 0.2) !important;
    }}
    [role="option"][aria-selected="true"],
    [role="menuitem"][aria-selected="true"] {{
        background-color: rgba(59, 130, 246, 0.35) !important;
        color: var(--app-text) !important;
    }}
    
    /* Text Input */
    .stTextInput input {{
        background-color: var(--app-surface) !important;
        color: var(--app-text) !important;
        border: 1px solid var(--app-border) !important;
        border-radius: 12px !important;
        caret-color: var(--app-accent) !important;
    }}
    .stTextInput input:focus {{
        border-color: var(--app-accent) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }}
    
    /* Checkbox & Radio */
    [data-testid="stCheckbox"] label,
    [data-testid="stRadio"] label {{
        color: var(--app-text) !important;
    }}
    input[type="checkbox"],
    input[type="radio"] {{
        accent-color: var(--app-accent) !important;
    }}
    
    /* Expander */
    [data-testid="stExpander"] > details {{
        background-color: rgba(15, 23, 42, 0.55) !important;
        border: 1px solid var(--app-border) !important;
        border-radius: 12px !important;
    }}
    [data-testid="stExpander"] summary {{
        color: var(--app-text) !important;
    }}
    [data-testid="stExpander"] summary:hover {{
        background-color: rgba(59, 130, 246, 0.1) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

ROLE_LABELS = {
    "Tank": "돌격",
    "Damage": "공격",
    "Support": "지원",
}
TIER_LABELS = {
    "All": "전체 티어",
    "Bronze": "브론즈",
    "Silver": "실버",
    "Gold": "골드",
    "Platinum": "플래티넘",
    "Diamond": "다이아몬드",
    "Master": "마스터",
    "Grandmaster": "그랜드마스터",
}


@st.cache_data
def load_data():
    df = pd.read_csv("overwatch_competitive_stats.csv")
    if "update_date" in df.columns and not df.empty:
        df["update_date"] = df["update_date"].astype(str)
        latest_date = df["update_date"].max()
        df = df[df["update_date"] == latest_date].copy()

    if "map" not in df.columns:
        df["map"] = "all-maps"
    if "role" not in df.columns:
        df["role"] = "Unknown"

    return df


def translate_role_name(role_name):
    return ROLE_LABELS.get(role_name, role_name)


def translate_tier_name(tier_name):
    return TIER_LABELS.get(str(tier_name), str(tier_name))


def get_selected_tier(df):
    tier_options = ["All"]
    if "data_tier" in df.columns:
        dynamic_tiers = sorted(
            t for t in df["data_tier"].dropna().astype(str).unique().tolist()
            if t != "All"
        )
        tier_options.extend(dynamic_tiers)
    default_tier = "Gold" if "Gold" in tier_options else tier_options[0]
    return st.selectbox(
        "티어",
        tier_options,
        index=tier_options.index(default_tier),
        format_func=translate_tier_name,
    )


st.title("💡 역할별 랭크 비중")


def render_top_navigation(current_page):
    nav_items = [
        ("main", "🏠 메인", "main.py"),
        ("pick_win", "🚀 픽률/승률 분포", "pages/1_pick_win_distribution.py"),
        ("role_rank", "💡 역할별 랭크 비중", "pages/2_role_rank_share.py"),
    ]

    nav_cols = st.columns(len(nav_items))
    for col, (page_key, label, target) in zip(nav_cols, nav_items):
        with col:
            is_current = page_key == current_page
            clicked = st.button(
                label,
                key=f"top_nav_{current_page}_{page_key}",
                use_container_width=True,
                type="primary" if is_current else "secondary",
                disabled=is_current,
            )
            if clicked and hasattr(st, "switch_page"):
                st.switch_page(target)


render_top_navigation("role_rank")
st.markdown("<div style='height: 0.4rem;'></div>", unsafe_allow_html=True)

raw_df = load_data()
selected_tier = get_selected_tier(raw_df)

role_base_df = raw_df[(raw_df["data_tier"] == selected_tier) & (raw_df["map"] == "all-maps")].copy()

if role_base_df.empty:
    st.warning("선택한 티어의 데이터가 없습니다.")
    st.stop()

role_rank_distribution = (
    role_base_df.groupby(["role", "rank"])["hero"]
    .count()
    .reset_index(name="count")
)

pie_color_map = {
    "S": "#FF4B4B",
    "A": "#FFA500",
    "B": "#2ECC71",
    "C": "#3498DB",
}

role_cols = st.columns(3)
for col, role_name in zip(role_cols, ["Tank", "Damage", "Support"]):
    with col:
        role_label = translate_role_name(role_name)
        one_role = role_rank_distribution[role_rank_distribution["role"] == role_name].copy()

        if one_role.empty:
            st.info(f"{role_label} 데이터 없음")
            continue

        fig_role_pie = px.pie(
            one_role,
            names="rank",
            values="count",
            color="rank",
            hole=0.48,
            category_orders={"rank": ["S", "A", "B", "C"]},
            color_discrete_map=pie_color_map,
        )
        fig_role_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            textfont=dict(size=22, family=GLOBAL_FONT_FAMILY),
            hovertemplate=f"포지션: {role_label}<br>랭크: %{{label}}<br>비율: %{{percent}}<extra></extra>",
        )
        fig_role_pie.update_layout(
            title=role_label,
            title_x=0.5,
            margin=dict(l=10, r=10, t=45, b=10),
            showlegend=False,
            font=dict(family=GLOBAL_FONT_FAMILY, size=12, color=GLOBAL_TEXT_COLOR),
            paper_bgcolor=GLOBAL_BG_COLOR,
            plot_bgcolor=GLOBAL_BG_COLOR,
            dragmode=False,
        )
        st.plotly_chart(fig_role_pie, use_container_width=True, config={"staticPlot": True})
