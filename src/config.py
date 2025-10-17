"""
SoccerHUD 설정 파일
모든 설정값을 여기서 관리
"""

import os
from pathlib import Path

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent

# 모델 설정
MODEL_PATH = PROJECT_ROOT / "yolov8s.pt"  # 또는 .mlpackage
MODEL_SIZE = "small"  # nano | small | medium
INPUT_SIZE = 640  # 입력 해상도
CONFIDENCE_THRESHOLD = 0.5  # 탐지 신뢰도 임계값
IOU_THRESHOLD = 0.4  # NMS IoU 임계값

# CoreML 설정 (Mac M-series)
USE_COREML = True  # Mac이면 True
COREML_MODEL_PATH = PROJECT_ROOT / "yolov8s.mlpackage"

# 서버 설정
HOST = "localhost"
PORT = 8765
CORS_ORIGINS = ["*"]  # 개발 중에는 모든 origin 허용

# 프레임 처리 설정
TARGET_FPS = 30
JPEG_QUALITY = 70  # 프레임 압축 품질

# 공 소유자 판단
BALL_OWNER_MAX_DISTANCE = 50  # 픽셀 단위, 이보다 멀면 "소유 없음"

# 유니폼 색상 클러스터링
N_TEAMS = 2  # 홈팀 + 원정팀
COLOR_MATCHING_THRESHOLD = 30  # RGB 유클리드 거리

# YOLO 클래스 필터 (COCO 데이터셋 기준)
BALL_CLASS_ID = 32  # sports ball
PERSON_CLASS_ID = 0  # person

# 로그 설정
LOG_LEVEL = "INFO"
