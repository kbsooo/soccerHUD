export function formatBallCarrierLabel(playerName?: string | null): string {
  const trimmed = typeof playerName === 'string' ? playerName.trim() : '';
  if (!trimmed) {
    return 'Ball Carrier: Unknown';
  }

  return `Ball Carrier: ${trimmed}`;
}
