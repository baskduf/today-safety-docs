# API Reference Notes

Today Safety에 직접 연결할 가능성이 높은 API를 우선 정리했습니다.

## 1. 국내재해사례 게시판 정보 조회서비스

- 데이터셋 ID: `15121001`
- 포털 페이지: [data.go.kr/dataset/15121001](https://www.data.go.kr/data/15121001/openapi.do)
- 활용 목적: 업종별 유사 재해사례 검색, RAG 근거 보강
- 비고:
  - 게시판 종류(`business`)를 넣어 제조업, 건설업, 조선업 등으로 조회
  - 첨부파일은 별도 데이터셋 `15121008`에서 조회
  - 영문 포털 스니펫 기준 요청 링크:
    - `http://apis.data.go.kr/B552468/disaster_api02/getdisaster_api02`

## 1-1. 국내재해사례 게시판 첨부파일 정보 조회서비스

- 데이터셋 ID: `15121008`
- 포털 페이지: [data.go.kr/dataset/15121008](https://www.data.go.kr/data/15121008/openapi.do)
- 활용 목적: 재해사례 첨부 PDF/HWP 원문 확보
- 비고:
  - 게시판 번호(`boardno`)로 첨부파일 목록 조회
  - 재해사례 API와 조합해야 실제 사례 원문까지 확보 가능

## 2. 사고사망 게시판 정보 조회서비스

- 데이터셋 ID: `15119137`
- 포털 페이지: [data.go.kr/dataset/15119137](https://www.data.go.kr/data/15119137/openapi.do)
- 활용 목적: 최신 사망사고 패턴 보강, 최근 중대위험 근거 제시
- 비고:
  - `callApiId = 1040` 고정값 사용
  - 포털 공지 기준 변경 후 URL:
    - `http://apis.data.go.kr/B552468/news_api02`

## 3. 물질안전보건자료(MSDS)

- 데이터셋 ID: `15001197`
- 포털 페이지: [data.go.kr/dataset/15001197](https://www.data.go.kr/data/15001197/openapi.do)
- 활용 목적: 화학물질 사용 작업의 주의사항, 보호구, 취급 경고 생성
- 서비스 URL:
  - `http://msds.kosha.or.kr/openapi/service/msdschem/chemlist`
- 비고:
  - 목록 조회 후 상세 조회를 조합하는 방식으로 활용
  - 포털 안내상 공단 제공 정보는 참고용이며, 공식 MSDS 작성 책임은 제조·수입자에게 있음

## 4. 기상청 단기예보 조회서비스

- 데이터셋 ID: `15084084`
- 포털 페이지: [data.go.kr/dataset/15084084](https://www.data.go.kr/data/15084084/openapi.do)
- 활용 목적: 당일 작업 위험 보강, 우천·강풍·폭염 등 기상 경고 생성
- 대표 서비스 URL:
  - `http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst`
- 비고:
  - 초단기실황, 초단기예보, 단기예보를 함께 검토하는 편이 좋음

## 4-1. 기상청 지상(종관, ASOS) 시간자료 조회서비스

- 데이터셋 ID: `15057210`
- 포털 페이지: [data.go.kr/dataset/15057210](https://www.data.go.kr/data/15057210/openapi.do)
- 활용 목적: 실제 관측된 강수, 풍속, 습도, 기온 기반 위험 보정
- 요청주소:
  - `http://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList`
- 서비스 URL:
  - `http://apis.data.go.kr/1360000/AsosHourlyInfoService`

## 5. 안전보건자료 링크 서비스

- 데이터셋 ID: `15139398`
- 포털 페이지: [data.go.kr/dataset/15139398](https://www.data.go.kr/data/15139398/openapi.do)
- 활용 목적: 업종·재해유형별 공식 교육자료/영상/책자 링크 추천
- 변경 후 URL 공지 기준 서비스 URL:
  - `http://apis.data.go.kr/B552468/selectMediaList01`
- 비고:
  - 코드 목록 XLSX를 같이 내려받아 업종/재해유형 코드 테이블로 관리하는 편이 좋음

## 6. 기술지원규정(KOSHA GUIDE) 조회 서비스

- 데이터셋 ID: `15144147`
- 포털 페이지: [data.go.kr/dataset/15144147](https://www.data.go.kr/data/15144147/openapi.do?recommendDataYn=Y)
- 활용 목적: 공식 기술 가이드 문서와 규정 근거 연결
- 비고:
  - 규정명, 규정번호, 공표일자, 다운로드 링크 조회 가능

## 7. NCS 기준정보 조회

- 데이터셋 ID: `15128213`
- 포털 페이지: [data.go.kr/dataset/15128213](https://www.data.go.kr/data/15128213/openapi.do)
- 활용 목적: 직종, 작업공정군, 능력단위 taxonomy 설계
- 비고:
  - 작업 입력값 정규화와 표준화에 도움

## 8. 건설현장 안전 신호등

- 데이터셋 ID: `15139182`
- 포털 페이지: [data.go.kr/dataset/15139182](https://www.data.go.kr/data/15139182/openapi.do)
- 활용 목적: 건설업 MVP에서 최신 기술지도 결과 반영
- 비고:
  - 중소규모 건설 현장 최근 지도 결과를 색상 구분 형태로 활용 가능

## 9. 보호구 안전인증 현황

- 데이터셋 ID: `15139497`
- 포털 페이지: [data.go.kr/dataset/15139497](https://www.data.go.kr/data/15139497/openapi.do?recommendDataYn=Y)
- 활용 목적: 보호구 추천 결과에 인증 근거 추가

## 10. 산재보험 요양 신청·승인 데이터

- 데이터셋 ID: `15144645`
- 포털 페이지: [data.go.kr/dataset/15144645](https://www.data.go.kr/data/15144645/openapi.do)
- 활용 목적: 승인 데이터 증분 수집, 세부 조건별 조회
- 비고:
  - 포털 설명상 과거 10년 데이터 제공
  - 공식 산업재해 통계와 상이할 수 있다는 주의사항 존재

## 11. API 운영 메모

- 공공데이터포털 인증키(`ServiceKey`)가 필요합니다.
- MVP는 파일데이터로 기본 코퍼스를 만들고, API는 최신성 보강 레이어로 붙이는 것이 가장 안정적입니다.
- API 응답 자체는 수시로 바뀔 수 있으므로 운영 시 호출 로그와 캐시 전략을 두는 편이 좋습니다.
