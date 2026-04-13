import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import urllib.request
import json
import html

# -------------------------------------------------
# 1. 페이지 설정
# -------------------------------------------------
st.set_page_config(
    page_title="오버워치 2 경쟁전 메타 분석기",
    layout="wide"
)

st.title("🎮 오버워치 2 경쟁전 메타 분석기")

# -------------------------------------------------
# 2. 데이터 로드
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("overwatch_competitive_stats.csv")
    return df

df_raw = load_data()

# -------------------------------------------------
# 3. 메인 상단 필터
# -------------------------------------------------
roles = ["Tank", "Damage", "Support"]
tiers = ["All", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster"]

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
            btn_label = f"▶ {tier_name}" if is_selected else tier_name
            if st.button(btn_label, key=f"tier_btn_{tier_name}", use_container_width=True, help=f"{tier_name} 데이터 분석"):
                st.session_state.selected_tier = tier_name

    role_filters = ["All"] + roles
    r_cols = st.columns(len(role_filters))
    for i, role_name in enumerate(role_filters):
        with r_cols[i]:
            is_selected = (st.session_state.selected_role == role_name)
            btn_label = f"▶ {role_name}" if is_selected else role_name
            if st.button(btn_label, key=f"role_btn_{role_name}", use_container_width=True, help=f"{role_name} 포지션 데이터 분석"):
                st.session_state.selected_role = role_name

    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        st.write(f"**선택된 포지션:** {st.session_state.selected_role}")
    with f2:
        sort_by = st.selectbox("📊 정렬 기준", ["종합 점수", "승률", "픽률"])
    with f3:
        search_hero = st.text_input("🔍 영웅 검색")

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
    (df_raw["role"].isin(selected_roles))
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
    styles = """
    <style>
    .overwatch-table {border-collapse: collapse; width: 100%;}
    .overwatch-table th, .overwatch-table td {border: 1px solid #ddd; padding: 8px; vertical-align: middle;}
    .overwatch-table th {background-color: #000; color: #fff; font-weight: 600;}
    .overwatch-table .portrait-cell {width: 88px; text-align: center;}
    .overwatch-table img {border-radius: 14px; display: block; margin: 0 auto; width: 64px; height: 64px; object-fit: cover;}
    .overwatch-table td.hero-cell {text-align: left; font-weight: 600;}
    .overwatch-table td:not(.portrait-cell) {padding: 10px 12px;}
    </style>
    """
    rows = []
    for _, row in df.iterrows():
        hero = html.escape(str(row["hero"]))
        role = html.escape(str(row["role"]))
        win_rate = f"{row['win_rate']:.1f}%"
        pick_rate = f"{row['pick_rate']:.1f}%"
        rank = html.escape(str(row["rank"]))
        hero_url = get_hero_image_url(row["hero"])
        img_html = f'<img src="{hero_url}" width="56"/>' if hero_url else "-"
        rows.append(
            f"<tr><td>{img_html}</td><td class='hero-cell'>{hero}</td><td>{role}</td><td>{win_rate}</td><td>{pick_rate}</td><td>{rank}</td></tr>"
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
    st.metric(f"{selected_tier} 1위 영웅", top_hero)

with m2:
    st.metric(
        "해당 구간 평균 승률",
        f"{df_filtered['win_rate'].mean():.1f}%"
    )

with m3:
    st.metric(
        "분석 대상 영웅 수",
        f"{len(df_filtered)}명"
    )

st.divider()

# -------------------------------------------------
# 11. 메인 시각화
# -------------------------------------------------

st.subheader("🚀 픽률 vs 승률 분포")

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

fig.update_traces(
    textposition="top center",
    marker=dict(line=dict(width=1, color="black"))
)

st.plotly_chart(
    fig,
    use_container_width=True
)

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
else:
    st.info("선택한 조건에 해당하는 영웅이 없습니다.")

# -------------------------------------------------
# 11. 포지션 메타 분석
# -------------------------------------------------
st.divider()

st.subheader("💡 역할별 랭크 비중")

role_rank_distribution = (
    df_raw
    .groupby(["role", "rank"])['hero']
    .count()
    .reset_index(name='count')
)

role_totals = (
    role_rank_distribution
    .groupby('role')['count']
    .transform('sum')
)

role_rank_distribution['percent'] = (
    role_rank_distribution['count'] / role_totals * 100
)

role_rank_distribution['label'] = (
    role_rank_distribution
    .apply(lambda row: f"{row['rank']}랭크 {row['percent']:.1f}%", axis=1)
)

fig_role_rank = px.bar(
    role_rank_distribution,
    x='role',
    y='percent',
    color='rank',
    text='label',
    category_orders={
        'role': ['Tank', 'Damage', 'Support'],
        'rank': ['C', 'B', 'A', 'S']
    },
    color_discrete_map={
        'S': '#FF4B4B',
        'A': '#FFA500',
        'B': '#2ECC71',
        'C': '#3498DB'
    },
    labels={
        'percent': '비율 (%)',
        'role': '포지션',
        'rank': '영웅 랭크'
    }
)

fig_role_rank.update_traces(
    textposition='inside',
    texttemplate='%{text}',
    hovertemplate='포지션: %{x}<br>영웅 랭크: %{customdata[0]}<br>비율: %{y:.1f}%<extra></extra>',
    customdata=role_rank_distribution[['rank']]
)
fig_role_rank.update_layout(
    barmode='stack',
    yaxis=dict(range=[0, 100], title='랭크 비중 (%)'),
    legend_title_text='영웅 랭크',
    uniformtext_minsize=10,
    uniformtext_mode='hide'
)
fig_role_rank.update_layout(legend_traceorder='normal')

st.plotly_chart(fig_role_rank, use_container_width=True)

st.write(
    '각 포지션 내에서 S/A/B/C 티어로 분류된 영웅 비중을 누적 막대 차트로 보여줍니다.'
)
