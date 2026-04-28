# Frontend API And Data Contract

## 1. 목적

이 문서는 Today Safety 프론트엔드가 백엔드와 어떤 방식으로 연결되어야 하는지 정리한다.

초기 목표는 복잡한 다중 API 연결이 아니라, `새 브리핑 생성 화면`에서 입력값을 받아 `브리핑 초안`을 보여주는 것이다.

## 2. MVP 연결 원칙

- 프론트는 구조화 폼 입력을 받는다.
- 백엔드에는 우선 자연어 질의 중심으로 전달한다.
- 백엔드가 검색과 생성 오케스트레이션을 담당한다.
- 프론트는 결과를 `위험요약`, `사고유형`, `체크리스트`, `브리핑 문안`, `근거 사례`로 재구성해 렌더링한다.

## 3. 우선 연결 API

### `POST /brief-draft-preview`

초기 MVP에서 가장 먼저 연결할 API로 둔다.

요청 목적:

- 사용자가 입력한 작업 조건을 바탕으로 브리핑 초안을 생성

예시 요청:

```json
{
  "query": "건설 현장 실외 철골 작업 중 크레인으로 자재 인양 예정. 강풍 예보가 있고 고소작업이 포함됨.",
  "top_k": 3,
  "search_mode": "hybrid",
  "weather": {
    "grid_x": 60,
    "grid_y": 127,
    "region_label": "Seoul"
  },
  "chemical_names": []
}
```

### 후속 연결 후보

- `POST /recommendation-context`
  - 결과 생성 전 추천 컨텍스트를 분리 조회할 때 사용
- `POST /brief-generation-inputs`
  - 구조화 입력 조합을 서버에서 별도 처리할 때 사용
- `GET /brief-generators`
  - 브리핑 생성기 버전, 프리셋, 엔진 정보 노출 시 사용
- `GET /health`
  - 프론트 운영 상태 체크용

## 4. 폼 입력을 API 질의로 조합하는 규칙

### 프론트 입력 예시

- 산업군: 건설
- 작업 유형: 철골 작업, 자재 인양
- 작업 장소: 실외
- 고소작업 여부: 예
- 중장비: 크레인
- 화학물질: 없음
- 날씨: 강풍
- 추가 설명: 오늘은 자재 인양 작업이 예정되어 있고 강풍 예보가 있음

### 조합 질의 예시

```text
건설 현장 실외 철골 작업 중 크레인으로 자재 인양 예정. 강풍 예보가 있고 고소작업이 포함됨. 오늘은 자재 인양 작업이 예정되어 있음.
```

### 조합 원칙

- 자연어 질의는 프론트에서 조합하되 과장된 해석은 넣지 않는다.
- 사용자가 입력한 사실과 선택값만 연결한다.
- 선택 입력이 비어 있으면 문장에 억지로 넣지 않는다.
- 화학물질명은 질의 본문과 `chemical_names` 배열에 모두 반영할 수 있다.

## 5. 프론트 내부 입력 모델 제안

```ts
type BriefInputForm = {
  industryMajor: string
  workTypes: string[]
  workLocation: "indoor" | "outdoor"
  isHeightWork: boolean | null
  equipmentNames: string[]
  chemicalNames: string[]
  weatherMode: "auto" | "manual" | "none"
  weatherLabel?: string
  weatherGridX?: number
  weatherGridY?: number
  regionLabel?: string
  crewSize?: number
  shift?: "morning" | "afternoon" | "night"
  notes: string
}
```

## 6. 프론트 내부 결과 모델 제안

```ts
type AccidentTypeItem = {
  rank: number
  label: string
  causes: string[]
  action: string
  evidenceIds: string[]
}

type ChecklistItem = {
  id: string
  text: string
  evidenceIds: string[]
  checked?: boolean
}

type EvidenceItem = {
  id: string
  title: string
  summary: string
  sourceName: string
  sourceUrl?: string
  accidentTypes: string[]
  similarityLabel?: string
}

type BriefDraftResult = {
  requestId: string
  summary: string
  accidentTypes: AccidentTypeItem[]
  checklist: ChecklistItem[]
  briefingText: string
  evidence: EvidenceItem[]
  reviewStatus: "draft" | "editing" | "approved" | "rejected"
}
```

## 7. 결과 응답이 바로 맞지 않을 때의 프론트 처리

초기 백엔드 응답이 프론트 최종 구조와 정확히 일치하지 않을 가능성이 높다.

따라서 프론트에는 `response mapper` 계층을 둔다.

역할:

- 검색 결과와 생성 결과를 화면 전용 모델로 변환
- 누락된 필드는 안전한 기본값으로 채움
- 근거 사례와 사고유형의 연결 키를 맞춤

예시 규칙:

- 사고유형이 3개 미만이면 받은 개수만 표시
- 체크리스트가 없으면 브리핑 문안에서 행동문 후보를 추출하지 않고 빈 상태로 둠
- 근거 URL이 없으면 원문 버튼을 숨김

## 8. 네트워크 상태 처리

### 생성 요청 중

- 결과 패널에 스켈레톤 표시
- 단계 문구 노출
  - `유사 사례 검색 중`
  - `위험요약 생성 중`
  - `체크리스트 정리 중`

### 생성 실패

- 폼 값 유지
- `다시 생성하기` 버튼 제공
- 실패 사유는 사용자 친화적으로 축약

### 부분 실패

- 날씨 조회 실패
  - 수동 날씨 선택으로 전환
- 근거 일부 누락
  - 브리핑 결과는 보여주되 근거 섹션에 `일부 근거를 불러오지 못함` 표시

## 9. 저장 및 히스토리 확장 방향

초기 MVP에서는 생성 결과를 화면에 보여주는 것만으로 시작할 수 있다.

다음 단계에서는 아래 저장 API가 필요해진다.

- `POST /briefs`
  - 초안 저장
- `PATCH /briefs/:id`
  - 수정/승인 상태 반영
- `GET /briefs`
  - 히스토리 목록
- `GET /briefs/:id`
  - 과거 브리핑 상세

현재 저장 API가 없다면 프론트 문서 구조는 먼저 고정하고, 구현 시점에 백엔드와 계약을 추가 정의한다.

## 10. 프론트 구현 순서 제안

1. 입력 폼 상태 모델 구현
2. 자연어 질의 조합 유틸 구현
3. `POST /brief-draft-preview` 연결
4. 결과 매퍼 구현
5. 결과 화면 렌더링
6. 승인 상태와 히스토리 API 확장
