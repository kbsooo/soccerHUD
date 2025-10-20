/**
 * SoccerHUD Offscreen Document
 * TabCapture MediaStream을 받아서 프레임을 캡처하고 content script로 전달
 */

// ============ 로깅 유틸리티 ============
const SERVER_LOG_URL = 'http://localhost:8765/api/log';
const logger = {
  error: (msg) => console.error(msg),
  warn: (msg) => console.warn(msg),
  log: (msg) => console.log(msg),
};

logger.log('🎬 Offscreen Document 로드됨');

let mediaStream = null;
let canvas = null;
let ctx = null;
let video = null;
let captureInterval = null;

// Background script로부터 메시지 수신
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('📩 Offscreen에서 메시지 수신:', message.action);

  if (message.action === 'startCapture') {
    startCapture(message.streamId);
    sendResponse({ success: true });
  }

  if (message.action === 'stopCapture') {
    stopCapture();
    sendResponse({ success: true });
  }

  if (message.action === 'getFrame') {
    const frame = captureFrame();
    sendResponse({ success: true, frame: frame });
  }

  return true;
});

/**
 * 캡처 시작
 */
async function startCapture(streamId) {
  console.log('🎥 Offscreen Capture 시작, streamId:', streamId);

  try {
    // streamId로부터 MediaStream 가져오기
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: {
        mandatory: {
          chromeMediaSource: 'tab',
          chromeMediaSourceId: streamId,
        },
      },
    });

    console.log('✅ MediaStream 획득 성공');

    // Video 요소 생성 및 스트림 연결
    if (!video) {
      video = document.createElement('video');
      video.autoplay = true;
      video.playsInline = true;
    }

    video.srcObject = mediaStream;
    await video.play();

    console.log('✅ Video 재생 시작');

    // Canvas 초기화
    if (!canvas) {
      canvas = document.getElementById('canvas');
      ctx = canvas.getContext('2d', { willReadFrequently: true });
    }

    // 비디오 크기에 맞춰 canvas 크기 설정
    video.addEventListener('loadedmetadata', () => {
      canvas.width = 640;
      canvas.height = Math.floor((video.videoHeight / video.videoWidth) * 640);
      console.log(`✅ Canvas 크기 설정: ${canvas.width}x${canvas.height}`);
    });

  } catch (error) {
    console.error('❌ Capture 시작 실패:', error);
  }
}

/**
 * 캡처 중지
 */
function stopCapture() {
  console.log('⏹️ Offscreen Capture 중지');

  if (captureInterval) {
    clearInterval(captureInterval);
    captureInterval = null;
  }

  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop());
    mediaStream = null;
  }

  if (video) {
    video.srcObject = null;
  }
}

/**
 * 단일 프레임 캡처
 */
function captureFrame() {
  if (!video || !canvas || !ctx) {
    console.warn('⚠️ Video 또는 Canvas가 준비되지 않음');
    return null;
  }

  if (video.readyState < 2) {
    console.warn('⚠️ Video가 아직 준비되지 않음');
    return null;
  }

  try {
    // Canvas에 비디오 프레임 그리기
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // JPEG로 인코딩
    const dataUrl = canvas.toDataURL('image/jpeg', 0.7);
    const base64Data = dataUrl.split(',')[1];

    if (!base64Data || base64Data.length === 0) {
      console.error('❌ Base64 데이터가 비어있음');
      return null;
    }

    return base64Data;

  } catch (error) {
    console.error('❌ 프레임 캡처 실패:', error);
    return null;
  }
}
