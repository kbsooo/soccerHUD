"""
선수 매칭 시스템
추적 ID와 실제 선수 명단을 매칭
"""

import logging
from typing import Dict, List, Optional
from models import PlayerDetection

logger = logging.getLogger(__name__)


class PlayerMatcher:
    """
    추적 ID를 실제 선수 정보와 매칭

    사용자가 입력한 선수 명단과 DeepSORT 추적 ID를 연결
    """

    def __init__(self):
        """초기화"""
        # 선수 명단 (사용자 입력)
        # Format: {"home": [...], "away": [...]}
        self.roster: Dict[str, List[dict]] = {
            "home": [],
            "away": [],
        }

        # 추적 ID → 선수 정보 매핑
        # Format: {track_id: {"name": "손흥민", "number": 7, "team": "home", ...}}
        self.id_to_player: Dict[int, dict] = {}

        # 선수 번호 → 추적 ID 역매핑
        # Format: {("home", 7): track_id}
        self.player_to_id: Dict[tuple, int] = {}

        logger.info("PlayerMatcher 초기화 완료")

    def set_roster(self, home_players: List[dict], away_players: List[dict]):
        """
        선수 명단 설정

        Args:
            home_players: 홈팀 선수 리스트
                [{"name": "손흥민", "number": 7, "position": "FW"}, ...]
            away_players: 원정팀 선수 리스트
        """
        self.roster["home"] = home_players
        self.roster["away"] = away_players

        logger.info(f"선수 명단 설정: 홈 {len(home_players)}명, 원정 {len(away_players)}명")

        # 기존 매핑 초기화
        self.id_to_player.clear()
        self.player_to_id.clear()

    def match_player(self, track_id: int, team: str, number: int = None):
        """
        수동 매칭: 추적 ID를 특정 선수에 할당

        Args:
            track_id: DeepSORT 추적 ID
            team: "home" or "away"
            number: 등번호 (옵션)
        """
        if not self.roster[team]:
            logger.warning(f"{team} 팀 명단이 비어있음")
            return

        if number:
            # 등번호로 선수 찾기
            player = next(
                (p for p in self.roster[team] if p.get("number") == number),
                None
            )
        else:
            logger.warning("등번호 없이 매칭 불가능")
            return

        if player:
            self.id_to_player[track_id] = {
                **player,
                "team": team,
            }
            self.player_to_id[(team, number)] = track_id
            logger.info(f"매칭: ID {track_id} → {player['name']} #{number}")
        else:
            logger.warning(f"{team} 팀에서 #{number} 선수를 찾을 수 없음")

    def get_player_info(self, track_id: int) -> Optional[dict]:
        """추적 ID로 선수 정보 조회"""
        return self.id_to_player.get(track_id)

    def get_track_id(self, team: str, number: int) -> Optional[int]:
        """선수 번호로 추적 ID 조회"""
        return self.player_to_id.get((team, number))

    def enrich_players(
        self, players: List[PlayerDetection]
    ) -> List[PlayerDetection]:
        """
        선수 리스트에 명단 정보 추가

        Args:
            players: 추적 ID가 있는 선수 리스트

        Returns:
            이름/번호가 추가된 선수 리스트
        """
        enriched_players = []

        for player in players:
            # 복사본 생성
            enriched = player.model_copy()

            # 매칭된 선수 정보 조회
            info = self.get_player_info(player.id)

            if info:
                enriched.name = info.get("name")
                enriched.number = info.get("number")
                enriched.position = info.get("position")

            enriched_players.append(enriched)

        return enriched_players

    def auto_match_by_position(
        self,
        players: List[PlayerDetection],
        formation: str = "4-4-2"
    ):
        """
        자동 매칭: 필드 위치 기반

        (실험적 기능, 현재 미구현)

        Args:
            players: 선수 리스트
            formation: 포메이션 (예: "4-4-2")
        """
        # TODO: Phase 3 확장 기능
        # 필드를 격자로 나누고, 각 영역의 포지션을 추정
        # 예: 왼쪽 위 = LB, 중앙 위 = CB, 오른쪽 위 = RB
        logger.warning("자동 매칭 기능은 아직 구현되지 않았습니다")
        pass

    def get_roster_summary(self) -> dict:
        """현재 명단 요약"""
        return {
            "home": len(self.roster["home"]),
            "away": len(self.roster["away"]),
            "matched": len(self.id_to_player),
        }
