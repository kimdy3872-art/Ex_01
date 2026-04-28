import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="픽률/승률 분포", layout="wide")

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
    
    /* Selectbox & Dropdowns */
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

    for col in ["win_rate", "pick_rate", "win_rate_z", "pick_rate_z", "total_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def get_selected_tier(df):
    tier_options = ["All"]
    if "data_tier" in df.columns:
        raw_tiers = set(df["data_tier"].dropna().astype(str).unique().tolist())
        raw_tiers.discard("All")
        preferred_order = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster"]
        ordered_tiers = [t for t in preferred_order if t in raw_tiers]
        extra_tiers = sorted(t for t in raw_tiers if t not in preferred_order)
        tier_options.extend(ordered_tiers + extra_tiers)
    default_tier = "Gold" if "Gold" in tier_options else tier_options[0]
    return st.selectbox(
        "티어",
        tier_options,
        index=tier_options.index(default_tier),
        format_func=translate_tier_name,
    )


def get_selected_role(df):
    roles = ["All", "Tank", "Damage", "Support"]
    valid_roles = [r for r in roles if r == "All" or r in df["role"].dropna().unique().tolist()]
    return st.selectbox("포지션", valid_roles, index=0, format_func=translate_role_name)


ROLE_LABELS = {
    "All": "전체 포지션",
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


def extract_selected_hero(event_data):
    if not event_data:
        return None

    points = []
    if isinstance(event_data, dict):
        points = event_data.get("selection", {}).get("points", [])
    elif hasattr(event_data, "selection") and hasattr(event_data.selection, "points"):
        points = event_data.selection.points

    if not points:
        return None

    first = points[0]
    custom_data = first.get("customdata") if isinstance(first, dict) else None
    if isinstance(custom_data, (list, tuple)) and custom_data:
        return str(custom_data[0])

    if isinstance(first, dict) and first.get("hovertext"):
        return str(first.get("hovertext"))

    return None


st.title("🚀 픽률 vs 승률 분포")


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


render_top_navigation("pick_win")
st.markdown("<div style='height: 0.4rem;'></div>", unsafe_allow_html=True)

raw_df = load_data()

f1, f2 = st.columns([1.0, 1.0])
with f1:
    selected_tier = get_selected_tier(raw_df)
with f2:
    selected_role = get_selected_role(raw_df)

filtered_df = raw_df[(raw_df["data_tier"] == selected_tier) & (raw_df["map"] == "all-maps")].copy()

if selected_role != "All":
    filtered_df = filtered_df[filtered_df["role"] == selected_role].copy()

if filtered_df.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    st.stop()

if "pick_rate_z" in filtered_df.columns and "win_rate_z" in filtered_df.columns:
    pick_z = pd.to_numeric(filtered_df["pick_rate_z"], errors="coerce")
    win_z = pd.to_numeric(filtered_df["win_rate_z"], errors="coerce")
    filtered_df["is_master"] = (pick_z <= -0.5) & (win_z >= 0.5)
else:
    filtered_df["is_master"] = False

filtered_df["display_size"] = filtered_df["total_score"] - filtered_df["total_score"].min() + 1
filtered_df["role_display"] = filtered_df["role"].map(translate_role_name)
filtered_df["master_label"] = filtered_df["is_master"].map(lambda x: "장인" if x else "일반")
filtered_df["hero_label"] = filtered_df.apply(
    lambda r: f"★ {r['hero']} (장인)" if r["is_master"] else str(r["hero"]),
    axis=1,
)

pick_center = filtered_df["pick_rate"].mean()
win_center = filtered_df["win_rate"].mean()
x_min = filtered_df["pick_rate"].min()
x_max = filtered_df["pick_rate"].max()
y_min = filtered_df["win_rate"].min()
y_max = filtered_df["win_rate"].max()

fig = px.scatter(
    filtered_df,
    x="pick_rate",
    y="win_rate",
    color="rank",
    size="display_size",
    hover_name="hero",
    text="hero_label",
    custom_data=["hero", "role_display", "rank", "master_label", "is_master"],
    category_orders={"rank": ["S", "A", "B", "C"]},
    color_discrete_map={
        "S": "#FF4B4B",
        "A": "#FFA500",
        "B": "#2ECC71",
        "C": "#3498DB",
    },
    labels={
        "pick_rate": "픽률 (%)",
        "win_rate": "승률 (%)",
        "rank": "영웅 랭크",
    },
)

fig.add_shape(
    type="line",
    x0=pick_center,
    x1=pick_center,
    y0=y_min,
    y1=y_max,
    line=dict(color="gray", width=1, dash="dash"),
    xref="x",
    yref="y",
)
fig.add_shape(
    type="line",
    x0=x_min,
    x1=x_max,
    y0=win_center,
    y1=win_center,
    line=dict(color="gray", width=1, dash="dash"),
    xref="x",
    yref="y",
)

fig.add_annotation(
    x=x_max,
    y=win_center,
    text="Popular",
    showarrow=False,
    xanchor="right",
    yanchor="bottom",
    font=dict(color="#4b5563", size=12),
    bgcolor="rgba(255,255,255,0.8)",
)
fig.add_annotation(
    x=pick_center,
    y=y_max,
    text="Strong",
    showarrow=False,
    xanchor="left",
    yanchor="top",
    font=dict(color="#4b5563", size=12),
    bgcolor="rgba(255,255,255,0.8)",
)
fig.add_annotation(
    x=x_max,
    y=y_max,
    text="Strong + Popular",
    showarrow=False,
    xanchor="right",
    yanchor="top",
    font=dict(color="#111827", size=12, family="Arial, sans-serif"),
    bgcolor="rgba(255,255,255,0.9)",
)

fig.update_traces(
    textposition="top center",
    marker=dict(line=dict(width=1, color="black")),
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "포지션: %{customdata[1]}<br>"
        "랭크: %{customdata[2]}<br>"
        "분류: %{customdata[3]}<br>"
        "픽률: %{x:.2f}%<br>"
        "승률: %{y:.2f}%<extra></extra>"
    ),
)

for trace in fig.data:
    line_widths = []
    line_colors = []
    marker_opacity = []
    customdata = trace.customdata if hasattr(trace, "customdata") else []
    for cd in customdata:
        is_master = bool(cd[4]) if len(cd) > 4 else False
        line_widths.append(3.0 if is_master else 0.8)
        line_colors.append("#f8fafc" if is_master else "rgba(148,163,184,0.35)")
        marker_opacity.append(1.0 if is_master else 0.42)
    trace.marker.line.width = line_widths
    trace.marker.line.color = line_colors
    trace.marker.opacity = marker_opacity

fig.update_layout(
    font=dict(family=GLOBAL_FONT_FAMILY, size=13, color=GLOBAL_TEXT_COLOR),
    paper_bgcolor=GLOBAL_BG_COLOR,
    plot_bgcolor=GLOBAL_BG_COLOR,
    dragmode=False,
    clickmode="event+select",
    hovermode="closest",
)

master_count = int(filtered_df["is_master"].sum())
st.caption(
    f"장인 기준: 픽률 Z <= -0.5 and 승률 Z >= 0.5 | 현재 {master_count}명"
)
st.caption("산점도 점에 커서를 올리면 요약 정보가 표시되고, 점을 클릭하면 상세 페이지로 이동합니다.")

event = st.plotly_chart(
    fig,
    use_container_width=True,
    key="pick_win_scatter",
    on_select="rerun",
    selection_mode="points",
    config={"displayModeBar": False},
)

selected_hero = extract_selected_hero(event)
if selected_hero:
    st.session_state.detail_hero = str(selected_hero)
    st.session_state.detail_tier = selected_tier
    st.session_state.detail_source = "pick_win"
    if hasattr(st, "switch_page"):
        st.switch_page("pages/3_hero_detail.py")
