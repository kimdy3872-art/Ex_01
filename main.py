import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import urllib.request
import urllib.parse
import json
import html
import os
import re

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
    .stButton > button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.1s ease;
        background-image: none !important;
        text-shadow: none !important;
        min-height: 40px !important;
    }}

    /* Unselected filter button (Streamlit secondary type) */
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"] {{
        background-color: var(--app-surface-alt) !important;
        color: var(--app-text) !important;
        -webkit-text-fill-color: var(--app-text) !important;
        border: 1px solid var(--app-border) !important;
        opacity: 1 !important;
        filter: none !important;
    }}
    .stButton > button[kind="secondary"] *,
    .stButton > button[data-testid="baseButton-secondary"] * {{
        color: var(--app-text) !important;
        -webkit-text-fill-color: var(--app-text) !important;
        opacity: 1 !important;
    }}
    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="baseButton-secondary"]:hover {{
        background-color: var(--app-surface) !important;
        color: var(--app-text) !important;
        -webkit-text-fill-color: var(--app-text) !important;
        border-color: #1e293b !important;
        opacity: 1 !important;
    }}
    .stButton > button[kind="secondary"]:focus-visible,
    .stButton > button[data-testid="baseButton-secondary"]:focus-visible {{
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
    .stButton > button[kind="primary"] {{
        background-color: var(--app-accent) !important;
        border-color: #60a5fa !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        box-shadow: 0 0 0 1px rgba(96, 165, 250, 0.35), 0 0 0 4px rgba(59, 130, 246, 0.2) !important;
    }}
    .stButton > button[kind="primary"] * {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: #2563eb !important;
        border-color: #60a5fa !important;
    }}

    /* Inputs */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stSelectbox [data-baseweb="select"] > div {{
        background-color: var(--app-surface) !important;
        color: var(--app-text) !important;
        border: 1px solid var(--app-border) !important;
        border-radius: 12px !important;
    }}
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {{
        color: var(--app-text-muted) !important;
    }}
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {{
        border-color: var(--app-accent) !important;
        box-shadow: 0 0 0 1px var(--app-accent) !important;
    }}
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"] {{
        background-color: var(--app-surface) !important;
        color: var(--app-text) !important;
        border: 1px solid var(--app-border) !important;
    }}
    [role="option"] {{
        color: var(--app-text) !important;
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
    }}
    [data-testid="stExpander"] summary p {{
        margin: 0 !important;
        line-height: 1.35 !important;
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

if 'selected_tier' not in st.session_state:
    st.session_state.selected_tier = "Gold"
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = "All"

with st.container():
    st.write("### 🏆 티어 구간 선택")
    t_cols = st.columns(len(tiers))

    for i, tier_name in enumerate(tiers):
        with t_cols[i]:
            is_selected = (st.session_state.selected_tier == tier_name)
            tier_display_name = translate_tier_name(tier_name)
            btn_label = f"▶ {tier_display_name}" if is_selected else tier_display_name
            if st.button(
                btn_label,
                key=f"tier_btn_{tier_name}",
                use_container_width=True,
                help=f"{tier_name} 데이터 분석",
                type="primary" if is_selected else "secondary",
            ):
                if st.session_state.selected_tier != tier_name:
                    st.session_state.selected_tier = tier_name
                    st.rerun()

    role_filters = ["All"] + roles
    r_cols = st.columns(len(role_filters))
    for i, role_name in enumerate(role_filters):
        with r_cols[i]:
            is_selected = (st.session_state.selected_role == role_name)
            role_display_name = translate_role_name(role_name)
            btn_label = f"▶ {role_display_name}" if is_selected else role_display_name
            if st.button(
                btn_label,
                key=f"role_btn_{role_name}",
                use_container_width=True,
                help=f"{role_name} 포지션 데이터 분석",
                type="primary" if is_selected else "secondary",
            ):
                if st.session_state.selected_role != role_name:
                    st.session_state.selected_role = role_name
                    st.rerun()

    st.markdown("---")
    summary_col1, summary_col2 = st.columns([1, 1])
    with summary_col1:
        st.markdown(
            f"**선택된 티어:** <span style='color:{GLOBAL_ACCENT_COLOR}; font-weight:700;'>{translate_tier_name(st.session_state.selected_tier)}</span>",
            unsafe_allow_html=True,
        )
    with summary_col2:
        st.markdown(
            f"**선택된 포지션:** <span style='color:{GLOBAL_ACCENT_COLOR}; font-weight:700;'>{translate_role_name(st.session_state.selected_role)}</span>",
            unsafe_allow_html=True,
        )

    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        sort_by = st.selectbox("📊 정렬 기준", ["종합 점수", "승률", "픽률"])
    with f2:
        search_hero = st.text_input("🔍 영웅 검색")
    with f3:
        st.write("\n")

selected_tier = st.session_state.selected_tier
selected_role = st.session_state.selected_role
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


@st.cache_data
def load_map_image_map():
    url = "https://overfast-api.tekrop.fr/maps"
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            maps_data = json.load(resp)
    except Exception:
        return {}
    return {
        m.get("key", "").lower(): m.get("screenshot")
        for m in maps_data
        if m.get("key") and m.get("screenshot")
    }


MAP_ID_ALIAS = {
    "paraiso": "paraíso",
    "esperanca": "esperança",
}


def get_map_image_url(map_id):
    alias = MAP_ID_ALIAS.get(map_id, map_id)
    image_map = load_map_image_map()
    url = image_map.get(alias) or image_map.get(map_id)
    return url if url else f"https://dummyimage.com/600x100/1f2937/475569.png&text={map_id}"


DEFAULT_HERO_IMAGE_URL = "https://dummyimage.com/320x320/1f2937/f8fafc.png&text=Hero"
DEFAULT_PERK_IMAGE_URL = "https://dummyimage.com/48x48/1f2937/94a3b8.png&text=Perk"
PERK_DATA_PATH = "overwatch_hero_perks.csv"


def normalize_hero_key(hero_name):
    text = str(hero_name).strip().lower()
    return re.sub(r"[^0-9a-z가-힣]+", "", text)


@st.cache_data
def load_hero_perk_data():
    if not os.path.exists(PERK_DATA_PATH):
        return pd.DataFrame()

    try:
        df = pd.read_csv(PERK_DATA_PATH)
    except Exception:
        return pd.DataFrame()

    required_cols = {"hero", "perk_type", "perk_name", "pick_rate"}
    if not required_cols.issubset(df.columns):
        return pd.DataFrame()

    if "update_date" in df.columns and not df.empty:
        df["update_date"] = df["update_date"].astype(str)
        latest_date = df["update_date"].max()
        df = df[df["update_date"] == latest_date].copy()

    df["hero_norm"] = df["hero"].astype(str).map(normalize_hero_key)
    df["perk_type"] = df["perk_type"].astype(str).str.lower()
    df["pick_rate"] = pd.to_numeric(df["pick_rate"], errors="coerce")
    return df


def get_hero_perk_rows(hero_name):
    perks_df = load_hero_perk_data()
    if perks_df.empty:
        return {"minor": [], "major": []}

    hero_norm = normalize_hero_key(hero_name)
    hero_perks = perks_df[perks_df["hero_norm"] == hero_norm].copy()
    if hero_perks.empty:
        return {"minor": [], "major": []}

    hero_perks = hero_perks.sort_values("pick_rate", ascending=False)
    minor_rows = hero_perks[hero_perks["perk_type"] == "minor"].head(2).to_dict("records")
    major_rows = hero_perks[hero_perks["perk_type"] == "major"].head(2).to_dict("records")
    return {"minor": minor_rows, "major": major_rows}


@st.dialog("영웅 상세 정보", width="large")
def show_hero_detail_dialog(hero_name, hero_role, current_tier, data_df):
    left_col, right_col = st.columns([1, 2.5], gap="large")

    with left_col:
        image_url = get_hero_image_url(hero_name) or DEFAULT_HERO_IMAGE_URL
        st.markdown(
            f"""
            <div style="
                position: relative;
                width: 182px;
                padding: 10px;
                border-radius: 18px;
                background:
                    linear-gradient(180deg, rgba(248, 250, 252, 0.08) 0%, rgba(15, 23, 42, 0.92) 18%, rgba(2, 6, 23, 0.98) 100%);
                border: 1px solid #5b6b84;
                box-shadow:
                    0 14px 30px rgba(2, 6, 23, 0.62),
                    0 0 0 1px rgba(148, 163, 184, 0.18),
                    0 0 18px rgba(56, 189, 248, 0.24),
                    inset 0 1px 0 rgba(255, 255, 255, 0.22);
                margin-bottom: 12px;
                overflow: hidden;
            ">
                <div style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 36%;
                    background: linear-gradient(180deg, rgba(255,255,255,0.18) 0%, rgba(255,255,255,0.0) 100%);
                    pointer-events: none;
                "></div>
                <img src="{html.escape(image_url)}" style="
                    width: 162px;
                    height: 162px;
                    object-fit: cover;
                    border-radius: 12px;
                    border: 1px solid rgba(148, 163, 184, 0.45);
                    display: block;
                    box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.85);
                " />
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="
                font-family: {GLOBAL_FONT_FAMILY};
                font-size: 1.48rem;
                font-weight: 800;
                color: #e2ecff;
                letter-spacing: 0.02em;
                text-shadow: 0 1px 0 rgba(12, 18, 32, 0.8), 0 0 10px rgba(96, 165, 250, 0.2);
                line-height: 1.2;
                margin-top: 6px;
            ">{html.escape(str(hero_name))}</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="
                display: inline-block;
                font-family: {GLOBAL_FONT_FAMILY};
                font-size: 0.9rem;
                font-weight: 700;
                color: #bfdbfe;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                margin-top: 8px;
                background: linear-gradient(180deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
                border: 1px solid rgba(96, 165, 250, 0.45);
                border-radius: 999px;
                padding: 4px 10px;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.16);
            ">{html.escape(translate_role_name(hero_role))}</div>
            """,
            unsafe_allow_html=True,
        )

        perk_rows = get_hero_perk_rows(hero_name)

        def render_perk_line(perks, line_title, accent_color):
            if not perks:
                return (
                    f'<div style="margin-top:10px;padding:8px 10px;border:1px dashed #334155;border-radius:10px;color:#94a3b8;font-size:0.8rem;">'
                    f'{line_title}: 특전 데이터 없음'
                    f'</div>'
                )

            numeric_rates = pd.to_numeric(
                [perk.get("pick_rate") for perk in perks],
                errors="coerce",
            )
            best_idx = int(numeric_rates.argmax()) if len(numeric_rates) and pd.notna(numeric_rates).any() else -1

            cards = []
            for idx, perk in enumerate(perks):
                perk_name = html.escape(str(perk.get("perk_name", "-")))
                perk_rate = perk.get("pick_rate")
                if pd.notna(perk_rate):
                    perk_rate_text = f"{float(perk_rate):.0f}%"
                else:
                    perk_rate_text = "-"
                best_mark = "👍 " if idx == best_idx else ""

                perk_image_url = perk.get("perk_image_raw_url") or perk.get("perk_image_url") or DEFAULT_PERK_IMAGE_URL
                perk_image_url = html.escape(str(perk_image_url))

                cards.append(
                    f'<div style="display:flex;align-items:center;gap:8px;background:rgba(15,23,42,0.72);border:1px solid #334155;border-radius:10px;padding:6px 8px;margin-top:6px;">'
                    f'<img src="{perk_image_url}" style="width:28px;height:28px;object-fit:cover;border-radius:6px;border:1px solid #475569;flex-shrink:0;" />'
                    f'<div style="flex:1;color:#e2e8f0;font-size:0.82rem;font-weight:700;line-height:1.2;">{perk_name}</div>'
                    f'<div style="color:{accent_color};font-size:0.82rem;font-weight:800;min-width:56px;text-align:right;">{best_mark}{perk_rate_text}</div>'
                    f'</div>'
                )

            return (
                f'<div style="margin-top:10px;">'
                f'<div style="font-size:0.72rem;font-weight:800;letter-spacing:0.04em;color:{accent_color};text-transform:uppercase;">{line_title}</div>'
                f'{"".join(cards)}'
                f'</div>'
            )

        perk_html = (
            '<div style="margin-top:12px;">'
            + render_perk_line(perk_rows["minor"], "Minor Perks", "#67e8f9")
            + render_perk_line(perk_rows["major"], "Major Perks", "#fbbf24")
            + '</div>'
        )
        st.markdown(perk_html, unsafe_allow_html=True)

    with right_col:
        st.subheader("🗺️ 전장별 승률")

        hero_map_df = data_df[
            (data_df["hero"] == hero_name) &
            (data_df["map"] != "all-maps") &
            (data_df["data_tier"] == current_tier)
        ].sort_values("win_rate", ascending=False)

        if hero_map_df.empty:
            st.info("이 티어의 전장별 데이터가 없습니다.")
        else:
            def make_map_card(row, badge_label=None, badge_color="#34d399"):
                m_id = str(row["map"])
                m_name = html.escape(str(row.get("map_name", m_id)))
                w_rate = float(row["win_rate"])
                p_rate = float(row["pick_rate"])
                rate_color = "#34d399" if w_rate >= 50 else "#f87171"
                bg_image = html.escape(get_map_image_url(m_id))
                badge = (f'<div style="position:absolute;top:8px;right:100px;background:{badge_color}22;border:1px solid {badge_color}88;border-radius:999px;padding:2px 8px;color:{badge_color};font-size:0.68rem;font-weight:700;letter-spacing:0.05em;">{badge_label}</div>' if badge_label else "")
                return (f'<div style="position:relative;width:100%;height:72px;border-radius:10px;background-image:url(\'{bg_image}\');background-size:cover;background-position:center;margin-bottom:10px;box-shadow:0 4px 10px rgba(0,0,0,0.4);overflow:hidden;">'
                        f'<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(15,23,42,0.95) 0%,rgba(15,23,42,0.55) 55%,rgba(15,23,42,0.82) 100%);"></div>'
                        f'{badge}'
                        f'<div style="position:absolute;top:50%;left:18px;transform:translateY(-50%);">'
                        f'<div style="color:#f8fafc;font-size:1.05rem;font-weight:700;letter-spacing:0.01em;line-height:1.2;">{m_name}</div>'
                        f'<div style="color:#94a3b8;font-size:0.78rem;margin-top:2px;">픽률 {p_rate:.1f}%</div>'
                        f'</div>'
                        f'<div style="position:absolute;top:50%;right:18px;transform:translateY(-50%);text-align:right;">'
                        f'<div style="color:{rate_color};font-size:1.35rem;font-weight:800;line-height:1.1;">{w_rate:.1f}%</div>'
                        f'<div style="color:#94a3b8;font-size:0.75rem;margin-top:2px;">승률</div>'
                        f'</div></div>')

            top_win_df  = hero_map_df.nlargest(2, "win_rate")
            top_pick_df = hero_map_df.nlargest(2, "pick_rate")

            st.markdown("**🏆 Top Winrate**")
            st.markdown("".join(make_map_card(row, "TOP WIN", "#34d399") for _, row in top_win_df.iterrows()), unsafe_allow_html=True)

            st.markdown("**📈 Top Pickrate**")
            st.markdown("".join(make_map_card(row, "TOP PICK", "#60a5fa") for _, row in top_pick_df.iterrows()), unsafe_allow_html=True)

            with st.expander(f"모두 보기 ({len(hero_map_df)}개 전장)"):
                st.markdown("".join(make_map_card(row) for _, row in hero_map_df.iterrows()), unsafe_allow_html=True)


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
            f"<tr><td class='portrait-cell'>{img_html}</td><td class='hero-cell'>{hero_link}</td><td class='role-cell'>{role}</td><td class='rate-cell'>{win_html}</td><td class='rate-cell'>{pick_html}</td><td class='rank-cell' style='color:{rank_color};'>{rank}</td></tr>"
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

# -------------------------------------------------
# 11. 메인 시각화
# -------------------------------------------------

st.subheader("🚀 픽률 vs 승률 분포")
pick_center = df_filtered["pick_rate"].mean()
win_center = df_filtered["win_rate"].mean()
x_min = df_filtered["pick_rate"].min()
x_max = df_filtered["pick_rate"].max()
y_min = df_filtered["win_rate"].min()
y_max = df_filtered["win_rate"].max()

fig = px.scatter(
    df_filtered,
    x="pick_rate",
    y="win_rate",
    color="rank",
    size="display_size",
    hover_name="hero",
    text="hero",
    category_orders={
        "rank": ["S", "A", "B", "C"]
    },
    color_discrete_map={
        "S": "#FF4B4B",
        "A": "#FFA500",
        "B": "#2ECC71",
        "C": "#3498DB"
    },
    labels={
        "pick_rate": "픽률 (%)",
        "win_rate": "승률 (%)",
        "rank": "영웅 랭크"
    }
)

fig.add_shape(
    type="line",
    x0=pick_center,
    x1=pick_center,
    y0=y_min,
    y1=y_max,
    line=dict(color="gray", width=1, dash="dash"),
    xref="x",
    yref="y"
)
fig.add_shape(
    type="line",
    x0=x_min,
    x1=x_max,
    y0=win_center,
    y1=win_center,
    line=dict(color="gray", width=1, dash="dash"),
    xref="x",
    yref="y"
)

fig.add_annotation(
    x=x_max,
    y=win_center,
    text="Popular",
    showarrow=False,
    xanchor="right",
    yanchor="bottom",
    font=dict(color="#4b5563", size=12),
    bgcolor="rgba(255,255,255,0.8)"
)
fig.add_annotation(
    x=pick_center,
    y=y_max,
    text="Strong",
    showarrow=False,
    xanchor="left",
    yanchor="top",
    font=dict(color="#4b5563", size=12),
    bgcolor="rgba(255,255,255,0.8)"
)
fig.add_annotation(
    x=x_max,
    y=y_max,
    text="Strong + Popular",
    showarrow=False,
    xanchor="right",
    yanchor="top",
    font=dict(color="#111827", size=12, family="Arial, sans-serif", weight="bold"),
    bgcolor="rgba(255,255,255,0.9)"
)

fig.update_traces(
    textposition="top center",
    marker=dict(line=dict(width=1, color="black")),
    hovertemplate="<b>%{customdata}</b><br>픽률: %{x:.2f}%<br>승률: %{y:.2f}%<extra></extra>",
    customdata=df_filtered["hero"]
)
fig.update_layout(
    font=dict(family=GLOBAL_FONT_FAMILY, size=13, color=GLOBAL_TEXT_COLOR),
    paper_bgcolor=GLOBAL_BG_COLOR,
    plot_bgcolor=GLOBAL_BG_COLOR,
    dragmode=False,
    hovermode='closest'
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"staticPlot": True}
)

st.subheader("💡 역할별 랭크 비중")
df_role_base = df_raw[
    (df_raw["data_tier"] == selected_tier) &
    (df_raw["map"] == "all-maps")
].copy()

role_rank_distribution = (
    df_role_base
    .groupby(["role", "rank"])["hero"]
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
for col, role_name in zip(role_cols, roles):
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
            title=f"{role_label}",
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

st.subheader("🏆 영웅 랭크 순위표 (S~C)")

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
    "rank"
]]

if not display_df.empty:
    st.markdown(render_rank_table_html(display_df), unsafe_allow_html=True)
    st.caption("영웅 이름을 클릭하면 상세 팝업이 열립니다.")
else:
    st.info("선택한 조건에 해당하는 영웅이 없습니다.")

hero_from_query = st.query_params.get("hero")
if isinstance(hero_from_query, list):
    hero_from_query = hero_from_query[0] if hero_from_query else None

if hero_from_query:
    hero_from_query = urllib.parse.unquote(str(hero_from_query))
    if "hero" in st.query_params:
        del st.query_params["hero"]
    hero_row = display_df[display_df["hero"].astype(str) == hero_from_query]
    if not hero_row.empty:
        show_hero_detail_dialog(
            hero_from_query,
            str(hero_row.iloc[0]["role"]),
            selected_tier,
            df_raw,
        )
