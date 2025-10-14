const isDev = import.meta.env?.DEV ?? false;
const SAMPLE_INTERVAL_MS = 100;
const CANVAS_WIDTH = 320;

interface PageVideoFrameCallbackMetadata {
  presentationTime: number;
  expectedDisplayTime: number;
  width: number;
  height: number;
  mediaTime: number;
  presentedFrames: number;
}

let samplerCanvas: HTMLCanvasElement | null = null;
let samplerContext: CanvasRenderingContext2D | null = null;

function getSamplerContext() {
  if (!samplerCanvas) {
    samplerCanvas = document.createElement('canvas');
    samplerCanvas.style.position = 'absolute';
    samplerCanvas.style.opacity = '0';
    samplerCanvas.style.pointerEvents = 'none';
    samplerCanvas.style.width = '0';
    samplerCanvas.style.height = '0';
    document.body.appendChild(samplerCanvas);
  }

  if (!samplerContext) {
    samplerContext = samplerCanvas.getContext('2d', { willReadFrequently: true });
  }

  return samplerContext;
}

function locateVideo(): HTMLVideoElement | null {
  const video = document.querySelector('video');
  return video instanceof HTMLVideoElement ? video : null;
}

function drawVideoFrame(video: HTMLVideoElement) {
  const ctx = getSamplerContext();
  const canvas = samplerCanvas;
  if (!ctx || !canvas) {
    return;
  }

  const width = CANVAS_WIDTH;
  const aspectRatio = video.videoWidth > 0 ? video.videoHeight / video.videoWidth : 9 / 16;
  const height = Math.max(1, Math.round(width * aspectRatio));

  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
  }

  try {
    ctx.drawImage(video, 0, 0, width, height);
  } catch (error) {
    if (isDev) {
      console.debug('Soccer HUD: unable to draw video frame', error);
    }
  }
}

function emitFrameSampled() {
  window.postMessage(
    {
      source: 'soccer-hud-page',
      type: 'FRAME_SAMPLED',
      timestamp: performance.now()
    },
    '*'
  );
}

function sampleFrame(video: HTMLVideoElement) {
  if (video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) {
    return;
  }

  drawVideoFrame(video);
  emitFrameSampled();
}

function scheduleNextSample(delay: number = SAMPLE_INTERVAL_MS) {
  window.setTimeout(runSampler, delay);
}

function runSampler() {
  const video = locateVideo();
  if (!video) {
    scheduleNextSample(500);
    return;
  }

  if (typeof (video as HTMLVideoElement & { requestVideoFrameCallback?: unknown }).requestVideoFrameCallback === 'function') {
    (video as HTMLVideoElement & {
      requestVideoFrameCallback: (
        callback: (now: DOMHighResTimeStamp, metadata: PageVideoFrameCallbackMetadata) => void
      ) => number;
    }).requestVideoFrameCallback(() => {
      sampleFrame(video);
      scheduleNextSample();
    });
  } else {
    sampleFrame(video);
    scheduleNextSample();
  }
}

if (!(window as unknown as { __soccerHudSamplerStarted?: boolean }).__soccerHudSamplerStarted) {
  (window as unknown as { __soccerHudSamplerStarted?: boolean }).__soccerHudSamplerStarted = true;
  runSampler();
}
