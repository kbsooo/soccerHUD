# SoccerHUD Chrome Extension

## Phase 2 MVP

YouTube 축구 영상에서 선수와 공을 실시간으로 탐지하고 오버레이로 표시하는 크롬 익스텐션입니다.

## 파일 구조

```
extension/
├── manifest.json         # 익스텐션 설정
├── content.js           # 메인 로직 (비디오 캡처, 오버레이)
├── background.js        # Service Worker (상태 관리)
├── popup.html          # 팝업 UI
├── popup.js            # 팝업 로직
├── styles/
│   └── overlay.css     # 오버레이 스타일
└── icons/
    ├── icon16.png      # (TODO)
    ├── icon48.png      # (TODO)
    └── icon128.png     # (TODO)
```

## 설치 방법 (개발 모드)

### 1. Python 서버 실행

먼저 백엔드 서버를 실행해야 합니다:

```bash
cd /path/to/soccerHUD
source .venv/bin/activate
python src/main.py
```

서버가 `ws://localhost:8765/ws`에서 실행됩니다.

### 2. 크롬 익스텐션 로드

1. Chrome 브라우저에서 `chrome://extensions/` 접속
2. 우측 상단의 "개발자 모드" 활성화
3. "압축해제된 확장 프로그램을 로드합니다" 클릭
4. `soccerHUD/extension` 폴더 선택

### 3. 사용 방법

1. YouTube에서 축구 영상 재생
   - 테스트: https://www.youtube.com/watch?v=tKg81nVeoUI
2. 익스텐션 아이콘 클릭
3. "활성화" 버튼 클릭
4. 비디오에 오버레이가 표시됨!

## 주요 기능

### Content Script (content.js)

- ✅ YouTube 비디오 요소 자동 감지
- ✅ Canvas API로 프레임 캡처 (5 FPS)
- ✅ WebSocket으로 서버에 프레임 전송
- ✅ SVG 오버레이 렌더링
- ✅ 선수 바운딩 박스 (빨강/파랑)
- ✅ 공 표시 (초록색)
- ✅ 공 소유자 강조 (노란색)

### Popup UI (popup.html/js)

- ✅ 활성화/비활성화 토글
- ✅ 연결 상태 표시
- ✅ 서버 상태 확인

### Background Service Worker (background.js)

- ✅ 활성화 상태 저장
- ✅ Content Script와 통신

## 설정

`content.js`의 `CONFIG` 객체에서 설정 변경 가능:

```javascript
const CONFIG = {
  SERVER_URL: 'ws://localhost:8765/ws',  // 서버 주소
  CAPTURE_FPS: 5,                        // 초당 프레임 수
  RECONNECT_DELAY: 3000,                 // 재연결 대기 시간
};
```

## 알려진 제한사항

### 공 탐지 이슈
- 사전학습 YOLO 모델이 축구공을 잘 탐지하지 못함
- 8개 프레임 중 1개만 탐지 (12.5%)
- **해결 예정**: Phase 5 파인튜닝

### 성능
- 현재 5 FPS로 캡처 (서버 부하 고려)
- 네트워크 대역폭: ~2 MB/s
- YOLO 추론 2번 실행 (선수 + 공)

### 지원 플랫폼
- ✅ YouTube (테스트 완료)
- ❌ 쿠팡플레이 (DRM, Phase 6에서 지원 예정)

## 디버깅

### Console 로그 확인

**Content Script**:
- F12 → Console 탭
- 로그: `🎯 SoccerHUD Content Script 로드됨`

**Background Worker**:
- `chrome://extensions/` → "Service Worker" 클릭
- 로그: `🔧 SoccerHUD Background Service Worker 시작`

**Popup**:
- 팝업 우클릭 → "검사"

### 일반적인 문제

**"비디오를 찾지 못함"**
- YouTube 페이지 새로고침
- 비디오 재생 시작

**"WebSocket 연결 실패"**
- Python 서버가 실행 중인지 확인
- `ws://localhost:8765/ws` 접근 가능한지 확인

**"오버레이가 안 보임"**
- Console에서 에러 확인
- 서버 응답 확인 (Network 탭)

## TODO (Phase 2 완성)

- [ ] 아이콘 제작 (16x16, 48x48, 128x128)
- [ ] 에러 처리 개선
- [ ] FPS 자동 조절
- [ ] 오버레이 스타일 개선
- [ ] 설정 UI (FPS, 색상 등)

## Phase 3 이후

- [ ] 선수 이름 표시
- [ ] 등번호 OCR
- [ ] DeepSORT 추적
- [ ] 사용자 입력 (선수 명단)
