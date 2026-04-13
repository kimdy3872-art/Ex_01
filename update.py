from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import numpy as np
import time

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
    '벤처': 'Damage', '벤데타': 'Damage', '안란': 'Damage', '엠레': 'Damage', '프레야': 'Damage',
    '메르시': 'Support', '아나': 'Support', '루시우': 'Support', '젠야타': 'Support', 
    '모이라': 'Support', '바티스트': 'Support', '브리기테': 'Support', '키리코': 'Support', 
    '라이프위버': 'Support', '일리아리': 'Support', '주노': 'Support', '미즈키': 'Support', '우양' : 'Support',
    '제트팩 캣': 'Support'
}

# 2. 티어 리스트 정의
tiers = ["All", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster % Champion"]

def scrape_tier_data(tier_name):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = f"https://overwatch.blizzard.com/ko-kr/rates/?input=PC&map=all-maps&region=Asia&role=All&rq=2&tier={tier_name}"
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hero-name")))
        time.sleep(3)

        script = """
        let data = [];
        let names = document.querySelectorAll('.hero-name');
        let winrates = document.querySelectorAll('.winrate-cell');
        let pickrates = document.querySelectorAll('.pickrate-cell');
        
        for (let i = 0; i < names.length; i++) {
            data.push({
                'hero': names[i].innerText.trim(),
                'win_rate': winrates[i] ? winrates[i].innerText : '0%',
                'pick_rate': pickrates[i] ? pickrates[i].innerText : '0%'
            });
        }
        return data;
        """
        hero_list = driver.execute_script(script)
        df = pd.DataFrame(hero_list)
        
        if not df.empty:
            # 포지션 매핑 적용
            df['role'] = df['hero'].map(role_dict)
            df['data_tier'] = tier_name
            if tier_name in ["Grandmaster % Champion", "Grandmaster & Champion"]:
                df['data_tier'] = 'Grandmaster'
        return df

    except Exception as e:
        print(f"❌ {tier_name} 에러: {e}")
        return pd.DataFrame()
    finally:
        driver.quit()

def main():
    final_list = []
    for t in tiers:
        print(f"🚀 {t} 수집 및 매핑 중...")
        tdf = scrape_tier_data(t)
        if not tdf.empty:
            # 매핑 검증
            missing = tdf[tdf['role'].isna()]['hero'].unique()
            if len(missing) > 0:
                print(f"⚠️ {t} 티어 누락 영웅 발견: {missing}")
            final_list.append(tdf)

    # 3. 데이터 통합 및 저장
    if final_list:
        full_df = pd.concat(final_list, ignore_index=True)
        
        # 숫자 변환
        full_df['win_rate'] = full_df['win_rate'].str.replace('%', '', regex=False).replace('--', '0').astype(float)
        full_df['pick_rate'] = full_df['pick_rate'].str.replace('%', '', regex=False).replace('--', '0').astype(float)

        # 랭크 계산
        def safe_zscore(series):
            std = series.std()
            if std == 0 or pd.isna(std):
                return pd.Series([0] * len(series), index=series.index)
            return (series - series.mean()) / std

    full_df['win_rate_z'] = full_df.groupby('data_tier')['win_rate'].transform(safe_zscore)
    full_df['pick_rate_log'] = np.log1p(full_df['pick_rate'])
    full_df['pick_rate_z'] = full_df.groupby('data_tier')['pick_rate_log'].transform(safe_zscore)
    full_df['total_score'] = full_df['win_rate_z'] * 0.6 + full_df['pick_rate_z'] * 0.4

    def assign_rank(scores):
        if len(scores) >= 4:
            return pd.qcut(scores, q=4, labels=['C', 'B', 'A', 'S'], duplicates='drop')
        return pd.Series(['A'] * len(scores), index=scores.index)

    full_df['rank'] = full_df.groupby('data_tier')['total_score'].transform(assign_rank)

    full_df.to_csv('overwatch_competitive_stats.csv', index=False, encoding='utf-8-sig')
    print("🎉 포지션 매핑 포함 모든 티어 저장 완료!")


if __name__ == "__main__":
    main()
