import { useEffect, useRef } from 'react';
import { useConnectionStore } from '../store/connection.store';

export function useWebSocket<T = unknown>(
  channel: string,
  onMessage?: (data: T) => void
) {
  const { setChannelConnected } = useConnectionStore();
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Use proxy relative host or fallback to port 8001
    const host = window.location.port === '5173' ? 'localhost:8001' : window.location.host;
    const wsUrl = `${protocol}//${host}/api/v1/ws/${channel}`;

    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    ws.onopen = () => {
      setChannelConnected(channel, true);
    };

    ws.onclose = () => {
      setChannelConnected(channel, false);
    };

    ws.onerror = (err) => {
      console.warn(`[WS Error] Channel ${channel}:`, err);
      setChannelConnected(channel, false);
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (onMessage) {
          onMessage(payload);
        }
      } catch (e) {
        console.error(`[WS Parse Error] Channel ${channel}:`, e);
      }
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
      setChannelConnected(channel, false);
    };
  }, [channel, onMessage, setChannelConnected]);

  return socketRef;
}
