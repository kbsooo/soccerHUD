"""
Phase 3: 선수 식별 시스템 테스트
DeepSORT 추적 + PlayerMatcher 통합 검증
"""

import sys
import os

# 상위 디렉토리의 src를 import path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import cv2
import numpy as np
from inference import InferencePipeline
from player_matcher import PlayerMatcher


def test_tracker_initialization():
    """추적 시스템 초기화 테스트"""
    print("\n=== 추적 시스템 초기화 테스트 ===")

    pipeline = InferencePipeline(enable_tracking=True)

    assert pipeline.tracker is not None, "Tracker가 초기화되지 않음"
    assert pipeline.matcher is not None, "PlayerMatcher가 초기화되지 않음"

    print("✅ 추적 시스템 초기화 성공")
    return pipeline


def test_roster_management(pipeline: InferencePipeline):
    """명단 관리 테스트"""
    print("\n=== 명단 관리 테스트 ===")

    # 명단 설정
    home_players = [
        {"name": "손흥민", "number": 7, "position": "FW"},
        {"name": "김민재", "number": 3, "position": "CB"},
        {"name": "이강인", "number": 18, "position": "MF"},
    ]

    away_players = [
        {"name": "메시", "number": 10, "position": "FW"},
        {"name": "호날두", "number": 7, "position": "FW"},
    ]

    pipeline.matcher.set_roster(home_players, away_players)

    # 명단 요약 확인
    summary = pipeline.matcher.get_roster_summary()
    assert summary["home"] == 3, "홈팀 선수 수 불일치"
    assert summary["away"] == 2, "원정팀 선수 수 불일치"
    assert summary["matched"] == 0, "초기 매칭 수는 0이어야 함"

    print(f"✅ 명단 설정 성공: {summary}")

    # 수동 매칭 테스트
    pipeline.matcher.match_player(track_id=1, team="home", number=7)
    pipeline.matcher.match_player(track_id=2, team="away", number=10)

    summary = pipeline.matcher.get_roster_summary()
    assert summary["matched"] == 2, "매칭 수 불일치"

    # 매칭 조회
    player1 = pipeline.matcher.get_player_info(1)
    assert player1["name"] == "손흥민", "매칭된 선수 이름 불일치"
    assert player1["number"] == 7, "매칭된 선수 번호 불일치"

    player2 = pipeline.matcher.get_player_info(2)
    assert player2["name"] == "메시", "매칭된 선수 이름 불일치"

    print(f"✅ 수동 매칭 성공: {summary}")
    print(f"   - Track 1: {player1['name']} #{player1['number']}")
    print(f"   - Track 2: {player2['name']} #{player2['number']}")


def test_inference_with_tracking(pipeline: InferencePipeline):
    """추적 시스템 포함 추론 테스트"""
    print("\n=== 추적 포함 추론 테스트 ===")

    # 테스트 프레임 로드
    test_image_path = os.path.join(
        os.path.dirname(__file__),
        'sample_frames',
        'frame_01_00.jpg'
    )

    if not os.path.exists(test_image_path):
        print(f"⚠️  테스트 이미지 없음: {test_image_path}")
        print("   sample_frames 폴더에 프레임 추가 필요")
        return

    # 프레임 로드 및 인코딩
    frame = cv2.imread(test_image_path)
    _, encoded = cv2.imencode('.jpg', frame)
    frame_bytes = encoded.tobytes()

    # 여러 프레임 처리 (추적 확인)
    print("\n프레임 처리 중...")
    for i in range(5):
        result = pipeline.process(frame_bytes)

        print(f"\n프레임 {i+1}:")
        print(f"  - FPS: {result.fps:.2f}")
        print(f"  - 선수 수: {len(result.players)}")
        print(f"  - 공 탐지: {'✅' if result.ball else '❌'}")

        if result.players:
            print(f"  - 추적 ID 범위: {min(p.id for p in result.players)} ~ {max(p.id for p in result.players)}")

            # 매칭된 선수 확인
            matched = [p for p in result.players if p.name is not None]
            if matched:
                print(f"  - 매칭된 선수: {len(matched)}명")
                for p in matched[:3]:  # 최대 3명만 출력
                    print(f"    • {p.name} #{p.number} (ID {p.id})")

        if result.ball_owner:
            print(f"  - 공 소유: Track ID {result.ball_owner.player_id} (거리: {result.ball_owner.distance:.1f}px)")

    print("\n✅ 추적 포함 추론 테스트 완료")


def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("Phase 3: 선수 식별 시스템 테스트")
    print("=" * 60)

    try:
        # 1. 초기화 테스트
        pipeline = test_tracker_initialization()

        # 2. 명단 관리 테스트
        test_roster_management(pipeline)

        # 3. 추적 포함 추론 테스트
        test_inference_with_tracking(pipeline)

        print("\n" + "=" * 60)
        print("✅ 모든 테스트 통과!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 예상치 못한 에러: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
