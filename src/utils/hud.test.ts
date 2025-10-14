import { describe, expect, it } from 'vitest';
import { formatBallCarrierLabel } from './hud';

describe('formatBallCarrierLabel', () => {
  it('returns unknown when input is missing', () => {
    expect(formatBallCarrierLabel()).toBe('Ball Carrier: Unknown');
    expect(formatBallCarrierLabel(null)).toBe('Ball Carrier: Unknown');
    expect(formatBallCarrierLabel('   ')).toBe('Ball Carrier: Unknown');
  });

  it('formats the player name when present', () => {
    expect(formatBallCarrierLabel('Alex Morgan')).toBe('Ball Carrier: Alex Morgan');
  });

  it('trims extraneous whitespace', () => {
    expect(formatBallCarrierLabel('  Sam Kerr  ')).toBe('Ball Carrier: Sam Kerr');
  });
});
