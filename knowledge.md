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
├── src/                      # ✅ Phase 1 완료
│   ├── config.py             # 설정값 관리
│   ├── models.py             # Pydantic 데이터 모델
│   ├── inference.py          # YOLO 추론 파이프라인
│   └── main.py               # FastAPI WebSocket 서버
├── tests/
│   ├── test_image_pipeline.py     # ✅ 이미지 테스트 (성공)
│   ├── test_pipeline.py           # 비디오 테스트 (예정)
│   └── extract_frame.py           # YouTube 프레임 추출
├── sample_videos/
│   ├── korea_vs_paraguay.mp4      # 테스트 영상 (95MB, 1280x720)
│   └── korea_vs_paraguay_frame.jpg # 테스트 프레임
├── test_results/
│   └── image_test_result.jpg      # ✅ 탐지 결과 시각화
├── models/
│   ├── yolov8n.pt
│   ├── yolov8s.pt            # 현재 사용 중
│   └── yolov8s.mlpackage     # CoreML 버전
├── AGENTS/                   # 프로젝트 문서
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT_PLAN.md
│   ├── TODO.md
│   └── PHASE0_RESULTS.md
└── requirements.txt          # ✅ Phase 1 패키지 포함
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

### 2025-10-17 (Phase 1 완료)
- ✅ FastAPI + WebSocket 서버 구현
- ✅ YOLO 추론 파이프라인 구현
- ✅ 공 소유자 판단 로직 구현
- ✅ K-means 팀 색상 클러스터링 구현
- ✅ 한국 vs 파라과이 경기 영상으로 테스트 성공
- ✅ 선수 탐지 및 팀 구분 매우 정확하게 작동

### 다음 세션 시작 시
- Phase 2 (크롬 익스텐션) 시작 또는
- Phase 1 추가 테스트 (비디오, WebSocket)
