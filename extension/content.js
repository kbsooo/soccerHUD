/**
 * SoccerHUD Content Script
 * YouTube 비디오에서 프레임을 캡처하고 서버로 전송하여 결과를 오버레이로 표시
 */

console.log('🎯 SoccerHUD Content Script 로드됨');

// 전역 상태
let videoElement = null;
let overlayContainer = null;
let isActive = false;
let ws = null;
let captureInterval = null;

// 설정
const CONFIG = {
  SERVER_URL: 'ws://localhost:8765/ws',
  CAPTURE_FPS: 5, // 초당 5프레임 (서버 부하 고려)
  RECONNECT_DELAY: 3000, // 재연결 대기 시간
};

/**
 * 초기화: YouTube 비디오 감지 및 오버레이 생성
 */
function initialize() {
  console.log('🔍 SoccerHUD 초기화 중...');

  // 비디오 요소 찾기
  findVideoElement();

  // 비디오를 찾았으면 오버레이 생성
  if (videoElement) {
    createOverlay();
    console.log('✅ 비디오 및 오버레이 준비 완료');
  } else {
    console.log('⏳ 비디오를 찾지 못함, 재시도 중...');
    // 1초 후 재시도
    setTimeout(initialize, 1000);
  }
}

/**
 * YouTube 비디오 요소 찾기
 */
function findVideoElement() {
  // YouTube의 비디오 요소는 보통 .html5-main-video 클래스
  videoElement = document.querySelector('video.html5-main-video');

  if (!videoElement) {
    // 일반 video 태그로 fallback
    videoElement = document.querySelector('video');
  }

  if (videoElement) {
    console.log('✅ 비디오 요소 발견:', videoElement);

    // 비디오 이벤트 리스너
    videoElement.addEventListener('play', onVideoPlay);
    videoElement.addEventListener('pause', onVideoPause);
    videoElement.addEventListener('seeked', onVideoSeeked);
  }
}

/**
 * SVG 오버레이 컨테이너 생성
 */
function createOverlay() {
  // 기존 오버레이 제거
  if (overlayContainer) {
    overlayContainer.remove();
  }

  // 비디오의 부모 요소 찾기
  const videoParent = videoElement.parentElement;

  // SVG 오버레이 생성
  overlayContainer = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  overlayContainer.id = 'soccerhud-overlay';
  overlayContainer.style.cssText = `
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 9999;
  `;

  // 비디오와 같은 위치에 추가
  videoParent.style.position = 'relative';
  videoParent.appendChild(overlayContainer);

  console.log('✅ 오버레이 컨테이너 생성됨');
}

/**
 * WebSocket 연결
 */
function connectWebSocket() {
  if (ws && ws.readyState === WebSocket.OPEN) {
    console.log('⚠️ 이미 WebSocket 연결됨');
    return;
  }

  console.log(`🔌 WebSocket 연결 시도: ${CONFIG.SERVER_URL}`);

  ws = new WebSocket(CONFIG.SERVER_URL);

  ws.onopen = () => {
    console.log('✅ WebSocket 연결 성공!');
    startCapture();
  };

  ws.onmessage = (event) => {
    console.log('📦 WebSocket 메시지 수신:', event.data.substring(0, 100) + '...');
    try {
      const result = JSON.parse(event.data);
      console.log('✅ JSON 파싱 성공:', {
        players: result.players ? result.players.length : 0,
        ball: !!result.ball,
        ball_owner: result.ball_owner ? result.ball_owner.player_id : null
      });
      renderOverlay(result);
    } catch (error) {
      console.error('❌ JSON 파싱 실패:', error);
    }
  };

  ws.onerror = (error) => {
    console.error('❌ WebSocket 에러:', error);
  };

  ws.onclose = () => {
    console.log('🔌 WebSocket 연결 종료');
    stopCapture();

    // 활성화 상태이면 재연결 시도
    if (isActive) {
      console.log(`⏳ ${CONFIG.RECONNECT_DELAY}ms 후 재연결 시도...`);
      setTimeout(connectWebSocket, CONFIG.RECONNECT_DELAY);
    }
  };
}

/**
 * 프레임 캡처 시작
 */
function startCapture() {
  if (captureInterval) {
    console.log('⚠️ 이미 캡처 중');
    return;
  }

  const intervalMs = 1000 / CONFIG.CAPTURE_FPS;
  console.log(`📹 프레임 캡처 시작 (${CONFIG.CAPTURE_FPS} FPS)`);

  captureInterval = setInterval(() => {
    if (!videoElement || videoElement.paused) {
      return;
    }

    captureAndSendFrame();
  }, intervalMs);
}

/**
 * 프레임 캡처 중지
 */
function stopCapture() {
  if (captureInterval) {
    clearInterval(captureInterval);
    captureInterval = null;
    console.log('⏹️ 프레임 캡처 중지');
  }
}

/**
 * 프레임 캡처 및 전송
 */
function captureAndSendFrame() {
  if (!videoElement || !ws || ws.readyState !== WebSocket.OPEN) {
    return;
  }

  // 비디오가 준비되지 않았으면 스킵
  if (!videoElement.videoWidth || !videoElement.videoHeight) {
    console.warn('⚠️ 비디오 크기가 0 - 아직 로드 안됨');
    return;
  }

  try {
    // Canvas 생성 (캐싱하면 더 효율적이지만 일단 간단하게)
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d', { willReadFrequently: true });

    // 비디오 크기로 캔버스 설정 (640x360으로 다운스케일)
    const targetWidth = 640;
    const targetHeight = Math.floor((videoElement.videoHeight / videoElement.videoWidth) * targetWidth);

    canvas.width = targetWidth;
    canvas.height = targetHeight;

    // 비디오 프레임을 캔버스에 그리기
    ctx.drawImage(videoElement, 0, 0, targetWidth, targetHeight);

    // Canvas가 실제로 그려졌는지 확인 (CORS 문제 디버깅)
    const imageData = ctx.getImageData(0, 0, Math.min(10, targetWidth), Math.min(10, targetHeight));
    const isBlank = imageData.data.every(v => v === 0);
    if (isBlank) {
      console.error('❌ Canvas가 검은색 - CORS 문제 가능성');
      // 그래도 일단 전송 시도
    }

    // JPEG로 인코딩 (품질 70%)
    const dataUrl = canvas.toDataURL('image/jpeg', 0.7);

    // Base64 데이터만 전송 (data:image/jpeg;base64, 제거)
    const base64Data = dataUrl.split(',')[1];

    // 빈 데이터 체크
    if (!base64Data || base64Data.length === 0) {
      console.error('❌ Base64 데이터가 비어있음!');
      return;
    }

    console.log(`📤 프레임 전송 (크기: ${base64Data.length} chars, ${Math.round(base64Data.length * 0.75)} bytes)`);

    // WebSocket으로 전송
    ws.send(base64Data);

  } catch (error) {
    console.error('❌ 프레임 캡처 실패:', error);
    console.error('에러 세부사항:', error.message, error.stack);
  }
}

/**
 * 탐지 결과를 오버레이로 렌더링
 */
function renderOverlay(result) {
  console.log('🎨 renderOverlay 호출됨');

  if (!overlayContainer) {
    console.error('❌ overlayContainer가 없음!');
    return;
  }

  if (!videoElement) {
    console.error('❌ videoElement가 없음!');
    return;
  }

  // 기존 오버레이 지우기
  overlayContainer.innerHTML = '';
  console.log('🧹 기존 오버레이 지움');

  // 비디오 크기 가져오기
  const videoRect = videoElement.getBoundingClientRect();
  const videoWidth = videoElement.videoWidth;
  const videoHeight = videoElement.videoHeight;

  console.log('📐 비디오 크기:', {
    displayWidth: videoRect.width,
    displayHeight: videoRect.height,
    videoWidth,
    videoHeight
  });

  // 스케일 계산 (화면에 표시되는 크기 vs 실제 비디오 크기)
  const scaleX = videoRect.width / videoWidth;
  const scaleY = videoRect.height / videoHeight;

  // 공 소유자 ID 미리 확인
  const ballOwnerId = result.ball_owner ? result.ball_owner.player_id : null;
  console.log('⚽ 공 소유자 ID:', ballOwnerId);

  // 선수 그리기
  if (result.players && result.players.length > 0) {
    console.log(`👥 선수 ${result.players.length}명 그리기 시작`);
    result.players.forEach((player, index) => {
      // 공 소유자는 노란색으로
      const hasBall = (player.id === ballOwnerId);
      console.log(`  - 선수 #${index}: ID=${player.id}, team=${player.team}, hasBall=${hasBall}`);
      drawPlayer(player, scaleX, scaleY, hasBall);
    });
    console.log('✅ 선수 그리기 완료');
  } else {
    console.log('⚠️ 선수 탐지 없음');
  }

  // 공 그리기
  if (result.ball) {
    console.log('⚽ 공 그리기');
    drawBall(result.ball, scaleX, scaleY);
  } else {
    console.log('⚠️ 공 탐지 없음');
  }
}

/**
 * 선수 바운딩 박스 그리기
 */
function drawPlayer(player, scaleX, scaleY, hasBall = false) {
  const x = (player.x - player.width / 2) * scaleX;
  const y = (player.y - player.height / 2) * scaleY;
  const width = player.width * scaleX;
  const height = player.height * scaleY;

  console.log(`    🎨 drawPlayer: x=${x.toFixed(1)}, y=${y.toFixed(1)}, w=${width.toFixed(1)}, h=${height.toFixed(1)}`);

  // 팀 색상 (공 소유자는 노란색)
  let color;
  if (hasBall) {
    color = '#FFFF00'; // 노란색
  } else {
    color = player.team === 'home' ? '#FF0000' : '#0000FF'; // 빨강/파랑
  }

  console.log(`    🎨 색상: ${color}`);

  // 바운딩 박스
  const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  rect.setAttribute('x', x);
  rect.setAttribute('y', y);
  rect.setAttribute('width', width);
  rect.setAttribute('height', height);
  rect.setAttribute('fill', 'none');
  rect.setAttribute('stroke', color);
  rect.setAttribute('stroke-width', '2');
  rect.setAttribute('opacity', '0.8');

  overlayContainer.appendChild(rect);
  console.log(`    ✅ rect 추가됨, overlayContainer 자식 수: ${overlayContainer.children.length}`);

  // 라벨
  let label;
  if (hasBall) {
    label = `[${player.id}] ⚽ HAS BALL`;
  } else if (player.name && player.number) {
    label = `[${player.id}] ${player.name} #${player.number}`;
  } else {
    label = `[${player.id}] ${player.team.toUpperCase()}`;
  }

  const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  text.setAttribute('x', x);
  text.setAttribute('y', y - 5);
  text.setAttribute('fill', color);
  text.setAttribute('font-size', '14');
  text.setAttribute('font-weight', 'bold');
  text.textContent = label;

  overlayContainer.appendChild(text);
}

/**
 * 공 그리기
 */
function drawBall(ball, scaleX, scaleY) {
  const cx = ball.x * scaleX;
  const cy = ball.y * scaleY;
  const radius = Math.max(ball.width, ball.height) * scaleX / 2;

  const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  circle.setAttribute('cx', cx);
  circle.setAttribute('cy', cy);
  circle.setAttribute('r', radius);
  circle.setAttribute('fill', 'none');
  circle.setAttribute('stroke', '#00FF00');
  circle.setAttribute('stroke-width', '3');

  overlayContainer.appendChild(circle);

  // "BALL" 텍스트
  const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  text.setAttribute('x', cx);
  text.setAttribute('y', cy - radius - 10);
  text.setAttribute('fill', '#00FF00');
  text.setAttribute('font-size', '14');
  text.setAttribute('font-weight', 'bold');
  text.setAttribute('text-anchor', 'middle');
  text.textContent = 'BALL';

  overlayContainer.appendChild(text);
}

/**
 * 공 소유자 강조
 */
function highlightBallOwner(ballOwner, players, scaleX, scaleY) {
  const owner = players.find((p) => p.id === ballOwner.player_id);
  if (!owner) return;

  const x = (owner.x - owner.width / 2) * scaleX;
  const y = (owner.y - owner.height / 2) * scaleY;
  const width = owner.width * scaleX;
  const height = owner.height * scaleY;

  // 강조 박스 (더 두껍게)
  const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  rect.setAttribute('x', x - 3);
  rect.setAttribute('y', y - 3);
  rect.setAttribute('width', width + 6);
  rect.setAttribute('height', height + 6);
  rect.setAttribute('fill', 'none');
  rect.setAttribute('stroke', '#FFFF00'); // 노란색
  rect.setAttribute('stroke-width', '4');

  overlayContainer.appendChild(rect);

  // "HAS BALL" 텍스트
  const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  text.setAttribute('x', 20);
  text.setAttribute('y', 40);
  text.setAttribute('fill', '#FFFF00');
  text.setAttribute('font-size', '24');
  text.setAttribute('font-weight', 'bold');
  text.textContent = `${owner.team.toUpperCase()} HAS BALL`;

  overlayContainer.appendChild(text);
}

/**
 * 비디오 재생 이벤트
 */
function onVideoPlay() {
  console.log('▶️ 비디오 재생');
  if (isActive && !captureInterval) {
    startCapture();
  }
}

/**
 * 비디오 일시정지 이벤트
 */
function onVideoPause() {
  console.log('⏸️ 비디오 일시정지');
  stopCapture();
}

/**
 * 비디오 탐색 이벤트
 */
function onVideoSeeked() {
  console.log('⏩ 비디오 탐색');
  // 탐색 후에는 즉시 캡처
  if (isActive && ws && ws.readyState === WebSocket.OPEN) {
    captureAndSendFrame();
  }
}

/**
 * SoccerHUD 활성화
 */
function activate() {
  if (isActive) {
    console.log('⚠️ 이미 활성화됨');
    return;
  }

  console.log('🚀 SoccerHUD 활성화');
  isActive = true;
  connectWebSocket();
}

/**
 * SoccerHUD 비활성화
 */
function deactivate() {
  if (!isActive) {
    console.log('⚠️ 이미 비활성화됨');
    return;
  }

  console.log('⏹️ SoccerHUD 비활성화');
  isActive = false;

  stopCapture();

  if (ws) {
    ws.close();
    ws = null;
  }

  // 오버레이 지우기
  if (overlayContainer) {
    overlayContainer.innerHTML = '';
  }
}

/**
 * Background Script로부터 메시지 수신
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('📩 메시지 수신:', message);

  if (message.action === 'activate') {
    activate();
    sendResponse({ success: true });
  } else if (message.action === 'deactivate') {
    deactivate();
    sendResponse({ success: true });
  } else if (message.action === 'getStatus') {
    sendResponse({
      isActive,
      hasVideo: !!videoElement,
      wsConnected: ws && ws.readyState === WebSocket.OPEN,
    });
  }

  return true; // 비동기 응답
});

// 페이지 로드 시 초기화
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initialize);
} else {
  initialize();
}

// Storage에서 활성화 상태 확인
chrome.storage.local.get(['soccerhudActive'], (result) => {
  if (result.soccerhudActive) {
    console.log('💾 저장된 상태: 활성화');
    activate();
  }
});
