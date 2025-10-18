"""
여러 시간대의 프레임을 추출하여 공 탐지 테스트
"""

import cv2
import sys
from pathlib import Path


def extract_multiple_frames(video_path, timestamps, output_dir):
    """
    비디오에서 여러 시간의 프레임 추출

    Args:
        video_path: 비디오 파일 경로
        timestamps: 추출할 시간 리스트 (초)
        output_dir: 저장할 디렉토리
    """
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        print(f"에러: 비디오를 열 수 없습니다 - {video_path}")
        return False

    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"비디오 FPS: {fps}\n")

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    for timestamp in timestamps:
        frame_number = int(timestamp * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()

        if not ret:
            print(f"⚠️  {timestamp}초: 프레임 읽기 실패")
            continue

        # 시간을 분:초 형식으로
        minutes = int(timestamp // 60)
        seconds = int(timestamp % 60)
        time_str = f"{minutes:02d}_{seconds:02d}"

        output_path = output_dir / f"frame_{time_str}.jpg"
        cv2.imwrite(str(output_path), frame)
        print(f"✅ {minutes}:{seconds:02d} → {output_path.name}")

    cap.release()
    print(f"\n총 {len(timestamps)}개 프레임 추출 완료!")
    return True


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    video_path = project_root / "sample_videos" / "korea_vs_paraguay.mp4"
    output_dir = project_root / "sample_videos" / "test_frames"

    if not video_path.exists():
        print(f"에러: 비디오가 없습니다 - {video_path}")
        sys.exit(1)

    # 다양한 시간대 (초 단위)
    # 킥오프, 패스, 슈팅 장면 등을 골고루
    timestamps = [
        30,   # 0:30 - 초반
        60,   # 1:00
        95,   # 1:35 - 원래 테스트
        120,  # 2:00
        180,  # 3:00
        240,  # 4:00
        300,  # 5:00
        360,  # 6:00
    ]

    extract_multiple_frames(video_path, timestamps, output_dir)
