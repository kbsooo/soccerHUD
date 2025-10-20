/**
 * SoccerHUD Background Service Worker
 * 활성화 상태 관리 및 Content Script와 통신
 */

// ============ 로깅 유틸리티 ============
const SERVER_LOG_URL = 'http://localhost:8765/api/log';
let logQueue = [];
let isSending = false;

async function sendLogToServer(level, source, message) {
  const logData = { level, source, message, timestamp: new Date().toISOString() };
  try {
    await fetch(SERVER_LOG_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(logData),
    });
  } catch (error) {
    // 무시
  }
}

async function processQueue() {
  if (isSending || logQueue.length === 0) return;
  isSending = true;
  while (logQueue.length > 0) {
    const log = logQueue.shift();
    await sendLogToServer(log.level, log.source, log.message);
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  isSending = false;
}

function shouldSendLog(level, message) {
  if (level === 'error') return true;
  const keywords = ['SoccerHUD', 'Tab Capture', 'Offscreen', '❌', '✅', '⚠️', '🎥', '🔌'];
  return keywords.some(keyword => message.includes(keyword));
}

const logger = {
  error: (msg) => {
    console.error(msg);
    if (shouldSendLog('error', msg)) {
      logQueue.push({ level: 'error', source: 'background', message: msg });
      processQueue();
    }
  },
  warn: (msg) => {
    console.warn(msg);
    if (shouldSendLog('warn', msg)) {
      logQueue.push({ level: 'warn', source: 'background', message: msg });
      processQueue();
    }
  },
  log: (msg) => {
    console.log(msg);
    if (shouldSendLog('info', msg)) {
      logQueue.push({ level: 'info', source: 'background', message: msg });
      processQueue();
    }
  },
};

logger.log('🔧 SoccerHUD Background Service Worker 시작');

let captureStream = null;
let offscreenCreated = false;

/**
 * Offscreen Document 생성
 */
async function createOffscreenDocument() {
  if (offscreenCreated) {
    return;
  }

  try {
    await chrome.offscreen.createDocument({
      url: 'offscreen.html',
      reasons: ['USER_MEDIA'],
      justification: 'Capture video frames from tab for soccer player detection',
    });

    offscreenCreated = true;
    logger.log('✅ Offscreen Document 생성 완료');
  } catch (error) {
    logger.error('❌ Offscreen Document 생성 실패:', error);
    throw error;
  }
}

/**
 * Tab Capture 시작 전체 플로우
 */
async function startTabCaptureFlow(tabId) {
  logger.log('🎬 Tab Capture Flow 시작, 탭 ID:', tabId);

  // 1. Offscreen Document 생성
  await createOffscreenDocument();

  // 2. Tab Capture 시작
  return new Promise((resolve, reject) => {
    chrome.tabCapture.capture(
      {
        video: true,
        audio: false,
        videoConstraints: {
          mandatory: {
            minWidth: 1280,
            minHeight: 720,
            maxWidth: 1920,
            maxHeight: 1080,
            maxFrameRate: 30,
          },
        },
      },
      (stream) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
          return;
        }

        if (!stream) {
          reject(new Error('Stream is null'));
          return;
        }

        logger.log('✅ Tab Capture Stream 획득:', stream.getVideoTracks()[0].getSettings());

        captureStream = stream;

        // 3. Offscreen document에 stream 시작 알림
        const streamId = stream.getVideoTracks()[0].id;
        chrome.runtime.sendMessage(
          { action: 'startCapture', streamId: streamId },
          (response) => {
            if (response && response.success) {
              logger.log('✅ Offscreen에 캡처 시작 알림 완료');
              resolve();
            } else {
              reject(new Error('Offscreen 캡처 시작 실패'));
            }
          }
        );
      }
    );
  });
}

/**
 * Tab Capture 중지
 */
function stopTabCaptureFlow() {
  // Offscreen에 중지 알림
  if (offscreenCreated) {
    chrome.runtime.sendMessage({ action: 'stopCapture' });
  }

  // Stream 중지
  if (captureStream) {
    captureStream.getTracks().forEach(track => track.stop());
    captureStream = null;
  }

  logger.log('✅ Tab Capture Flow 중지 완료');
}

/**
 * Offscreen으로부터 프레임 가져오기
 */
async function getFrameFromOffscreen() {
  if (!offscreenCreated) {
    throw new Error('Offscreen document가 생성되지 않음');
  }

  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ action: 'getFrame' }, (response) => {
      if (response && response.success && response.frame) {
        resolve(response.frame);
      } else {
        reject(new Error('프레임 캡처 실패'));
      }
    });
  });
}

// 설치 시
chrome.runtime.onInstalled.addListener(() => {
  console.log('✅ SoccerHUD 설치 완료');

  // 초기 상태 설정
  chrome.storage.local.set({
    soccerhudActive: false,
    serverStatus: 'disconnected',
  });
});

// Content Script로부터 메시지 수신
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('📩 Background에서 메시지 수신:', message);

  if (message.action === 'updateStatus') {
    // 상태 업데이트
    chrome.storage.local.set({
      serverStatus: message.status,
    });
  }

  // Tab Capture 요청 처리
  if (message.action === 'startTabCapture') {
    console.log('🎥 Tab Capture 시작 요청 받음, 탭 ID:', sender.tab?.id);

    startTabCaptureFlow(sender.tab.id)
      .then(() => {
        sendResponse({ success: true });
      })
      .catch((error) => {
        logger.error('❌ Tab Capture 실패:', error);
        sendResponse({ success: false, error: error.message });
      });

    return true; // 비동기 응답
  }

  // Tab Capture 중지 요청
  if (message.action === 'stopTabCapture') {
    logger.log('⏹️ Tab Capture 중지 요청');
    stopTabCaptureFlow();
    sendResponse({ success: true });
    return true;
  }

  // 프레임 요청 처리
  if (message.action === 'getFrame') {
    getFrameFromOffscreen()
      .then((frame) => {
        sendResponse({ success: true, frame: frame });
      })
      .catch((error) => {
        sendResponse({ success: false, error: error.message });
      });

    return true;
  }

  return true;
});

// Storage 변경 감지
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace === 'local' && changes.soccerhudActive) {
    const isActive = changes.soccerhudActive.newValue;
    console.log(`🔄 활성화 상태 변경: ${isActive}`);

    // 모든 YouTube 탭에 메시지 전송
    chrome.tabs.query({ url: 'https://www.youtube.com/*' }, (tabs) => {
      tabs.forEach((tab) => {
        chrome.tabs.sendMessage(
          tab.id,
          {
            action: isActive ? 'activate' : 'deactivate',
          },
          (response) => {
            if (chrome.runtime.lastError) {
              console.error('메시지 전송 실패:', chrome.runtime.lastError);
            } else {
              console.log('✅ 메시지 전송 성공:', response);
            }
          }
        );
      });
    });
  }
});
