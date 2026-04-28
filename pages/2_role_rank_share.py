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
    html, body {{
        color-scheme: dark !important;
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
    /* Inputs: selectbox + search */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] input,
    .stSelectbox [data-baseweb="select"] span,
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] input,
    div[data-baseweb="select"] span {{
        background-color: var(--app-surface) !important;
        color: var(--app-text) !important;
        -webkit-text-fill-color: var(--app-text) !important;
        border: 1px solid var(--app-border) !important;
        border-radius: 12px !important;
        opacity: 1 !important;
    }}
    .stSelectbox svg,
    div[data-baseweb="select"] svg {{
        fill: var(--app-text) !important;
        color: var(--app-text) !important;
    }}
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder,
    .stSelectbox input::placeholder,
    div[data-baseweb="select"] input::placeholder {{
        color: var(--app-text-muted) !important;
        -webkit-text-fill-color: var(--app-text-muted) !important;
        opacity: 1 !important;
    }}
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus,
    .stSelectbox [data-baseweb="select"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within {{
        border-color: var(--app-accent) !important;
        box-shadow: 0 0 0 1px var(--app-accent) !important;
    }}

    /* Dropdown popup and options */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"],
    ul[role="listbox"] {{
        background-color: var(--app-surface) !important;
        color: var(--app-text) !important;
        border: 1px solid var(--app-border) !important;
        border-radius: 12px !important;
        opacity: 1 !important;
    }}
    [role="option"],
    li[role="option"] {{
        background-color: var(--app-surface) !important;
        color: var(--app-text) !important;
        -webkit-text-fill-color: var(--app-text) !important;
    }}
    [role="option"]:hover,
    li[role="option"]:hover {{
        background-color: rgba(59, 130, 246, 0.2) !important;
    }}
    [role="option"][aria-selected="true"],
    li[role="option"][aria-selected="true"] {{
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
        font-size: 1.02rem !important;
        font-weight: 700 !important;
        line-height: 1.35 !important;
        color: var(--app-text) !important;
        -webkit-text-fill-color: var(--app-text) !important;
        background-color: transparent !important;
    }}
    [data-testid="stExpander"] details[open] > summary,
    [data-testid="stExpander"] details[open] > summary * {{
        color: var(--app-text) !important;
        -webkit-text-fill-color: var(--app-text) !important;
        background-color: transparent !important;
    }}
    [data-testid="stExpander"] summary:hover {{
        background-color: rgba(59, 130, 246, 0.1) !important;
    }}
    [data-testid="stExpander"] summary p {{
        margin: 0 !important;
        line-height: 1.35 !important;
    }}
    [data-testid="stIconMaterial"],
    [data-testid="stExpander"] summary span[class*="material"] {{
        font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
    }}
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {{
        margin-top: 0 !important;
        margin-bottom: 0.55rem !important;
        line-height: 1.65 !important;
    }}
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p:last-child {{
        margin-bottom: 0 !important;
    }}
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] li {{
        margin-bottom: 0.35rem !important;
        line-height: 1.65 !important;
    }}
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] li:last-child {{
        margin-bottom: 0 !important;
    }}
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] ul,
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] ol {{
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-left: 1.4rem !important;
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

st.divider()

with st.expander("이 페이지는 어떤 정보를 보여주나요?"):
    st.markdown(
        """- **역할별 랭크 비중** 차트는 선택한 티어에서 각 포지션(돌격·공격·지원) 영웅들이 `S / A / B / C` 랭크에 얼마나 분포하는지 보여줍니다.
- 원형 차트 안의 숫자는 해당 랭크가 해당 포지션 전체 영웅 수 대비 차지하는 **비율(%)**입니다.
- 랭크는 메인 페이지와 동일한 기준(승률 Z점수 + 픽률 로그 Z점수 기반 종합 점수)으로 산정됩니다.
- 티어 드롭다운을 변경하면 해당 티어 기준 분포로 즉시 갱신됩니다."""
    )

with st.expander("차트 해석 가이드"):
    st.markdown(
        """**S·A 비율이 높은 포지션** → 현재 메타에서 강세인 포지션입니다. 해당 포지션 영웅 픽을 우선 고려하세요.

**C 비율이 높은 포지션** → 성능 편차가 크거나 전반적으로 하향세인 포지션입니다. 영웅 선택에 주의가 필요합니다.

**티어별 비교 팁**
- 낮은 티어(브론즈·실버)와 높은 티어(마스터·그랜드마스터)의 분포 차이를 비교하면 **숙련도 의존성**이 높은 포지션을 파악할 수 있습니다.
- 예: 공격 포지션이 낮은 티어에선 C가 많고 높은 티어에선 S·A가 많다면, 조작 난이도가 높은 영웅이 집중된 포지션일 가능성이 높습니다."""
    )
