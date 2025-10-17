"""
FastAPI WebSocket 서버
크롬 익스텐션으로부터 프레임을 받아서 YOLO 추론 후 결과 반환
"""

import logging
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import base64

from inference import InferencePipeline
from config import HOST, PORT, CORS_ORIGINS

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(title="SoccerHUD Backend")

# CORS 설정 (크롬 익스텐션 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# YOLO 파이프라인 (서버 시작 시 한 번만 로드)
pipeline = None


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 모델 로딩"""
    global pipeline
    logger.info("서버 시작 중...")
    pipeline = InferencePipeline()
    logger.info(f"서버 준비 완료! ws://{HOST}:{PORT}/ws")


@app.get("/")
async def root():
    """헬스체크 엔드포인트"""
    return {
        "status": "ok",
        "service": "SoccerHUD Backend",
        "message": "WebSocket available at /ws",
    }


@app.get("/health")
async def health():
    """상태 확인"""
    return {"status": "healthy", "model_loaded": pipeline is not None}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 엔드포인트
    프레임을 받아서 YOLO 추론 후 결과 반환
    """
    await websocket.accept()
    logger.info("WebSocket 클라이언트 연결됨")

    try:
        while True:
            # 프레임 수신
            data = await websocket.receive_text()

            # JSON 파싱 (또는 직접 Base64 디코딩)
            # 일단 간단하게 Base64 문자열로 받는다고 가정
            try:
                # "data:image/jpeg;base64," 프리픽스 제거
                if data.startswith("data:image"):
                    data = data.split(",")[1]

                # Base64 디코딩
                frame_bytes = base64.b64decode(data)

                # YOLO 추론
                result = pipeline.process(frame_bytes)

                # 결과 전송 (Pydantic 모델이 자동으로 JSON 변환)
                await websocket.send_json(result.model_dump())

            except Exception as e:
                logger.error(f"프레임 처리 중 에러: {e}")
                await websocket.send_json(
                    {"error": str(e), "status": "processing_failed"}
                )

    except WebSocketDisconnect:
        logger.info("WebSocket 클라이언트 연결 끊김")
    except Exception as e:
        logger.error(f"WebSocket 에러: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,  # 개발 중에는 자동 리로드
        log_level="info",
    )
