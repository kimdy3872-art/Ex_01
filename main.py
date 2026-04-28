import streamlit as st
import plotly.express as px
import pandas as pd
import urllib.request
import urllib.parse
import json
import html

# -------------------------------------------------
# 1. 페이지 설정
# -------------------------------------------------
st.set_page_config(
    page_title="오버워치 2 경쟁전 메타 분석기",
    layout="wide"
)

GLOBAL_BG_COLOR = "#0f172a"
GLOBAL_TEXT_COLOR = "#f8fafc"
GLOBAL_SURFACE_COLOR = "#111827"
GLOBAL_SURFACE_ALT_COLOR = "#0b1220"
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
        --app-surface-alt: {GLOBAL_SURFACE_ALT_COLOR};
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
    body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMarkdownContainer"],
    [data-testid="stText"],
    p, span, div, label, li, a, summary,
    input, textarea, select, button,
    table, th, td {{
        font-family: var(--app-font) !important;
    }}
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-icons,
    [class*="material-symbols"],
    [class*="material-icons"] {{
        font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
    }}
    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {{
        background-color: var(--app-bg) !important;
        color: var(--app-text) !important;
    }}
    header[data-testid="stHeader"] {{
        display: none !important;
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
    .block-container {{
        padding-top: 3.5rem !important;
        padding-bottom: 2rem !important;
    }}
    h1, h2, h3, h4 {{
        letter-spacing: -0.01em;
        line-height: 1.25;
    }}
    h1 {{ font-size: clamp(1.65rem, 1.55rem + 0.6vw, 2.15rem) !important; font-weight: 800 !important; }}
    h2 {{ font-size: clamp(1.35rem, 1.25rem + 0.45vw, 1.8rem) !important; font-weight: 750 !important; }}
    h3 {{ font-size: clamp(1.05rem, 1.0rem + 0.3vw, 1.35rem) !important; font-weight: 700 !important; }}
    body {{
        font-size: 0.95rem;
    }}
    [data-testid="stToolbar"] {{
        background-color: transparent !important;
    }}
    [data-testid="stMarkdownContainer"],
    [data-testid="stText"],
    label,
    .stSelectbox label,
    .stTextInput label {{
        color: var(--app-text) !important;
    }}

    /* Buttons */
    .stButton > button,
    div[data-testid="stButton"] > button,
    button[data-testid^="stBaseButton-"] {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.1s ease;
        background-image: none !important;
        text-shadow: none !important;
        min-height: 40px !important;
        opacity: 1 !important;
    }}

    /* Unselected filter button (Streamlit secondary type) */
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"],
    .stButton > button[data-testid="stBaseButton-secondary"],
    button[data-testid="baseButton-secondary"],
    button[data-testid="stBaseButton-secondary"],
    div[data-testid="stButton"] > button:not([kind="primary"]):not([data-testid$="-primary"]) {{
        background-color: var(--app-surface-alt) !important;
        color: var(--app-text) !important;
        -webkit-text-fill-color: var(--app-text) !important;
        border: 1px solid var(--app-border) !important;
        opacity: 1 !important;
        filter: none !important;
    }}
    .stButton > button[kind="secondary"] *,
    .stButton > button[data-testid="baseButton-secondary"] *,
    .stButton > button[data-testid="stBaseButton-secondary"] *,
    button[data-testid="baseButton-secondary"] *,
    button[data-testid="stBaseButton-secondary"] *,
    div[data-testid="stButton"] > button:not([kind="primary"]):not([data-testid$="-primary"]) * {{
        color: var(--app-text) !important;
        -webkit-text-fill-color: var(--app-text) !important;
        opacity: 1 !important;
    }}
    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="baseButton-secondary"]:hover,
    .stButton > button[data-testid="stBaseButton-secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover,
    button[data-testid="stBaseButton-secondary"]:hover,
    div[data-testid="stButton"] > button:not([kind="primary"]):not([data-testid$="-primary"]):hover {{
        background-color: var(--app-surface) !important;
        color: var(--app-text) !important;
        -webkit-text-fill-color: var(--app-text) !important;
        border-color: #1e293b !important;
        opacity: 1 !important;
    }}
    .stButton > button[kind="secondary"]:focus-visible,
    .stButton > button[data-testid="baseButton-secondary"]:focus-visible,
    .stButton > button[data-testid="stBaseButton-secondary"]:focus-visible,
    button[data-testid="baseButton-secondary"]:focus-visible,
    button[data-testid="stBaseButton-secondary"]:focus-visible,
    div[data-testid="stButton"] > button:not([kind="primary"]):not([data-testid$="-primary"]):focus-visible {{
        outline: 2px solid #334155 !important;
        outline-offset: 1px !important;
    }}
    .stButton > button:focus-visible {{
        outline: 2px solid #60a5fa !important;
        outline-offset: 1px !important;
    }}
    .stButton > button:active {{
        transform: translateY(1px);
    }}

    /* Selected filter button (Streamlit primary type) */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"],
    .stButton > button[data-testid="stBaseButton-primary"],
    button[data-testid="baseButton-primary"],
    button[data-testid="stBaseButton-primary"] {{
        background-color: var(--app-accent) !important;
        border-color: #60a5fa !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        box-shadow: 0 0 0 1px rgba(96, 165, 250, 0.35), 0 0 0 4px rgba(59, 130, 246, 0.2) !important;
    }}
    .stButton > button[kind="primary"] *,
    .stButton > button[data-testid="baseButton-primary"] *,
    .stButton > button[data-testid="stBaseButton-primary"] *,
    button[data-testid="baseButton-primary"] *,
    button[data-testid="stBaseButton-primary"] * {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }}
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover,
    button[data-testid="baseButton-primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {{
        background-color: #2563eb !important;
        border-color: #60a5fa !important;
    }}

    /* Inputs: sort selectbox + hero search */
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

    /* Selectbox input focus state */
    .stSelectbox [data-baseweb="select"]:focus-within,
    div[data-baseweb="select"]:focus-within {{
        border-color: var(--app-accent) !important;
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
    }}\n    
    /* Checkbox & Radio */
    [data-testid="stCheckbox"] label,
    [data-testid="stRadio"] label {{
        color: var(--app-text) !important;
    }}
    input[type="checkbox"],
    input[type="radio"] {{
        accent-color: var(--app-accent) !important;
    }}
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
    [data-testid="stExpander"] summary p {{
        margin: 0 !important;
        line-height: 1.35 !important;
    }}
    [data-testid="stIconMaterial"],
    [data-testid="stExpander"] summary span[class*="material"] {{
        font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
    }}
    [data-testid="stDialog"] [role="dialog"] {{
        border-radius: 16px !important;
        border: 1px solid var(--app-border) !important;
        background: linear-gradient(180deg, #0b1428 0%, #0a1222 100%) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎮 오버워치 2 경쟁전 메타 분석기")


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


render_top_navigation("main")
st.markdown("<div style='height: 0.4rem;'></div>", unsafe_allow_html=True)

# -------------------------------------------------
# 2. 데이터 로드
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("overwatch_competitive_stats.csv")
    if "update_date" in df.columns and not df.empty:
        df["update_date"] = df["update_date"].astype(str)
        latest_date = df["update_date"].max()
        df = df[df["update_date"] == latest_date].copy()

    if "map" not in df.columns:
        df["map"] = "all-maps"
    if "map_name" not in df.columns:
        df["map_name"] = df["map"]
    if "role" not in df.columns:
        df["role"] = "Unknown"

    numeric_cols = ["win_rate", "pick_rate", "win_rate_z", "pick_rate_log", "pick_rate_z", "total_score"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

df_raw = load_data()

if "update_date" in df_raw.columns and not df_raw.empty:
    base_date = str(df_raw["update_date"].iloc[0])
else:
    base_date = "-"

st.caption(f"데이터 기준일: {base_date}")

# -------------------------------------------------
# 3. 메인 상단 필터
# -------------------------------------------------
roles = ["Tank", "Damage", "Support"]
tiers = ["All", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster"]
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
ROLE_LABELS = {
    "All": "전체 포지션",
    "Tank": "돌격",
    "Damage": "공격",
    "Support": "지원",
}


def translate_tier_name(tier_name):
    return TIER_LABELS.get(tier_name, tier_name)


def translate_role_name(role_name):
    return ROLE_LABELS.get(role_name, role_name)


def render_metric_card(title, value, accent_color="#0b69ff"):
    safe_title = html.escape(str(title))
    safe_value = html.escape(str(value))
    return f"""
    <div style="
        background: linear-gradient(180deg, {GLOBAL_SURFACE_COLOR} 0%, #0f1b31 100%);
        border: 1px solid {GLOBAL_BORDER_COLOR};
        border-radius: 16px;
        padding: 16px 18px;
        min-height: 122px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    ">
        <div style="
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            background: rgba(59, 130, 246, 0.12);
            border: 1px solid rgba(59, 130, 246, 0.3);
            color: #bfdbfe;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            margin-bottom: 12px;
        ">{safe_title}</div>
        <div style="
            color: {accent_color};
            font-size: 1.62rem;
            font-weight: 800;
            line-height: 1.2;
            word-break: keep-all;
        ">{safe_value}</div>
    </div>
    """

if "selected_tier" not in st.session_state:
    st.session_state.selected_tier = "Gold"
if "selected_role" not in st.session_state:
    st.session_state.selected_role = "All"
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "종합 점수"
if "search_hero" not in st.session_state:
    st.session_state.search_hero = ""


def reset_filters():
    st.session_state.selected_tier = "Gold"
    st.session_state.selected_role = "All"
    st.session_state.sort_by = "종합 점수"
    st.session_state.search_hero = ""

with st.container():
    c1, c2, c3, c4, c5 = st.columns([1.05, 1.0, 0.95, 1.65, 0.55])

    with c1:
        selected_tier = st.selectbox(
            "티어",
            tiers,
            key="selected_tier",
            format_func=translate_tier_name,
            label_visibility="collapsed",
            placeholder="티어",
        )
    with c2:
        selected_role = st.selectbox(
            "포지션",
            ["All"] + roles,
            key="selected_role",
            format_func=translate_role_name,
            label_visibility="collapsed",
            placeholder="포지션",
        )
    with c3:
        sort_by = st.selectbox(
            "정렬",
            ["종합 점수", "승률", "픽률"],
            key="sort_by",
            label_visibility="collapsed",
            placeholder="정렬",
        )
    with c4:
        search_hero = st.text_input(
            "영웅 검색",
            key="search_hero",
            placeholder="영웅 검색",
            label_visibility="collapsed",
        )
    with c5:
        st.button("초기화", use_container_width=True, on_click=reset_filters)

st.divider()

# -------------------------------------------------
# 4. 데이터 필터링
# -------------------------------------------------
if selected_role == "All":
    selected_roles = roles
else:
    selected_roles = [selected_role]

df_filtered = df_raw[
    (df_raw["data_tier"] == selected_tier) &
    (df_raw["role"].isin(selected_roles)) &
    (df_raw["map"] == "all-maps")
].copy()

if search_hero:
    df_filtered = df_filtered[
        df_filtered["hero"].str.contains(search_hero, case=False, na=False)
    ].copy()

if "pick_rate_z" in df_filtered.columns and "win_rate_z" in df_filtered.columns:
    pick_z = pd.to_numeric(df_filtered["pick_rate_z"], errors="coerce")
    win_z = pd.to_numeric(df_filtered["win_rate_z"], errors="coerce")
    df_filtered["is_master"] = (pick_z <= -0.5) & (win_z >= 0.5)
else:
    df_filtered["is_master"] = False

# -------------------------------------------------
# 5. 데이터 준비
# -------------------------------------------------
if not df_filtered.empty:
    df_filtered["rank"] = pd.Categorical(
        df_filtered["rank"],
        categories=["C", "B", "A", "S"],
        ordered=True
    )

    # 시각화 크기 보정
    if "total_score" in df_filtered.columns:
        df_filtered["display_size"] = (
            df_filtered["total_score"]
            - df_filtered["total_score"].min()
            + 1
        )
    else:
        df_filtered["display_size"] = 1

# -------------------------------------------------
# 8. 영웅 초상화 URL 매핑
# -------------------------------------------------
@st.cache_data
def load_hero_portrait_map():
    url = "https://overfast-api.tekrop.fr/heroes"
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            heroes = json.load(resp)
    except Exception:
        return {}
    return {
        hero.get("name"): hero.get("portrait")
        for hero in heroes
        if hero.get("name") and hero.get("portrait")
    }

HERO_NAME_TO_API_NAME = {
    "D.VA": "D.Va",
    "겐지": "Genji",
    "도미나": "Domina",
    "둠피스트": "Doomfist",
    "라마트라": "Ramattra",
    "라이프위버": "Lifeweaver",
    "라인하르트": "Reinhardt",
    "레킹볼": "Wrecking Ball",
    "로드호그": "Roadhog",
    "루시우": "Lúcio",
    "리퍼": "Reaper",
    "마우가": "Mauga",
    "메르시": "Mercy",
    "메이": "Mei",
    "모이라": "Moira",
    "미즈키": "Mizuki",
    "바스티온": "Bastion",
    "바티스트": "Baptiste",
    "벤데타": "Vendetta",
    "벤처": "Venture",
    "브리기테": "Brigitte",
    "소전": "Sojourn",
    "솔저: 76": "Soldier: 76",
    "솜브라": "Sombra",
    "시그마": "Sigma",
    "시메트라": "Symmetra",
    "시에라": "Sierra",
    "아나": "Ana",
    "안란": "Anran",
    "애쉬": "Ashe",
    "에코": "Echo",
    "엠레": "Emre",
    "오리사": "Orisa",
    "우양": "Wuyang",
    "위도우메이커": "Widowmaker",
    "윈스턴": "Winston",
    "일리아리": "Illari",
    "자리야": "Zarya",
    "정커퀸": "Junker Queen",
    "정크랫": "Junkrat",
    "제트팩 캣": "Jetpack Cat",
    "젠야타": "Zenyatta",
    "주노": "Juno",
    "캐서디": "Cassidy",
    "키리코": "Kiriko",
    "토르비욘": "Torbjörn",
    "트레이서": "Tracer",
    "파라": "Pharah",
    "프레야": "Freja",
    "한조": "Hanzo",
    "해저드": "Hazard",
}


def get_hero_image_url(hero_name):
    api_name = HERO_NAME_TO_API_NAME.get(hero_name, hero_name)
    portrait_map = load_hero_portrait_map()
    return portrait_map.get(api_name)


def render_rank_table_html(df):
    rank_color_map = {
        "S": "#ef4444",
        "A": "#f59e0b",
        "B": "#22c55e",
        "C": "#60a5fa",
    }

    styles = """
    <style>
    .overwatch-table {border-collapse: collapse; width: 100%; font-family: "Apple SD Gothic Neo", "Segoe UI", sans-serif;}
    .overwatch-table th, .overwatch-table td {border: 1px solid __GLOBAL_BORDER_COLOR__; padding: 11px 13px; vertical-align: middle; color: __GLOBAL_TEXT_COLOR__; font-size: 0.92rem;}
    .overwatch-table {background-color: __GLOBAL_BG_COLOR__;}
    .overwatch-table th {background-color: __GLOBAL_SURFACE_COLOR__; color: #f8fafc; font-weight: 700; font-size: 0.9rem; letter-spacing: 0.03em; text-transform: uppercase;}
    .overwatch-table tbody tr:hover {background-color: #111827;}
    .overwatch-table .portrait-cell {width: 98px; text-align: center;}
    .overwatch-table .portrait-cell img {border-radius: 16px; width: 68px; height: 68px; object-fit: cover;}
    .overwatch-table .hero-cell {text-align: left; font-weight: 700; color: __GLOBAL_TEXT_COLOR__;}
    .overwatch-table .role-cell {text-align: center; color: __GLOBAL_TEXT_COLOR__;}
    .overwatch-table .rate-cell {text-align: left; min-width: 180px;}
    .overwatch-table .rank-cell {text-align: center; font-weight: 900; font-size: 1.38rem; line-height: 1; letter-spacing: 0.01em; padding: 4px 8px; color: __GLOBAL_TEXT_COLOR__;}
    .artisan-badge {display: inline-block; margin-left: 8px; padding: 2px 7px; border-radius: 999px; font-size: 0.68rem; font-weight: 800; letter-spacing: 0.02em; vertical-align: middle;}
    .artisan-strong {background: rgba(250, 204, 21, 0.14); color: #fde68a; border: 1px solid rgba(250, 204, 21, 0.36);}
    .rate-bar {background: #1f2937; border-radius: 999px; height: 10px; overflow: hidden; margin-top: 6px;}
    .rate-fill {height: 100%; border-radius: 999px;}
    .rate-fill.pick {background: #60a5fa;}
    .rate-fill.win {background: #34d399;}
    .rate-text {font-size: 0.85rem; color: __GLOBAL_TEXT_COLOR__; margin-top: 6px;}
    .header-note {font-size: 0.9rem; color: #cbd5e1; margin-bottom: 8px;}
    </style>
    """
    styles = styles.replace("__GLOBAL_BG_COLOR__", GLOBAL_BG_COLOR)
    styles = styles.replace("__GLOBAL_TEXT_COLOR__", GLOBAL_TEXT_COLOR)
    styles = styles.replace("__GLOBAL_BORDER_COLOR__", GLOBAL_BORDER_COLOR)
    styles = styles.replace("__GLOBAL_SURFACE_COLOR__", GLOBAL_SURFACE_COLOR)
    rows = []
    for _, row in df.iterrows():
        hero_name = str(row["hero"])
        hero = html.escape(hero_name)
        hero_query = urllib.parse.quote(hero_name, safe="")
        hero_link = (
            f"<a href='?hero={hero_query}' target='_self' "
            f"style='color:{GLOBAL_TEXT_COLOR}; text-decoration: underline; text-underline-offset: 3px;'>"
            f"{hero}</a>"
        )
        is_master = bool(row.get("is_master", False))
        badge_html = ""
        if is_master:
            badge_html = "<span class='artisan-badge artisan-strong'>장인</span>"
        hero_cell_html = f"{hero_link}{badge_html}"
        role = html.escape(translate_role_name(str(row["role"])))
        win_rate = f"{row['win_rate']:.1f}%"
        pick_rate = f"{row['pick_rate']:.1f}%"
        rank = html.escape(str(row["rank"]))
        rank_color = rank_color_map.get(str(row["rank"]), GLOBAL_TEXT_COLOR)
        hero_url = get_hero_image_url(row["hero"])
        img_html = f'<img src="{hero_url}"/>' if hero_url else "-"

        pick_html = (
            f"<div class='rate-bar'><div class='rate-fill pick' style='width:{min(max(row['pick_rate'],0),100)}%'></div></div>"
            f"<div class='rate-text'>{pick_rate}</div>"
        )
        win_html = (
            f"<div class='rate-bar'><div class='rate-fill win' style='width:{min(max(row['win_rate'],0),100)}%'></div></div>"
            f"<div class='rate-text'>{win_rate}</div>"
        )
        rows.append(
            f"<tr><td class='portrait-cell'>{img_html}</td><td class='hero-cell'>{hero_cell_html}</td><td class='role-cell'>{role}</td><td class='rate-cell'>{win_html}</td><td class='rate-cell'>{pick_html}</td><td class='rank-cell' style='color:{rank_color};'>{rank}</td></tr>"
        )
    table_html = (
        styles
        + "<table class='overwatch-table'><thead><tr>"
        + "<th>Portrait</th><th>영웅</th><th>포지션</th><th>승률</th><th>픽률</th><th>랭크</th>"
        + "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )
    return table_html

# -------------------------------------------------
# 9. 데이터 없는 경우 처리
# -------------------------------------------------
if df_filtered.empty:

    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    st.stop()

# -------------------------------------------------
# 9. 상단 요약 지표
# -------------------------------------------------
top_hero = df_filtered.sort_values(
    "total_score",
    ascending=False
).iloc[0]["hero"]

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(
        render_metric_card(
            f"{translate_tier_name(selected_tier)} 1위 영웅",
            top_hero,
            accent_color="#f8fafc",
        ),
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        render_metric_card(
            "해당 구간 평균 승률",
            f"{df_filtered['win_rate'].mean():.1f}%",
            accent_color="#34d399",
        ),
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        render_metric_card(
            "분석 대상 영웅 수",
            f"{len(df_filtered)}명",
            accent_color="#60a5fa",
        ),
        unsafe_allow_html=True,
    )

st.divider()

st.subheader("🏆 영웅 랭크 순위표")
st.caption("영웅 이름을 클릭하면 상세 페이지로 이동합니다.")

sort_col = {
    "종합 점수": "total_score",
    "승률": "win_rate",
    "픽률": "pick_rate"
}.get(sort_by, "total_score")

display_df = df_filtered.sort_values(
    sort_col,
    ascending=False
)[[
    "hero",
    "role",
    "win_rate",
    "pick_rate",
    "rank",
    "is_master",
]]

if not display_df.empty:
    st.markdown(render_rank_table_html(display_df), unsafe_allow_html=True)
else:
    st.info("선택한 조건에 해당하는 영웅이 없습니다.")

with st.expander("랭크는 어떻게 산정되나요?"):
    st.markdown(
        """
        - 랭크는 티어/포지션/전장(all-maps) 필터 기준의 종합 지표로 산정됩니다.
        - 기본적으로 승률과 픽률 기반 점수를 함께 반영해 `S > A > B > C`로 구간화합니다.
        - 표의 정렬 기준(종합 점수/승률/픽률)을 바꾸면 같은 집합 내 우선순위가 달라집니다.
        - 데이터는 최신 수집일 기준으로만 비교됩니다.
        """
    )

with st.expander("장인챔프는 뭔가요?"):
    st.markdown(
        """
        - 장인챔프는 **낮은 픽률 대비 높은 승률**을 보이는 영웅입니다.
        - 현재 기준: `pick_rate_z <= -0.5` and `win_rate_z >= 0.5`
        - 즉, 평균보다 덜 선택되지만 성과가 높은 영웅을 뜻합니다.
        """
    )

hero_from_query = st.query_params.get("hero")
if isinstance(hero_from_query, list):
    hero_from_query = hero_from_query[0] if hero_from_query else None

if hero_from_query:
    hero_from_query = urllib.parse.unquote(str(hero_from_query))
    hero_row = display_df[display_df["hero"].astype(str) == hero_from_query]
    if not hero_row.empty:
        st.session_state.detail_hero = hero_from_query
        st.session_state.detail_tier = selected_tier
        st.session_state.detail_source = "main"
        if hasattr(st, "switch_page"):
            st.switch_page("pages/3_hero_detail.py")
