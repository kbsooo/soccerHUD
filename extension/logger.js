/**
 * SoccerHUD 로깅 유틸리티
 * 중요한 로그를 서버로 자동 전송
 */

const SERVER_LOG_URL = 'http://localhost:8765/api/log';

// 로그 전송 대기열 (너무 많은 요청 방지)
let logQueue = [];
let isSending = false;

/**
 * 서버로 로그 전송
 */
async function sendLogToServer(level, source, message) {
  const logData = {
    level,
    source,
    message,
    timestamp: new Date().toISOString(),
  };

  try {
    await fetch(SERVER_LOG_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(logData),
    });
  } catch (error) {
    // 서버 전송 실패는 무시 (무한 루프 방지)
  }
}

/**
 * 대기열 처리
 */
async function processQueue() {
  if (isSending || logQueue.length === 0) return;

  isSending = true;

  while (logQueue.length > 0) {
    const log = logQueue.shift();
    await sendLogToServer(log.level, log.source, log.message);
    await new Promise(resolve => setTimeout(resolve, 50)); // 50ms 간격
  }

  isSending = false;
}

/**
 * 필터링된 로그만 서버로 전송
 *
 * 필터 조건:
 * - 에러는 모두 전송
 * - 경고 중 SoccerHUD 관련만 전송
 * - 특정 키워드 포함 로그만 전송
 */
function shouldSendLog(level, message) {
  // 에러는 항상 전송
  if (level === 'error') return true;

  // 중요 키워드 체크
  const keywords = [
    'SoccerHUD',
    'Tab Capture',
    'WebSocket',
    'Offscreen',
    '❌', '✅', '⚠️', '🎥', '🔌', '📤',
  ];

  return keywords.some(keyword => message.includes(keyword));
}

/**
 * 로깅 함수들
 */
function createLogger(source) {
  return {
    error: (message, ...args) => {
      console.error(message, ...args);
      const fullMessage = typeof message === 'string'
        ? message
        : JSON.stringify(message);

      if (shouldSendLog('error', fullMessage)) {
        logQueue.push({ level: 'error', source, message: fullMessage });
        processQueue();
      }
    },

    warn: (message, ...args) => {
      console.warn(message, ...args);
      const fullMessage = typeof message === 'string'
        ? message
        : JSON.stringify(message);

      if (shouldSendLog('warn', fullMessage)) {
        logQueue.push({ level: 'warn', source, message: fullMessage });
        processQueue();
      }
    },

    info: (message, ...args) => {
      console.log(message, ...args);
      const fullMessage = typeof message === 'string'
        ? message
        : JSON.stringify(message);

      if (shouldSendLog('info', fullMessage)) {
        logQueue.push({ level: 'info', source, message: fullMessage });
        processQueue();
      }
    },

    log: (message, ...args) => {
      console.log(message, ...args);
      const fullMessage = typeof message === 'string'
        ? message
        : JSON.stringify(message);

      if (shouldSendLog('info', fullMessage)) {
        logQueue.push({ level: 'info', source, message: fullMessage });
        processQueue();
      }
    },
  };
}

// Export for different contexts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { createLogger };
}
