# Today Safety Data Sources

Today Safety에서 바로 활용할 수 있는 핵심 공공데이터를 `파일데이터`와 `API 메타데이터`로 나누어 정리한 폴더입니다.

## 폴더 구조

- `raw/`
  - 실제로 내려받은 원본 파일데이터
- `catalog/`
  - 공공데이터포털의 공식 카탈로그 JSON
- `notes/`
  - API 엔드포인트, 활용 메모, 라이선스 주의사항

## 이번에 수집한 핵심 데이터

### 파일데이터

- `raw/15140383_sif_archive.xlsx`
  - 한국산업안전보건공단 사망사고 고위험요인(SIF) 아카이브
  - 용도: 고위험작업·상황, 재해유발요인, 감소대책 코퍼스
- `raw/3082968_first_medical_approval.csv`
  - 근로복지공단 산재보험 최초요양 승인 정보
  - 용도: 업종, 재해발생형태, 직종, 상병, 지역 등 구조화 통계 분석
- `raw/15002150_employment_workers_comp_insurance_sites.zip`
  - 근로복지공단 고용 산재보험 가입 현황
  - 용도: 사업장 규모, 업종, 상시근로자 수, 보험 가입 맥락 보강
  - 비고: 연도별 CSV가 들어있는 압축 원본
- `raw/15121557_foreign_worker_accident_detail.csv`
  - 근로복지공단 외국인근로자 산재처리 상세현황
  - 용도: 외국인 근로자 시나리오, 다국어 안전 브리핑 우선순위 설정
- `raw/15104692_special_worker_accident_status.csv`
  - 근로복지공단 노무제공자(특수형태근로종사자) 산재처리현황
  - 용도: 특고/플랫폼 노동 시나리오 확장

### API 메타데이터

- `catalog/15121001_openapi.json`
  - 국내재해사례 게시판 정보 조회서비스
- `catalog/15121008_openapi.json`
  - 국내재해사례 게시판 첨부파일 정보 조회서비스
- `catalog/15119137_openapi.json`
  - 사고사망 게시판 정보 조회서비스
- `catalog/15139398_openapi.json`
  - 안전보건자료 링크 서비스
- `catalog/15144147_openapi.json`
  - 기술지원규정(KOSHA GUIDE) 조회 서비스
- `catalog/15057210_openapi.json`
  - 기상청 지상(종관, ASOS) 시간자료 조회서비스
- `catalog/15084084_openapi.json`
  - 기상청 단기예보 조회서비스
- `catalog/15128213_openapi.json`
  - NCS 기준정보 조회
- `catalog/15139182_openapi.json`
  - 건설현장 안전 신호등
- `catalog/15139497_openapi.json`
  - 보호구 안전인증 현황
- `catalog/15144645_openapi.json`
  - 산재보험 요양 신청·승인 데이터
- `notes/api_reference.md`
  - 위 API들과 MSDS API의 페이지 URL, 서비스 URL, 활용 포인트 정리

### 파일데이터 메타데이터

- `catalog/15140383_fileData.json`
- `catalog/3082968_fileData.json`
- `catalog/15002150_fileData.json`
- `catalog/15121557_fileData.json`
- `catalog/15104692_fileData.json`

## 권장 활용 방식

- 학습/탐색/통계 기준 데이터: `raw/` 파일데이터 우선 사용
- 오늘 작업용 최신 사례 보강: 재해사례/사고사망 API 사용
- 사례 원문 확장: 재해사례 첨부파일 API 사용
- 공식 대응 가이드 결합: 안전보건자료 링크 서비스, KOSHA GUIDE 사용
- 화학물질 경고: MSDS API 사용
- 당일 작업 조건 반영: 기상청 단기예보 API + ASOS 시간자료 함께 사용
- 작업공정 표준화: NCS 기준정보 사용
- 건설업 특화 고도화: 건설현장 안전 신호등 사용

## 주의사항

- SIF 아카이브는 출처표시 및 변경금지 조건을 반드시 확인해야 합니다.
- MSDS 정보는 참고용이며, 공식 MSDS 작성 책임은 제조·수입자에게 있습니다.
- 승인 데이터는 사고 후 승인 사례 중심이므로 절대확률 예측보다 위험유형 분석과 설명 근거에 적합합니다.
- `15002150` 원본은 압축 파일이므로 사용 전에 필요한 연도 CSV만 골라 전처리하는 편이 좋습니다.

## 전처리 파이프라인

- 실행 스크립트: `scripts/preprocess_today_safety.py`
- 의존성 설치: `python -m pip install pandas openpyxl pyarrow`
- 실행 명령: `python scripts/preprocess_today_safety.py`
- 처리 단계: `ingest -> normalize -> validate -> export`

## 생성 산출물

- `processed/master_incident_events.csv`
- `processed/master_incident_events.jsonl`
- `processed/industry_job_process_taxonomy.csv`
- `processed/company_context_priors.csv`
- `processed/worker_segment_priors.csv`
- `intermediate/15140383_sif_raw_events.csv`
- `intermediate/3082968_approval_raw_events.csv`
- `intermediate/15121557_foreign_raw_events.csv`
- `reports/schema_summary.md`
- `reports/data_quality_report.md`
