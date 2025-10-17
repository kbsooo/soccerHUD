"""
Phase 1 간단 테스트
샘플 이미지로 파이프라인 테스트
"""

import sys
import cv2
from pathlib import Path

# src 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from inference import InferencePipeline


def test_image(image_path: str):
    """이미지로 파이프라인 테스트"""
    print(f"이미지 로딩: {image_path}")

    # 이미지 읽기
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"에러: 이미지를 열 수 없습니다 - {image_path}")
        return

    print(f"이미지 크기: {frame.shape[1]}x{frame.shape[0]}")

    # JPEG 인코딩
    _, jpeg_buffer = cv2.imencode(".jpg", frame)
    frame_bytes = jpeg_buffer.tobytes()

    # 파이프라인 초기화
    print("\nYOLO 파이프라인 초기화 중...")
    pipeline = InferencePipeline()
    print("초기화 완료!\n")

    # 추론
    print("추론 실행 중...")
    result = pipeline.process(frame_bytes)

    # 결과 출력
    print("\n=== 탐지 결과 ===")
    print(f"FPS: {result.fps:.1f}")
    print(f"타임스탬프: {result.timestamp}")

    if result.ball:
        print(f"\n공 탐지:")
        print(f"  위치: ({result.ball.x:.1f}, {result.ball.y:.1f})")
        print(f"  크기: {result.ball.width:.1f}x{result.ball.height:.1f}")
        print(f"  신뢰도: {result.ball.confidence:.2f}")
    else:
        print("\n공: 탐지 안 됨")

    print(f"\n선수 탐지: {len(result.players)}명")
    for i, player in enumerate(result.players):
        print(f"  선수 {i + 1}:")
        print(f"    팀: {player.team}")
        print(f"    위치: ({player.x:.1f}, {player.y:.1f})")
        print(f"    색상: RGB{tuple(player.color)}")
        print(f"    신뢰도: {player.confidence:.2f}")

    if result.ball_owner:
        owner = next(
            (p for p in result.players if p.id == result.ball_owner.player_id),
            None,
        )
        print(f"\n공 소유자:")
        print(f"  선수 ID: {result.ball_owner.player_id}")
        print(f"  팀: {owner.team if owner else 'Unknown'}")
        print(f"  거리: {result.ball_owner.distance:.1f}px")
        print(f"  신뢰도: {result.ball_owner.confidence:.2f}")
    else:
        print("\n공 소유자: 없음 (공이 없거나 너무 멂)")

    # 결과 시각화
    print("\n결과 시각화 중...")
    vis = visualize(frame, result)

    # 결과 저장
    output_path = Path(__file__).parent.parent / "test_results" / "image_test_result.jpg"
    output_path.parent.mkdir(exist_ok=True)
    cv2.imwrite(str(output_path), vis)
    print(f"결과 저장됨: {output_path}")

    # 화면 표시
    cv2.imshow("Result", vis)
    print("\n아무 키나 누르면 종료...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def visualize(frame, result):
    """결과 시각화"""
    vis = frame.copy()

    # 선수 그리기
    for player in result.players:
        x1 = int(player.x - player.width / 2)
        y1 = int(player.y - player.height / 2)
        x2 = int(player.x + player.width / 2)
        y2 = int(player.y + player.height / 2)

        # 팀 색상 (home은 빨강, away는 파랑)
        color = (0, 0, 255) if player.team == "home" else (255, 0, 0)

        cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)
        label = f"{player.team}"
        cv2.putText(vis, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # 공 그리기
    if result.ball:
        center = (int(result.ball.x), int(result.ball.y))
        radius = int(max(result.ball.width, result.ball.height) / 2)
        cv2.circle(vis, center, radius, (0, 255, 0), 3)
        cv2.putText(vis, "BALL", (center[0] - 20, center[1] - radius - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # 공 소유자 강조
    if result.ball_owner:
        owner = next((p for p in result.players if p.id == result.ball_owner.player_id), None)
        if owner:
            x1 = int(owner.x - owner.width / 2)
            y1 = int(owner.y - owner.height / 2)
            x2 = int(owner.x + owner.width / 2)
            y2 = int(owner.y + owner.height / 2)
            cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 255), 4)

            text = f"{owner.team.upper()} has ball!"
            cv2.putText(vis, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)

    return vis


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    image_path = project_root / "sample_videos" / "korea_vs_paraguay_frame.jpg"

    if not image_path.exists():
        print(f"에러: 이미지가 없습니다 - {image_path}")
        sys.exit(1)

    test_image(str(image_path))
