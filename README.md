# LP 투자 동향 자동 모니터링 시스템

벤처캐피탈 펀드레이징을 위해 전세계 주요 LP(Limited Partner)들의 투자 활동을 자동으로 모니터링하고, 한국 VC에 관심 보일만한 시그널을 감지하는 시스템입니다.

## 주요 기능

- 🔍 **자동 뉴스 수집**: 주요 LP 기관별 최신 뉴스 자동 검색
- 🤖 **AI 기반 분석**: GPT-4/Claude를 활용한 뉴스 분류 및 요약
- 📊 **한국 관련성 스코어링**: 1-5점 스케일로 한국 VC 관련성 자동 평가
- 📄 **자동 리포트 생성**: 주간/월간 종합 리포트
- 🔔 **실시간 알림**: 고득점 시그널 발생 시 이메일/Slack 알림
- ⏰ **스케줄 실행**: 일일/주간/월간 자동 실행

## 모니터링 LP 목록

**Tier 1 (11개 기관)**:
- CalPERS (미국)
- CalSTRS (미국)
- CPPIB (캐나다)
- Ontario Teachers (캐나다)
- GIC (싱가포르)
- Temasek (싱가포르)
- NPS (한국)
- GPIF (일본)
- ADIA (UAE)
- PIF (사우디)
- GPFG (노르웨이)

## 설치 및 설정

### 1. 환경 준비

```bash
# Python 3.9 이상 필요
python --version

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일 생성:

```bash
cp .env.example .env
```

`.env` 파일 편집:

```bash
# API Keys (하나 이상 필수)
OPENAI_API_KEY=your_openai_api_key_here
# 또는
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Email 알림 (선택사항)
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com

# Slack 알림 (선택사항)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 3. 설정 파일 확인

`config/config.yaml` 파일에서 설정 조정 가능:
- LP 목록 및 우선순위
- 검색 키워드
- 스코어링 가중치
- 알림 임계값
- 리포트 설정

## 사용 방법

### 즉시 실행 모드

최근 7일간 뉴스 수집 및 분석:

```bash
python main.py --mode instant --days 7
```

리포트 생성 포함:

```bash
python main.py --mode instant --days 7 --report weekly
```

고득점 시그널 알림 발송:

```bash
python main.py --mode instant --days 7 --alert
```

특정 LP만 모니터링:

```bash
python main.py --mode instant --days 7 --lps GIC Temasek NPS
```

AI 분석 없이 실행 (비용 절감):

```bash
python main.py --mode instant --days 7 --no-ai
```

### 주간/월간 리포트 생성

```bash
# 주간 리포트
python main.py --mode weekly

# 월간 리포트
python main.py --mode monthly
```

### 스케줄 모드 (자동 실행)

```bash
python scheduler.py
```

기본 스케줄:
- **매일 오전 9시**: 뉴스 수집 및 알림
- **매주 월요일 오전 10시**: 주간 리포트
- **매월 1일 오전 10시**: 월간 리포트

스케줄 변경은 `config/config.yaml` 파일에서 수정.

### 시스템 테스트

```bash
python main.py --mode test
```

## 프로젝트 구조

```
lp-monitor/
├── src/
│   ├── collectors/          # 뉴스 수집
│   │   ├── news_collector.py
│   │   ├── lp_profiles.py
│   │   └── search_queries.py
│   ├── analyzers/           # AI 분석
│   │   ├── classifier.py
│   │   ├── scorer.py
│   │   └── summarizer.py
│   ├── reporters/           # 리포트 생성
│   │   ├── weekly_report.py
│   │   ├── monthly_report.py
│   │   └── alert_system.py
│   └── database/            # 데이터 관리
│       ├── db_manager.py
│       └── models.py
├── data/                    # 데이터 파일
│   ├── lp_entities.json
│   ├── search_keywords.json
│   └── news_archive.db
├── config/                  # 설정 파일
│   └── config.yaml
├── reports/                 # 생성된 리포트
│   ├── weekly/
│   └── monthly/
├── logs/                    # 로그 파일
├── tests/                   # 테스트
├── main.py                  # 메인 실행 파일
├── scheduler.py             # 스케줄러
└── requirements.txt
```

## 뉴스 분류 카테고리

1. **신규_출자_약정**: 새로운 펀드 커밋먼트 발표
2. **전략_변화**: 투자 전략 또는 정책 변경
3. **인사_변동**: CIO 등 주요 인사 이동
4. **성과_발표**: 수익률, 포트폴리오 성과 공개
5. **한국_관련**: 한국 시장/기업 직접 언급
6. **일반_소식**: 기타 뉴스

## 한국 관련성 스코어

- **5점**: 한국 VC 직접 언급 또는 한국 시장 투자 계획
- **4점**: 아시아 벤처 투자 확대, AI/반도체 섹터 집중
- **3점**: 신흥시장 투자 증가, 새로운 GP 관계 구축
- **2점**: 전반적인 VC 배분 증가
- **1점**: 일반적인 소식

## 리포트 예시

### 주간 리포트 포함 내용

- 📌 이번 주 핵심 요약 (3-5개 주요 포인트)
- 🔥 한국 VC 주목 시그널 (스코어 4-5점)
- 📊 신규 커밋먼트 현황 (금액별, 지역별)
- 💡 시사점 및 액션 아이템
- 📂 카테고리별 분류
- 📰 LP별 활동 요약

생성된 리포트 위치: `reports/weekly/weekly_report_YYYYMMDD.md`

### 월간 리포트 추가 내용

- 🏆 LP별 활동 순위
- 🎯 섹터별 투자 트렌드
- 🌏 지역별 관심도
- 📈 트렌드 및 시사점

## 개발 및 테스트

### 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 커버리지 포함
pytest --cov=src --cov-report=html

# 특정 테스트만 실행
pytest tests/test_classifier.py
```

### 코드 품질 검사

```bash
# 포맷팅
black src/ tests/

# 린팅
flake8 src/ tests/

# 타입 체크
mypy src/
```

## 성능 최적화

### API 비용 절감

1. **AI 분석 비활성화**: `--no-ai` 플래그 사용
2. **수집 빈도 조정**: 설정에서 `lookback_days` 줄이기
3. **결과 제한**: `max_results_per_lp` 값 조정
4. **캐싱 활용**: 동일 뉴스 중복 분석 방지

### 성능 지표 목표

- 100개 뉴스 처리 시간 < 5분
- DB 쿼리 응답 < 1초
- 주요 LP 뉴스 커버리지 > 90%
- 한국 관련 시그널 탐지율 > 80%

## 확장 기능 (향후 계획)

- [ ] 웹 대시보드 (Streamlit/Flask)
- [ ] 더 많은 LP 추가 (100+ 기관)
- [ ] 다국어 지원 (영어, 중국어)
- [ ] PostgreSQL 지원
- [ ] REST API
- [ ] 고급 검색 API 통합 (SerpAPI, NewsAPI)
- [ ] ML 기반 시그널 예측

## 문제 해결

### 뉴스가 수집되지 않는 경우

1. 인터넷 연결 확인
2. 검색 키워드 조정 (`data/search_keywords.json`)
3. 로그 확인 (`logs/lp_monitor.log`)
4. Rate limiting 확인 (요청 딜레이 증가)

### AI 분석이 작동하지 않는 경우

1. API 키 확인 (`.env` 파일)
2. API 크레딧/사용량 확인
3. `--no-ai` 플래그로 우회 실행
4. 로그에서 에러 메시지 확인

### 알림이 발송되지 않는 경우

1. 이메일/Slack 설정 확인 (`.env`)
2. `config.yaml`에서 알림 활성화 확인
3. 테스트 알림 실행: `main.py --mode test --alert`
4. 방화벽/SMTP 포트 차단 확인

## 라이선스

이 프로젝트는 내부 사용을 위한 도구입니다.

## 기여

이슈 및 개선사항은 GitHub Issues를 통해 제보해주세요.

## 문의

프로젝트 관련 문의: [your-email@example.com]

---

**마지막 업데이트**: 2024-12-10
**버전**: 1.0.0
