"""
DeepSORT 기반 선수 추적 시스템
프레임 간 선수 ID 일관성 유지
"""

import numpy as np
from typing import List, Tuple, Optional
from deep_sort_realtime.deepsort_tracker import DeepSort
import logging

from models import PlayerDetection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlayerTracker:
    """
    DeepSORT를 사용한 선수 추적

    기능:
    - 프레임 간 선수 ID 일관성 유지
    - 외형 기반 Re-Identification
    - 카메라 전환 감지 및 자동 리셋
    """

    def __init__(
        self,
        max_age: int = 30,  # 30 프레임 동안 보이지 않으면 삭제
        n_init: int = 3,     # 3 프레임 연속 탐지되면 확정
        max_iou_distance: float = 0.7,
        embedder: str = "mobilenet",  # 'mobilenet' | 'torchreid' | 'clip'
    ):
        """
        Args:
            max_age: 트랙이 유지되는 최대 프레임 수 (보이지 않을 때)
            n_init: 트랙이 확정되기까지 필요한 연속 탐지 수
            max_iou_distance: IoU 임계값 (낮을수록 엄격)
            embedder: ReID 모델 선택
        """
        self.tracker = DeepSort(
            max_age=max_age,
            n_init=n_init,
            max_iou_distance=max_iou_distance,
            embedder=embedder,
            embedder_gpu=False,  # CPU 사용 (속도 우선)
        )

        # 카메라 전환 감지용
        self.prev_detection_count = 0
        self.camera_switch_threshold = 0.5  # 50% 이상 변화 시 전환으로 판단

        logger.info(f"PlayerTracker 초기화 완료 (embedder={embedder})")

    def update(
        self,
        players: List[PlayerDetection],
        frame: np.ndarray,
    ) -> List[PlayerDetection]:
        """
        선수 탐지 결과를 추적 시스템에 업데이트

        Args:
            players: YOLO가 탐지한 선수 리스트
            frame: 원본 프레임 (BGR)

        Returns:
            추적 ID가 업데이트된 선수 리스트
        """
        # 카메라 전환 감지
        if self._detect_camera_switch(len(players)):
            logger.info("카메라 전환 감지 - 트랙 리셋")
            self.reset()

        # DeepSORT 입력 형식으로 변환
        # Format: ([left, top, width, height], confidence, class_id)
        detections = []
        for player in players:
            bbox = [
                player.x - player.width / 2,   # left
                player.y - player.height / 2,  # top
                player.width,
                player.height,
            ]
            detections.append((bbox, player.confidence, 0))  # class_id=0 (person)

        # DeepSORT 업데이트
        tracks = self.tracker.update_tracks(detections, frame=frame)

        # 추적 결과를 PlayerDetection에 반영
        tracked_players = []

        # 모든 트랙 사용 (confirmed + tentative)
        # n_init=3이므로 초기 프레임에서는 tentative 상태임
        for track in tracks:
            if not track.is_confirmed() and not track.is_tentative():
                continue

            # DeepSORT의 바운딩 박스 (원본 detection과 매칭)
            ltwh = track.to_ltwh()
            track_x = ltwh[0] + ltwh[2] / 2  # center x
            track_y = ltwh[1] + ltwh[3] / 2  # center y

            # 원본 players에서 가장 가까운 선수 찾기 (매칭)
            min_dist = float('inf')
            matched_player = None

            for player in players:
                dist = np.sqrt((track_x - player.x)**2 + (track_y - player.y)**2)
                if dist < min_dist:
                    min_dist = dist
                    matched_player = player

            if matched_player is None:
                continue

            # 원본 선수 정보 복사
            tracked_player = matched_player.model_copy()

            # 추적 ID 할당 (DeepSORT의 track_id를 int로 변환)
            tracked_player.id = int(track.track_id)

            # 바운딩 박스 업데이트 (DeepSORT가 보정한 위치)
            # numpy float32 → Python float 변환
            tracked_player.x = float(track_x)
            tracked_player.y = float(track_y)
            tracked_player.width = float(ltwh[2])
            tracked_player.height = float(ltwh[3])

            tracked_players.append(tracked_player)

        self.prev_detection_count = len(players)
        return tracked_players

    def _detect_camera_switch(self, current_count: int) -> bool:
        """
        카메라 전환 감지

        갑자기 탐지된 선수 수가 크게 변하면 카메라가 전환된 것으로 판단
        """
        if self.prev_detection_count == 0:
            return False

        change_ratio = abs(current_count - self.prev_detection_count) / self.prev_detection_count
        return change_ratio > self.camera_switch_threshold

    def reset(self):
        """트랙 초기화 (카메라 전환 시)"""
        self.tracker.delete_all_tracks()
        self.prev_detection_count = 0
        logger.info("트랙 리셋 완료")

    def get_track_count(self) -> int:
        """현재 추적 중인 트랙 수"""
        return len([t for t in self.tracker.tracks if t.is_confirmed()])
