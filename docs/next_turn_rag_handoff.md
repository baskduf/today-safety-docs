# Next Turn Handoff: RAG 구현 시작

## 1. 목적

이 문서는 다음 턴에서 바로 RAG 구현 작업을 시작할 수 있도록 현재 상태와 첫 구현 범위를 고정해 둔 핸드오프 문서이다.

이번 시작점의 목표는 `Today Safety 검색 중심 MVP`를 위한 최소 코퍼스 구축이다.  
즉, 지금 당장 만드는 것은 정밀 예측 모델이 아니라 아래 흐름이다.

1. 공공데이터 수집
2. 공통 문서 스키마 정규화
3. 검색 가능한 코퍼스 생성
4. 이후 브리핑 생성에 연결

## 2. 현재 기준선

현재 저장소에는 아래 기반 작업이 이미 정리되어 있다.

- 제품 포지셔닝 문서 정리 완료
- 건설·제조 우선 MVP 방향 확정
- 전처리 1차 파이프라인과 taxonomy 초안 존재
- RAG 코퍼스 설계 문서 존재
- RAG 수집 작업목록 문서 존재

반대로 아직 없는 것은 아래다.

- 실제 API 수집기 코드
- 첨부 PDF 다운로드/본문 추출 코드
- `CorpusDocument` 타입 정의 코드
- 코퍼스 JSONL exporter
- 검색 MVP 엔드포인트

즉, 다음 턴부터는 `문서 단계`가 아니라 `구현 시작 단계`로 보면 된다.

## 3. 다음 턴의 첫 작업 범위

다음 턴에서는 범위를 좁혀 아래 3가지만 먼저 구현한다.

### 1차 구현 대상

1. `15121001` 국내재해사례 게시판 수집기
2. `15121008` 첨부파일 메타 수집기
3. `CorpusDocument` 공통 스키마 + JSONL export

이 3개를 먼저 하는 이유는 다음과 같다.

- 재해사례 게시판이 RAG의 핵심 근거 소스다.
- 첨부파일 메타가 있어야 PDF 본문 추출 단계로 자연스럽게 이어진다.
- 공통 스키마가 먼저 있어야 이후 SIF, 사고사망, MSDS를 같은 코퍼스에 넣을 수 있다.

## 4. 구현 순서

다음 턴에서는 아래 순서로 작업한다.

### 단계 1. 새 구현 레포 또는 구현 작업공간 골격 생성

권장 이름:

- `today-safety-rag`
- 또는 `today-safety-mvp`

권장 구조:

- `apps/api`
- `packages/ingestion`
- `packages/corpus`
- `packages/shared`

Python 중심으로 간다면 더 단순하게 아래 구조도 가능하다.

- `app/`
- `ingestion/`
- `corpus/`
- `shared/`
- `tests/`

### 단계 2. 공통 타입 정의

최소 아래 타입을 코드로 만든다.

- `RawCase`
- `RawAttachment`
- `CorpusDocument`

`CorpusDocument`는 기존 [rag_corpus_design.md](C:\Users\SSAFY\Desktop\today-safety-docs\docs\rag_corpus_design.md)의 필드를 그대로 따른다.

최소 필드:

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

### 단계 3. 게시판 수집기 구현

우선 `15121001` 게시판 API 수집기를 구현한다.

최소 요구사항:

- 목록 또는 조회 결과를 받아 `RawCase` 리스트로 변환
- 제목, 본문, 날짜, source URL 유지
- 원본 응답은 재현 가능하도록 raw 저장 가능 구조 고려

### 단계 4. 첨부파일 메타 수집기 구현

`15121008` 첨부파일 API 수집기를 구현한다.

최소 요구사항:

- 게시글 식별자 기준 첨부파일 메타 조회
- 파일명, 확장자, 다운로드 URL 저장
- PDF 여부 식별
- HWP/HWPX는 메타만 유지

### 단계 5. 정규화와 export

게시글과 첨부 메타를 `CorpusDocument` 또는 메타 출력 포맷으로 변환한다.

최소 산출물:

- `corpus_cases.jsonl`
- `corpus_meta.csv`
- `ingestion_failures.csv`

## 5. 이번 시작 단계에서 하지 않는 것

다음 턴에서는 아래를 하지 않는다.

- 벡터 DB 선정
- BM25/embedding 최적화
- LLM 프롬프트 튜닝
- HWP 본문 추출
- 사고유형 분류모델 학습
- 정밀 위험도 모델 구현
- 프론트엔드 구현

즉, 다음 턴의 성공 기준은 `검색 가능한 근거 코퍼스의 첫 버전`을 만드는 것이다.

## 6. 완료 기준

다음 턴의 최소 완료 기준은 아래다.

- `15121001` 수집기 동작
- `15121008` 첨부 메타 수집기 동작
- 공통 `CorpusDocument` 스키마 코드화
- JSONL/CSV export 가능
- 실패 케이스를 별도 파일로 남길 수 있음

여기까지 되면 그다음 턴에서 바로 아래로 이어간다.

1. PDF 다운로드
2. PDF 본문 추출
3. SIF 연결
4. 검색 API 또는 내부 검색 함수 구현

## 7. 다음 턴 시작 문장 권장안

다음 턴에서 바로 이어서 요청하려면 아래처럼 시작하면 된다.

`today-safety-rag 구현 시작. 15121001 게시판 수집기, 15121008 첨부파일 메타 수집기, CorpusDocument 스키마, JSONL export까지 한 번에 구현해줘.`
