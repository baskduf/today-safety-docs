# Today Safety RAG 코퍼스 1차 설계

## 1. 목적

이 문서는 Today Safety의 1차 RAG 코퍼스를 어떻게 구성할지 고정하는 설계 문서입니다.

이번 단계의 목표는 다음과 같습니다.

- 건설업과 제조업 중심의 검색용 코퍼스 범위 확정
- 공공데이터 API/파일별 문서 단위 고정
- 공통 문서 스키마와 저장 방식 고정
- 수집 파이프라인의 단계와 실패 처리 기준 정의

이 코퍼스의 목적은 `유사 재해사례 검색 + 브리핑 근거 제공`입니다.  
정밀 사고확률 예측 모델 학습은 이번 범위에 포함하지 않습니다.

## 2. 코퍼스 범위

### 2.1 대상 산업

- 1차 산업 범위는 `건설 + 제조`로 고정합니다.
- 건설/제조 외 데이터는 수집하더라도 1차 RAG 코퍼스 기본 집합에는 포함하지 않습니다.
- 향후 물류, 설비보전, 폐기물 처리 등은 2차 확장 범위로 둡니다.

### 2.2 대상 데이터셋

1차 코퍼스 소스는 아래로 고정합니다.

- `15121001` 국내재해사례 게시판 API
- `15121008` 국내재해사례 첨부파일 정보 API
- `15119137` 사고사망 게시판 API
- `15140383` 산업재해 고위험요인(SIF) 아카이브
- `15001197` MSDS API 메타/본문
- `15084084` 단기예보 API

### 2.3 문서 단위

각 소스의 문서 단위는 아래처럼 고정합니다.

- 재해사례 게시글 1건 = 문서 1개
- 사고사망 게시글 1건 = 문서 1개
- SIF 사례 1행 = 문서 1개
- PDF 첨부파일 1개 = 문서 1개
- MSDS 1물질 = 문서 1개
- 날씨는 영구 문서 저장 대상이 아니라 요청 시점 보강 문서로 취급

### 2.4 첨부파일 범위

- 1차에서는 `PDF 우선 본문 추출`로 고정합니다.
- `HWP/HWPX`는 본문 추출하지 않습니다.
- HWP/HWPX는 아래 메타만 저장합니다.
  - 파일명
  - 확장자
  - 다운로드 URL
  - 게시글 연결 정보
  - 수집 시각
- PDF 추출 실패 문서는 폐기하지 않고 메타만 유지합니다.

## 3. 저장 구조

### 3.1 기본 원칙

- 본문은 `JSONL`
- 조회용 메타는 `PostgreSQL`
- 원본 응답/원문은 재현 가능한 형태로 보존

즉, 저장 구조는 `JSONL 문서 본문 + PostgreSQL 메타데이터` 하이브리드로 갑니다.

### 3.2 JSONL 문서 스키마

모든 문서는 최소 아래 필드를 가져야 합니다.

- `doc_id`
- `source_type`
- `source_dataset_id`
- `source_url`
- `source_title`
- `source_date`
- `industry_major`
- `industry_minor`
- `job_group_standard`
- `process_group_standard`
- `accident_type_standard`
- `hazard_factor_standard`
- `severity_band`
- `chemical_related`
- `weather_related`
- `text_content`
- `text_summary`
- `attachment_type`
- `parent_case_id`
- `ingested_at`

### 3.3 PostgreSQL 메타 스키마

조회/필터링용 메타는 최소 아래 컬럼을 가져야 합니다.

- `doc_id`
- `source_type`
- `source_dataset_id`
- `source_url`
- `source_date`
- `industry_major`
- `accident_type_standard`
- `process_group_standard`
- `has_attachment`
- `attachment_type`
- `text_length`
- `ingestion_status`

### 3.4 ID 규칙

- `doc_id`는 소스별 충돌이 없도록 접두어를 포함합니다.
- 예시
  - `case-15121001-<boardNo>`
  - `fatal-15119137-<recordId>`
  - `sif-15140383-<rowId>`
  - `pdf-15121008-<boardNo>-<fileSeq>`
  - `msds-15001197-<materialId>`

### 3.5 권장 디렉터리 구조

실제 구현 시 코퍼스 출력 경로는 아래를 권장합니다.

- `data_sources/rag/raw_api/`
- `data_sources/rag/raw_attachments/`
- `data_sources/rag/corpus_jsonl/`
- `data_sources/rag/meta_exports/`
- `data_sources/rag/reports/`

## 4. 수집 파이프라인

수집 파이프라인은 `fetch -> normalize -> enrich -> export` 4단계로 고정합니다.

### 4.1 fetch

수집 단계에서 수행할 작업:

- 게시판 API 원문 수집
- 첨부파일 메타 수집
- PDF 첨부 다운로드
- SIF 파일 로드
- MSDS 조회

### 4.2 normalize

정규화 단계에서 수행할 작업:

- 게시판 원문을 공통 문서 구조로 변환
- PDF 추출 본문을 공통 문서 구조로 변환
- SIF 1행을 공통 문서 구조로 변환
- 기존 전처리 결과의 taxonomy를 재사용해 산업/사고유형/공정 태그 매핑

### 4.3 enrich

보강 단계에서 수행할 작업:

- 게시글과 첨부파일 연결
- 건설/제조 필터 적용
- 표준 taxonomy 태그 추가
- `text_summary` 생성 규칙 적용
- `chemical_related`, `weather_related` 플래그 부여

### 4.4 export

내보내기 단계에서 수행할 작업:

- 코퍼스 JSONL 출력
- PostgreSQL 적재용 메타 CSV 출력
- 수집 실패/파싱 실패 리포트 출력

## 5. 표준 타입과 내부 인터페이스

### 5.1 내부 타입

구현 시 아래 4개 타입을 기본 타입으로 둡니다.

- `RawCase`
- `RawAttachment`
- `ExtractedDocument`
- `CorpusDocument`

### 5.2 내부 인터페이스

구현 시 아래 인터페이스를 기준으로 모듈을 나눕니다.

- `fetch_cases(dataset_id, params) -> list[RawCase]`
- `fetch_attachments(case_id) -> list[RawAttachment]`
- `extract_pdf_text(file_path) -> ExtractedDocument`
- `normalize_to_corpus_doc(raw) -> CorpusDocument`
- `export_corpus_jsonl(docs) -> file`

### 5.3 기존 전처리와의 관계

- `scripts/preprocess_today_safety.py`
  - 구조화 사고/위험 데이터 정규화 담당
- 새 RAG 수집 파이프라인
  - 비정형 문서 코퍼스 구축 담당
- 두 파이프라인은 아래를 공유합니다.
  - 산업 taxonomy
  - 사고유형 taxonomy
  - 공정 taxonomy
  - 일부 공통 필드명

## 6. 실패 처리 원칙

- API 응답 누락 시 해당 요청 단위를 실패 리포트에 기록
- 첨부파일 없는 게시글은 게시글 본문만 문서화
- PDF 파싱 실패 시
  - 문서를 버리지 않음
  - `ingestion_status = pdf_parse_failed`
  - 첨부 메타는 유지
- HWP/HWPX는
  - `ingestion_status = hwp_metadata_only`
  - 링크와 메타만 유지

## 7. 검색 응답 요구사항

이번 단계에서 검색 API 자체를 구현하지는 않지만, 이후를 위해 검색 결과 요구사항을 고정합니다.

검색 결과는 최소 아래 정보를 반환할 수 있어야 합니다.

- `title`
- `summary`
- `source_url`
- `source_type`
- `taxonomy tags`

브리핑 생성 입력은 최소 아래 필드를 받을 수 있어야 합니다.

- 업종
- 직종
- 공정
- 장소
- 날씨
- 화학물질 여부

## 8. 이번 단계에서 하지 않는 것

- 벡터 DB 선정
- BM25/embedding 랭킹 상세 설계
- LLM 프롬프트 최적화
- HWP 본문 추출
- 전 산업 범용 코퍼스 확장
