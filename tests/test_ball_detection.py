"""
공 탐지 상세 테스트
YOLO의 모든 탐지 결과를 확인하여 공이 탐지되는지 검증
"""

import sys
import cv2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ultralytics import YOLO
from config import MODEL_PATH, CONFIDENCE_THRESHOLD, BALL_CLASS_ID


def test_ball_detection(image_path):
    """공 탐지 상세 분석"""
    print(f"\n{'='*60}")
    print(f"이미지: {Path(image_path).name}")
    print(f"{'='*60}")

    # 이미지 읽기
    frame = cv2.imread(str(image_path))
    if frame is None:
        print("❌ 이미지를 열 수 없습니다")
        return

    print(f"크기: {frame.shape[1]}x{frame.shape[0]}")

    # YOLO 모델 로드
    model = YOLO(str(MODEL_PATH))

    # 추론 (낮은 임계값으로)
    print(f"\n🔍 YOLO 추론 중 (임계값: 0.1)...")
    results = model(
        frame,
        imgsz=640,
        conf=0.1,  # 매우 낮은 임계값
        verbose=False,
    )[0]

    boxes = results.boxes

    # 모든 탐지 결과 출력
    print(f"\n총 {len(boxes)}개 객체 탐지됨\n")

    # 클래스별로 그룹화
    class_counts = {}
    ball_detections = []

    for i in range(len(boxes)):
        cls = int(boxes.cls[i])
        conf = float(boxes.conf[i])
        box = boxes.xyxy[i].cpu().numpy()

        # 클래스 카운트
        class_name = model.names[cls]
        if class_name not in class_counts:
            class_counts[class_name] = 0
        class_counts[class_name] += 1

        # sports ball 찾기
        if cls == BALL_CLASS_ID:
            ball_detections.append({
                'conf': conf,
                'box': box,
                'class_name': class_name
            })

    # 클래스별 통계
    print("📊 탐지된 클래스:")
    for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {class_name}: {count}개")

    # 공 탐지 결과
    print(f"\n⚽ 공(sports ball) 탐지 결과:")
    if ball_detections:
        print(f"  ✅ {len(ball_detections)}개 탐지됨!")
        for idx, det in enumerate(ball_detections):
            x1, y1, x2, y2 = det['box']
            print(f"\n  공 #{idx + 1}:")
            print(f"    신뢰도: {det['conf']:.3f}")
            print(f"    위치: ({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f})")
            print(f"    크기: {x2-x1:.0f}x{y2-y1:.0f}")
    else:
        print(f"  ❌ 탐지 안 됨")
        print(f"\n  💡 힌트:")
        print(f"    - 현재 임계값: {CONFIDENCE_THRESHOLD}")
        print(f"    - 공이 작거나 가려져 있을 수 있음")
        print(f"    - 다른 프레임을 테스트해보세요")

    # 결과 시각화
    vis = frame.copy()

    # 공만 그리기
    for det in ball_detections:
        x1, y1, x2, y2 = det['box'].astype(int)
        cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 0), 3)
        cv2.putText(
            vis,
            f"BALL {det['conf']:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )

    # 저장
    output_dir = Path(__file__).parent.parent / "test_results" / "ball_detection"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_name = Path(image_path).stem + "_ball.jpg"
    output_path = output_dir / output_name
    cv2.imwrite(str(output_path), vis)
    print(f"\n💾 결과 저장: {output_path}")


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    test_frames_dir = project_root / "sample_videos" / "test_frames"

    if not test_frames_dir.exists():
        print("❌ test_frames 디렉토리가 없습니다")
        print("먼저 extract_multiple_frames.py를 실행하세요")
        sys.exit(1)

    # 모든 프레임 테스트
    frames = sorted(test_frames_dir.glob("frame_*.jpg"))

    print(f"🎯 총 {len(frames)}개 프레임 테스트\n")

    for frame_path in frames:
        test_ball_detection(frame_path)

    print(f"\n{'='*60}")
    print("✅ 모든 테스트 완료!")
    print(f"{'='*60}")
