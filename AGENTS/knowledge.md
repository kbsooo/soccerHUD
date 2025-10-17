# 🧠 프로젝트 지식 베이스

> 이 파일은 프로젝트의 핵심 컨텍스트를 유지하기 위한 문서입니다. 세션이 바뀌어도 프로젝트를 이어갈 수 있도록 중요한 정보를 기록합니다.

**최종 업데이트**: 2025-10-16

---

## 🎯 프로젝트 목적

**"실시간 축구 중계 영상에서 공을 소유한 선수를 자동으로 인식하고 표시하는 크롬 익스텐션"**

### 동기
- 축구 중계를 보면서 선수 이름이 헷갈림
- FIFA 게임처럼 머리 위에 이름/번호가 표시되면 편리할 것
- 딥러닝 기술로 실제 중계에서도 구현 가능한지 실험

### 최종 목표
1. Chrome Web Store 배포
2. YouTube 및 쿠팡플레이 지원
3. 실시간 성능 (20+ FPS)
4. 오픈소스 공개

---

## 💻 개발 환경

### 하드웨어
- **개발 머신**: MacBook Pro M4, 16GB RAM
- **GPU**: Metal (Apple Silicon)
- **최소 사양**: GPU 필수 (NVIDIA/AMD/Apple Silicon)

### 소프트웨어
- **OS**: macOS (주 개발), Windows 추후 지원
- **Python**: 3.10+
- **Node.js**: 18+ (Electron용)
- **Chrome**: 최신 버전

### 기술 스택 요약
```
AI/ML:     YOLOv8, DeepSORT, EasyOCR
Backend:   Python, FastAPI, OpenCV
Frontend:  Chrome Extension (Manifest V3), Vanilla JS
Packaging: Electron, PyInstaller
GPU:       CoreML (Mac), CUDA (Windows)
```

---

## 📊 현재 상태

### Phase 0: 환경 구축 및 검증 ✅ (완료 - 2025-10-16)
- [x] 프로젝트 문서화 완료
- [x] Git 저장소 구조 설정
- [x] YOLOv8 설치 및 테스트
- [x] CoreML 변환 및 M4 벤치마크
- [x] 샘플 축구 영상으로 정확도 검증

**핵심 결과**:
- **FPS**: 43.6 (yolov8s + MPS) | 119 (CoreML) ✅
- **선수 탐지**: 성공 ✅
- **CoreML**: PyTorch보다 134% 빠름 ✅
- **결론**: 실시간 처리 가능! Phase 1 진행 승인

### 주요 완료 문서
- `README.md`: 프로젝트 소개
- `AGENTS/OVERVIEW.md`: 프로젝트 개요
- `AGENTS/ARCHITECTURE.md`: 시스템 아키텍처
- `AGENTS/DEVELOPMENT_PLAN.md`: 8주 로드맵
- `AGENTS/TODO.md`: 세부 작업 목록
- `AGENTS/DECISIONS.md`: 의사결정 기록
- `AGENTS/PHASE0_RESULTS.md`: Phase 0 벤치마크 결과 ✅
- `finetuning/README.md`: 파인튜닝 가이드
- `tests/`: 테스트 스크립트 (basic, soccer, benchmark, coreml)

---

## 🔑 핵심 기술 결정

### 1. 로컬 처리 우선
- ✅ **채택**: Electron 앱에 Python 서버 내장
- ❌ **제외**: 클라우드 API (비용, 레이턴시, 프라이버시 이슈)

### 2. 선수 식별 전략
- **멀티모달 하이브리드**: 색상 + OCR + 위치 + 추적
- **신뢰도 기반 표시**: 불확실하면 팀 정보만
- **Lazy Tracking**: 5 프레임마다 YOLO, 나머지는 Optical Flow

### 3. 플랫폼 지원
- **Phase 1**: YouTube (DRM 없음, 검증 쉬움)
- **Phase 2**: 쿠팡플레이 (Screen Capture API)

### 4. 모델 선택
- **시작**: YOLOv8-small 사전학습 모델
- **필요 시**: 축구 데이터셋 파인튜닝
- **목표**: 공 90%+, 선수 85%+ 탐지율

---

## 🏗️ 아키텍처 핵심

### 데이터 플로우
```
1. [Browser] 비디오 재생 (YouTube/쿠팡플레이)
2. [Extension Content Script] Canvas로 프레임 캡처 (30fps)
3. [Extension] WebSocket으로 localhost:8765 전송
4. [Electron App] Python 서버 수신
5. [Python] YOLO 추론 + 선수 식별 (30-40ms)
6. [Python] JSON 결과 반환
7. [Extension] SVG 오버레이 렌더링

총 레이턴시: ~50-60ms (실시간 가능)
```

### 컴포넌트
- **Chrome Extension**: 비디오 캡처 + 오버레이
- **Electron App**: Python 서버 자동 실행
- **FastAPI Server**: WebSocket + YOLO 파이프라인
- **YOLO Model**: CoreML 변환 (Metal 가속)

---

## 📈 성능 목표

### FPS 목표
- **M4 MacBook**: 25-35 FPS (YOLOv8-small)
- **Lazy Tracking**: 실효 FPS 더 높음

### 정확도 목표
- **공 탐지**: 90%+
- **선수 탐지**: 85%+
- **팀 구분**: 95%+
- **선수 이름**: 70%+ (합리적)

### 리소스 사용량
- **CPU**: 30-50% (1 코어)
- **GPU**: Metal 활용
- **메모리**: ~500MB
- **네트워크**: 1.5 MB/s (localhost)

---

## 🧪 실험 계획

### Phase 0 검증 항목
1. **YOLO FPS 벤치마크**
   - yolov8n vs yolov8s vs yolov8m 비교
   - 입력 크기별 (480, 640, 800)
   - CoreML 변환 전후 비교

2. **공/선수 탐지 정확도**
   - 다양한 샷 (측면, 원경, 클로즈업)
   - 다양한 조명 (주간, 야간)
   - False Positive 분석

3. **Go/No-Go 기준**
   - FPS >= 20 AND 탐지율 >= 70%

### Phase 3 선수 식별 실험
- **실험 A**: 등번호 OCR (EasyOCR vs PaddleOCR)
- **실험 B**: DeepSORT 추적 (ID 일관성)
- **실험 C**: 공간 정보 (호모그래피 변환)
- **하이브리드**: 점수 시스템 통합

### Phase 5 파인튜닝 실험
- **Baseline**: COCO 사전학습 모델
- **실험 1**: Roboflow 데이터 (~3,000장)
- **실험 2**: 다중 데이터셋 병합 (~6,000장)
- **실험 3**: 데이터 증강 효과
- **실험 4**: 모델 크기 비교

---

## 🚧 알려진 제약사항

### 기술적 제약
1. **저사양 PC**: GPU 없으면 실시간 불가능 → 최소 사양 명시
2. **등번호 인식**: 항상 보이지 않음 → 멀티모달 접근
3. **카메라 전환**: 추적 끊김 → 장면 변화 감지 및 재초기화
4. **DRM 플랫폼**: 쿠팡플레이 Screen Capture 권한 필요

### 사용자 경험 트레이드오프
- **장점**: 실시간, 프라이버시, 무료
- **단점**: Companion 앱 설치 필요, GPU 필수

---

## 📝 개발 원칙 (CLAUDE.md 기반)

### 빠른 프로토타입 모드
- **Phase 0-2**: 일단 작동하게 만들기
- 단순한 방법 우선 (하드코딩 OK)
- 불필요한 추상화 금지
- 과도한 에러 핸들링 금지

### 정리 및 강화 모드
- **Phase 3 이후**: 코드 품질 향상
- 중복 제거 (DRY 원칙)
- 에러 핸들링 추가
- 하드코딩 제거 (config 파일)

### 문서화 원칙
- "무엇"보다 "왜"를 설명
- 트레이드오프 명시
- 불확실하면 물어보기

---

## 🎯 다음 할 일

### 즉시 (Phase 0)
1. Python 가상환경 생성
2. `requirements.txt` 작성 및 패키지 설치
3. YOLOv8 설치 및 샘플 추론 테스트
4. YouTube에서 축구 영상 다운로드 (3-5개)
5. CoreML 변환 테스트
6. FPS 벤치마크 스크립트 작성 및 실행
7. 공/선수 탐지 정확도 확인
8. Phase 0 결과 문서화 (`AGENTS/PHASE0_RESULTS.md`)

### 이후 (Phase 1)
1. FastAPI 서버 기본 구조
2. WebSocket 엔드포인트
3. YOLO 추론 파이프라인
4. 로컬 비디오로 E2E 테스트

---

## 📚 유용한 링크

### 공식 문서
- YOLOv8: https://docs.ultralytics.com/
- FastAPI: https://fastapi.tiangolo.com/
- Chrome Extension: https://developer.chrome.com/docs/extensions/mv3/

### 데이터셋
- Roboflow: https://universe.roboflow.com/search?q=football
- SoccerNet: https://www.soccer-net.org/
- Kaggle: https://www.kaggle.com/search?q=football+detection

### 참고 프로젝트
- YOLO Sports: https://github.com/ultralytics/ultralytics/tree/main/examples
- Football Analytics: https://github.com/topics/football-analytics

---

## 🔄 변경 이력

| 날짜 | 내용 |
|------|------|
| 2025-10-16 | 프로젝트 초기화, 문서화 완료 |
| 2025-10-16 | Phase 0 시작 준비 |

---

## 💡 메모 및 아이디어

### 향후 확장 가능성 (V2.0)
- **실시간 통계**: 패스 성공률, 터치 수, 달리기 거리
- **미니맵**: 선수 위치 추적 (2D 필드)
- **하이라이트 감지**: 슈팅, 골, 파울 자동 감지
- **전술 분석**: 포메이션 시각화, 히트맵
- **멀티 스포츠**: 농구, 야구 등

### 기술 실험 아이디어
- **Transformer 기반 추적**: BoT-SORT, StrongSORT
- **포즈 추정**: 선수 자세 분석 (MediaPipe)
- **경기 이벤트 분류**: 골, 파울 등 (Video Classification)

### 수익화 옵션 (장기)
- 무료 버전: 기본 기능
- 프리미엄: 고급 통계, 다시보기 저장
- 기부: Buy Me a Coffee, Patreon

---

## 🙋 FAQ

### Q: 왜 클라우드 API를 제외했나요?
A: 비용 부담, 프라이버시, 레이턴시 때문입니다. 로컬 처리가 모든 면에서 우수하며, 타겟 사용자는 대부분 GPU를 보유하고 있을 것으로 예상합니다.

### Q: 선수 이름이 항상 정확하지 않으면 어떡하나요?
A: 신뢰도 기반 표시로 사용자 기대치를 조정합니다. 불확실하면 팀 정보만 표시하며, 완벽한 식별은 목표가 아닙니다.

### Q: 파인튜닝은 필수인가요?
A: 아니오. Phase 0에서 사전학습 모델로 충분한지 먼저 검증합니다. 정확도가 부족할 때만 파인튜닝을 진행합니다.

### Q: 저사양 PC는 지원 안 하나요?
A: 현재는 GPU 필수입니다. 추후 수요가 있다면 클라우드 옵션을 재고려할 수 있습니다.

---

**이 문서는 프로젝트 진행에 따라 지속적으로 업데이트됩니다.**
