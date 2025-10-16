# 🎯 YOLO 모델 파인튜닝

이 디렉토리는 축구 특화 데이터셋으로 YOLOv8 모델을 파인튜닝하는 작업을 담당합니다.

---

## 📂 디렉토리 구조

```
finetuning/
├── README.md           # 이 파일
├── data/               # 데이터셋
│   ├── raw/            # 원본 데이터 (다운로드)
│   ├── processed/      # 전처리된 데이터
│   └── dataset.yaml    # YOLO 데이터셋 설정
├── scripts/            # 학습 스크립트
│   ├── download_data.py
│   ├── preprocess.py
│   ├── train.py
│   └── evaluate.py
├── models/             # 학습된 모델
│   └── (checkpoints)
└── notebooks/          # 실험 노트북 (Colab 등)
    └── training.ipynb
```

---

## 🎯 파인튜닝 목표

### 기존 COCO 모델의 한계
- **공 탐지**: COCO `sports ball` 클래스는 범용적 (축구공, 농구공, 야구공 등)
- **선수 탐지**: COCO `person` 클래스는 일반인도 포함
- **방송 화면 특성**: 압축, 모션 블러, 다양한 조명 조건

### 파인튜닝 기대 효과
- **공 탐지**: 70% → 90%+
- **선수 탐지**: 80% → 90%+
- **방송 화면 최적화**: False Positive 감소

---

## 📊 데이터셋 소스

### 1. Roboflow - Football Players Detection
- **링크**: https://universe.roboflow.com/search?q=football+players
- **크기**: ~3,000 이미지
- **클래스**: ball, player, goalkeeper, referee
- **장점**: 이미 YOLO 포맷으로 제공

### 2. SoccerNet
- **링크**: https://www.soccer-net.org/
- **크기**: 매우 방대함 (500+ 경기)
- **클래스**: 다양한 이벤트 어노테이션
- **장점**: 학술 데이터셋, 고품질
- **단점**: 다운로드/전처리 복잡

### 3. Kaggle - Football Object Detection
- **링크**: https://www.kaggle.com/search?q=football+detection
- **크기**: 다양 (1,000-5,000 이미지)
- **클래스**: ball, player
- **장점**: 다양한 각도/조명 조건

### 4. 직접 수집 (YouTube)
- **방법**: 유튜브 경기 영상에서 프레임 추출
- **도구**: `youtube-dl` + `ffmpeg`
- **라벨링**: Roboflow로 수동 어노테이션
- **필요 시**: 등번호 특화 데이터셋

---

## 🔧 파인튜닝 파이프라인

### Step 1: 데이터 다운로드

```bash
# Roboflow API로 데이터셋 다운로드
python scripts/download_data.py --source roboflow --api-key YOUR_API_KEY

# Kaggle 데이터셋 다운로드
python scripts/download_data.py --source kaggle --dataset football-detection
```

### Step 2: 데이터 전처리

```bash
# YOLO 포맷 변환 및 병합
python scripts/preprocess.py \
    --input data/raw/ \
    --output data/processed/ \
    --split 0.7 0.2 0.1  # train/val/test
```

**전처리 작업**:
- 다양한 포맷 → YOLO 포맷 통일
- 클래스 매핑 (player, goalkeeper → player)
- 이미지 리사이즈 (640x640)
- Train/Val/Test 분할 (70/20/10)
- 데이터 증강 (선택적)

### Step 3: 학습 환경 설정

**로컬 (M4 Mac)**:
```bash
# CoreML 학습은 느림, 검증용으로만 사용
python scripts/train.py --device mps --epochs 10
```

**Google Colab (권장)**:
```python
# notebooks/training.ipynb에서 실행
# GPU: T4 (무료) or A100 (Pro)
```

**AWS SageMaker**:
```bash
# 대규모 학습 시 사용
# g4dn.xlarge 인스턴스
```

### Step 4: 학습 실행

```bash
python scripts/train.py \
    --data data/dataset.yaml \
    --model yolov8s.pt \
    --epochs 100 \
    --batch 16 \
    --imgsz 640 \
    --device 0  # GPU ID
```

**하이퍼파라미터**:
- **모델**: yolov8s (small, 균형)
- **Epochs**: 50-100
- **Batch size**: 16 (GPU 메모리에 따라)
- **Image size**: 640
- **Learning rate**: 0.01 (자동 조정)
- **Optimizer**: AdamW

### Step 5: 평가

```bash
# 테스트 셋에서 평가
python scripts/evaluate.py \
    --model models/best.pt \
    --data data/dataset.yaml

# 실제 영상으로 정성적 평가
python scripts/evaluate.py \
    --model models/best.pt \
    --video test_videos/sample.mp4 \
    --save-output
```

**평가 지표**:
- **mAP@0.5**: Mean Average Precision (IoU 0.5)
- **mAP@0.5:0.95**: IoU 0.5~0.95 평균
- **Precision/Recall**: 클래스별
- **FPS**: 추론 속도 (CoreML 변환 후)

### Step 6: 모델 변환

```bash
# PyTorch → CoreML 변환 (Mac 배포용)
python scripts/convert.py \
    --model models/best.pt \
    --format coreml \
    --output models/best.mlmodel

# 추론 테스트
python scripts/test_inference.py --model models/best.mlmodel
```

---

## 📈 학습 모니터링

### TensorBoard
```bash
tensorboard --logdir runs/train
```

### 체크포인트 관리
- `models/best.pt`: 최고 성능 모델 (mAP 기준)
- `models/last.pt`: 마지막 epoch 모델
- `models/epoch_*.pt`: 주기적 저장 (선택적)

---

## 🧪 실험 계획

### Baseline (사전학습 모델)
```
Model: yolov8s.pt (COCO)
공 탐지: ~70%
선수 탐지: ~80%
FPS: 25-35 (M4)
```

### 실험 1: Roboflow 데이터만
```
Dataset: Roboflow (~3,000 images)
Epochs: 50
예상 개선: 공 85%, 선수 85%
```

### 실험 2: 다중 데이터셋 병합
```
Dataset: Roboflow + Kaggle (~6,000 images)
Epochs: 100
예상 개선: 공 90%+, 선수 90%+
```

### 실험 3: 데이터 증강
```
Augmentation: Flip, Rotate, Color jitter
예상 효과: 다양한 조명 조건 강건성
```

### 실험 4: 모델 크기 비교
```
nano vs small vs medium
트레이드오프: 속도 vs 정확도
```

---

## 📝 데이터셋 포맷

### YOLO 포맷 (Ultralytics)

```
data/
├── images/
│   ├── train/
│   │   ├── img1.jpg
│   │   └── img2.jpg
│   ├── val/
│   └── test/
└── labels/
    ├── train/
    │   ├── img1.txt
    │   └── img2.txt
    ├── val/
    └── test/
```

### 라벨 파일 형식 (`img1.txt`)
```
# class x_center y_center width height (normalized 0-1)
0 0.5 0.5 0.1 0.1  # 공
1 0.3 0.6 0.2 0.4  # 선수
1 0.7 0.6 0.2 0.4  # 선수
```

### dataset.yaml
```yaml
path: /path/to/data
train: images/train
val: images/val
test: images/test

nc: 2  # number of classes
names: ['ball', 'player']
```

---

## 🚨 주의사항

### 1. 데이터셋 라이선스
- Roboflow: 각 데이터셋마다 다름 (확인 필요)
- SoccerNet: 학술 목적 무료, 상업 사용 제한
- Kaggle: 대부분 CC BY 4.0

### 2. 저작권 (YouTube 수집 시)
- 개인 학습 목적: OK
- 데이터셋 공개 배포: 저작권 문제 가능성
- 해결책: 프레임 추출 스크립트만 공유

### 3. 클래스 불균형
- 공: 1개 (한 프레임에)
- 선수: 10-22개
- 해결: Focal Loss or 가중치 조정

### 4. 방송 화면 특성
- 카메라 각도 변화
- 모션 블러
- 압축 아티팩트
- → 다양한 조건의 데이터 필요

---

## 📚 참고 자료

### YOLOv8 공식 문서
- https://docs.ultralytics.com/modes/train/
- https://docs.ultralytics.com/guides/model-export/

### 데이터셋 어노테이션 도구
- **Roboflow**: https://roboflow.com/ (추천)
- **LabelImg**: https://github.com/heartexlabs/labelImg
- **CVAT**: https://github.com/opencv/cvat

### 학습 팁
- https://github.com/ultralytics/yolov5/wiki/Tips-for-Best-Training-Results
- https://blog.roboflow.com/yolov8-training-tips/

---

## 🎯 다음 단계

1. **Phase 0 완료 후**: Baseline 성능 확인
2. **정확도 부족 시**: 파인튜닝 시작
3. **정확도 충분 시**: 바로 익스텐션 개발

**파인튜닝은 필요시에만 진행하는 선택적 단계입니다.**
