import { formatBallCarrierLabel } from '../utils/hud';

const OVERLAY_ROOT_ID = 'soccer-hud-overlay-root';
const RENDER_INTERVAL_MS = 100;

interface HudState {
  label: string;
  lastFrameSampledAt: number;
}

const state: HudState = {
  label: formatBallCarrierLabel(),
  lastFrameSampledAt: 0
};

let overlayRoot: HTMLDivElement | null = null;
let overlayCanvas: HTMLCanvasElement | null = null;
let canvasContext: CanvasRenderingContext2D | null = null;
let videoElement: HTMLVideoElement | null = null;

function ensureOverlay() {
  if (!overlayRoot) {
    overlayRoot = document.createElement('div');
    overlayRoot.id = OVERLAY_ROOT_ID;
    overlayRoot.style.position = 'fixed';
    overlayRoot.style.pointerEvents = 'none';
    overlayRoot.style.zIndex = '2147483647';
    overlayRoot.style.display = 'flex';
    overlayRoot.style.alignItems = 'flex-start';
    overlayRoot.style.justifyContent = 'center';

    overlayCanvas = document.createElement('canvas');
    overlayCanvas.style.width = '100%';
    overlayCanvas.style.height = '100%';
    overlayRoot.appendChild(overlayCanvas);
    document.body.appendChild(overlayRoot);

    canvasContext = overlayCanvas.getContext('2d');
  }
}

function updateVideoElement() {
  const candidate = document.querySelector('video');
  if (candidate instanceof HTMLVideoElement) {
    videoElement = candidate;
  }
}

function updateOverlayGeometry() {
  if (!overlayRoot || !overlayCanvas || !videoElement) {
    return;
  }

  const rect = videoElement.getBoundingClientRect();
  overlayRoot.style.left = `${rect.left}px`;
  overlayRoot.style.top = `${rect.top}px`;
  overlayRoot.style.width = `${rect.width}px`;
  overlayRoot.style.height = `${rect.height}px`;

  const dpr = window.devicePixelRatio || 1;
  const width = Math.max(1, Math.floor(rect.width * dpr));
  const height = Math.max(1, Math.floor(rect.height * dpr));

  if (overlayCanvas.width !== width || overlayCanvas.height !== height) {
    overlayCanvas.width = width;
    overlayCanvas.height = height;
  }
}

function renderHud() {
  if (!canvasContext || !overlayCanvas) {
    return;
  }

  canvasContext.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
  canvasContext.font = `${Math.round(overlayCanvas.height * 0.05)}px "Segoe UI", sans-serif`;
  canvasContext.fillStyle = 'rgba(0, 0, 0, 0.6)';

  const padding = Math.max(16, Math.round(overlayCanvas.width * 0.02));
  const label = state.label;
  const labelWidth = canvasContext.measureText(label).width;
  const labelHeight = Math.round(overlayCanvas.height * 0.06);

  const boxWidth = labelWidth + padding * 2;
  const boxHeight = labelHeight + padding;

  canvasContext.fillRect(padding, padding, boxWidth, boxHeight);

  canvasContext.fillStyle = '#ffffff';
  canvasContext.textBaseline = 'top';
  canvasContext.fillText(label, padding * 1.5, padding * 1.2);

  if (state.lastFrameSampledAt > 0) {
    const elapsedMs = Math.round(performance.now() - state.lastFrameSampledAt);
    const status = `Frame sampled ${elapsedMs} ms ago`;
    canvasContext.font = `${Math.round(overlayCanvas.height * 0.035)}px "Segoe UI", sans-serif`;
    canvasContext.fillStyle = '#f0f0f0';
    canvasContext.fillText(status, padding * 1.5, padding * 1.2 + labelHeight);
  }
}

function startRendering() {
  ensureOverlay();
  updateVideoElement();

  window.setInterval(() => {
    updateVideoElement();
    updateOverlayGeometry();
    renderHud();
  }, RENDER_INTERVAL_MS);
}

function handlePageMessage(event: MessageEvent) {
  if (event.source !== window) {
    return;
  }

  const data = event.data;
  if (!data || typeof data !== 'object') {
    return;
  }

  if (data.source !== 'soccer-hud-page') {
    return;
  }

  if (data.type === 'FRAME_SAMPLED') {
    state.lastFrameSampledAt = typeof data.timestamp === 'number' ? data.timestamp : performance.now();
    if ('carrierName' in data) {
      state.label = formatBallCarrierLabel(data.carrierName as string | null | undefined);
    }
  }
}

function injectPageScript() {
  const script = document.createElement('script');
  script.src = chrome.runtime.getURL('page/index.js');
  script.type = 'module';
  script.onload = () => {
    script.remove();
  };
  (document.head || document.documentElement).appendChild(script);
}

(function init() {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      startRendering();
      injectPageScript();
    });
  } else {
    startRendering();
    injectPageScript();
  }

  window.addEventListener('message', handlePageMessage);
})();
