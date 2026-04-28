# Data Quality Report

## Snapshot

- master incident rows: `167356`
- taxonomy rows: `10993`
- company context prior rows: `95877`
- worker segment prior rows: `498`
- duplicate source records: `0`

## Coverage

- accident taxonomy coverage: `79.51%`
- industry taxonomy coverage: `83.07%`
- process taxonomy explicit coverage: `58.28%`

## Blank Rates

| Column | Blank ratio |
| --- | --- |
| `source_dataset_id` | 0.00% |
| `source_record_id` | 0.00% |
| `source_year` | 0.00% |
| `industry_major` | 0.00% |
| `industry_minor` | 0.00% |
| `job_title_raw` | 3.60% |
| `job_group_standard` | 0.00% |
| `process_group_standard` | 0.00% |
| `accident_type_raw` | 0.00% |
| `accident_type_standard` | 0.00% |
| `injury_or_disease_type` | 1.66% |
| `hazard_factor_standard` | 0.00% |
| `severity_band` | 0.00% |
| `worker_type` | 0.00% |
| `employment_type` | 0.00% |
| `company_size_band` | 0.00% |
| `region` | 0.00% |
| `narrative_text` | 96.40% |
| `countermeasure_text` | 96.40% |

- `narrative_text` blank ratio: `96.40%`
- `countermeasure_text` blank ratio: `96.40%`

## Match Strategy Counts

### industry

| Strategy | Count |
| --- | ---: |
| `fallback` | 28334 |
| `keyword:가공` | 339 |
| `keyword:가스` | 30 |
| `keyword:건설` | 39792 |
| `keyword:건축` | 342 |
| `keyword:광업` | 1630 |
| `keyword:금속` | 905 |
| `keyword:기계` | 1371 |
| `keyword:기타의사업` | 1958 |
| `keyword:농업` | 498 |
| `keyword:보건` | 9443 |
| `keyword:서비스` | 17804 |
| `keyword:소매` | 10167 |
| `keyword:수도` | 63 |
| `keyword:숙박` | 13611 |
| `keyword:어업` | 91 |
| `keyword:운송` | 63 |
| `keyword:운수` | 5889 |
| `keyword:인쇄` | 331 |
| `keyword:임업` | 106 |
| `keyword:자동차` | 1418 |
| `keyword:전기` | 137 |
| `keyword:제조` | 30477 |
| `keyword:창고` | 204 |
| `keyword:철골` | 208 |
| `keyword:축산` | 230 |
| `keyword:택배` | 1424 |
| `keyword:토공` | 206 |
| `keyword:하역` | 285 |

### job

| Strategy | Count |
| --- | ---: |
| `empty` | 6032 |
| `identity` | 71049 |
| `keyword:가공` | 735 |
| `keyword:건설` | 32756 |
| `keyword:검사원` | 611 |
| `keyword:경비` | 1433 |
| `keyword:관리` | 3984 |
| `keyword:기사` | 7188 |
| `keyword:배관` | 843 |
| `keyword:배달` | 981 |
| `keyword:배송` | 68 |
| `keyword:설비` | 538 |
| `keyword:용접` | 2317 |
| `keyword:운전` | 2914 |
| `keyword:점검` | 296 |
| `keyword:정비` | 2212 |
| `keyword:제조` | 17026 |
| `keyword:조작원` | 6524 |
| `keyword:지게차` | 1 |
| `keyword:청소` | 8446 |
| `keyword:크레인` | 44 |
| `keyword:택배` | 1317 |
| `keyword:화학` | 41 |

### process

| Strategy | Count |
| --- | ---: |
| `fallback` | 69826 |
| `keyword:가공` | 1962 |
| `keyword:거푸집` | 4 |
| `keyword:건설관련 기능` | 8302 |
| `keyword:건설구조관련` | 929 |
| `keyword:검사` | 611 |
| `keyword:검침` | 217 |
| `keyword:경비` | 1433 |
| `keyword:굴삭기` | 5 |
| `keyword:굴착` | 110 |
| `keyword:금속공작` | 347 |
| `keyword:금형` | 256 |
| `keyword:기계조작원` | 2700 |
| `keyword:도금` | 467 |
| `keyword:도장` | 158 |
| `keyword:리프트` | 82 |
| `keyword:마감` | 1316 |
| `keyword:목재` | 440 |
| `keyword:방수` | 80 |
| `keyword:배관` | 843 |
| `keyword:배달` | 981 |
| `keyword:배송` | 68 |
| `keyword:비계` | 98 |
| `keyword:상하차` | 136 |
| `keyword:생산기 조작` | 727 |
| `keyword:설치` | 2526 |
| `keyword:수리` | 19 |
| `keyword:시험원` | 77 |
| `keyword:용접` | 2317 |
| `keyword:운반` | 340 |
| `keyword:운송` | 2414 |
| `keyword:음식관련` | 4538 |
| `keyword:음식서비스` | 4647 |
| `keyword:이동` | 336 |
| `keyword:인양` | 205 |
| `keyword:전기` | 5381 |
| `keyword:절단` | 77 |
| `keyword:점검` | 463 |
| `keyword:정리` | 9 |
| `keyword:정비` | 1120 |
| `keyword:제관` | 285 |
| `keyword:제조관련` | 17026 |
| `keyword:조리사` | 7521 |
| `keyword:조립` | 1229 |
| `keyword:주차` | 1 |
| `keyword:지게차` | 149 |
| `keyword:채굴` | 529 |
| `keyword:천공` | 1 |
| `keyword:철근` | 104 |
| `keyword:청소` | 8878 |
| `keyword:퀵서비스` | 6692 |
| `keyword:크레인` | 302 |
| `keyword:택배` | 1317 |
| `keyword:토공` | 73 |
| `keyword:토목` | 651 |
| `keyword:통행` | 132 |
| `keyword:폐기물` | 8 |
| `keyword:하역` | 2439 |
| `keyword:해체` | 334 |
| `keyword:화물차` | 2658 |
| `keyword:화학` | 460 |

### accident

| Strategy | Count |
| --- | ---: |
| `fallback` | 34299 |
| `keyword:감전` | 127 |
| `keyword:골절` | 52681 |
| `keyword:관절증` | 1878 |
| `keyword:교통` | 30 |
| `keyword:긴장` | 1 |
| `keyword:끼` | 706 |
| `keyword:낙하` | 483 |
| `keyword:노출` | 1 |
| `keyword:떨어져` | 9 |
| `keyword:떨어짐` | 516 |
| `keyword:무너` | 18 |
| `keyword:무리` | 35 |
| `keyword:반달연골` | 1557 |
| `keyword:부딪` | 204 |
| `keyword:붕괴` | 185 |
| `keyword:비래` | 47 |
| `keyword:상과염` | 799 |
| `keyword:손목터널` | 283 |
| `keyword:수지신경의 손상` | 392 |
| `keyword:신경뿌리병증` | 323 |
| `keyword:연소` | 6 |
| `keyword:열린 상처` | 6402 |
| `keyword:열상` | 5441 |
| `keyword:염좌` | 17068 |
| `keyword:요추` | 3188 |
| `keyword:용제` | 3 |
| `keyword:유해` | 53 |
| `keyword:으깸` | 2988 |
| `keyword:인대의 파열` | 3246 |
| `keyword:적재물` | 4 |
| `keyword:전기` | 1 |
| `keyword:전도` | 227 |
| `keyword:전십자인대` | 863 |
| `keyword:절단` | 3522 |
| `keyword:접촉` | 155 |
| `keyword:중독` | 17 |
| `keyword:중량물` | 1 |
| `keyword:진탕` | 1205 |
| `keyword:질식` | 39 |
| `keyword:찢김` | 74 |
| `keyword:차량` | 22 |
| `keyword:추락` | 2215 |
| `keyword:출퇴근` | 10508 |
| `keyword:충격증후군` | 378 |
| `keyword:충돌` | 37 |
| `keyword:타박상` | 3515 |
| `keyword:폭발` | 25 |
| `keyword:협착` | 1218 |
| `keyword:화상` | 5982 |
| `keyword:화재` | 131 |
| `keyword:화학` | 29 |
| `keyword:회전근개` | 4219 |

### hazard

| Strategy | Count |
| --- | ---: |
| `fallback` | 161324 |
| `keyword:가스` | 21 |
| `keyword:감전` | 66 |
| `keyword:개구부` | 365 |
| `keyword:거푸집` | 117 |
| `keyword:고소` | 226 |
| `keyword:굴착기` | 186 |
| `keyword:기계` | 544 |
| `keyword:도금` | 1 |
| `keyword:맨홀` | 3 |
| `keyword:미끄` | 43 |
| `keyword:바닥` | 1079 |
| `keyword:배선` | 4 |
| `keyword:백호` | 1 |
| `keyword:벨트` | 59 |
| `keyword:보행` | 1 |
| `keyword:붕괴` | 81 |
| `keyword:비계` | 464 |
| `keyword:사다리` | 316 |
| `keyword:산` | 162 |
| `keyword:설비` | 724 |
| `keyword:용접` | 47 |
| `keyword:용제` | 5 |
| `keyword:윤활유` | 1 |
| `keyword:인양` | 38 |
| `keyword:전기` | 133 |
| `keyword:중량물` | 111 |
| `keyword:지게차` | 51 |
| `keyword:지붕` | 467 |
| `keyword:질식` | 19 |
| `keyword:차량` | 81 |
| `keyword:컨베이어` | 77 |
| `keyword:크레인` | 232 |
| `keyword:탱크` | 6 |
| `keyword:통로` | 6 |
| `keyword:폭발` | 15 |
| `keyword:풀리` | 16 |
| `keyword:프레스` | 16 |
| `keyword:하역` | 15 |
| `keyword:혼합기` | 40 |
| `keyword:화물자동차` | 12 |
| `keyword:화재` | 8 |
| `keyword:화학` | 136 |
| `keyword:활선` | 3 |
| `keyword:흙막이` | 34 |

## Process Unmapped Samples

| source_dataset_id | source_record_id | sample_process_raw |
| --- | --- | --- |
| `15140383` | `sif_manufacturing-7` | 지붕, 천장 등 위에서 작업 |
| `15140383` | `sif_manufacturing-8` | 지붕, 천장 등 위에서 작업 |
| `15140383` | `sif_manufacturing-9` | 위험물질 취급 또는 그 장소에서 작업 |
| `15140383` | `sif_manufacturing-13` | 혼재작업(작업자-작업차량) |
| `15140383` | `sif_manufacturing-14` | 혼재작업(작업자-작업차량) |
| `15140383` | `sif_manufacturing-16` | 지붕, 천장 등 위에서 작업 |
| `15140383` | `sif_manufacturing-17` | 위험물질 취급 또는 그 장소에서 작업 |
| `15140383` | `sif_manufacturing-18` | 위험물질 취급 또는 그 장소에서 작업 |
| `15140383` | `sif_manufacturing-19` | 위험물질 취급 또는 그 장소에서 작업 |
| `15140383` | `sif_manufacturing-20` | 위험물질 취급 또는 그 장소에서 작업 |
| `15140383` | `sif_manufacturing-21` | 위험물질 취급 또는 그 장소에서 작업 |
| `15140383` | `sif_manufacturing-22` | 위험물질 취급 또는 그 장소에서 작업 |
| `15140383` | `sif_manufacturing-23` | 위험물질 취급 또는 그 장소에서 작업 |
| `15140383` | `sif_manufacturing-24` | 건설기계 사용 작업 |
| `15140383` | `sif_manufacturing-25` | 그라인더 등 공구 사용 작업 |
| `15140383` | `sif_manufacturing-38` | 설비, 구조물 등 높은 장소에서의 작업 |
| `15140383` | `sif_manufacturing-39` | 원료 투입 작업 |
| `15140383` | `sif_manufacturing-40` | 원료 투입 작업 |
| `15140383` | `sif_manufacturing-41` | 보일러, 공기압축기, 기타 설비 등 사용작업 |
| `15140383` | `sif_manufacturing-43` | 위험물질 취급 또는 그 장소에서 작업 |
