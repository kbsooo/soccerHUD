# 디버깅 테스트 가이드

## 변경 사항

`extension/content.js`에 상세한 디버깅 로그를 추가했습니다:

1. **WebSocket 메시지 수신**: 메시지가 도착하는지 확인
2. **JSON 파싱**: 데이터가 올바르게 파싱되는지 확인
3. **renderOverlay 호출**: 함수가 호출되는지 확인
4. **비디오 크기**: 비디오 크기와 스케일 계산 확인
5. **선수 그리기**: 각 선수가 그려지는 과정 확인
6. **SVG 요소 추가**: SVG rect 요소가 실제로 추가되는지 확인

## 테스트 방법

### 1단계: 크롬 익스텐션 리로드

1. Chrome에서 `chrome://extensions/` 열기
2. SoccerHUD 익스텐션 찾아서 **새로고침** 버튼 클릭 🔄
3. **반드시 리로드 해야 수정된 content.js가 적용됩니다!**

### 2단계: YouTube 페이지 새로고침

1. YouTube 축구 영상 페이지를 **완전히 새로고침** (Cmd+Shift+R 또는 Ctrl+Shift+F5)
2. 개발자 도구 열기 (F12)
3. Console 탭 선택

### 3단계: SoccerHUD 활성화

1. 익스텐션 아이콘 클릭
2. "활성화" 버튼 클릭

### 4단계: 영상 재생 및 로그 확인

영상을 재생하면 다음과 같은 로그가 나와야 합니다:

```
📦 WebSocket 메시지 수신: {"timestamp":...
✅ JSON 파싱 성공: {players: 15, ball: false, ball_owner: null}
🎨 renderOverlay 호출됨
🧹 기존 오버레이 지움
📐 비디오 크기: {displayWidth: 1365, displayHeight: 768, videoWidth: 640, videoHeight: 360}
⚽ 공 소유자 ID: null
👥 선수 15명 그리기 시작
  - 선수 #0: ID=1, team=home, hasBall=false
    🎨 drawPlayer: x=123.4, y=234.5, w=45.6, h=78.9
    🎨 색상: #FF0000
    ✅ rect 추가됨, overlayContainer 자식 수: 1
  - 선수 #1: ID=2, team=away, hasBall=false
    ...
✅ 선수 그리기 완료
⚠️ 공 탐지 없음
```

## 예상되는 문제들

### 문제 1: "📦 WebSocket 메시지 수신" 로그가 안 나옴
**원인**: WebSocket 연결이 제대로 안됨
**해결**: 서버가 실행 중인지 확인 (`ws://localhost:8765/ws`)

### 문제 2: JSON 파싱은 성공하지만 players가 0
**원인**: DeepSORT가 카메라 전환으로 인식하고 리셋함
**해결**: `src/tracker.py`의 `camera_switch_threshold` 값을 높이기 (현재 0.5 → 0.8)

### 문제 3: "🎨 renderOverlay 호출됨" 로그가 안 나옴
**원인**: WebSocket onmessage 핸들러가 실행 안됨
**해결**: 크롬 익스텐션을 완전히 제거 후 재설치

### 문제 4: rect가 추가되지만 화면에 안 보임
**원인**: SVG 오버레이가 비디오 뒤에 숨어있거나 z-index 문제
**해결**:
1. 개발자 도구 Elements 탭에서 `#soccerhud-overlay` 요소 찾기
2. `z-index` 값 확인 (현재: 9999)
3. 비디오 플레이어가 fullscreen API를 사용하는지 확인

### 문제 5: 로그는 완벽한데 화면에 안 보임
**원인**: YouTube 플레이어가 오버레이를 덮어씀
**가능한 해결책**:
- SVG 대신 Canvas 오버레이 사용
- YouTube Player API를 사용해서 커스텀 컨트롤 추가

## 다음 단계

로그를 확인한 후 @console.md에 붙여넣어주세요. 어느 단계에서 문제가 발생하는지 파악하겠습니다.

특히 다음 로그들이 중요합니다:
- ✅ JSON 파싱 성공 → players 개수 확인
- 🎨 renderOverlay 호출됨 → 함수가 실행되는지 확인
- ✅ rect 추가됨 → SVG 요소가 생성되는지 확인
- overlayContainer 자식 수 → 실제로 DOM에 추가되는지 확인
