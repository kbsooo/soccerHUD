import { describe, expect, it } from 'vitest';

import { fpsToInterval } from './fps';

describe('fpsToInterval', () => {
  it('기본 FPS에서 올바른 인터벌을 반환한다', () => {
    expect(fpsToInterval(10)).toBe(100);
  });

  it('최소 FPS 미만일 때 최소값으로 클램프한다', () => {
    expect(fpsToInterval(0.5, 5, 60)).toBe(200);
  });

  it('최대 FPS 초과일 때 최대값으로 클램프한다', () => {
    expect(fpsToInterval(240, 5, 60)).toBe(Math.round(1000 / 60));
  });

  it('비정상 입력일 때 기본 최소 FPS를 사용한다', () => {
    expect(fpsToInterval(Number.NaN)).toBe(1000);
  });
});
