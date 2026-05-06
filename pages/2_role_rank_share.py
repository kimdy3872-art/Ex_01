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

st.set_page_config(page_title="역할별 랭크 비중", layout="wide")
apply_global_theme()

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


render_page_hero(
    "역할별 랭크 비중",
    "티어별로 돌격·공격·지원 포지션의 랭크 구조를 직관적으로 비교합니다.",
    badge="Role Composition",
)
render_top_navigation("role_rank")
st.markdown("<div style='height: 0.25rem;'></div>", unsafe_allow_html=True)

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
        st.plotly_chart(
            fig_role_pie,
            use_container_width=True,
            config={"staticPlot": True},
        )

st.divider()

with st.expander("차트 해석 가이드"):
    st.markdown(
        """- 차트는 선택 티어 기준으로 각 포지션의 `S / A / B / C` 비율을 보여줍니다.
- 원형 내부 값은 해당 포지션 내 랭크 점유율(%)입니다.

- `S·A` 비율이 높은 포지션: 현재 메타 강세 구간일 가능성이 큽니다.
- `C` 비율이 높은 포지션: 성능 편차가 크거나 전반적으로 불리할 수 있습니다.

- 티어 간 분포 차이가 크면 숙련도 의존성이 높은 포지션일 수 있습니다.
- 랭크 산정 기준은 메인 페이지와 동일합니다."""
    )
