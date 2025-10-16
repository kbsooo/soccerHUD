# ⚽ SoccerHUD

> 실시간 축구 중계에서 공을 소유한 선수를 자동으로 인식하고 표시하는 크롬 익스텐션

![Phase](https://img.shields.io/badge/Phase-0%20%7C%20%EA%B2%80%EC%A6%9D-yellow)
![License](https://img.shields.io/badge/License-MIT-blue)
![Platform](https://img.shields.io/badge/Platform-Chrome%20Extension-brightgreen)

---

## 📖 프로젝트 소개

FIFA 게임처럼 실제 축구 중계 영상에서도 선수 머리 위에 이름과 번호가 표시되면 얼마나 좋을까요?

**SoccerHUD**는 AI 객체 탐지 기술을 활용하여:
- 실시간으로 공과 선수를 인식
- 공을 소유한 선수를 자동 판단
- 선수 정보를 비디오 위에 오버레이로 표시

### 🎯 핵심 기능

- ⚽ **공 탐지**: YOLOv8으로 실시간 축구공 위치 추적
- 👤 **선수 인식**: 유니폼 색상, 등번호, 위치 정보로 선수 식별
- 🎨 **오버레이 표시**: 피파 게임 스타일의 깔끔한 UI
- 🚀 **실시간 처리**: 로컬 GPU로 20-30 FPS 성능
- 🔒 **프라이버시**: 모든 처리는 로컬에서만 진행

---

## 🏗️ 아키텍처

```
Chrome Extension ←→ Electron Companion App (Python + YOLOv8)
                     WebSocket (localhost)
```

**기술 스택**:
- **AI 모델**: YOLOv8 (객체 탐지), DeepSORT (추적)
- **백엔드**: Python, FastAPI, OpenCV
- **프론트엔드**: Chrome Extension (Manifest V3), Vanilla JS
- **패키징**: Electron (Mac/Windows)
- **GPU 가속**: CoreML (Mac M-series), CUDA (Windows)

자세한 내용은 [`AGENTS/ARCHITECTURE.md`](AGENTS/ARCHITECTURE.md) 참조

---

## 📂 프로젝트 구조

```
soccerHUD/
├── README.md                    # 이 파일
├── LICENSE                      # MIT License
│
├── AGENTS/                      # 프로젝트 문서 (중요!)
│   ├── OVERVIEW.md              # 프로젝트 개요
│   ├── ARCHITECTURE.md          # 시스템 아키텍처
│   ├── DEVELOPMENT_PLAN.md      # 개발 로드맵 (8-10주)
│   ├── TODO.md                  # 작업 목록
│   ├── DECISIONS.md             # 주요 의사결정 기록
│   └── EXPERIMENTS.md           # 실험 결과 (추후)
│
├── finetuning/                  # YOLO 모델 파인튜닝
│   ├── README.md                # 파인튜닝 가이드
│   ├── data/                    # 데이터셋
│   ├── scripts/                 # 학습 스크립트
│   └── models/                  # 학습된 모델
│
├── src/                         # Python 백엔드 (추후)
│   ├── main.py                  # FastAPI 서버
│   ├── inference.py             # YOLO 파이프라인
│   ├── player_identification.py # 선수 식별
│   └── config.py                # 설정
│
├── extension/                   # Chrome Extension (추후)
│   ├── manifest.json
│   ├── content.js
│   ├── background.js
│   └── popup.html
│
└── electron/                    # Electron 앱 (추후)
    └── main.js
```

---

## 🚀 개발 로드맵

### Phase 0: 환경 구축 및 검증 (진행 중)
- [x] 프로젝트 문서화
- [ ] YOLOv8 설치 및 CoreML 변환
- [ ] M4 성능 벤치마크 (목표: 20+ FPS)
- [ ] 샘플 영상으로 공/선수 탐지 검증

### Phase 1: 백엔드 파이프라인 (Week 2)
- [ ] FastAPI + WebSocket 서버
- [ ] YOLO 추론 파이프라인
- [ ] 공 소유자 판단 로직
- [ ] 유니폼 색상 클러스터링

### Phase 2: 크롬 익스텐션 MVP (Week 3)
- [ ] YouTube 비디오 프레임 캡처
- [ ] WebSocket 통신
- [ ] 오버레이 렌더링

### Phase 3: 선수 식별 (Week 4-5)
- [ ] 등번호 OCR
- [ ] DeepSORT 추적
- [ ] 멀티모달 점수 시스템

### Phase 4: Electron 패키징 (Week 6)
- [ ] Python 서버 번들링
- [ ] Mac .dmg 인스톨러

### Phase 5: 파인튜닝 (병렬 진행)
- [ ] 축구 데이터셋 수집
- [ ] YOLOv8 파인튜닝

### Phase 6: 쿠팡플레이 지원 (Week 7)
- [ ] Screen Capture API 통합

### Phase 7: 배포 (Week 8)
- [ ] Chrome Web Store 출시
- [ ] 문서화 및 마케팅

자세한 일정은 [`AGENTS/DEVELOPMENT_PLAN.md`](AGENTS/DEVELOPMENT_PLAN.md) 참조

---

## 💡 핵심 기술 결정

### 왜 로컬 처리인가?
- **빠름**: 네트워크 레이턴시 없음 (<5ms)
- **안전**: 비디오 프레임을 외부로 전송하지 않음
- **무료**: 클라우드 비용 없음

### 왜 Electron인가?
- **GPU 활용**: Metal/CUDA를 제대로 활용
- **사용자 편의**: 자동 실행, 시스템 트레이
- **선례**: Grammarly, Loom 등 유사 구조

### 선수 식별 전략
- **멀티모달 접근**: 색상(40%) + OCR(30%) + 위치(20%) + 추적(10%)
- **신뢰도 기반 표시**: 불확실하면 팀 정보만 표시
- **Lazy Tracking**: 5 프레임마다 YOLO, 나머지는 Optical Flow

모든 결정 사항은 [`AGENTS/DECISIONS.md`](AGENTS/DECISIONS.md)에 기록

---

## 🔧 설치 및 실행 (개발 중)

### 필수 요구사항
- **OS**: macOS (M-series) or Windows (NVIDIA GPU)
- **GPU**: Metal (Mac) or CUDA (Windows) 필수
- **메모리**: 8GB+ 권장
- **Python**: 3.10+
- **Chrome**: 최신 버전

### 개발 환경 설정 (Phase 0)

```bash
# 저장소 클론
git clone https://github.com/yourusername/soccerHUD.git
cd soccerHUD

# Python 가상환경
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치 (추후 제공)
pip install -r requirements.txt

# YOLOv8 테스트
python test_yolo.py
```

---

## 📚 문서

- **[OVERVIEW.md](AGENTS/OVERVIEW.md)**: 프로젝트 개요 및 목표
- **[ARCHITECTURE.md](AGENTS/ARCHITECTURE.md)**: 시스템 아키텍처 상세 설계
- **[DEVELOPMENT_PLAN.md](AGENTS/DEVELOPMENT_PLAN.md)**: 8주 개발 로드맵
- **[TODO.md](AGENTS/TODO.md)**: 세부 작업 목록
- **[DECISIONS.md](AGENTS/DECISIONS.md)**: 주요 의사결정 기록

---

## 🤝 기여하기

현재 초기 개발 단계입니다. 기여는 Phase 2 이후 환영합니다!

관심 있으신 분은 [GitHub Issues](https://github.com/yourusername/soccerHUD/issues)를 확인해주세요.

---

## 📜 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

---

## 🙏 크레딧

- **YOLOv8**: [Ultralytics](https://github.com/ultralytics/ultralytics)
- **DeepSORT**: [nwojke/deep_sort](https://github.com/nwojke/deep_sort)
- **데이터셋**: Roboflow, SoccerNet, Kaggle 커뮤니티

---

## 📧 연락처

프로젝트 관련 문의: [GitHub Issues](https://github.com/yourusername/soccerHUD/issues)

---

**⚡ 현재 상태**: Phase 0 - 환경 구축 및 검증 중

**🎯 다음 목표**: YOLOv8 M4 벤치마크 20+ FPS 달성
