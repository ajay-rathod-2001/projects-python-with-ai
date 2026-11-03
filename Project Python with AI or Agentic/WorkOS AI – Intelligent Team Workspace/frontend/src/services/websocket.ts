type EventHandler = (data: any) => void;

class WebSocketClient {
  private socket: WebSocket | null = null;
  private workspaceId: string | null = null;
  private token: string | null = null;
  private listeners: Map<string, Set<EventHandler>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimer: number | null = null;

  connect(workspaceId: string, token: string) {
    this.workspaceId = workspaceId;
    this.token = token;
    const wsBaseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws';
    const url = `${wsBaseUrl}/${workspaceId}?token=${token}`;

    if (this.socket) {
      this.socket.close();
    }

    try {
      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        console.log(`[WS] Connected to workspace: ${workspaceId}`);
        this.reconnectAttempts = 0;
      };

      this.socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const handlers = this.listeners.get(payload.event);
          if (handlers) {
            handlers.forEach((fn) => fn(payload.data));
          }
        } catch (e) {
          console.error('[WS] Failed to parse message', e);
        }
      };

      this.socket.onclose = () => {
        console.log('[WS] Connection closed');
        this.attemptReconnect();
      };

      this.socket.onerror = (err) => {
        console.error('[WS] Error', err);
      };
    } catch (err) {
      console.error('[WS] Connection exception', err);
      this.attemptReconnect();
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.workspaceId && this.token) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * 2 ** this.reconnectAttempts, 10000);
      console.log(`[WS] Reconnecting in ${delay}ms... (Attempt ${this.reconnectAttempts})`);
      this.reconnectTimer = window.setTimeout(() => {
        this.connect(this.workspaceId!, this.token!);
      }, delay);
    }
  }

  subscribe(event: string, handler: EventHandler) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(handler);
    return () => {
      this.listeners.get(event)?.delete(handler);
    };
  }

  send(event: string, data: any) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ event, data }));
    }
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export const wsClient = new WebSocketClient();

