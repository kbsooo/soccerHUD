export const MESSAGE_SOURCE = 'soccerhud' as const;

export type FrameSampleEvent = {
  source: typeof MESSAGE_SOURCE;
  type: 'frame-sample';
  timestamp: number;
  width: number;
  height: number;
  status: 'ok' | 'error';
  errorMessage?: string;
};

export function isFrameSampleEvent(value: unknown): value is FrameSampleEvent {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  const record = value as Record<string, unknown>;
  return (
    record.source === MESSAGE_SOURCE &&
    record.type === 'frame-sample' &&
    typeof record.timestamp === 'number' &&
    typeof record.width === 'number' &&
    typeof record.height === 'number' &&
    (record.status === 'ok' || record.status === 'error')
  );
}
