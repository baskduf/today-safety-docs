# Today Safety Docs

공공데이터와 유사 재해사례를 바탕으로, 오늘의 작업에 맞는 위험요약과 브리핑 문안을 생성하는 AI 서비스 문서 저장소입니다.

## 개요

Today Safety는 산업현장의 작업 조건을 입력하면 공공데이터, 유사 재해사례, MSDS, 기상정보를 바탕으로 주요 사고유형과 중대 위험요인을 정리하고, 그 결과를 작업 전 안전 체크리스트와 브리핑 문안으로 전환하는 서비스를 목표로 합니다.

이 프로젝트의 핵심은 `정밀 사고확률 예측기`가 아니라 `공공 안전데이터를 현장 실행문서로 바꾸는 AI 브리핑 생성 서비스`라는 점입니다.
또한 이 서비스는 `위험성평가를 자동 대체하는 시스템`이 아니라 `위험성평가 초안 생성과 작업 전 사전 브리핑을 지원하는 도구`를 지향합니다.

## 핵심 아이디어

- 오늘 작업 조건 기반 위험요약 생성
- 주요 사고유형과 위험요인 우선순위화
- 유사 재해사례와 안전기준 근거 제시
- 작업 전 안전 체크리스트 자동 생성
- 현장 반장 및 관리자용 브리핑 문안 자동 생성

## 문서 구성

- [docs/proposal.md](./docs/proposal.md)
  - 아이디어 제안서와 제품 포지셔닝
- [docs/user_scenarios.md](./docs/user_scenarios.md)
  - 사용자 시나리오 및 활용 흐름
- [docs/technical_architecture.md](./docs/technical_architecture.md)
  - 권장 프레임워크, 시스템 구조, 구현 전략
- [docs/implementation_feasibility_review.md](./docs/implementation_feasibility_review.md)
  - 실제 공개 데이터셋 기준 구현 가능성 검토
- [docs/rag_corpus_design.md](./docs/rag_corpus_design.md)
  - 건설+제조 중심 RAG 코퍼스 범위, 스키마, 저장 구조 설계
- [docs/rag_ingestion_todo.md](./docs/rag_ingestion_todo.md)
  - RAG 수집 구현 순서와 완료 기준 작업목록
- [frontend/README.md](./frontend/README.md)
  - 프론트엔드 MVP 구상과 화면/컴포넌트/API 문서 모음
- [docs/★주요 공공데이터 및 우수사례 모음집.pdf](./docs/%E2%98%85%EC%A3%BC%EC%9A%94%20%EA%B3%B5%EA%B3%B5%EB%8D%B0%EC%9D%B4%ED%84%B0%20%EB%B0%8F%20%EC%9A%B0%EC%88%98%EC%82%AC%EB%A1%80%20%EB%AA%A8%EC%9D%8C%EC%A7%91.pdf)
  - 참고용 공공데이터 및 우수사례 자료집

## 구현 방향 요약

- 프론트엔드: Next.js + TypeScript
- 백엔드: FastAPI + Pydantic
- AI 계층: Python 서비스 레이어 + OpenAI Responses API
- 데이터 저장소: PostgreSQL
- 데이터 결합: 공공데이터 API + 사례 검색 + 생성형 AI
- 현재 MVP 우선순위: 건설·제조 중심 검색 기반 브리핑 생성

초기 단계에서는 프론트엔드와 백엔드를 분리하고, AI는 별도 독립 서비스로 떼지 않고 백엔드 내부 계층으로 포함하는 구조를 기본 전략으로 합니다.

## 제품 정의

이 서비스는 다음을 목표로 합니다.

- 현장의 복잡한 안전자료를 오늘 작업용 위험 브리핑으로 전환
- 중소사업장의 사전 위험 인지와 브리핑 품질 향상
- 공공데이터를 실제 행동지침으로 바꾸는 실용형 AI 제공
- 승인자 검토를 전제로 한 작업 전 체크리스트 초안과 브리핑 초안 제공

즉, Today Safety는 `자동 안전판정 시스템`이 아니라 `작업 전 위험 해석과 브리핑 생성 서비스`로 정의하는 것이 가장 현실적입니다.

## 단계별 진화 경로

1. 문서/데이터 정비
2. 검색 중심 MVP 구축
3. 하이브리드 분류/생성 고도화
4. 현장 승인·수정 로그 기반 위험도 보정 및 개인화
