import { fpsToInterval } from '../shared/fps';
import { FrameSampleEvent, MESSAGE_SOURCE } from '../shared/messages';
const TARGET_FPS = 10;
const SAMPLE_INTERVAL = fpsToInterval(TARGET_FPS, 5, 30);


class VideoFrameSampler {
  private timerId: number | null = null;
  private readonly canvas: OffscreenCanvas | HTMLCanvasElement;
  private readonly ctx: OffscreenCanvasRenderingContext2D | CanvasRenderingContext2D | null;
  private readonly isOffscreen: boolean;
  private lastErrorMessage = '';
  private lastErrorTimestamp = 0;

  constructor(private readonly video: HTMLVideoElement) {
    if (typeof OffscreenCanvas !== 'undefined') {
      this.canvas = new OffscreenCanvas(1, 1);
      this.ctx = this.canvas.getContext('2d');
      this.isOffscreen = true;
    } else {
      const canvas = document.createElement('canvas');
      canvas.width = 1;
      canvas.height = 1;
      canvas.style.position = 'absolute';
      canvas.style.opacity = '0';
      canvas.style.pointerEvents = 'none';
      canvas.style.top = '0';
      canvas.style.left = '0';
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      this.isOffscreen = false;
      document.documentElement.appendChild(canvas);
    }
  }

  start() {
    if (this.timerId !== null || !this.ctx) {
      return;
    }

    const tick = () => {
      this.sample();
      this.timerId = window.setTimeout(tick, SAMPLE_INTERVAL);
    };

    this.timerId = window.setTimeout(tick, SAMPLE_INTERVAL);
  }

  stop() {
    if (this.timerId !== null) {
      window.clearTimeout(this.timerId);
      this.timerId = null;
    }
  }

  dispose() {
    this.stop();
    if (!this.isOffscreen) {
      (this.canvas as HTMLCanvasElement).remove();
    }
  }

  private sample() {
    const video = this.video;
    if (video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA || video.paused) {
      return;
    }

    const width = video.videoWidth;
    const height = video.videoHeight;
    if (!width || !height) {
      return;
    }

    if (this.isOffscreen) {
      const canvas = this.canvas as OffscreenCanvas;
      canvas.width = width;
      canvas.height = height;
    } else {
      const canvas = this.canvas as HTMLCanvasElement;
      if (canvas.width !== width) {
        canvas.width = width;
      }
      if (canvas.height !== height) {
        canvas.height = height;
      }
    }

    try {
      this.ctx!.drawImage(video, 0, 0, width, height);
      this.postMessage({
        source: MESSAGE_SOURCE,
        type: 'frame-sample',
        timestamp: Date.now(),
        width,
        height,
        status: 'ok'
      });
      this.lastErrorMessage = '';
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      const now = Date.now();
      if (message !== this.lastErrorMessage || now - this.lastErrorTimestamp > 1000) {
        this.postMessage({
          source: MESSAGE_SOURCE,
          type: 'frame-sample',
          timestamp: now,
          width,
          height,
          status: 'error',
          errorMessage: message
        });
        this.lastErrorMessage = message;
        this.lastErrorTimestamp = now;
      }
    }
  }

  private postMessage(payload: FrameSampleEvent) {
    window.postMessage(payload, '*');
  }
}

function findPrimaryVideo(): HTMLVideoElement | null {
  const videos = Array.from(document.querySelectorAll('video'));
  if (videos.length === 0) {
    return null;
  }

  let bestVideo: HTMLVideoElement | null = null;
  let bestScore = 0;

  for (const video of videos) {
    const rect = video.getBoundingClientRect();
    const visibleArea = Math.max(0, rect.width) * Math.max(0, rect.height);
    if (visibleArea === 0) {
      continue;
    }

    const score = visibleArea * (video.readyState >= HTMLMediaElement.HAVE_METADATA ? 2 : 1);
    if (score > bestScore) {
      bestScore = score;
      bestVideo = video;
    }
  }

  return bestVideo;
}

function startSampling() {
  let sampler: VideoFrameSampler | null = null;
  let currentVideo: HTMLVideoElement | null = null;

  const activateSampler = (video: HTMLVideoElement) => {
    if (sampler && currentVideo === video) {
      return;
    }

    sampler?.dispose();
    sampler = new VideoFrameSampler(video);
    sampler.start();
    currentVideo = video;
  };

  const evaluate = () => {
    const video = findPrimaryVideo();
    if (video) {
      activateSampler(video);
    }
  };

  evaluate();

  const observer = new MutationObserver(() => {
    evaluate();
  });

  if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
  }

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
      sampler?.start();
    } else {
      sampler?.stop();
    }
  });

  window.addEventListener('beforeunload', () => {
    observer.disconnect();
    sampler?.dispose();
  });
}

if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', startSampling, { once: true });
} else {
  startSampling();
}
