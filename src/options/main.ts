const app = document.getElementById('app');

if (app) {
  app.innerHTML = `
    <header>
      <h1>SoccerHUD 설정</h1>
      <p>
        팀 로스터 CSV를 업로드하면 선수 번호와 이름 매핑을 구성할 수 있습니다. MVP에서는 파일을 저장하지 않지만, 이후 빌드에서 브라우저 저장소에 동기화할 예정입니다.
      </p>
    </header>
    <section>
      <label for="roster-upload">팀 로스터 CSV 업로드</label>
      <input id="roster-upload" name="roster-upload" type="file" accept=".csv" />
      <small>샘플 포맷: <code>number,name,position</code></small>
      <div id="upload-status" role="status" aria-live="polite" style="margin-top: 16px;"></div>
    </section>
  `;

  const fileInput = document.getElementById('roster-upload') as HTMLInputElement | null;
  const status = document.getElementById('upload-status');

  fileInput?.addEventListener('change', () => {
    if (!fileInput.files || fileInput.files.length === 0) {
      if (status) {
        status.textContent = '';
      }
      return;
    }

    const [file] = fileInput.files;
    const fileName = file.name;
    const fileSize = (file.size / 1024).toFixed(1);
    if (status) {
      status.textContent = `선택된 파일: ${fileName} (${fileSize}KB) — 향후 릴리스에서 파싱됩니다.`;
    }
  });
}
