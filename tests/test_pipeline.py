"""
Phase 1 E2E 테스트
로컬 비디오 파일로 파이프라인 테스트 및 결과 시각화
"""

import sys
import cv2
import time
from pathlib import Path

# src 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from inference import InferencePipeline
from models import DetectionResult


def test_pipeline_with_video(video_path: str, output_path: str = None):
    """
    비디오 파일로 파이프라인 테스트

    Args:
        video_path: 입력 비디오 경로
        output_path: 결과 비디오 저장 경로 (None이면 화면에만 표시)
    """
    print(f"비디오 로딩: {video_path}")
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"에러: 비디오를 열 수 없습니다 - {video_path}")
        return

    # 비디오 정보
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"비디오 정보: {width}x{height} @ {fps} FPS, 총 {total_frames} 프레임")

    # 결과 비디오 writer
    writer = None
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        print(f"결과 저장 경로: {output_path}")

    # 파이프라인 초기화
    print("\nYOLO 파이프라인 초기화 중...")
    pipeline = InferencePipeline()
    print("초기화 완료!\n")

    frame_count = 0
    start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # 프레임을 JPEG로 인코딩 (실제 WebSocket 전송 시뮬레이션)
            _, jpeg_buffer = cv2.imencode(".jpg", frame)
            frame_bytes = jpeg_buffer.tobytes()

            # 추론
            result: DetectionResult = pipeline.process(frame_bytes)

            # 결과 시각화
            vis_frame = visualize_result(frame, result)

            # 화면 표시
            cv2.imshow("SoccerHUD Test", vis_frame)

            # 비디오 저장
            if writer:
                writer.write(vis_frame)

            # FPS 출력 (10 프레임마다)
            if frame_count % 10 == 0:
                elapsed = time.time() - start_time
                current_fps = frame_count / elapsed
                print(
                    f"프레임 {frame_count}/{total_frames} | "
                    f"처리 FPS: {current_fps:.1f} | "
                    f"공: {result.ball is not None} | "
                    f"선수: {len(result.players)}명 | "
                    f"소유: {result.ball_owner is not None}"
                )

            # 'q' 키로 종료
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("\n사용자가 중단했습니다.")
                break

    finally:
        # 리소스 정리
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()

        # 최종 통계
        elapsed = time.time() - start_time
        avg_fps = frame_count / elapsed
        print(f"\n=== 테스트 완료 ===")
        print(f"처리한 프레임: {frame_count}/{total_frames}")
        print(f"소요 시간: {elapsed:.1f}초")
        print(f"평균 FPS: {avg_fps:.1f}")


def visualize_result(frame, result: DetectionResult):
    """
    탐지 결과를 프레임에 그리기

    Args:
        frame: 원본 프레임
        result: 탐지 결과

    Returns:
        시각화된 프레임
    """
    vis = frame.copy()

    # 1. 선수 그리기
    for player in result.players:
        # 바운딩 박스
        x1 = int(player.x - player.width / 2)
        y1 = int(player.y - player.height / 2)
        x2 = int(player.x + player.width / 2)
        y2 = int(player.y + player.height / 2)

        # 팀 색상
        color = tuple(player.color) if player.team == "home" else (0, 255, 255)

        # 박스 그리기
        cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)

        # 라벨
        label = f"{player.team} ({player.confidence:.2f})"
        cv2.putText(
            vis,
            label,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
        )

    # 2. 공 그리기
    if result.ball:
        ball = result.ball
        center = (int(ball.x), int(ball.y))
        radius = int(max(ball.width, ball.height) / 2)

        cv2.circle(vis, center, radius, (0, 255, 0), 2)
        cv2.putText(
            vis,
            f"BALL {ball.confidence:.2f}",
            (center[0] - 30, center[1] - radius - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2,
        )

    # 3. 공 소유자 표시
    if result.ball_owner:
        # 소유자 찾기
        owner = next(
            (p for p in result.players if p.id == result.ball_owner.player_id),
            None,
        )
        if owner:
            # 소유자 박스를 더 두껍게
            x1 = int(owner.x - owner.width / 2)
            y1 = int(owner.y - owner.height / 2)
            x2 = int(owner.x + owner.width / 2)
            y2 = int(owner.y + owner.height / 2)
            cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 0, 255), 4)

            # 텍스트 표시
            text = f"{owner.team.upper()} has ball!"
            cv2.putText(
                vis,
                text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                2,
            )

    # 4. FPS 표시
    cv2.putText(
        vis,
        f"FPS: {result.fps:.1f}",
        (10, vis.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    return vis


if __name__ == "__main__":
    # 샘플 비디오 경로
    video_path = "../sample_videos/sample1.mp4"  # 여기를 실제 경로로 수정
    output_path = "../test_results/pipeline_test_output.mp4"

    # 비디오 경로 확인
    if not Path(video_path).exists():
        print(f"에러: 비디오 파일이 없습니다 - {video_path}")
        print("\n사용법:")
        print("  python test_pipeline.py <비디오_경로> [출력_경로]")
        print("\n또는 코드에서 video_path를 수정하세요.")
        sys.exit(1)

    # 테스트 실행
    test_pipeline_with_video(video_path, output_path)
