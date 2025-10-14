# Architecture Overview

본 문서는 크롬 MV3 확장 기반 MVP의 구조, 추론 파이프라인, 핵심 데이터 계약을 간결히 요약합니다. 세부 운영/절차는 `AGENT/AGENTS.md`를 참고하세요.

## MV3 구성요소
- Background(Service Worker)
  - 메시지 브로커, 단축키 처리, 사용자 설정 저장(sync/local).
- Content Script
  - `<video>` 요소 탐지, 오버레이 DOM/Canvas 주입, 프레임 추출(OffscreenCanvas).
- Inference Worker
  - 다운스케일→감지(사람/공)→추적(SORT 계열)→소유자 추정→스무딩.
  - ONNX Runtime Web(WebGPU/WASM) 또는 MediaPipe 경량 감지기.
- Overlay Renderer
  - 박스/라벨/디버그 HUD 렌더, 사용자 클릭 이벤트 전달.

## 파이프라인 개요
1) 프레임 캡처(다운스케일, 색상 정규화)
2) 감지: 사람(person), 공(ball) 박스 + 점수
3) 추적: 칼만필터+IoU(appearance 미사용)로 ID 안정화
4) 소유자 추정: 공-선수 거리/속도/접촉 지속시간 히스토리 기반 간단 규칙
5) 라벨 안정화: 지수평활, 화면 이탈/오클루전 시 페이드아웃
6) 렌더: 화면 좌표 변환, 팀 컬러/이름 적용

## 데이터 계약(요약)
- Detection
  - `id: string`(optional), `cls: 'person'|'ball'`, `conf: number`, `bbox: [x,y,w,h]`(0–1 정규화)
- Track
  - `trackId: number`, `bbox: [x,y,w,h]`, `velocity?: [vx,vy]`, `conf: number`
- Ownership
  - `playerTrackId: number|null`, `confidence: number`, `updatedAt: number`
- Roster(JSON)
  - `{ team: string, color?: string, players: Array<{ number: string|number, name: string }> }`

예시(Roster):
```json
{
  "team": "FC Example",
  "color": "#1144cc",
  "players": [
    { "number": 7, "name": "Kim" },
    { "number": 10, "name": "Lee" }
  ]
}
```

메시지(간단):
- `CS→Worker`: `{ type: 'FRAME', imageBitmap, ts }`
- `Worker→CS`: `{ type: 'OVERLAY', tracks, ownership, debug? }`
- `CS↔BG`: 설정/단축키/상태 동기화

## 성능 전략(핵심)
- 입력 다운스케일(예: 너비 640), ROI 우선 탐색, 프레임 스킵(동적)
- WebGPU 우선, 미지원 시 WASM 경로로 폴백, 연산량 스로틀
- 디버그 HUD 오프 시 최소 렌더, 객체 수 제한(Top-K)

## 제약/주의
- DRM/보호 콘텐츠: 픽셀 접근 불가 시 브라우저 내 추론 비권장
- 저해상도/압축 강한 소스: 공/등번호 인식 신뢰도 급락
- 노트북 환경 발열/스로틀링 고려(프레임레이트 자동 하향)

## 향후 고도화 메모
- 팀 컬러 분류로 팀 식별 보조
- 컷 전환 감지(히스토그램/검은 프레임) 후 추적 리셋/재동기화
- 등번호 OCR(숫자 전용) + 포즈로 등/가슴 영역 크롭
