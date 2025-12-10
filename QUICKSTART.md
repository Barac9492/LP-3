# Quick Start Guide

LP 투자 동향 모니터링 시스템을 빠르게 시작하는 방법입니다.

## 1. 최소 설정 (5분)

### 설치

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 파일 생성
cp .env.example .env
```

### API 키 설정

`.env` 파일을 열고 OpenAI 또는 Anthropic API 키를 추가하세요:

```bash
# 둘 중 하나만 있으면 됩니다
OPENAI_API_KEY=sk-...
# 또는
ANTHROPIC_API_KEY=sk-ant-...
```

## 2. 첫 실행 (즉시 테스트)

### 테스트 모드로 시스템 확인

```bash
python main.py --mode test
```

예상 출력:
```
🧪 테스트 모드
============================================================
✅ Config loaded: 7 sections
✅ Loaded 11 LP profiles
✅ Total news in DB (30 days): 0
✅ 시스템 테스트 완료
```

### 실제 뉴스 수집 (AI 없이)

먼저 API 비용을 들이지 않고 뉴스 수집만 테스트:

```bash
python main.py --mode instant --days 3 --no-ai --lps GIC Temasek
```

이 명령은:
- 최근 3일간 뉴스 수집
- GIC, Temasek 2개 LP만 모니터링
- AI 분석 비활성화 (비용 절감)

예상 출력:
```
🔍 LP 뉴스 모니터링 시작... (최근 3일)
============================================================

📰 GIC 뉴스 수집 중...
✅ GIC: 5개 뉴스 수집

📰 Temasek 뉴스 수집 중...
✅ Temasek: 3개 뉴스 수집

============================================================
📊 총 8개 뉴스 분석 완료
```

### AI 분석 포함 실행

API 키가 설정되어 있다면:

```bash
python main.py --mode instant --days 3 --lps GIC NPS
```

### 리포트 생성

```bash
python main.py --mode instant --days 7 --report weekly
```

생성된 리포트 확인:
```bash
cat reports/weekly/weekly_report_*.md
```

## 3. 실제 운영 시작

### 매일 자동 실행 설정

```bash
# 스케줄러 시작
python scheduler.py
```

스케줄러가 다음 작업을 자동으로 수행합니다:
- **매일 오전 9시**: 뉴스 수집
- **매주 월요일 10시**: 주간 리포트
- **매월 1일 10시**: 월간 리포트

### 백그라운드 실행 (Linux/Mac)

```bash
nohup python scheduler.py > scheduler.out 2>&1 &
```

스케줄러 중지:
```bash
pkill -f scheduler.py
```

## 4. 알림 설정 (선택사항)

### 이메일 알림

`.env` 파일에 추가:

```bash
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENTS=recipient@example.com
```

> Gmail 사용 시 App Password 생성 필요:
> https://support.google.com/accounts/answer/185833

### Slack 알림

1. Slack Webhook URL 생성
2. `.env`에 추가:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

3. `config/config.yaml`에서 활성화:

```yaml
alerts:
  enabled: true
  slack:
    enabled: true
```

### 알림 테스트

```bash
python main.py --mode instant --days 1 --alert --lps GIC
```

## 5. 유용한 명령어 모음

### 특정 LP만 모니터링

```bash
python main.py --mode instant --days 7 --lps GIC Temasek NPS CPPIB
```

### 한 달치 데이터 수집 및 월간 리포트

```bash
python main.py --mode instant --days 30 --report monthly
```

### AI 없이 빠른 수집 (비용 절감)

```bash
python main.py --mode instant --days 7 --no-ai
```

### 고득점 시그널만 확인

리포트에서 스코어 4-5점 항목만 확인하거나, 데이터베이스 직접 쿼리:

```python
from src.database.db_manager import DatabaseManager

db = DatabaseManager()
high_score_news = db.get_high_relevance_news(days=7, threshold=4)

for news in high_score_news:
    print(f"[{news.korea_relevance_score}⭐] {news.lp_name}: {news.title}")
```

## 6. 디버깅 및 로그

### 로그 확인

```bash
# 최근 로그 확인
tail -f logs/lp_monitor.log

# 에러만 확인
grep ERROR logs/lp_monitor.log
```

### 자세한 로그 출력

```bash
python main.py --mode instant --days 3 --log-level DEBUG
```

### 데이터베이스 확인

```bash
sqlite3 data/news_archive.db

# 테이블 확인
.tables

# 최근 뉴스 확인
SELECT lp_name, title, korea_relevance_score, date
FROM news_items
ORDER BY date DESC
LIMIT 10;

# 통계 확인
SELECT lp_name, COUNT(*) as count
FROM news_items
GROUP BY lp_name
ORDER BY count DESC;
```

## 7. 다음 단계

1. **커스터마이징**
   - `config/config.yaml`: 스케줄, 임계값 조정
   - `data/lp_entities.json`: LP 목록 추가/수정
   - `data/search_keywords.json`: 검색 키워드 최적화

2. **고급 기능**
   - 웹 대시보드 개발 (Streamlit)
   - PostgreSQL 마이그레이션
   - 커스텀 분석 로직 추가

3. **최적화**
   - API 호출 빈도 조정
   - 캐싱 전략 개선
   - 검색 정확도 향상

## 문제 해결

### "No module named 'src'"

```bash
# 프로젝트 루트 디렉토리에서 실행하는지 확인
cd /path/to/LP-3
python main.py ...
```

### "API key not found"

```bash
# .env 파일 확인
cat .env

# 환경 변수가 로드되는지 확인
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

### 뉴스가 수집되지 않음

1. 인터넷 연결 확인
2. 다른 LP로 테스트: `--lps GIC`
3. 날짜 범위 확대: `--days 14`
4. 디버그 모드: `--log-level DEBUG`

## 도움말

```bash
# 전체 옵션 보기
python main.py --help
```

더 자세한 내용은 `README.md`를 참조하세요.
