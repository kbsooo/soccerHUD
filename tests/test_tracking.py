"""
DeepSORT 추적 시스템 테스트
여러 프레임에서 선수 ID 일관성 확인
"""

import sys
from pathlib import Path

# src 폴더를 import 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import cv2
import numpy as np
from inference import InferencePipeline
import json


def test_tracking_on_video():
    """
    비디오 여러 프레임에서 추적 테스트

    목표:
    - 같은 선수가 프레임 간 같은 ID 유지하는지 확인
    - 카메라 전환 시 ID 리셋되는지 확인
    """
    # 비디오 경로
    video_path = Path(__file__).parent.parent / "sample_videos" / "korea_vs_paraguay.mp4"

    if not video_path.exists():
        print(f"❌ 비디오 파일 없음: {video_path}")
        return

    # InferencePipeline 초기화 (추적 활성화)
    print("🚀 InferencePipeline 초기화 (추적 활성화)...")
    pipeline = InferencePipeline(enable_tracking=True)

    # 비디오 열기
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"❌ 비디오 열기 실패: {video_path}")
        return

    print(f"✅ 비디오 열기 성공: {video_path}")

    # 테스트할 프레임 범위 (1분 35초 ~ 1분 40초, 약 150 프레임)
    start_frame = int(95 * 30)  # 95초 * 30 FPS
    num_frames = 150

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # 결과 저장
    tracking_results = []
    output_dir = Path(__file__).parent.parent / "test_results" / "tracking"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🎬 프레임 처리 시작 ({num_frames} 프레임)...")
    print("=" * 60)

    for frame_idx in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            print(f"⚠️ 프레임 읽기 실패 (idx={frame_idx})")
            break

        # JPEG 인코딩
        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        # 추론 + 추적
        result = pipeline.process(frame_bytes)

        # 결과 기록
        frame_result = {
            "frame_idx": frame_idx,
            "timestamp": result.timestamp,
            "fps": result.fps,
            "num_players": len(result.players),
            "players": [
                {
                    "id": p.id,
                    "team": p.team,
                    "x": int(p.x),
                    "y": int(p.y),
                }
                for p in result.players
            ],
        }
        tracking_results.append(frame_result)

        # 10프레임마다 출력
        if frame_idx % 10 == 0:
            print(
                f"Frame {frame_idx:3d} | Players: {len(result.players):2d} | "
                f"FPS: {result.fps:5.1f} | "
                f"IDs: {sorted([p.id for p in result.players])}"
            )

        # 일부 프레임 시각화 (30프레임마다)
        if frame_idx % 30 == 0:
            vis_frame = frame.copy()

            # 선수 바운딩 박스 그리기
            for player in result.players:
                x1 = int(player.x - player.width / 2)
                y1 = int(player.y - player.height / 2)
                x2 = int(player.x + player.width / 2)
                y2 = int(player.y + player.height / 2)

                # 팀 색상으로 박스 그리기
                color = (0, 0, 255) if player.team == "home" else (255, 0, 0)
                cv2.rectangle(vis_frame, (x1, y1), (x2, y2), color, 2)

                # ID 표시
                text = f"ID:{player.id} ({player.team})"
                cv2.putText(
                    vis_frame,
                    text,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2,
                )

            # 저장
            output_path = output_dir / f"frame_{frame_idx:04d}.jpg"
            cv2.imwrite(str(output_path), vis_frame)

    cap.release()

    print("\n" + "=" * 60)
    print(f"✅ 테스트 완료! ({len(tracking_results)} 프레임)")

    # 결과 JSON 저장
    json_path = output_dir / "tracking_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(tracking_results, f, indent=2, ensure_ascii=False)

    print(f"📊 결과 저장: {json_path}")
    print(f"🖼️  시각화 이미지: {output_dir}/*.jpg")

    # ID 일관성 분석
    analyze_tracking_consistency(tracking_results)


def analyze_tracking_consistency(results):
    """
    추적 일관성 분석

    - ID 스와핑 빈도
    - 평균 트랙 길이
    - 가장 오래 추적된 선수
    """
    print("\n" + "=" * 60)
    print("📈 추적 일관성 분석")
    print("=" * 60)

    # ID별 등장 프레임 수 계산
    id_counts = {}
    for frame in results:
        for player in frame["players"]:
            player_id = player["id"]
            if player_id not in id_counts:
                id_counts[player_id] = 0
            id_counts[player_id] += 1

    # 통계
    if id_counts:
        total_tracks = len(id_counts)
        avg_track_length = sum(id_counts.values()) / total_tracks
        max_track_length = max(id_counts.values())
        max_track_id = max(id_counts, key=id_counts.get)

        print(f"총 트랙 수: {total_tracks}")
        print(f"평균 트랙 길이: {avg_track_length:.1f} 프레임")
        print(f"가장 긴 트랙: ID {max_track_id} ({max_track_length} 프레임)")

        # 긴 트랙 (50 프레임 이상)
        long_tracks = {k: v for k, v in id_counts.items() if v >= 50}
        print(f"\n안정적인 트랙 (50+ 프레임): {len(long_tracks)}개")
        for track_id, count in sorted(long_tracks.items(), key=lambda x: -x[1])[:10]:
            print(f"  - ID {track_id}: {count} 프레임")
    else:
        print("⚠️ 추적된 선수가 없습니다.")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 DeepSORT 추적 테스트")
    print("=" * 60)
    test_tracking_on_video()
