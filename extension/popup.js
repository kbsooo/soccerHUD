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

// ============ Phase 3: 명단 관리 ============

// 탭 전환
const tabs = document.querySelectorAll('.tab');
const tabContents = document.querySelectorAll('.tab-content');

tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    const targetTab = tab.dataset.tab;

    // 모든 탭 비활성화
    tabs.forEach(t => t.classList.remove('active'));
    tabContents.forEach(content => content.classList.remove('active'));

    // 선택한 탭 활성화
    tab.classList.add('active');
    document.getElementById(`${targetTab}-tab`).classList.add('active');
  });
});

// 명단 데이터 (로컬 저장)
let rosterData = {
  home: [],
  away: []
};

// Storage에서 명단 로드
chrome.storage.local.get(['roster'], (result) => {
  if (result.roster) {
    rosterData = result.roster;
    renderRoster();
  }
});

/**
 * 명단 렌더링
 */
function renderRoster() {
  renderTeamRoster('home');
  renderTeamRoster('away');
}

function renderTeamRoster(team) {
  const listElement = document.getElementById(`${team}-player-list`);
  listElement.innerHTML = '';

  rosterData[team].forEach((player, index) => {
    const playerItem = document.createElement('div');
    playerItem.className = 'player-item';
    playerItem.innerHTML = `
      <div class="player-info">
        #${player.number} ${player.name} ${player.position ? `(${player.position})` : ''}
      </div>
      <button class="remove-btn" data-team="${team}" data-index="${index}">삭제</button>
    `;
    listElement.appendChild(playerItem);
  });

  // 삭제 버튼 이벤트
  listElement.querySelectorAll('.remove-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const team = e.target.dataset.team;
      const index = parseInt(e.target.dataset.index);
      removePlayer(team, index);
    });
  });
}

/**
 * 선수 추가
 */
function addPlayer(team) {
  const number = parseInt(document.getElementById(`${team}-number`).value);
  const name = document.getElementById(`${team}-name`).value.trim();
  const position = document.getElementById(`${team}-position`).value.trim();

  if (!number || !name) {
    alert('등번호와 이름은 필수입니다.');
    return;
  }

  // 중복 확인
  const exists = rosterData[team].some(p => p.number === number);
  if (exists) {
    alert('이미 존재하는 등번호입니다.');
    return;
  }

  rosterData[team].push({
    number,
    name,
    position: position || null
  });

  // 입력 필드 초기화
  document.getElementById(`${team}-number`).value = '';
  document.getElementById(`${team}-name`).value = '';
  document.getElementById(`${team}-position`).value = '';

  // 로컬 저장
  chrome.storage.local.set({ roster: rosterData });

  renderRoster();
}

/**
 * 선수 삭제
 */
function removePlayer(team, index) {
  rosterData[team].splice(index, 1);
  chrome.storage.local.set({ roster: rosterData });
  renderRoster();
}

/**
 * 명단 서버로 전송
 */
async function saveRosterToServer() {
  try {
    const response = await fetch('http://localhost:8765/api/roster', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(rosterData),
    });

    const result = await response.json();

    if (result.status === 'success') {
      alert(`명단 저장 성공!\n홈: ${result.roster.home}명, 원정: ${result.roster.away}명`);
    } else {
      alert(`저장 실패: ${result.message}`);
    }
  } catch (error) {
    console.error('명단 저장 실패:', error);
    alert('서버 연결 실패. Python 서버가 실행 중인지 확인하세요.');
  }
}

// 이벤트 리스너
document.getElementById('add-home-player').addEventListener('click', () => addPlayer('home'));
document.getElementById('add-away-player').addEventListener('click', () => addPlayer('away'));
document.getElementById('save-roster-btn').addEventListener('click', saveRosterToServer);
