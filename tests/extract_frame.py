"""
YouTube 영상에서 특정 시간의 프레임 추출
"""

import cv2
import sys
from pathlib import Path


def extract_frame(video_path, timestamp_seconds, output_path):
    """
    비디오에서 특정 시간의 프레임 추출

    Args:
        video_path: 비디오 파일 경로
        timestamp_seconds: 추출할 시간 (초)
        output_path: 저장할 이미지 경로
    """
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        print(f"에러: 비디오를 열 수 없습니다 - {video_path}")
        return False

    # FPS 정보
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"비디오 FPS: {fps}")

    # 프레임 번호 계산
    frame_number = int(timestamp_seconds * fps)
    print(f"추출할 프레임 번호: {frame_number} (at {timestamp_seconds}초)")

    # 해당 프레임으로 이동
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    # 프레임 읽기
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print(f"에러: 프레임을 읽을 수 없습니다")
        return False

    # 저장
    cv2.imwrite(str(output_path), frame)
    print(f"프레임 저장 완료: {output_path}")
    print(f"크기: {frame.shape[1]}x{frame.shape[0]}")

    return True


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent

    video_path = project_root / "sample_videos" / "korea_vs_paraguay.mp4"
    timestamp = 95  # 1분 35초
    output_path = project_root / "sample_videos" / "korea_vs_paraguay_frame.jpg"

    if not video_path.exists():
        print(f"에러: 비디오가 없습니다 - {video_path}")
        sys.exit(1)

    extract_frame(video_path, timestamp, output_path)
