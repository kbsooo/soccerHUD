# TODO List

## 🔴 Phase 0: 환경 구축 및 검증 (진행 중)

### 개발 환경 설정
- [ ] Python 가상환경 생성
  - [ ] Python 3.10+ 설치 확인
  - [ ] venv or conda 환경 생성
  - [ ] 환경 활성화 스크립트 작성
- [ ] 필수 패키지 설치
  - [ ] `requirements.txt` 작성
  - [ ] ultralytics (YOLOv8)
  - [ ] fastapi, uvicorn, websockets
  - [ ] opencv-python
  - [ ] coremltools (Mac)
  - [ ] numpy, pillow
- [ ] Git 저장소 구조 정리
  - [x] AGENTS 디렉토리 문서 작성
  - [ ] finetuning 디렉토리 생성
  - [ ] src 디렉토리 구조 설계

### YOLO 모델 검증
- [ ] YOLOv8 기본 테스트
  - [ ] 사전학습 모델 다운로드 (yolov8s.pt)
  - [ ] 샘플 이미지로 추론 테스트
  - [ ] 클래스 확인 (sports ball, person)
- [ ] CoreML 변환 테스트
  - [ ] YOLOv8 → CoreML 변환
  - [ ] Metal GPU 활용 확인
  - [ ] 변환 전후 정확도 비교
- [ ] 샘플 영상 수집
  - [ ] YouTube에서 축구 경기 영상 다운로드 (3-5개)
  - [ ] 다양한 조건 (낮/밤, 다양한 각도)
  - [ ] 720p, 1080p 해상도 포함
- [ ] 성능 벤치마크
  - [ ] FPS 측정 스크립트 작성
  - [ ] yolov8n vs yolov8s vs yolov8m 비교
  - [ ] 입력 크기별 성능 비교 (480, 640, 800)
  - [ ] 목표: 20+ FPS 달성 확인

### 탐지 정확도 검증
- [ ] 공 탐지 테스트
  - [ ] 다양한 샷에서 축구공 탐지율 확인
  - [ ] False Positive 분석 (얼굴을 공으로 오인식 등)
  - [ ] 목표: 70%+ 탐지율
- [ ] 선수 탐지 테스트
  - [ ] Person 클래스로 선수 탐지
  - [ ] 심판, 관중과 구분 가능한지 확인
  - [ ] 목표: 80%+ 탐지율
- [ ] **Go/No-Go 결정**
  - [ ] FPS >= 20 AND 탐지율 >= 70%
  - [ ] 결과 문서화 (AGENTS/PHASE0_RESULTS.md)

---

## 🟠 Phase 1: 백엔드 파이프라인

### FastAPI 서버 기본 구조
- [ ] 프로젝트 구조 생성
  ```
  src/
  ├── main.py           # FastAPI 앱
  ├── inference.py      # YOLO 파이프라인
  ├── models.py         # 데이터 모델
  ├── utils.py          # 유틸리티
  └── config.py         # 설정
  ```
- [ ] WebSocket 엔드포인트 구현
  - [ ] `/ws` 엔드포인트 생성
  - [ ] 프레임 수신 로직 (Base64 디코딩)
  - [ ] 비동기 처리 (async/await)
- [ ] CORS 설정
  - [ ] localhost 허용
  - [ ] 포트 설정 (8765)

### YOLO 추론 파이프라인
- [ ] InferencePipeline 클래스 구현
  - [ ] 모델 로딩 (CoreML)
  - [ ] 프레임 전처리 (리사이즈, 정규화)
  - [ ] 배치 처리 (선택적)
- [ ] 후처리 구현
  - [ ] NMS (Non-Maximum Suppression)
  - [ ] 클래스 필터링 (ball, person만)
  - [ ] 신뢰도 임계값 적용
- [ ] 결과 포맷팅
  - [ ] JSON 스키마 정의
  - [ ] 바운딩 박스 좌표 변환

### 공 소유자 판단
- [ ] 거리 계산 로직
  - [ ] 유클리드 거리 (픽셀 기반)
  - [ ] 임계값 설정 (최대 거리)
- [ ] Edge case 처리
  - [ ] 공이 감지 안 될 때
  - [ ] 선수가 없을 때
  - [ ] 여러 선수가 비슷한 거리일 때

### 유니폼 색상 클러스터링
- [ ] 색상 추출
  - [ ] 선수 바운딩 박스에서 유니폼 영역 추정
  - [ ] K-means 클러스터링 (k=2, 양팀)
- [ ] 팀 매칭
  - [ ] 색상 히스토리 유지 (프레임 간 일관성)
  - [ ] 홈/원정 라벨링

### E2E 테스트 (로컬 비디오)
- [ ] 테스트 스크립트 작성
  - [ ] OpenCV로 비디오 읽기
  - [ ] 프레임마다 서버로 전송
  - [ ] 결과 받아서 시각화
- [ ] 결과 영상 생성
  - [ ] 바운딩 박스 그리기
  - [ ] 공 소유자 표시
  - [ ] 검증용 영상 저장

---

## 🟡 Phase 2: 크롬 익스텐션 MVP

### 익스텐션 기본 구조
- [ ] manifest.json 작성
  - [ ] Manifest V3 포맷
  - [ ] 권한 설정 (activeTab, storage)
  - [ ] Content Script 등록
- [ ] 디렉토리 구조
  ```
  extension/
  ├── manifest.json
  ├── content.js        # 메인 로직
  ├── background.js     # Service Worker
  ├── popup.html        # UI
  ├── popup.js
  ├── styles.css
  └── icons/
  ```

### Content Script 구현
- [ ] 비디오 감지
  - [ ] `<video>` 태그 찾기
  - [ ] MutationObserver (동적 로딩 대응)
- [ ] 프레임 캡처
  - [ ] Canvas API 활용
  - [ ] 30 FPS 타이머 (requestAnimationFrame)
  - [ ] 리사이즈 및 압축
- [ ] 이벤트 처리
  - [ ] play/pause 이벤트
  - [ ] seeked 이벤트 (탐색 시)

### WebSocket 클라이언트
- [ ] 연결 로직
  - [ ] ws://localhost:8765 연결
  - [ ] 자동 재연결 (exponential backoff)
- [ ] 메시지 송수신
  - [ ] 프레임 전송 (JSON with Base64)
  - [ ] 결과 수신 및 파싱
- [ ] 에러 핸들링
  - [ ] 연결 실패 시 알림
  - [ ] 타임아웃 처리

### 오버레이 렌더링
- [ ] SVG 레이어 생성
  - [ ] 비디오 위에 절대 위치
  - [ ] z-index 조정
- [ ] 바운딩 박스 그리기
  - [ ] 선수별 박스
  - [ ] 팀 색상 구분 (빨강/파랑)
- [ ] 텍스트 표시
  - [ ] "빨간 팀 선수가 공 소유"
  - [ ] 선수 이름 (Phase 3 이후)

### Popup UI
- [ ] 활성화 토글
  - [ ] ON/OFF 버튼
  - [ ] 상태 저장 (chrome.storage)
- [ ] 연결 상태 표시
  - [ ] 녹색 (연결) / 빨간색 (끊김)
- [ ] 기본 설정
  - [ ] FPS 슬라이더
  - [ ] 민감도 조절

---

## 🟢 Phase 3: 선수 식별

### 실험 A: 등번호 OCR
- [ ] OCR 라이브러리 통합
  - [ ] EasyOCR 설치 및 테스트
  - [ ] PaddleOCR 비교
- [ ] 등번호 영역 검출
  - [ ] 선수 박스 상단 중앙 영역 추출
  - [ ] 전처리 (대비 향상, 이진화)
- [ ] 숫자 인식
  - [ ] 1-99 범위 필터링
  - [ ] 신뢰도 임계값 설정
- [ ] 성능 평가
  - [ ] 정확도 측정
  - [ ] 속도 측정 (FPS 영향)

### 실험 B: 추적 기반
- [ ] DeepSORT 통합
  - [ ] 라이브러리 설치
  - [ ] ReID 모델 로딩
- [ ] 추적 로직
  - [ ] YOLO 탐지 → DeepSORT 업데이트
  - [ ] ID 일관성 유지
- [ ] 카메라 전환 대응
  - [ ] 장면 변화 감지 (프레임 차이)
  - [ ] 추적 리셋
- [ ] ID 스와핑 방지
  - [ ] 외형 특징 활용
  - [ ] 위치 예측

### 실험 C: 공간 정보
- [ ] 필드 매핑
  - [ ] 호모그래피 변환 구현
  - [ ] 2D → 3D 좌표
- [ ] 포지션 추정
  - [ ] 필드 영역 분할
  - [ ] 포지션 템플릿 매칭
- [ ] 경기 정보 UI
  - [ ] 선수 명단 입력 폼
  - [ ] 포메이션 선택 (4-4-2 등)

### 하이브리드 통합
- [ ] 멀티모달 점수 시스템
  - [ ] 색상(40%) + OCR(30%) + 위치(20%) + 추적(10%)
  - [ ] 가중치 튜닝
- [ ] 신뢰도 기반 표시
  - [ ] 90%+: 확정 (이름 + 번호)
  - [ ] 70-90%: 추정 (이름 + "?")
  - [ ] 50-70%: 포지션만
  - [ ] <50%: 팀만

### Lazy Tracking
- [ ] Optical Flow 구현
  - [ ] OpenCV Lucas-Kanade
  - [ ] 특징점 추출 및 추적
- [ ] YOLO 스케줄링
  - [ ] 5 프레임마다 YOLO
  - [ ] 중간은 Optical Flow
- [ ] 장면 변화 감지
  - [ ] 프레임 차이 임계값
  - [ ] 즉시 YOLO 재실행

---

## 🔵 Phase 4: Electron 패키징

### Electron 프로젝트 설정
- [ ] electron-builder 설정
- [ ] Main/Renderer 프로세스 구조
- [ ] IPC 통신 설정

### Python 서버 번들링
- [ ] PyInstaller 변환
  - [ ] 실행파일 생성
  - [ ] 의존성 포함
- [ ] Electron에 내장
  - [ ] resources 폴더에 배치
  - [ ] 자동 실행 스크립트

### 시스템 트레이 UI
- [ ] 트레이 아이콘 생성
- [ ] 메뉴 (시작/중지/설정/종료)
- [ ] 상태 표시

### 인스톨러 생성
- [ ] Mac: .dmg
- [ ] Windows: .exe
- [ ] 서명 (선택적)

---

## 🟣 Phase 5: 파인튜닝

### 데이터셋 수집
- [ ] Roboflow 데이터셋 다운로드
- [ ] SoccerNet 탐색
- [ ] Kaggle 데이터셋 병합
- [ ] 목표: 3000+ 이미지

### 데이터 전처리
- [ ] YOLO 포맷 변환
- [ ] 클래스 매핑
- [ ] Train/Val/Test 분할

### 학습 환경
- [ ] Google Colab 노트북
- [ ] 학습 스크립트
- [ ] 하이퍼파라미터 설정

### 파인튜닝 실행
- [ ] 50-100 epochs
- [ ] Validation 모니터링
- [ ] 최적 체크포인트 저장

### 평가
- [ ] mAP 측정
- [ ] 기존 모델 vs 파인튜닝 비교
- [ ] 실제 영상 테스트

---

## ⚫ Phase 6: 쿠팡플레이 지원

- [ ] Screen Capture API 통합
- [ ] 권한 요청 플로우
- [ ] 플랫폼 자동 감지
- [ ] UX 개선 (권한 안내)

---

## ⚪ Phase 7: 배포

### Chrome Web Store
- [ ] 아이콘 디자인
- [ ] 스크린샷 준비
- [ ] 프로모션 비디오
- [ ] 상세 설명 작성
- [ ] 개인정보 처리방침
- [ ] 스토어 제출

### 문서화
- [ ] README.md (사용자용)
- [ ] 개발자 문서
- [ ] 트러블슈팅 가이드
- [ ] FAQ

### 마케팅
- [ ] 랜딩 페이지
- [ ] Reddit 홍보
- [ ] 커뮤니티 공유
- [ ] Product Hunt 등록

---

## 📝 지속적 작업

- [ ] 이슈 트래킹
- [ ] 버그 수정
- [ ] 성능 개선
- [ ] 사용자 피드백 반영
- [ ] 문서 업데이트
