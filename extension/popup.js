/**
 * SoccerHUD Popup Script
 * 활성화/비활성화 토글 및 상태 표시
 */

const toggleBtn = document.getElementById('toggle-btn');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const serverStatus = document.getElementById('server-status');

let isActive = false;

/**
 * UI 업데이트
 */
function updateUI() {
  if (isActive) {
    toggleBtn.textContent = '비활성화';
    toggleBtn.classList.remove('inactive');
    toggleBtn.classList.add('active');

    statusIndicator.classList.remove('inactive');
    statusIndicator.classList.add('active');
    statusText.textContent = '활성화됨';
  } else {
    toggleBtn.textContent = '활성화';
    toggleBtn.classList.remove('active');
    toggleBtn.classList.add('inactive');

    statusIndicator.classList.remove('active');
    statusIndicator.classList.add('inactive');
    statusText.textContent = '대기 중';
  }
}

/**
 * 활성화 상태 토글
 */
function toggleActivation() {
  isActive = !isActive;

  // Storage에 저장
  chrome.storage.local.set({ soccerhudActive: isActive }, () => {
    console.log(`상태 저장: ${isActive}`);
    updateUI();
  });
}

/**
 * 현재 탭의 Content Script 상태 확인
 */
function checkContentScriptStatus() {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const currentTab = tabs[0];

    if (!currentTab) {
      serverStatus.textContent = '탭 없음';
      return;
    }

    // YouTube 페이지인지 확인
    if (!currentTab.url || !currentTab.url.includes('youtube.com')) {
      serverStatus.textContent = 'YouTube 아님';
      return;
    }

    // Content Script에 상태 요청
    chrome.tabs.sendMessage(
      currentTab.id,
      { action: 'getStatus' },
      (response) => {
        if (chrome.runtime.lastError) {
          console.error('상태 확인 실패:', chrome.runtime.lastError);
          serverStatus.textContent = '연결 안 됨';
          return;
        }

        if (response) {
          if (response.wsConnected) {
            serverStatus.textContent = '✅ 연결됨';
          } else if (response.isActive) {
            serverStatus.textContent = '⏳ 연결 중...';
          } else {
            serverStatus.textContent = '대기 중';
          }
        }
      }
    );
  });
}

// 초기화
chrome.storage.local.get(['soccerhudActive'], (result) => {
  isActive = result.soccerhudActive || false;
  updateUI();
  checkContentScriptStatus();
});

// 토글 버튼 클릭
toggleBtn.addEventListener('click', toggleActivation);

// 주기적으로 상태 확인 (2초마다)
setInterval(checkContentScriptStatus, 2000);
