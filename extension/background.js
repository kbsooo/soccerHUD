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
  error: (...args) => {
    console.error(...args);
    const msg = args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : String(arg)).join(' ');
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
