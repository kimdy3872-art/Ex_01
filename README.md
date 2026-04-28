# Overwatch Analysis

오버워치 2 경쟁전 메타를 시각화하는 Streamlit 기반 대시보드 프로젝트입니다.  
티어별/포지션별 승률과 픽률을 바탕으로 영웅 랭크를 계산하고, 페이지별로 분포/비중/영웅 상세 정보를 확인할 수 있습니다.

## 주요 기능

- 메인 대시보드
  - 티어, 포지션, 정렬, 영웅 검색 필터
  - 승률/픽률 기반 영웅 랭크 테이블 (S/A/B/C)
  - 장인챔프(낮은 픽률 대비 높은 승률) 표시
- 픽률/승률 분포 페이지
  - 선택한 티어/포지션 기준 분포 시각화
- 역할별 랭크 비중 페이지
  - 포지션별 랭크 구성 비율 분석
- 영웅 상세 페이지
  - 특정 영웅의 상세 지표와 관련 정보 확인
- 데이터 수집 자동화 스크립트
  - 경쟁전 메타 데이터 수집: update.py
  - 영웅 퍼크 데이터 수집: update_perk.py

## 사용 기술

- Python
- Streamlit
- Pandas / NumPy
- Plotly
- Selenium (동적 페이지 크롤링)

## 프로젝트 구조

```text
Overwatch_analysis/
├─ main.py
├─ update.py
├─ update_perk.py
├─ requirements.txt
├─ overwatch_competitive_stats.csv
├─ overwatch_hero_perks.csv
└─ pages/
   ├─ 1_pick_win_distribution.py
   ├─ 2_role_rank_share.py
   └─ 3_hero_detail.py
```

## 시작하기

### 1) 저장소 클론

```bash
git clone <YOUR_REPOSITORY_URL>
cd Overwatch_analysis
```

### 2) 가상환경 생성 및 활성화

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3) 패키지 설치

```bash
pip install -r requirements.txt
```

### 4) 대시보드 실행

```bash
streamlit run main.py
```

브라우저에서 기본 주소(보통 http://localhost:8501)로 접속합니다.

## 데이터 갱신

### 경쟁전 통계 데이터 갱신

```bash
python update.py
```

- Blizzard 경쟁전 통계를 수집해 overwatch_competitive_stats.csv를 갱신합니다.
- 동일 날짜에 재수집 시 중복을 제거하고 최신 값을 유지합니다.

### 영웅 특전 데이터 갱신

```bash
python update_perk.py
```

- OW Perks 데이터를 수집해 overwatch_hero_perks.csv를 갱신합니다.
- 옵션 예시:

```bash
python update_perk.py --max-heroes 5
python update_perk.py --locale ko --output overwatch_hero_perks.csv
```

## 데이터 컬럼 (요약)

### overwatch_competitive_stats.csv

- hero, role, data_tier
- map, map_name, update_date
- win_rate, pick_rate
- win_rate_z, pick_rate_log, pick_rate_z
- total_score, rank

### overwatch_hero_perks.csv

- hero, hero_slug, role, category
- perk_type, perk_name, pick_rate
- perk_slug, perk_image_url, perk_image_raw_url
- hero_image_url, source_url, update_date

## 실행 환경 메모

- Selenium 기반 크롤링을 위해 Chrome(또는 Chromium) 실행 환경이 필요합니다.
- Streamlit은 최신 수집일(update_date) 데이터를 중심으로 시각화합니다.

## 향후 개선 아이디어
- 테스트 코드 및 데이터 검증 파이프라인 추가
- 시계열 변화(일자별 메타 변화) 페이지 추가

## License

개인/학습 목적 예제 프로젝트입니다.  
배포 시 사용 데이터 소스의 정책과 라이선스를 반드시 확인하세요.
