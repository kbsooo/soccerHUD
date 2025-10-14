export function fpsToInterval(fps: number, minFps = 1, maxFps = 60): number {
  if (!Number.isFinite(fps) || fps <= 0) {
    fps = minFps;
  }
  const clampedFps = Math.min(Math.max(fps, minFps), maxFps);
  return Math.round(1000 / clampedFps);
}
