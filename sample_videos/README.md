# 샘플 축구 영상

이 디렉토리에는 YOLO 테스트용 축구 경기 영상을 저장합니다.

## 📥 영상 준비 방법

### 옵션 1: YouTube에서 다운로드

```bash
# yt-dlp 설치 (없으면)
brew install yt-dlp  # Mac
# pip install yt-dlp  # Python

# 축구 영상 다운로드 (720p, 10초 클립)
yt-dlp -f "best[height<=720]" --download-sections "*0-10" \
  -o "sample_videos/soccer_sample_%(id)s.%(ext)s" \
  "YOUTUBE_URL"
```

### 옵션 2: 직접 파일 추가

1. 축구 경기 영상 파일을 이 디렉토리에 복사
2. 파일명 형식: `soccer_*.mp4` or `soccer_*.mov`
3. 권장 해상도: 720p 이상
4. 권장 길이: 10-30초 (테스트용)

### 옵션 3: 테스트용 샘플 (Ultralytics 제공)

```python
# 스크립트에서 자동 다운로드
from ultralytics import YOLO
model = YOLO('yolov8s.pt')
# 기본 샘플 비디오 사용
results = model('https://ultralytics.com/images/bus.jpg')
```

## 📋 추천 영상 조건

### 다양한 조건 테스트를 위해:

1. **조명**
   - ✅ 주간 경기 (밝음)
   - ✅ 야간 경기 (조명)
   - ✅ 흐린 날씨

2. **카메라 각도**
   - ✅ 측면 샷 (가장 일반적)
   - ✅ 원경 샷 (전체 필드)
   - ✅ 클로즈업 샷 (선수 얼굴)

3. **경기 상황**
   - ✅ 공격 상황 (공이 빠르게 움직임)
   - ✅ 패스 플레이 (공 소유 변경)
   - ✅ 세트피스 (정적)

## 🚫 주의사항

### 저작권
- 개인 학습/연구 목적: OK
- 공개 배포: 저작권 문제 가능
- → 샘플 영상을 Git에 커밋하지 마세요!

### .gitignore 설정
이 디렉토리의 비디오 파일은 자동으로 무시됩니다:
```
sample_videos/*.mp4
sample_videos/*.mov
sample_videos/*.avi
```

## 📊 현재 영상 목록

(여기에 다운로드한 영상을 기록하세요)

- [ ] `soccer_sample_1.mp4` - 주간 경기, 측면 샷
- [ ] `soccer_sample_2.mp4` - 야간 경기, 원경 샷
- [ ] `soccer_sample_3.mp4` - 클로즈업 샷

---

**다음 단계**: 영상을 추가한 후 `python tests/test_yolo_video.py` 실행
