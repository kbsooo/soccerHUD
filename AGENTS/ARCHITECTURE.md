# 시스템 아키텍처 상세 설계

## 🏛️ 전체 구조

```
┌─────────────────────────────────────────────────────────────┐
│                      사용자 브라우저                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Chrome Extension                           │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │  Content Script (injected)                  │    │    │
│  │  │  - Video element 감지                       │    │    │
│  │  │  - Canvas로 프레임 캡처 (30fps)            │    │    │
│  │  │  - SVG 오버레이 렌더링                      │    │    │
│  │  └──────────────┬──────────────────────────────┘    │    │
│  │                 │                                    │    │
│  │  ┌──────────────┴──────────────────────────────┐    │    │
│  │  │  Background Service Worker                   │    │    │
│  │  │  - WebSocket 연결 관리                       │    │    │
│  │  │  - 상태 관리 (연결/끊김)                    │    │    │
│  │  │  - Storage API (설정 저장)                  │    │    │
│  │  └──────────────┬──────────────────────────────┘    │    │
│  │                 │                                    │    │
│  │  ┌──────────────┴──────────────────────────────┐    │    │
│  │  │  Popup UI                                    │    │    │
│  │  │  - 활성화 토글                               │    │    │
│  │  │  - 설정 (FPS, 민감도)                       │    │    │
│  │  │  - 경기 정보 입력                            │    │    │
│  │  └──────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ WebSocket (ws://localhost:8765)
                         │ JSON messages
                         │
┌────────────────────────┴────────────────────────────────────┐
│                  Electron Companion App                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Main Process (Node.js)                              │   │
│  │  - Python 서버 프로세스 관리                         │   │
│  │  - 시스템 트레이 UI                                  │   │
│  │  - 자동 업데이트                                     │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                            │
│  ┌──────────────┴───────────────────────────────────────┐   │
│  │  Embedded Python Server (FastAPI)                    │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  WebSocket Handler                             │  │   │
│  │  │  - 프레임 수신 (Base64/Binary)                 │  │   │
│  │  │  - 결과 전송 (JSON)                            │  │   │
│  │  └───────────┬────────────────────────────────────┘  │   │
│  │              │                                        │   │
│  │  ┌───────────┴────────────────────────────────────┐  │   │
│  │  │  Inference Pipeline                            │  │   │
│  │  │  1. Frame Preprocessing                        │  │   │
│  │  │  2. YOLO Detection (CoreML/Metal)              │  │   │
│  │  │  3. Post-processing                            │  │   │
│  │  │  4. Ball Owner Calculation                     │  │   │
│  │  │  5. Player Identification                      │  │   │
│  │  └───────────┬────────────────────────────────────┘  │   │
│  │              │                                        │   │
│  │  ┌───────────┴────────────────────────────────────┐  │   │
│  │  │  Modules                                       │  │   │
│  │  │  - YOLO Model (CoreML)                         │  │   │
│  │  │  - Color Clustering (K-means)                  │  │   │
│  │  │  - OCR Engine (EasyOCR)                        │  │   │
│  │  │  - Tracker (DeepSORT/ByteTrack)                │  │   │
│  │  │  - Optical Flow (OpenCV)                       │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## 📦 컴포넌트 상세

### 1. Chrome Extension

#### 1.1 Content Script
**역할**: 웹페이지에 주입되어 비디오 요소와 직접 상호작용

**주요 기능**:
```javascript
// 비디오 감지
function detectVideo() {
  const video = document.querySelector('video');
  if (video) {
    setupVideoCapture(video);
  }
}

// 프레임 캡처
function captureFrame(video) {
  const canvas = document.createElement('canvas');
  canvas.width = 640;  // 다운스케일
  canvas.height = 640;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, 640, 640);
  return canvas.toDataURL('image/jpeg', 0.7);  // 압축
}

// 오버레이 렌더링
function renderOverlay(results) {
  const svg = createSVGOverlay(video);
  results.players.forEach(player => {
    drawBoundingBox(svg, player);
    if (player.name) {
      drawLabel(svg, player.name, player.number);
    }
  });
}
```

**이벤트 처리**:
- `play`: 비디오 재생 시작 → 캡처 시작
- `pause`: 비디오 일시정지 → 캡처 중지
- `seeked`: 탐색 완료 → YOLO 재실행 (Optical Flow 리셋)

#### 1.2 Background Service Worker
**역할**: WebSocket 연결 관리 및 상태 동기화

**주요 기능**:
```javascript
// WebSocket 연결
let ws = null;

function connectToServer() {
  ws = new WebSocket('ws://localhost:8765');

  ws.onopen = () => {
    chrome.storage.local.set({ serverStatus: 'connected' });
  };

  ws.onmessage = (event) => {
    const results = JSON.parse(event.data);
    // Content Script로 결과 전달
    chrome.tabs.sendMessage(activeTabId, { type: 'YOLO_RESULTS', data: results });
  };

  ws.onerror = () => {
    chrome.storage.local.set({ serverStatus: 'error' });
    // 재연결 시도
    setTimeout(connectToServer, 3000);
  };
}
```

**상태 관리**:
- `serverStatus`: connected | disconnected | error
- `settings`: { fps: 30, sensitivity: 0.7, showNames: true }
- `matchInfo`: { homeTeam: [], awayTeam: [], formation: '4-4-2' }

#### 1.3 Popup UI
**역할**: 사용자 설정 및 경기 정보 입력

**화면 구성**:
```
┌────────────────────────┐
│  SoccerHUD             │
├────────────────────────┤
│  [●] 활성화  (녹색)    │
│                        │
│  서버 상태: 연결됨 ✓   │
│                        │
│  설정                  │
│  FPS: [▓▓▓▓░░] 30      │
│  민감도: [▓▓▓░░░] 0.7  │
│  [✓] 선수 이름 표시     │
│                        │
│  경기 정보             │
│  [경기 정보 입력 ▶]    │
│                        │
│  도움말 | GitHub       │
└────────────────────────┘
```

---

### 2. Python Backend (FastAPI)

#### 2.1 서버 구조

```python
# main.py
from fastapi import FastAPI, WebSocket
from inference import InferencePipeline
import asyncio

app = FastAPI()
pipeline = InferencePipeline(model_path="yolov8s.mlmodel")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # 프레임 수신
            frame_data = await websocket.receive_bytes()

            # 추론
            results = await pipeline.process(frame_data)

            # 결과 전송
            await websocket.send_json(results)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()
```

#### 2.2 Inference Pipeline

```python
# inference.py
import cv2
import numpy as np
from ultralytics import YOLO

class InferencePipeline:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = DeepSORT()
        self.color_clusterer = ColorClusterer()

    async def process(self, frame_bytes):
        # 1. 디코딩
        frame = self.decode_frame(frame_bytes)

        # 2. YOLO 추론 (Lazy Tracking 적용)
        if self.should_run_yolo():
            detections = self.model(frame)
            self.last_yolo_frame = frame
        else:
            detections = self.optical_flow_track(frame)

        # 3. 공 소유자 계산
        ball_owner = self.calculate_ball_owner(detections)

        # 4. 선수 식별
        players = self.identify_players(detections)

        # 5. JSON 생성
        return {
            "timestamp": time.time(),
            "ball": self.format_ball(detections.ball),
            "players": self.format_players(players),
            "ball_owner": ball_owner
        }

    def should_run_yolo(self):
        # Lazy Tracking: 5 프레임마다 YOLO 실행
        if self.frame_count % 5 == 0:
            return True
        # 카메라 전환 감지
        if self.detect_scene_change():
            return True
        return False
```

#### 2.3 선수 식별 모듈

```python
# player_identification.py

class PlayerIdentifier:
    def __init__(self):
        self.ocr = easyocr.Reader(['en'])
        self.tracker = DeepSORT()
        self.color_clusterer = KMeans(n_clusters=2)  # 2팀

    def identify(self, player_bbox, frame, match_info):
        score = 0
        candidate = {}

        # 1. 유니폼 색상 (40%)
        color = self.extract_uniform_color(player_bbox, frame)
        team = self.match_color_to_team(color)
        candidate['team'] = team
        score += 0.4

        # 2. 등번호 OCR (30%)
        number_region = self.detect_number_region(player_bbox, frame)
        if number_region:
            number = self.ocr_number(number_region)
            if number:
                candidate['number'] = number
                candidate['name'] = match_info.get_player_by_number(team, number)
                score += 0.3

        # 3. 필드 위치 (20%)
        position = self.estimate_position(player_bbox, frame)
        if position:
            candidate['position'] = position
            score += 0.2

        # 4. 추적 이력 (10%)
        tracked_id = self.tracker.update(player_bbox)
        if tracked_id in self.player_history:
            candidate.update(self.player_history[tracked_id])
            score += 0.1

        candidate['confidence'] = score
        return candidate
```

---

## 🔄 데이터 플로우

### 정상 플로우
```
1. [Browser] 비디오 재생 중
2. [Content Script] Canvas로 프레임 캡처 (30fps)
3. [Content Script] 640x640 리사이즈 + JPEG 압축
4. [Background Worker] WebSocket으로 전송 (~50KB)
5. [Python Server] 프레임 수신 (<5ms)
6. [Inference] YOLO 추론 (30-40ms)
7. [Inference] 후처리 (공 소유, 선수 식별) (10ms)
8. [Python Server] JSON 결과 전송
9. [Background Worker] Content Script로 전달
10. [Content Script] SVG 오버레이 렌더링 (5ms)

총 레이턴시: ~50-60ms (실시간 가능)
```

### 에러 플로우
```
1. [Background Worker] WebSocket 연결 실패
   → 3초 후 재연결 시도
   → 5회 실패 시 사용자 알림 ("Companion 앱 실행 필요")

2. [Python Server] YOLO 추론 실패
   → 이전 결과 재사용
   → 로그 기록 후 계속 진행

3. [Content Script] 비디오 요소 없음
   → 1초마다 재탐색
   → 10초 후 포기 및 알림
```

---

## 🗄️ 데이터 모델

### WebSocket 메시지 포맷

#### Request (Browser → Server)
```json
{
  "type": "frame",
  "timestamp": 1234567890.123,
  "data": "base64_encoded_jpeg_image...",
  "metadata": {
    "videoWidth": 1920,
    "videoHeight": 1080,
    "currentTime": 123.45
  }
}
```

#### Response (Server → Browser)
```json
{
  "type": "detection",
  "timestamp": 1234567890.124,
  "fps": 28.5,
  "ball": {
    "x": 320,
    "y": 240,
    "width": 20,
    "height": 20,
    "confidence": 0.95
  },
  "players": [
    {
      "id": 1,
      "x": 300,
      "y": 250,
      "width": 60,
      "height": 120,
      "team": "home",
      "color": [255, 0, 0],
      "number": 7,
      "name": "손흥민",
      "position": "FW",
      "confidence": 0.88
    }
  ],
  "ball_owner": {
    "player_id": 1,
    "distance": 15.3,
    "confidence": 0.92
  }
}
```

---

## ⚙️ 설정 및 최적화

### 성능 튜닝 파라미터

```python
# config.py
class Config:
    # 모델 설정
    MODEL_SIZE = "small"  # nano | small | medium
    INPUT_SIZE = 640      # 입력 해상도
    CONFIDENCE_THRESHOLD = 0.5
    IOU_THRESHOLD = 0.4

    # Lazy Tracking
    YOLO_INTERVAL = 5     # 5 프레임마다 YOLO 실행
    SCENE_CHANGE_THRESHOLD = 0.3  # 장면 전환 감지 임계값

    # 프레임 처리
    TARGET_FPS = 30
    JPEG_QUALITY = 70

    # 선수 식별
    OCR_CONFIDENCE_THRESHOLD = 0.6
    COLOR_MATCHING_THRESHOLD = 30  # RGB 유클리드 거리
    BALL_OWNER_MAX_DISTANCE = 50   # 픽셀
```

### 리소스 사용량 예상

| 항목 | 사용량 |
|------|--------|
| **CPU** | 30-50% (1 코어) |
| **GPU** | Metal 활용 시 효율적 |
| **메모리** | ~500MB (모델 로딩 포함) |
| **네트워크** | 1.5 MB/s (30fps × 50KB) |
| **디스크** | ~200MB (모델 + 앱) |

---

## 🔐 보안 및 프라이버시

### 데이터 처리 정책
- ✅ **비디오 프레임**: 로컬에서만 처리, 외부 전송 없음
- ✅ **개인정보**: 수집하지 않음
- ✅ **경기 정보**: 브라우저 로컬 스토리지에만 저장
- ✅ **네트워크**: localhost만 사용 (외부 통신 없음)

### Chrome 스토어 정책 준수
- Content Security Policy (CSP) 준수
- `host_permissions` 최소화 (필요한 사이트만)
- `externally_connectable` 제한
- 개인정보 처리방침 명시

---

## 🧪 테스트 전략

### 단위 테스트
- YOLO 추론 정확도
- 공 소유자 계산 로직
- 색상 클러스터링
- OCR 정확도

### 통합 테스트
- WebSocket 통신
- 프레임 캡처 → 추론 → 렌더링 E2E
- 에러 핸들링 (서버 끊김, 재연결)

### 성능 테스트
- FPS 벤치마크 (다양한 해상도)
- 메모리 누수 체크 (장시간 실행)
- GPU 활용률 모니터링

### 사용자 테스트
- 다양한 경기 영상 (조명, 각도)
- YouTube, 쿠팡플레이 호환성
- 다양한 PC 사양에서 테스트
