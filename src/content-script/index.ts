import { fpsToInterval } from '../shared/fps';
import { FrameSampleEvent, MESSAGE_SOURCE, isFrameSampleEvent } from '../shared/messages';

const OVERLAY_ID = 'soccerhud-overlay';
const OVERLAY_FPS = 10;

class OverlayHUD {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private animationHandle: number | null = null;
  private lastFrameTimestamp = 0;
  private lastSampleStatus: FrameSampleEvent['status'] = 'ok';
  private lastErrorMessage = '';

  constructor() {
    this.canvas = document.createElement('canvas');
    this.canvas.id = OVERLAY_ID;
    this.canvas.style.position = 'fixed';
    this.canvas.style.top = '0';
    this.canvas.style.left = '0';
    this.canvas.style.width = '100vw';
    this.canvas.style.height = '100vh';
    this.canvas.style.pointerEvents = 'none';
    this.canvas.style.zIndex = '2147483647';
    this.canvas.style.transition = 'opacity 0.2s ease-in-out';
    this.canvas.style.opacity = '1';

    const context = this.canvas.getContext('2d');
    if (!context) {
      throw new Error('Failed to create overlay canvas context');
    }
    this.ctx = context;

    window.addEventListener('resize', () => this.resize());
  }

  attach() {
    if (!document.body.contains(this.canvas)) {
      document.body.appendChild(this.canvas);
    }
    this.resize();
    this.start();
  }

  detach() {
    this.stop();
    this.canvas.remove();
  }

  updateFrameInfo(event: FrameSampleEvent) {
    this.lastFrameTimestamp = event.timestamp;
    this.lastSampleStatus = event.status;
    this.lastErrorMessage = event.errorMessage ?? '';
  }

  private resize() {
    const dpr = window.devicePixelRatio || 1;
    const width = Math.floor(window.innerWidth * dpr);
    const height = Math.floor(window.innerHeight * dpr);
    if (this.canvas.width !== width || this.canvas.height !== height) {
      this.canvas.width = width;
      this.canvas.height = height;
    }
  }

  private start() {
    if (this.animationHandle !== null) {
      return;
    }
    const interval = fpsToInterval(OVERLAY_FPS, 5, 30);
    const loop = () => {
      this.draw();
      this.animationHandle = window.setTimeout(loop, interval);
    };
    this.animationHandle = window.setTimeout(loop, interval);
  }

  private stop() {
    if (this.animationHandle !== null) {
      window.clearTimeout(this.animationHandle);
      this.animationHandle = null;
    }
  }

  private draw() {
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;

    ctx.clearRect(0, 0, width, height);

    const panelWidth = Math.min(420, width * 0.4);
    const panelHeight = 130;

    ctx.save();
    ctx.globalAlpha = 0.8;
    ctx.fillStyle = '#0b1d26';
    ctx.beginPath();
    if ('roundRect' in ctx) {
      ctx.roundRect(24, 24, panelWidth, panelHeight, 16);
    } else {
      const radius = 16;
      ctx.moveTo(24 + radius, 24);
      ctx.lineTo(24 + panelWidth - radius, 24);
      ctx.quadraticCurveTo(24 + panelWidth, 24, 24 + panelWidth, 24 + radius);
      ctx.lineTo(24 + panelWidth, 24 + panelHeight - radius);
      ctx.quadraticCurveTo(
        24 + panelWidth,
        24 + panelHeight,
        24 + panelWidth - radius,
        24 + panelHeight
      );
      ctx.lineTo(24 + radius, 24 + panelHeight);
      ctx.quadraticCurveTo(24, 24 + panelHeight, 24, 24 + panelHeight - radius);
      ctx.lineTo(24, 24 + radius);
      ctx.quadraticCurveTo(24, 24, 24 + radius, 24);
      ctx.closePath();
    }
    ctx.fill();
    ctx.restore();

    ctx.save();
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 28px "Segoe UI", Helvetica, Arial, sans-serif';
    ctx.fillText('Ball Carrier: Unknown', 48, 72);

    ctx.font = '16px "Segoe UI", Helvetica, Arial, sans-serif';
    const timestampText = this.lastFrameTimestamp
      ? `Last frame: ${new Date(this.lastFrameTimestamp).toLocaleTimeString()}`
      : 'Waiting for video frames…';
    ctx.fillText(timestampText, 48, 100);

    if (this.lastSampleStatus === 'error' && this.lastErrorMessage) {
      ctx.fillStyle = '#ffb4a2';
      ctx.fillText(`Sampling issue: ${this.lastErrorMessage}`, 48, 126);
    }

    ctx.restore();
  }
}

function injectPageScript() {
  if (document.getElementById('soccerhud-page-script')) {
    return;
  }

  const script = document.createElement('script');
  script.id = 'soccerhud-page-script';
  script.type = 'module';
  script.src = chrome.runtime.getURL('page-script/index.js');
  (document.head || document.documentElement).appendChild(script);
  script.addEventListener('load', () => {
    script.remove();
  });
}

function init() {
  if (window.top !== window) {
    return;
  }

  const overlay = new OverlayHUD();
  overlay.attach();

  window.addEventListener('message', (event: MessageEvent<unknown>) => {
    if (event.source !== window) {
      return;
    }
    if (!isFrameSampleEvent(event.data)) {
      return;
    }
    overlay.updateFrameInfo(event.data);
  });

  injectPageScript();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init, { once: true });
} else {
  init();
}
