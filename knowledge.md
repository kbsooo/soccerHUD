# SoccerHUD - Project Knowledge Base

## 프로젝트 개요

**목적**: 실시간 축구 중계 영상에서 공을 소유한 선수를 자동으로 인식하고 표시하는 크롬 익스텐션
**기간**: 8-10주 (현재 Week 2 완료)
**배포 계획**: Chrome Web Store 정식 출시
**협업**: 혼자 개발

---

## 기술 스택

### AI/ML
- **YOLOv8s**: 객체 탐지 (공, 선수)
- **CoreML**: Mac M-series GPU 가속 (119 FPS 달성!)
- **K-means**: 유니폼 색상 클러스터링으로 팀 구분
- **DeepSORT**: 프레임 간 선수 추적 (MobileNet ReID)
- **deep-sort-realtime**: Python DeepSORT 구현체

### 백엔드
- **Python 3.12**: 가상환경 사용
- **FastAPI**: WebSocket 서버
- **OpenCV**: 비디오/이미지 처리
- **scikit-learn**: 클러스터링

### 프론트엔드 (예정)
- **Chrome Extension**: Manifest V3
- **Vanilla JS**: Content Script, Background Service Worker
- **SVG**: 오버레이 렌더링

### 패키징 (예정)
- **Electron**: Python 서버 번들링

---

## 현재 프로젝트 구조

```
soccerHUD/
├── .venv/                    # Python 3.12 가상환경
├── src/                      # ✅ Phase 3 완료
│   ├── config.py             # 설정값 관리
│   ├── models.py             # Pydantic 데이터 모델
│   ├── inference.py          # YOLO 추론 + 추적 파이프라인
│   ├── main.py               # FastAPI WebSocket 서버 + 명단 API
│   ├── tracker.py            # DeepSORT 선수 추적
│   └── player_matcher.py     # 추적 ID → 선수 매칭
├── extension/                # ✅ Phase 3 완료
│   ├── manifest.json         # 익스텐션 설정
│   ├── content.js            # 메인 로직 (비디오 캡처, 오버레이)
│   ├── background.js         # Service Worker
│   ├── popup.html/js         # 팝업 UI (명단 입력 탭 추가)
│   ├── styles/
│   │   └── overlay.css
│   ├── icons/                # 임시 아이콘
│   │   ├── icon16.png
│   │   ├── icon48.png
│   │   └── icon128.png
│   └── README.md             # 익스텐션 사용 가이드
├── tests/
│   ├── test_image_pipeline.py      # ✅ 이미지 테스트
│   ├── test_ball_detection.py      # ✅ 공 탐지 분석
│   ├── test_phase3.py              # ✅ Phase 3 추적 테스트
│   ├── extract_multiple_frames.py  # 여러 프레임 추출
│   └── create_icons.py             # 아이콘 생성
├── sample_videos/
│   ├── korea_vs_paraguay.mp4       # 테스트 영상
│   └── test_frames/                # 8개 테스트 프레임
├── test_results/
│   ├── image_test_result.jpg       # 탐지 결과
│   └── ball_detection/             # 공 탐지 분석 결과
├── models/
│   ├── yolov8s.pt                  # 현재 사용 중
│   └── yolov8s.mlpackage           # CoreML 버전
├── AGENTS/                          # 프로젝트 문서
└── requirements.txt                 # Phase 1 패키지
```

---

## Phase 1 완료 상태 (✅ 2025-10-17)

### 구현된 기능

#### 1. **config.py** - 설정 관리
- 모델 경로, 임계값 등 모든 설정 중앙 관리
- CoreML/PyTorch 자동 선택

#### 2. **models.py** - 데이터 모델
```python
- BallDetection: 공 위치, 크기, 신뢰도
- PlayerDetection: 선수 위치, 팀, 색상, 신뢰도
- BallOwner: 공 소유자 정보
- DetectionResult: 전체 결과 (JSON 응답 형식)
```

#### 3. **inference.py** - YOLO 추론 파이프라인
**주요 기능:**
- ✅ YOLO 모델 로딩 (PyTorch/CoreML 자동 선택)
- ✅ 프레임 디코딩 (JPEG → OpenCV)
- ✅ 공 탐지 (COCO class 32: sports ball)
- ✅ 선수 탐지 (COCO class 0: person)
- ✅ 유니폼 색상 추출 (바운딩 박스 30-60% 영역)
- ✅ K-means 클러스터링으로 2개 팀 분류
- ✅ 공 소유자 계산 (유클리드 거리 기반)
- ✅ FPS 성능 측정

**핵심 로직:**
```python
def _calculate_ball_owner():
    # 공과 각 선수 간 거리 계산
    # 50px 이내에서 가장 가까운 선수 = 소유자
    # 신뢰도 = 1.0 - (distance / 50px)
```

#### 4. **main.py** - FastAPI 서버
- ✅ WebSocket 엔드포인트 (`/ws`)
- ✅ Base64 프레임 수신
- ✅ YOLO 추론 → JSON 응답
- ✅ 에러 핸들링
- ✅ CORS 설정 (크롬 익스텐션 허용)

### 테스트 결과

#### 테스트 데이터
- **영상**: 대한민국 vs 파라과이 경기 (YouTube)
- **URL**: https://www.youtube.com/watch?v=tKg81nVeoUI
- **팀 색상**: 빨강(한국) vs 남색/파랑(파라과이)
- **프레임**: 1분 35초 시점, 1280x720

#### 결과 분석
✅ **선수 탐지**: 매우 정확 (양팀 선수 모두 탐지)
✅ **팀 구분**: K-means가 빨강/파랑 완벽하게 구분
✅ **바운딩 박스**: 정확한 위치와 크기
⏸️ **공 탐지**: 이 프레임에서는 미확인 (다른 프레임 테스트 필요)

---

## 주요 설정값

```python
# config.py
MODEL_PATH = "yolov8s.pt"
INPUT_SIZE = 640
CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.4
BALL_OWNER_MAX_DISTANCE = 50  # 픽셀

BALL_CLASS_ID = 32  # COCO: sports ball
PERSON_CLASS_ID = 0  # COCO: person

HOST = "localhost"
PORT = 8765
```

---

## 알려진 이슈 / 주의사항

### 1. Python 버전 이슈
- ❌ Python 3.13: PyTorch 미지원
- ✅ Python 3.12: 정상 작동
- 해결: `.venv`를 Python 3.12로 재생성

### 2. NumPy 버전 충돌
- PyTorch는 NumPy 1.x 필요
- opencv-python은 NumPy 2.x 선호
- 해결: NumPy 1.26.4로 다운그레이드 (경고 무시)

### 3. 가상환경 문제
- 시스템 Python보다 가상환경 사용 필수
- `source .venv/bin/activate` 후 작업

### 4. ⚠️ 공 탐지 성능 이슈 (중요!)
**문제**: 사전학습 YOLOv8 모델이 축구공을 잘 탐지하지 못함
- 8개 테스트 프레임 중 1개만 탐지 (12.5% 탐지율)
- 탐지된 프레임도 신뢰도 0.424로 낮음
- COCO 데이터셋의 "sports ball" 클래스가 축구공에 최적화되지 않음

**임시 해결책** (Phase 2 진행을 위해):
- `BALL_CONFIDENCE_THRESHOLD = 0.3`으로 낮춤 (일반은 0.5)
- 공 전용으로 별도 YOLO 추론 실행 (classes=[32])
- 공이 탐지되는 프레임(frame_02_00.jpg)으로 테스트

**근본 해결책** (Phase 5에서 진행):
- 축구 전용 데이터셋으로 YOLOv8 파인튜닝 필요
- 목표: 공 탐지율 70%+ 달성
- Roboflow, SoccerNet 데이터셋 사용 예정

---

## 다음 할 일 (Phase 2 대비)

### 즉시 처리 필요
- [ ] 비디오 전체로 테스트 (test_pipeline.py 실행)
- [ ] 공 탐지 정확도 확인 (여러 프레임 테스트)
- [ ] FastAPI 서버 실제 실행 테스트
- [ ] WebSocket 통신 테스트 (간단한 클라이언트 작성)

### Phase 2 준비사항
- [ ] Chrome Extension 기본 구조
- [ ] manifest.json 작성
- [ ] Content Script로 `<video>` 태그 감지
- [ ] Canvas API로 프레임 캡처
- [ ] WebSocket 클라이언트 연결

---

## 실행 방법

### 환경 설정
```bash
# 가상환경 활성화
source .venv/bin/activate

# 패키지 설치 (최초 1회)
pip install -r requirements.txt
```

### 테스트 실행
```bash
# 이미지 테스트
.venv/bin/python tests/test_image_pipeline.py

# 비디오 테스트 (예정)
.venv/bin/python tests/test_pipeline.py

# FastAPI 서버 실행 (예정)
.venv/bin/python src/main.py
```

---

## 성능 목표

| 항목 | Phase 0 목표 | Phase 0 실제 | Phase 1 현재 |
|------|--------------|-------------|-------------|
| FPS | 20+ | 43.6 (PyTorch)<br>119 (CoreML) | 측정 중 |
| 공 탐지율 | 70%+ | ✅ 달성 | 검증 필요 |
| 선수 탐지율 | 80%+ | ✅ 달성 | ✅ 매우 우수 |
| 팀 구분 | - | - | ✅ 완벽 |

---

## 참고 문서

- [ARCHITECTURE.md](AGENTS/ARCHITECTURE.md): 전체 시스템 아키텍처
- [DEVELOPMENT_PLAN.md](AGENTS/DEVELOPMENT_PLAN.md): 8주 로드맵
- [TODO.md](AGENTS/TODO.md): 세부 작업 목록
- [PHASE0_RESULTS.md](AGENTS/PHASE0_RESULTS.md): Phase 0 벤치마크 결과

---

## 변경 이력

### 2025-10-18 (Phase 2 완료)
- ✅ Chrome Extension Manifest V3 구현
- ✅ Content Script: YouTube 비디오 감지 및 프레임 캡처
- ✅ WebSocket 클라이언트: 서버와 실시간 통신
- ✅ SVG 오버레이: 선수/공/소유자 시각화
- ✅ Popup UI: 활성화 토글 및 상태 표시
- ✅ Background Service Worker: 상태 관리
- ✅ 임시 아이콘 생성 (Python/OpenCV)
- ⚠️ 공 탐지 이슈 확인 (8개 중 1개만 탐지)
- 📝 임시 해결: BALL_CONFIDENCE_THRESHOLD = 0.3

### 2025-10-17 (Phase 1 완료)
- ✅ FastAPI + WebSocket 서버 구현
- ✅ YOLO 추론 파이프라인 구현
- ✅ 공 소유자 판단 로직 구현
- ✅ K-means 팀 색상 클러스터링 구현
- ✅ 한국 vs 파라과이 경기 영상으로 테스트 성공
- ✅ 선수 탐지 및 팀 구분 매우 정확하게 작동

### 2025-10-18 (Phase 3 완료)
- ✅ PlayerTracker (DeepSORT) 통합
- ✅ PlayerMatcher 구현 (추적 ID ↔ 선수 명단 매핑)
- ✅ 명단 관리 API 엔드포인트 추가 (POST/GET /api/roster)
- ✅ 크롬 익스텐션 명단 입력 UI (탭 구조로 개선)
- ✅ Phase 3 테스트 작성 및 통과

**구현된 기능:**
1. **DeepSORT 추적** (src/tracker.py):
   - MobileNet ReID embedder 사용
   - 카메라 전환 자동 감지
   - max_age=30, n_init=3 설정

2. **PlayerMatcher** (src/player_matcher.py):
   - 명단 설정: set_roster(home, away)
   - 수동 매칭: match_player(track_id, team, number)
   - 선수 정보 조회: get_player_info(track_id)
   - 자동 enrichment: enrich_players(players)

3. **명단 관리 UI** (extension/popup.html):
   - 탭 구조: "컨트롤" + "명단"
   - 홈/원정 팀 입력 폼
   - 선수 추가/삭제 기능
   - 서버 저장 버튼

**테스트 결과:**
- ✅ 추적 시스템 초기화 성공
- ✅ 명단 설정 및 수동 매칭 성공
- ✅ PlayerMatcher 정상 작동

### 다음 세션 시작 시
- Phase 3 E2E 테스트 (실제 YouTube 영상에서 추적 확인)
- Phase 4 (통계 시스템) 또는 Phase 5 (파인튜닝) 선택
