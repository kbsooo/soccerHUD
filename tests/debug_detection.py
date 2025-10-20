"""
YOLO 탐지만 테스트 (추적 없이)
선수 탐지가 왜 실패하는지 확인
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import cv2
from inference import InferencePipeline

# 비디오 경로
video_path = Path(__file__).parent.parent / "sample_videos" / "korea_vs_paraguay.mp4"

# InferencePipeline 초기화 (추적 비활성화)
print("🚀 InferencePipeline 초기화 (추적 비활성화)...")
pipeline = InferencePipeline(enable_tracking=False)

# 비디오 열기
cap = cv2.VideoCapture(str(video_path))

# 처음부터 순차적으로 읽기 (seek 사용하지 않음)
# start_frame = int(30 * 30)
# cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

print("\n🎬 프레임별 탐지 결과:")
print("=" * 60)

for frame_idx in range(10):  # 10 프레임만
    ret, frame = cap.read()
    if not ret:
        print(f"⚠️ 프레임 읽기 실패 (idx={frame_idx})")
        break

    # JPEG 인코딩
    _, buffer = cv2.imencode(".jpg", frame)
    frame_bytes = buffer.tobytes()

    # 추론
    result = pipeline.process(frame_bytes)

    print(
        f"Frame {frame_idx:2d} | "
        f"Players: {len(result.players):2d} | "
        f"Ball: {'O' if result.ball else 'X'} | "
        f"FPS: {result.fps:5.1f}"
    )

    # Frame 0과 Frame 1의 탐지 상세 정보
    if frame_idx <= 1:
        print(f"  └─ Players: {[f'({p.team}, conf={p.confidence:.2f})' for p in result.players]}")

cap.release()

print("\n" + "=" * 60)
print("✅ 디버깅 완료")
