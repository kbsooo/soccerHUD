/**
 * SoccerHUD Background Service Worker
 * 활성화 상태 관리 및 Content Script와 통신
 */

console.log('🔧 SoccerHUD Background Service Worker 시작');

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
