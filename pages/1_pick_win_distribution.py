import streamlit as st
import plotly.express as px
import pandas as pd
from ui import (
    GLOBAL_BG_COLOR,
    GLOBAL_FONT_FAMILY,
    GLOBAL_TEXT_COLOR,
    apply_global_theme,
    render_page_hero,
    render_top_navigation,
)

st.set_page_config(page_title="픽률/승률 분포", layout="wide")
apply_global_theme()


@st.cache_data
def load_data():
    df = pd.read_csv("overwatch_competitive_stats.csv")

    def is_degenerate_snapshot(snapshot_df):
        if snapshot_df.empty:
            return True

        map_rows = snapshot_df[snapshot_df["map"].astype(str) != "all-maps"].copy()
        if map_rows.empty:
            return False

        map_rows["win_rate"] = pd.to_numeric(map_rows.get("win_rate"), errors="coerce")
        map_rows["pick_rate"] = pd.to_numeric(map_rows.get("pick_rate"), errors="coerce")

        group_cols = ["hero", "data_tier"]
        win_nunique = map_rows.groupby(group_cols)["win_rate"].nunique(dropna=True)
        pick_nunique = map_rows.groupby(group_cols)["pick_rate"].nunique(dropna=True)
        if win_nunique.empty or pick_nunique.empty:
            return False

        no_win_variance_ratio = (win_nunique <= 1).mean()
        no_pick_variance_ratio = (pick_nunique <= 1).mean()
        return no_win_variance_ratio >= 0.98 and no_pick_variance_ratio >= 0.98

    if "update_date" in df.columns and not df.empty:
        df["update_date"] = df["update_date"].astype(str)
        selected_date = None
        for candidate_date in sorted(df["update_date"].dropna().unique(), reverse=True):
            candidate_df = df[df["update_date"] == candidate_date].copy()
            if not is_degenerate_snapshot(candidate_df):
                selected_date = candidate_date
                break

        if selected_date is None:
            selected_date = df["update_date"].max()

        df = df[df["update_date"] == selected_date].copy()

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


render_page_hero(
    "픽률 vs 승률 분포",
    "영웅 메타 포지셔닝을 한 화면에서 확인하고, 점 클릭으로 상세 분석으로 이동합니다.",
    badge="Meta Positioning",
)
render_top_navigation("pick_win")
st.markdown("<div style='height: 0.25rem;'></div>", unsafe_allow_html=True)

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
