"""
데이터 모델 정의
WebSocket으로 주고받는 JSON 스키마
"""

from pydantic import BaseModel
from typing import Optional, List


class BallDetection(BaseModel):
    """공 탐지 결과"""
    x: float
    y: float
    width: float
    height: float
    confidence: float


class PlayerDetection(BaseModel):
    """선수 탐지 결과"""
    id: int
    x: float
    y: float
    width: float
    height: float
    team: str  # "home" | "away" | "unknown"
    color: List[int]  # RGB [r, g, b]
    confidence: float
    # Phase 3에서 추가될 필드
    number: Optional[int] = None
    name: Optional[str] = None
    position: Optional[str] = None


class BallOwner(BaseModel):
    """공 소유자 정보"""
    player_id: int
    distance: float  # 픽셀 단위
    confidence: float


class DetectionResult(BaseModel):
    """전체 탐지 결과"""
    timestamp: float
    fps: float
    ball: Optional[BallDetection] = None
    players: List[PlayerDetection]
    ball_owner: Optional[BallOwner] = None
