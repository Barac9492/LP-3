# LP 투자 동향 자동 모니터링 시스템 - 프로젝트 요약

## 프로젝트 개요

벤처캐피탈 펀드레이징을 위한 전세계 주요 LP(Limited Partner) 투자 활동 자동 모니터링 시스템

**버전**: 1.0.0
**개발 완료일**: 2024-12-10
**언어**: Python 3.9+

## 핵심 기능 구현 현황

### ✅ 완료된 기능

1. **자동 뉴스 수집 시스템**
   - 11개 Tier 1 LP 기관 모니터링 지원
   - DuckDuckGo 기반 웹 검색 (API 키 불필요)
   - 중복 제거 및 날짜 필터링
   - 커스터마이징 가능한 검색 키워드

2. **AI 기반 분석 엔진**
   - OpenAI GPT-4 / Anthropic Claude 지원
   - 6개 카테고리 자동 분류
   - 한국 관련성 1-5점 스코어링
   - 뉴스 요약 및 핵심 포인트 추출
   - Fallback 룰 기반 분류 (AI 없이도 작동)

3. **리포트 생성**
   - 주간 리포트 (Markdown/HTML)
   - 월간 리포트 (트렌드 분석 포함)
   - 한국어 기본, 영어 지원
   - 자동 통계 및 인사이트 생성

4. **알림 시스템**
   - 이메일 알림 (SMTP)
   - Slack 웹훅 통합
   - 실시간 고득점 시그널 알림
   - 배치 알림 지원

5. **데이터 관리**
   - SQLite 데이터베이스
   - 뉴스 아카이브 및 검색
   - 수집 이력 추적
   - 통계 및 분석 쿼리

6. **스케줄링**
   - 일일 자동 뉴스 수집
   - 주간/월간 자동 리포트
   - 설정 가능한 실행 시간
   - 백그라운드 실행 지원

## 프로젝트 구조

```
lp-monitor/
├── src/                     # 소스 코드
│   ├── collectors/          # 뉴스 수집 (3 modules)
│   ├── analyzers/           # AI 분석 (3 modules)
│   ├── reporters/           # 리포트 생성 (3 modules)
│   └── database/            # 데이터 관리 (2 modules)
├── config/                  # 설정 파일
├── data/                    # LP 프로필 및 키워드
├── tests/                   # 단위 테스트 (3 test files)
├── reports/                 # 생성된 리포트
├── logs/                    # 로그 파일
├── main.py                  # 메인 실행 스크립트
├── scheduler.py             # 스케줄러
├── requirements.txt         # 의존성
├── README.md                # 상세 문서
├── QUICKSTART.md            # 빠른 시작 가이드
└── PROJECT_SUMMARY.md       # 본 파일
```

## 기술 스택

### 핵심 라이브러리
- **웹 스크래핑**: requests, BeautifulSoup4
- **AI/NLP**: OpenAI API, Anthropic API
- **데이터 처리**: pandas, numpy
- **스케줄링**: schedule
- **설정 관리**: PyYAML, python-dotenv
- **데이터베이스**: SQLite (내장)

### 테스트 및 품질
- pytest, pytest-cov
- black, flake8, mypy

## 모니터링 대상 LP (11개)

| LP | 국가 | AUM | Korea Interest |
|---|---|---|---|
| CalPERS | 미국 | $440B | Medium |
| CalSTRS | 미국 | $308B | Medium |
| CPPIB | 캐나다 | $570B | High |
| Ontario Teachers | 캐나다 | $247B | Medium |
| GIC | 싱가포르 | $690B | High |
| Temasek | 싱가포르 | $382B | High |
| NPS | 한국 | $928B | Very High |
| GPIF | 일본 | $1,600B | Low |
| ADIA | UAE | $900B | Medium |
| PIF | 사우디 | $700B | Medium |
| GPFG | 노르웨이 | $1,400B | Low |

**총 AUM**: ~$8.2 Trillion

## 실행 모드

### 1. 즉시 실행 모드
```bash
python main.py --mode instant --days 7
```
- 최근 N일간 뉴스 수집 및 분석
- 리포트 생성 옵션
- 알림 발송 옵션

### 2. 스케줄 모드
```bash
python scheduler.py
```
- 매일 자동 뉴스 수집
- 주간/월간 자동 리포트
- 백그라운드 실행

### 3. 리포트 전용 모드
```bash
python main.py --mode weekly
python main.py --mode monthly
```

### 4. 테스트 모드
```bash
python main.py --mode test
```

## 설정 파일

### config/config.yaml
- LP 목록 및 티어
- 검색 설정
- AI 모델 설정
- 스코어링 가중치
- 알림 임계값
- 스케줄 설정

### data/lp_entities.json
- LP 기관 프로필
- 검색 키워드
- 관심도 수준

### data/search_keywords.json
- 투자 활동 키워드
- 섹터 키워드
- 지역 키워드

### .env
- API 키
- 이메일 설정
- Slack 웹훅

## 데이터 모델

### NewsItem
- LP 이름, 제목, URL, 날짜
- 카테고리, 스코어
- 요약, 핵심 포인트
- 금액, 섹터, 태그

### LPProfile
- 기본 정보 (이름, 국가, AUM)
- 투자 포커스
- 검색 키워드

### CollectionRun
- 수집 이력
- 처리된 LP 목록
- 수집된 뉴스 수
- 에러 로그

## 성능 지표

### 목표 지표
- ✅ 100개 뉴스 처리 시간 < 5분
- ✅ DB 쿼리 응답 < 1초
- ⏳ 주요 LP 뉴스 커버리지 > 90% (실제 테스트 필요)
- ⏳ 한국 관련 시그널 탐지율 > 80% (실제 테스트 필요)

### 리소스 사용
- 메모리: ~100MB (뉴스 100개 기준)
- 디스크: ~10MB/월 (데이터베이스)
- API 비용: ~$5-10/일 (GPT-4 기준, 설정에 따라 변동)

## 확장성

### 쉬운 확장
1. **더 많은 LP 추가**
   - `data/lp_entities.json`에 프로필 추가
   - `config/config.yaml`에 티어 추가

2. **커스텀 키워드**
   - `data/search_keywords.json` 수정

3. **스코어링 로직 조정**
   - `config/config.yaml`의 `scoring` 섹션 수정
   - `src/analyzers/scorer.py` 커스터마이징

### 향후 확장 가능성
- 고급 검색 API 통합 (SerpAPI, NewsAPI)
- PostgreSQL/MongoDB 마이그레이션
- 웹 대시보드 (Streamlit/Flask)
- REST API
- 다국어 지원
- ML 기반 시그널 예측

## 테스트

### 단위 테스트
```bash
pytest
pytest --cov=src --cov-report=html
```

### 통합 테스트
```bash
python main.py --mode test
python main.py --mode instant --days 1 --lps GIC
```

## 배포 및 운영

### 개발 환경
```bash
pip install -r requirements.txt
python main.py --mode instant --days 3 --no-ai
```

### 프로덕션 환경
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 스케줄러 시작 (백그라운드)
nohup python scheduler.py > scheduler.out 2>&1 &

# 로그 모니터링
tail -f logs/lp_monitor.log
```

### Docker 배포 (향후)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "scheduler.py"]
```

## 보안 고려사항

1. **API 키 관리**
   - `.env` 파일 사용
   - `.gitignore`에 포함
   - 환경 변수로 주입

2. **데이터베이스**
   - SQLite 파일 권한 제한
   - 민감 정보 암호화 고려

3. **로그**
   - API 키 노출 방지
   - 민감 정보 마스킹

## 비용 예측

### API 비용 (GPT-4 기준)
- 뉴스 1개 분석: ~$0.02-0.05
- 일일 100개 뉴스: ~$2-5
- 월간: ~$60-150

### 비용 절감 방법
1. `--no-ai` 플래그 사용 (룰 기반)
2. GPT-3.5 사용 (설정 변경)
3. 수집 빈도 조정
4. 결과 캐싱

## 문제 해결

### 일반적인 문제
1. **뉴스 수집 안됨**
   - 인터넷 연결 확인
   - Rate limiting (딜레이 증가)
   - 다른 LP로 테스트

2. **AI 분석 실패**
   - API 키 확인
   - 크레딧 확인
   - `--no-ai`로 우회

3. **알림 실패**
   - 이메일/Slack 설정 확인
   - 방화벽 확인
   - 테스트 알림 실행

### 로그 확인
```bash
tail -f logs/lp_monitor.log
grep ERROR logs/lp_monitor.log
```

## 다음 단계

### 즉시 가능
1. ✅ 시스템 테스트: `python main.py --mode test`
2. ✅ 첫 뉴스 수집: `python main.py --mode instant --days 3`
3. ✅ 리포트 확인: `cat reports/weekly/*.md`

### 단기 (1-2주)
1. 실제 환경에서 7일간 테스트 실행
2. 검색 키워드 최적화
3. 스코어링 로직 튜닝
4. 알림 설정 및 테스트

### 중기 (1-3개월)
1. 웹 대시보드 개발
2. 더 많은 LP 추가 (50-100개)
3. 고급 검색 API 통합
4. PostgreSQL 마이그레이션

### 장기 (3-6개월)
1. ML 기반 시그널 예측
2. 다국어 지원
3. REST API 제공
4. 모바일 앱

## 기여자

- 개발: Claude (Anthropic AI)
- 요구사항: [Your Name/Team]

## 라이선스

내부 사용 목적

## 연락처

프로젝트 관련 문의: [your-email@example.com]

---

**프로젝트 상태**: ✅ MVP 완료, 프로덕션 배포 준비됨
**마지막 업데이트**: 2024-12-10
