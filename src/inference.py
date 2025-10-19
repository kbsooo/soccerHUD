"""
YOLO 추론 파이프라인
프레임 수신 → 전처리 → YOLO 추론 → 후처리 → 공 소유자 판단
"""

import time
import numpy as np
import cv2
from ultralytics import YOLO
from sklearn.cluster import KMeans
from typing import Optional, List, Tuple
import logging

from config import (
    MODEL_PATH,
    COREML_MODEL_PATH,
    USE_COREML,
    INPUT_SIZE,
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD,
    BALL_CLASS_ID,
    PERSON_CLASS_ID,
    BALL_OWNER_MAX_DISTANCE,
    N_TEAMS,
)
from models import (
    BallDetection,
    PlayerDetection,
    BallOwner,
    DetectionResult,
)
from tracker import PlayerTracker
from player_matcher import PlayerMatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InferencePipeline:
    """YOLO 추론 및 선수/공 탐지 파이프라인"""

    def __init__(self, enable_tracking: bool = False):  # 임시로 False
        """모델 로딩

        Args:
            enable_tracking: DeepSORT 추적 활성화 여부 (기본: False, 임시로 비활성화)
        """
        logger.info("InferencePipeline 초기화 시작...")

        # YOLO 모델 로드
        if USE_COREML and COREML_MODEL_PATH.exists():
            logger.info(f"CoreML 모델 로딩: {COREML_MODEL_PATH}")
            # CoreML은 ultralytics로 직접 로드 가능
            self.model = YOLO(str(COREML_MODEL_PATH))
        else:
            logger.info(f"PyTorch 모델 로딩: {MODEL_PATH}")
            self.model = YOLO(str(MODEL_PATH))

        # DeepSORT 추적 (Phase 3)
        self.enable_tracking = enable_tracking
        if enable_tracking:
            self.tracker = PlayerTracker()
            logger.info("DeepSORT 추적 활성화")
        else:
            self.tracker = None
            logger.info("추적 비활성화 (YOLO만 사용)")

        # 선수 매칭 시스템 (Phase 3)
        self.matcher = PlayerMatcher()

        # 성능 측정용
        self.frame_count = 0
        self.total_time = 0.0

        # 팀 색상 히스토리 (프레임 간 일관성 유지)
        self.team_colors = None  # [(r,g,b), (r,g,b)] for [home, away]

        logger.info("InferencePipeline 초기화 완료!")

    def process(self, frame_bytes: bytes) -> DetectionResult:
        """
        프레임을 받아서 탐지 결과 반환

        Args:
            frame_bytes: JPEG 인코딩된 프레임 바이트

        Returns:
            DetectionResult: 탐지 결과
        """
        start_time = time.time()

        # 1. 프레임 디코딩
        frame = self._decode_frame(frame_bytes)

        # 🔍 디버깅: 처음 3프레임만 이미지로 저장
        if self.frame_count < 3:
            from pathlib import Path
            debug_dir = Path("debug_frames")
            debug_dir.mkdir(exist_ok=True)
            debug_path = debug_dir / f"frame_{self.frame_count}.jpg"
            cv2.imwrite(str(debug_path), frame)
            logger.info(f"✅ 프레임 #{self.frame_count} 저장: {debug_path} (shape={frame.shape})")

        # 2. YOLO 추론 (선수용)
        detections = self._run_yolo(frame)
        logger.info(f"🔍 YOLO 탐지 결과: {len(detections.boxes)} 개 객체")

        # 3. YOLO 추론 (공 전용 - 낮은 임계값)
        ball_detections = self._run_yolo_for_ball(frame)

        # 4. 공과 선수 분리
        ball = self._extract_ball(ball_detections, frame)
        players = self._extract_players(detections, frame)
        logger.info(f"🔍 추출 완료: 선수 {len(players)}명, 공 {'O' if ball else 'X'}")

        # 5. DeepSORT 추적 (Phase 3)
        if self.enable_tracking and self.tracker and players:
            players = self.tracker.update(players, frame)
            # 추적 ID에 선수 명단 정보 추가
            players = self.matcher.enrich_players(players)

        # 6. 공 소유자 계산
        ball_owner = self._calculate_ball_owner(ball, players)

        # 성능 측정
        elapsed = time.time() - start_time
        self.total_time += elapsed
        self.frame_count += 1
        avg_fps = self.frame_count / self.total_time if self.total_time > 0 else 0

        return DetectionResult(
            timestamp=time.time(),
            fps=avg_fps,
            ball=ball,
            players=players,
            ball_owner=ball_owner,
        )

    def _decode_frame(self, frame_bytes: bytes) -> np.ndarray:
        """JPEG 바이트를 OpenCV 이미지로 디코딩"""
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return frame

    def _run_yolo(self, frame: np.ndarray):
        """YOLO 추론 실행 (일반 - 선수용)"""
        results = self.model(
            frame,
            imgsz=INPUT_SIZE,
            conf=CONFIDENCE_THRESHOLD,
            iou=IOU_THRESHOLD,
            verbose=False,  # 로그 출력 안함
        )
        return results[0]  # 첫 번째 이미지 결과만 사용

    def _run_yolo_for_ball(self, frame: np.ndarray):
        """
        YOLO 추론 실행 (공 전용 - 낮은 임계값)

        사전학습 모델이 축구공을 잘 탐지하지 못하므로
        낮은 신뢰도로 재실행
        """
        from config import BALL_CONFIDENCE_THRESHOLD

        results = self.model(
            frame,
            imgsz=INPUT_SIZE,
            conf=BALL_CONFIDENCE_THRESHOLD,  # 낮은 임계값
            iou=IOU_THRESHOLD,
            classes=[BALL_CLASS_ID],  # sports ball만
            verbose=False,
        )
        return results[0]

    def _extract_ball(
        self, detections, frame: np.ndarray
    ) -> Optional[BallDetection]:
        """
        공 탐지 결과 추출

        Note: 사전학습 모델이 축구공을 잘 탐지하지 못하므로
        낮은 신뢰도의 탐지도 허용 (추후 파인튜닝으로 개선 예정)
        """
        boxes = detections.boxes

        # BALL_CONFIDENCE_THRESHOLD import 추가 필요
        from config import BALL_CONFIDENCE_THRESHOLD

        best_ball = None
        best_conf = 0.0

        for i in range(len(boxes)):
            cls = int(boxes.cls[i])
            conf = float(boxes.conf[i])

            # sports ball이고 최소 임계값 이상이면
            if cls == BALL_CLASS_ID and conf >= BALL_CONFIDENCE_THRESHOLD:
                # 가장 신뢰도 높은 공 선택
                if conf > best_conf:
                    box = boxes.xyxy[i].cpu().numpy()
                    x1, y1, x2, y2 = box

                    best_ball = BallDetection(
                        x=float((x1 + x2) / 2),
                        y=float((y1 + y2) / 2),
                        width=float(x2 - x1),
                        height=float(y2 - y1),
                        confidence=conf,
                    )
                    best_conf = conf

        return best_ball

    def _extract_players(
        self, detections, frame: np.ndarray
    ) -> List[PlayerDetection]:
        """선수 탐지 결과 추출"""
        boxes = detections.boxes
        players = []

        logger.info(f"🔍 _extract_players: 총 {len(boxes)} 개 박스")

        # person 클래스만 필터링
        person_indices = []
        for i in range(len(boxes)):
            cls = int(boxes.cls[i])
            conf = float(boxes.conf[i])
            logger.info(f"  - 박스 #{i}: class={cls}, conf={conf:.3f}")
            if cls == PERSON_CLASS_ID:
                person_indices.append(i)

        logger.info(f"🔍 person 클래스 필터링 결과: {len(person_indices)} 명")

        if not person_indices:
            return players

        # 유니폼 색상 추출
        uniform_colors = []
        for i in person_indices:
            box = boxes.xyxy[i].cpu().numpy()
            color = self._extract_uniform_color(box, frame)
            uniform_colors.append(color)

        # 팀 분류 (K-means)
        team_labels = self._cluster_teams(uniform_colors)

        # PlayerDetection 객체 생성
        for idx, i in enumerate(person_indices):
            box = boxes.xyxy[i].cpu().numpy()
            conf = float(boxes.conf[i])
            x1, y1, x2, y2 = map(float, box)  # numpy float32 → Python float

            team_label = team_labels[idx]
            team_name = "home" if team_label == 0 else "away"

            players.append(
                PlayerDetection(
                    id=int(i),  # 임시 ID (Phase 3에서 추적 ID로 교체)
                    x=float((x1 + x2) / 2),
                    y=float((y1 + y2) / 2),
                    width=float(x2 - x1),
                    height=float(y2 - y1),
                    team=team_name,
                    color=uniform_colors[idx],
                    confidence=float(conf),
                )
            )

        return players

    def _extract_uniform_color(
        self, box: np.ndarray, frame: np.ndarray
    ) -> List[int]:
        """
        선수 바운딩 박스에서 유니폼 색상 추출
        바운딩 박스의 중앙 30-60% 영역을 유니폼으로 가정
        """
        x1, y1, x2, y2 = box.astype(int)
        h = y2 - y1

        # 상체 영역 (30-60%)
        y_start = int(y1 + h * 0.3)
        y_end = int(y1 + h * 0.6)

        # 영역 추출
        uniform_region = frame[y_start:y_end, x1:x2]

        if uniform_region.size == 0:
            return [128, 128, 128]  # 회색 (기본값)

        # 평균 색상 계산 (BGR → RGB)
        mean_color = cv2.mean(uniform_region)[:3]  # (B, G, R)
        rgb_color = [int(mean_color[2]), int(mean_color[1]), int(mean_color[0])]

        return rgb_color

    def _cluster_teams(self, uniform_colors: List[List[int]]) -> List[int]:
        """
        유니폼 색상을 K-means로 2개 팀으로 클러스터링

        Returns:
            team_labels: 각 선수의 팀 라벨 (0 or 1)
        """
        if len(uniform_colors) < N_TEAMS:
            # 선수가 2명 미만이면 모두 같은 팀으로
            return [0] * len(uniform_colors)

        # K-means 클러스터링
        kmeans = KMeans(n_clusters=N_TEAMS, random_state=42, n_init=10)
        labels = kmeans.fit_predict(uniform_colors)

        # 팀 색상 저장 (다음 프레임에서 일관성 유지용)
        self.team_colors = kmeans.cluster_centers_.astype(int).tolist()

        return labels.tolist()

    def _calculate_ball_owner(
        self, ball: Optional[BallDetection], players: List[PlayerDetection]
    ) -> Optional[BallOwner]:
        """
        공과 가장 가까운 선수를 공 소유자로 판단

        Args:
            ball: 공 탐지 결과
            players: 선수 탐지 결과 리스트

        Returns:
            BallOwner 또는 None (공이 없거나 너무 멀 때)
        """
        if ball is None or len(players) == 0:
            return None

        # 공과 각 선수 간 거리 계산
        min_distance = float("inf")
        closest_player = None

        for player in players:
            distance = np.sqrt(
                (ball.x - player.x) ** 2 + (ball.y - player.y) ** 2
            )
            if distance < min_distance:
                min_distance = distance
                closest_player = player

        # 거리가 너무 멀면 소유 없음
        if min_distance > BALL_OWNER_MAX_DISTANCE:
            return None

        # 신뢰도 계산 (거리가 가까울수록 높음)
        confidence = 1.0 - (min_distance / BALL_OWNER_MAX_DISTANCE)
        confidence = max(0.5, min(1.0, confidence))  # 0.5~1.0 범위

        return BallOwner(
            player_id=int(closest_player.id),
            distance=float(min_distance),
            confidence=float(confidence),
        )
