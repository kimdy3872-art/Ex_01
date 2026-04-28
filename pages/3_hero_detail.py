import streamlit as st
import pandas as pd
import urllib.request
import json
import html
import os
import re

st.set_page_config(page_title="영웅 상세", layout="wide")

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
    header[data-testid="stHeader"] {{
        display: none !important;
    }}
    .block-container {{
        padding-top: 3.35rem !important;
        padding-bottom: 1.8rem !important;
    }}
    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}
    [data-testid="stSidebarCollapseButton"],
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
    }}
    .stButton > button[kind="secondary"],
    button[data-testid="stBaseButton-secondary"] {{
        background-color: #0b1220 !important;
        color: var(--app-text) !important;
        border: 1px solid var(--app-border) !important;
        -webkit-text-fill-color: var(--app-text) !important;
    }}
    .stButton > button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {{
        background-color: var(--app-accent) !important;
        border-color: #60a5fa !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}
    .stButton > button[kind="primary"]:disabled,
    button[data-testid="stBaseButton-primary"]:disabled {{
        opacity: 1 !important;
    }}
    .stSelectbox [data-baseweb="select"] > div,
    div[data-baseweb="select"] > div {{
        background-color: var(--app-surface) !important;
        color: var(--app-text) !important;
        border: 1px solid var(--app-border) !important;
        border-radius: 12px !important;
    }}
    [data-testid="stExpander"] > details {{
        background-color: rgba(15, 23, 42, 0.55) !important;
        border: 1px solid var(--app-border) !important;
        border-radius: 12px !important;
    }}
    [data-testid="stExpander"] summary {{
        font-size: 1.01rem !important;
        font-weight: 700 !important;
        line-height: 1.3 !important;
    }}
    [data-testid="stExpander"] summary p {{
        margin: 0 !important;
    }}
    [data-testid="stExpander"] [data-testid="stIconMaterial"] {{
        display: none !important;
    }}
    [data-testid="stExpander"] summary span[class*="material"],
    [data-testid="stIconMaterial"] {{
        font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

ROLE_LABELS = {
    "Tank": "돌격",
    "Damage": "공격",
    "Support": "지원",
    "Unknown": "미분류",
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


def translate_role_name(role_name):
    return ROLE_LABELS.get(str(role_name), str(role_name))


def translate_tier_name(tier_name):
    return TIER_LABELS.get(str(tier_name), str(tier_name))


def clear_detail_query_params():
    for key in ["hero", "tier", "source"]:
        if key in st.query_params:
            del st.query_params[key]
    for key in ["detail_hero", "detail_tier", "detail_source"]:
        if key in st.session_state:
            del st.session_state[key]


def render_top_navigation():
    nav_items = [
        ("main", "🏠 메인", "main.py"),
        ("pick_win", "🚀 픽률/승률 분포", "pages/1_pick_win_distribution.py"),
        ("role_rank", "💡 역할별 랭크 비중", "pages/2_role_rank_share.py"),
    ]
    nav_cols = st.columns(len(nav_items))
    for col, (_, label, target) in zip(nav_cols, nav_items):
        with col:
            if st.button(label, key=f"top_nav_detail_{target}", use_container_width=True, type="secondary"):
                clear_detail_query_params()
                if hasattr(st, "switch_page"):
                    st.switch_page(target)


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

    for col in ["win_rate", "pick_rate", "total_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


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
    "바스티온": "Bastion",
    "바티스트": "Baptiste",
    "벤처": "Venture",
    "브리기테": "Brigitte",
    "소전": "Sojourn",
    "솔저: 76": "Soldier: 76",
    "솜브라": "Sombra",
    "시그마": "Sigma",
    "시메트라": "Symmetra",
    "아나": "Ana",
    "애쉬": "Ashe",
    "에코": "Echo",
    "오리사": "Orisa",
    "위도우메이커": "Widowmaker",
    "윈스턴": "Winston",
    "일리아리": "Illari",
    "자리야": "Zarya",
    "정커퀸": "Junker Queen",
    "정크랫": "Junkrat",
    "젠야타": "Zenyatta",
    "주노": "Juno",
    "캐서디": "Cassidy",
    "키리코": "Kiriko",
    "토르비욘": "Torbjörn",
    "트레이서": "Tracer",
    "파라": "Pharah",
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


PERK_DATA_PATH = "overwatch_hero_perks.csv"
DEFAULT_PERK_IMAGE_URL = "https://dummyimage.com/48x48/1f2937/94a3b8.png&text=Perk"


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


st.title("🧾 영웅 상세 페이지")
render_top_navigation()
st.markdown("<div style='height: 0.35rem;'></div>", unsafe_allow_html=True)

hero_from_query = st.session_state.get("detail_hero") or st.query_params.get("hero")
if isinstance(hero_from_query, list):
    hero_from_query = hero_from_query[0] if hero_from_query else None

if not hero_from_query:
    st.warning("영웅이 선택되지 않았습니다. 메인 또는 분포 페이지에서 영웅을 선택해 주세요.")
    st.stop()

hero_name = str(hero_from_query)

df_raw = load_data()
hero_summary_df = df_raw[(df_raw["hero"].astype(str) == hero_name) & (df_raw["map"] == "all-maps")].copy()

if hero_summary_df.empty:
    st.warning("선택한 영웅 데이터를 찾을 수 없습니다.")
    st.stop()

tier_candidates = sorted(
    t for t in hero_summary_df["data_tier"].dropna().astype(str).unique().tolist()
    if t != "All"
)
if "All" not in tier_candidates:
    tier_candidates = ["All"] + tier_candidates
query_tier = str(st.query_params.get("tier", "Gold"))
query_tier = str(st.session_state.get("detail_tier") or query_tier)
default_tier = query_tier if query_tier in tier_candidates else ("Gold" if "Gold" in tier_candidates else tier_candidates[0])

tier_col, _ = st.columns([1.25, 3.75])
with tier_col:
    selected_tier = st.selectbox(
        "티어",
        tier_candidates,
        index=tier_candidates.index(default_tier),
        format_func=translate_tier_name,
    )

hero_tier_df = hero_summary_df[hero_summary_df["data_tier"] == selected_tier].copy()
if hero_tier_df.empty:
    hero_row = hero_summary_df.sort_values("total_score", ascending=False).iloc[0]
else:
    hero_row = hero_tier_df.sort_values("total_score", ascending=False).iloc[0]

left_col, right_col = st.columns([1, 2.5], gap="large")

with left_col:
    image_url = get_hero_image_url(hero_name) or "https://dummyimage.com/320x320/1f2937/f8fafc.png&text=Hero"
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
        ">{html.escape(translate_role_name(str(hero_row.get("role", "Unknown"))))}</div>
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

    hero_map_df = df_raw[
        (df_raw["hero"].astype(str) == hero_name)
        & (df_raw["map"] != "all-maps")
        & (df_raw["data_tier"].astype(str) == selected_tier)
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
            badge = (
                f'<div style="position:absolute;top:8px;right:100px;background:{badge_color}22;border:1px solid {badge_color}88;border-radius:999px;padding:2px 8px;color:{badge_color};font-size:0.68rem;font-weight:700;letter-spacing:0.05em;">{badge_label}</div>'
                if badge_label else ""
            )
            return (
                f'<div style="position:relative;width:100%;height:72px;border-radius:10px;background-image:url(\'{bg_image}\');background-size:cover;background-position:center;margin-bottom:10px;box-shadow:0 4px 10px rgba(0,0,0,0.4);overflow:hidden;">'
                f'<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(15,23,42,0.95) 0%,rgba(15,23,42,0.55) 55%,rgba(15,23,42,0.82) 100%);"></div>'
                f'{badge}'
                f'<div style="position:absolute;top:50%;left:18px;transform:translateY(-50%);">'
                f'<div style="color:#f8fafc;font-size:1.05rem;font-weight:700;letter-spacing:0.01em;line-height:1.2;">{m_name}</div>'
                f'<div style="color:#94a3b8;font-size:0.78rem;margin-top:2px;">픽률 {p_rate:.1f}%</div>'
                f'</div>'
                f'<div style="position:absolute;top:50%;right:18px;transform:translateY(-50%);text-align:right;">'
                f'<div style="color:{rate_color};font-size:1.35rem;font-weight:800;line-height:1.1;">{w_rate:.1f}%</div>'
                f'<div style="color:#94a3b8;font-size:0.75rem;margin-top:2px;">승률</div>'
                f'</div></div>'
            )

        top_win_df = hero_map_df.nlargest(2, "win_rate")
        top_pick_df = hero_map_df.nlargest(2, "pick_rate")

        st.markdown("**🏆 Top Winrate**")
        st.markdown(
            "".join(make_map_card(row, "TOP WIN", "#34d399") for _, row in top_win_df.iterrows()),
            unsafe_allow_html=True,
        )

        st.markdown("**📈 Top Pickrate**")
        st.markdown(
            "".join(make_map_card(row, "TOP PICK", "#60a5fa") for _, row in top_pick_df.iterrows()),
            unsafe_allow_html=True,
        )

        with st.expander(f"모두 보기 ({len(hero_map_df)}개 전장)"):
            st.markdown(
                "".join(make_map_card(row) for _, row in hero_map_df.iterrows()),
                unsafe_allow_html=True,
            )
