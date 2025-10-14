function initOptions(): void {
  const app = document.getElementById('app');
  if (!app) {
    return;
  }

  app.innerHTML = `
    <h1>Soccer HUD Settings</h1>
    <p>
      Upload a CSV roster to map jersey numbers to player names. This placeholder will be
      replaced with in-browser parsing and persistence in a future milestone.
    </p>
    <div class="upload-card">
      <label for="roster-upload">Team roster CSV</label>
      <input id="roster-upload" type="file" accept=".csv" />
      <div id="roster-status" role="status" aria-live="polite">No file selected.</div>
      <div class="button-row">
        <button id="roster-save" disabled>Save roster</button>
        <button id="roster-clear" disabled>Clear</button>
      </div>
    </div>
  `;

  const uploadInput = document.getElementById('roster-upload') as HTMLInputElement | null;
  const status = document.getElementById('roster-status');
  const saveButton = document.getElementById('roster-save') as HTMLButtonElement | null;
  const clearButton = document.getElementById('roster-clear') as HTMLButtonElement | null;

  if (!status) {
    return;
  }

  uploadInput?.addEventListener('change', () => {
    const file = uploadInput.files?.item(0);
    if (file) {
      status.textContent = `${file.name} (${Math.round(file.size / 1024)} KB)`;
      saveButton && (saveButton.disabled = true);
      clearButton && (clearButton.disabled = false);
    } else {
      status.textContent = 'No file selected.';
      saveButton && (saveButton.disabled = true);
      clearButton && (clearButton.disabled = true);
    }
  });

  clearButton?.addEventListener('click', () => {
    if (uploadInput) {
      uploadInput.value = '';
    }
    status.textContent = 'No file selected.';
    if (clearButton) {
      clearButton.disabled = true;
    }
  });
}

initOptions();
