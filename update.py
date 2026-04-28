from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import numpy as np
import time
from time import perf_counter
from datetime import date
import os

# 1. 영웅별 포지션 매핑 딕셔너리
role_dict = {
    'D.VA': 'Tank', '라인하르트': 'Tank', '윈스턴': 'Tank', '자리야': 'Tank', 
    '오리사': 'Tank', '로드호그': 'Tank', '시그마': 'Tank', '레킹볼': 'Tank', 
    '둠피스트': 'Tank', '라마트라': 'Tank', '마우가': 'Tank', '도미나': 'Tank',
    '정커퀸': 'Tank', '해저드': 'Tank',
    '겐지': 'Damage', '트레이서': 'Damage', '리퍼': 'Damage', '파라': 'Damage', 
    '캐서디': 'Damage', '애쉬': 'Damage', '솔저: 76': 'Damage', '솜브라': 'Damage', 
    '위도우메이커': 'Damage', '한조': 'Damage', '메이': 'Damage', '정크랫': 'Damage', 
    '토르비욘': 'Damage', '바스티온': 'Damage', '시메트라': 'Damage', '에코': 'Damage', '소전': 'Damage',
    '시에라': 'Damage',
    '벤처': 'Damage', '벤데타': 'Damage', '안란': 'Damage', '엠레': 'Damage', '프레야': 'Damage',
    '메르시': 'Support', '아나': 'Support', '루시우': 'Support', '젠야타': 'Support', 
    '모이라': 'Support', '바티스트': 'Support', '브리기테': 'Support', '키리코': 'Support', 
    '라이프위버': 'Support', '일리아리': 'Support', '주노': 'Support', '미즈키': 'Support', '우양' : 'Support',
    '제트팩 캣': 'Support'
}

# 2. 티어 리스트 정의
tiers = ["All", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster & Champion"]

map_dict = {
    "all-maps": "전체 전장",

    # 푸시
    "colosseo": "콜로세오",
    "esperanca": "에스페란사",
    "runasapi": "루나사피",
    "new-queen-street": "뉴 퀸 스트리트",

    # 하이브리드
    "hollywood": "할리우드",
    "paraiso": "파라이수",
    "kings-row": "왕의 길",
    "eichenwalde": "아이헨발데",
    "blizzard-world": "블리자드 월드",
    "midtown": "미드타운",
    "numbani": "눔바니",

    # 플래시포인트
    "aatlis": "아틀리스",
    "suravasa": "수라바사",
    "new-junk-city": "뉴 정크 시티",

    # 호위
    "havana": "하바나",
    "junkertown": "정크타운",
    "circuit-royal": "서킷 로얄",
    "shambali-monastery": "샴발리 수도원",
    "rialto": "리알토",
    "dorado": "도라도",
    "watchpoint-gibraltar": "감시 기지: 지브롤터",
    "route-66": "66번 국도",

    # 쟁탈
    "ilios": "일리오스",
    "oasis": "오아시스",
    "samoa": "사모아",
    "busan": "부산",
    "lijiang-tower": "리장 타워",
    "nepal": "네팔",
    "antarctic-peninsula": "남극 반도"
}

STATS_COLUMNS = [
    'hero', 'role', 'data_tier', 'map', 'map_name', 'update_date',
    'win_rate', 'pick_rate', 'win_rate_z', 'pick_rate_log', 'pick_rate_z', 'total_score', 'rank',
]

DEFAULT_MAX_WORKERS = 2 if os.getenv("GITHUB_ACTIONS") == "true" else 4
MAX_WORKERS = int(os.getenv("MAX_WORKERS", str(DEFAULT_MAX_WORKERS)))
DRIVER_CREATE_RETRIES = 3
TASK_RETRIES = 2

def format_elapsed(seconds):
    total_seconds = int(round(seconds))
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f"{hours}시간 {minutes}분 {seconds}초"
    if minutes > 0:
        return f"{minutes}분 {seconds}초"
    return f"{seconds}초"

def build_chrome_options():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--remote-debugging-pipe")
    opts.add_argument("--window-size=1920,1080")
    return opts


def create_driver(max_retries=DRIVER_CREATE_RETRIES):
    """Create Chrome session with retries for CI renderer startup failures."""
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            opts = build_chrome_options()
            return webdriver.Chrome(options=opts)
        except (SessionNotCreatedException, WebDriverException) as exc:
            last_error = exc
            wait_sec = attempt * 2
            print(f"⚠️  드라이버 세션 생성 실패(시도 {attempt}/{max_retries}), {wait_sec}초 후 재시도")
            if attempt < max_retries:
                time.sleep(wait_sec)

    raise RuntimeError(f"Chrome 세션 생성 실패: {last_error}")

def normalize_dataset_for_scoring(df):
    valid_maps = set(map_dict.keys())

    if 'map' not in df.columns:
        df['map'] = 'all-maps'

    df = df[df['map'].isin(valid_maps)].copy()
    df['map_name'] = df['map'].map(map_dict)
    return df


def scrape_data(driver, tier_name, map_id):
    """기존 드라이버로 특정 티어 + 전장 데이터 수집"""
    url = (f"https://overwatch.blizzard.com/ko-kr/rates/"
           f"?input=PC&map={map_id}&region=Asia&role=All&rq=2&tier={tier_name}")
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hero-name")))
        time.sleep(2)

        script = """
        let data = [];
        let names    = document.querySelectorAll('.hero-name');
        let winrates  = document.querySelectorAll('.winrate-cell');
        let pickrates = document.querySelectorAll('.pickrate-cell');
        for (let i = 0; i < names.length; i++) {
            data.push({
                'hero':      names[i].innerText.trim(),
                'win_rate':  winrates[i]  ? winrates[i].innerText  : '0%',
                'pick_rate': pickrates[i] ? pickrates[i].innerText : '0%'
            });
        }
        return data;
        """
        hero_list = driver.execute_script(script)
        df = pd.DataFrame(hero_list)

        if not df.empty:
            df['role'] = df['hero'].map(role_dict)
            df['data_tier'] = tier_name
            if tier_name in ["Grandmaster % Champion", "Grandmaster & Champion"]:
                df['data_tier'] = 'Grandmaster'
            df['map'] = map_id
            df['map_name'] = df['map'].map(map_dict)
            df['update_date'] = str(date.today())
        return df

    except Exception as e:
        print(f"❌ {tier_name} / {map_id} 에러: {e}")
        return pd.DataFrame()

def scrape_task(task):
    tier_name, map_id = task
    for attempt in range(1, TASK_RETRIES + 1):
        driver = None
        try:
            driver = create_driver()
            df = scrape_data(driver, tier_name, map_id)
            missing = []
            if not df.empty:
                missing = df[df['role'].isna()]['hero'].unique().tolist()
            if df.empty and attempt < TASK_RETRIES:
                print(f"⚠️  {tier_name} / {map_id} 빈 결과(시도 {attempt}/{TASK_RETRIES}), 재시도")
                time.sleep(attempt)
                continue
            return {
                'tier_name': tier_name,
                'map_id': map_id,
                'df': df,
                'missing': missing,
            }
        except Exception as exc:
            if attempt < TASK_RETRIES:
                print(f"⚠️  {tier_name} / {map_id} 작업 실패(시도 {attempt}/{TASK_RETRIES}), 재시도: {exc}")
                time.sleep(attempt * 2)
                continue
            print(f"❌ {tier_name} / {map_id} 최종 실패: {exc}")
            return {
                'tier_name': tier_name,
                'map_id': map_id,
                'df': pd.DataFrame(),
                'missing': [],
            }
        finally:
            if driver is not None:
                driver.quit()

def main():
    started_at = perf_counter()
    stats_csv_path = 'overwatch_competitive_stats.csv'
    map_ids = list(map_dict.keys())
    print(f"🗺️  전장 {len(map_ids)}개: {map_ids}")

    tasks = [(tier_name, map_id) for map_id in map_ids for tier_name in tiers]
    total = len(tasks)
    print(f"🧵 병렬 수집 시작: worker={MAX_WORKERS}, task={total}")

    final_list = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(scrape_task, task): task for task in tasks}
        for done, future in enumerate(as_completed(futures), start=1):
            tier_name, map_id = futures[future]
            print(f"🚀 [{done}/{total}] {tier_name} / {map_id} 완료")
            result = future.result()
            if result['missing']:
                print(f"⚠️  누락 영웅: {result['missing']}")
            if not result['df'].empty:
                final_list.append(result['df'])

    if not final_list:
        print("❌ 수집된 데이터가 없습니다.")
        return

    # 데이터 통합
    full_df = pd.concat(final_list, ignore_index=True)

    # 숫자 변환
    full_df['win_rate']  = full_df['win_rate'].str.replace('%', '', regex=False).replace('--', '0').astype(float)
    full_df['pick_rate'] = full_df['pick_rate'].str.replace('%', '', regex=False).replace('--', '0').astype(float)

    # 랭크 계산
    def safe_zscore(series):
        std = series.std()
        if std == 0 or pd.isna(std):
            return pd.Series([0] * len(series), index=series.index)
        return (series - series.mean()) / std

    group_key = ['data_tier', 'map']
    full_df['win_rate_z']    = full_df.groupby(group_key)['win_rate'].transform(safe_zscore)
    full_df['pick_rate_log'] = np.log1p(full_df['pick_rate'])
    full_df['pick_rate_z']   = full_df.groupby(group_key)['pick_rate_log'].transform(safe_zscore)
    full_df['total_score']   = full_df['win_rate_z'] * 0.6 + full_df['pick_rate_z'] * 0.4

    def assign_rank(scores):
        if len(scores) >= 4:
            return pd.qcut(scores, q=4, labels=['C', 'B', 'A', 'S'], duplicates='drop')
        return pd.Series(['A'] * len(scores), index=scores.index)

    full_df['rank'] = full_df.groupby(group_key)['total_score'].transform(assign_rank)
    full_df = normalize_dataset_for_scoring(full_df)
    full_df = full_df.reindex(columns=STATS_COLUMNS)

    today = str(date.today())

    if os.path.exists(stats_csv_path):
        existing_df = pd.read_csv(stats_csv_path)

        if 'update_date' in existing_df.columns and not existing_df.empty:
            latest_date = existing_df['update_date'].astype(str).max()
            latest_df = existing_df[existing_df['update_date'].astype(str) == latest_date].copy()

            str_cols = ['hero', 'data_tier', 'map']
            num_cols = ['win_rate', 'pick_rate']

            new_str = full_df[str_cols].astype(str).reset_index(drop=True)
            new_num = full_df[num_cols].astype(float).round(4)
            new_compare = pd.concat([new_str, new_num], axis=1).sort_values(str_cols + num_cols).reset_index(drop=True)

            old_str = latest_df[str_cols].astype(str).reset_index(drop=True)
            old_num = latest_df[num_cols].astype(float).round(4)
            old_compare = pd.concat([old_str, old_num], axis=1).sort_values(str_cols + num_cols).reset_index(drop=True)

            if new_compare.equals(old_compare):
                elapsed = format_elapsed(perf_counter() - started_at)
                print(f"⏭️  데이터 변동 없음. 업데이트를 건너뜁니다. (최신 날짜: {latest_date}, 소요 시간: {elapsed})")
                return

        merged_df = pd.concat([existing_df, full_df], ignore_index=True)
    else:
        merged_df = full_df

    # 같은 날짜에 재수집 시 중복 방지: 최신 값을 우선 유지
    merged_df = merged_df.drop_duplicates(
        subset=['hero', 'data_tier', 'map', 'update_date'],
        keep='last'
    ).reset_index(drop=True)

    merged_df.to_csv(stats_csv_path, index=False, encoding='utf-8-sig')

    elapsed = format_elapsed(perf_counter() - started_at)
    print(
        f"🎉 {today} 데이터 추가 완료! "
        f"(누적 {len(merged_df)}행, 소요 시간: {elapsed})"
    )


if __name__ == "__main__":
    main()
