# Schema Summary

## Common Event Schema

| Column | Description |
| --- | --- |
| `source_dataset_id` | 원본 데이터셋 ID |
| `source_record_id` | 원본 레코드를 재현할 수 있는 내부 키 |
| `source_year` | 사고 또는 통계 기준 연도 |
| `industry_major` | 표준화된 상위 업종 |
| `industry_minor` | 원본 업종명 또는 세부 업종 |
| `job_title_raw` | 원본 직종/직무명 |
| `job_group_standard` | 표준화된 직무 그룹 |
| `process_group_standard` | 표준화된 작업공정 그룹 |
| `accident_type_raw` | 원본 사고유형 관련 텍스트 |
| `accident_type_standard` | 표준화된 사고유형 |
| `injury_or_disease_type` | 원본 상병/재해종류 요약 |
| `hazard_factor_standard` | 표준화된 위험요인 그룹 |
| `severity_band` | fatal_or_sif/serious/general/unknown |
| `worker_type` | employee/foreign_worker/special_worker/unknown |
| `employment_type` | 고용형태 또는 노무제공 구분 |
| `company_size_band` | 통합 사업장 규모 구간 |
| `region` | 지역 텍스트 |
| `weather_linkable` | 기상 데이터 결합 가능 여부 |
| `chemical_related` | 화학물질 관련 여부 |
| `narrative_text` | 사례 본문 또는 요약 |
| `countermeasure_text` | 감소대책 또는 대응 문장 |

## Source Mapping

| Dataset | Source | Key fields used | Notes |
| --- | --- | --- | --- |
| `15140383` | SIF 아카이브 | 산재업종/재해개요/재해유발요인/감소대책 | fatal_or_sif 고정, 제조업/건설업 시트 분리 처리 |
| `3082968` | 최초요양 승인 정보 | 업종명/재해발생형태/세부상병명/재해일자/직종명/성별/연령대 | 승인 통계 기반, narrative 비어 있음 |
| `15121557` | 외국인근로자 산재처리 상세현황 | 재해발생형태/산재업종/사업장규모/지역본부 | foreign_worker 고정 |
| `15104692` | 특수형태근로종사자 산재처리현황 | 직종별 연도 집계 | 이벤트가 아닌 priors 테이블용 |
| `15002150` | 고용 산재보험 가입 현황 | 업종명/사업장 주소/상시근로자수 | ZIP 내부 연도별 CSV 전량 집계 |
