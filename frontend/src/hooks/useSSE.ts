'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import type { SSEEvent, SSEEventType } from '@/types';

/**
 * SSE (Server-Sent Events) Hook
 * 用于流式接收后端推送的事件
 * - 自动重连
 * - 事件类型路由
 * - 生命周期管理
 */

/** SSE 事件监听器 */
type SSEEventListener<T = unknown> = (data: T) => void;

/** useSSE Hook 配置 */
interface UseSSEOptions {
  /** SSE 端点 URL */
  url: string | null;
  /** 请求头 */
  headers?: Record<string, string>;
  /** 是否自动连接 */
  autoConnect?: boolean;
  /** 重连间隔（毫秒） */
  reconnectInterval?: number;
  /** 最大重连次数 */
  maxReconnectAttempts?: number;
}

/** useSSE Hook 返回值 */
interface UseSSEReturn {
  /** 是否已连接 */
  isConnected: boolean;
  /** 是否正在连接 */
  isConnecting: boolean;
  /** 最后收到的数据 */
  lastEvent: SSEEvent | null;
  /** 错误信息 */
  error: string | null;
  /** 手动连接 */
  connect: () => void;
  /** 手动断开 */
  disconnect: () => void;
  /** 订阅特定事件类型 */
  on: <T = unknown>(eventType: SSEEventType, listener: SSEEventListener<T>) => () => void;
}

/**
 * SSE Hook
 */
export function useSSE(options: UseSSEOptions): UseSSEReturn {
  const {
    url,
    autoConnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);
  const [error, setError] = useState<string | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const listenersRef = useRef<Map<SSEEventType, Set<SSEEventListener>>>(new Map());
  const shouldReconnectRef = useRef(true);

  /**
   * 处理 SSE 消息
   */
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const sseEvent: SSEEvent = JSON.parse(event.data as string);
      setLastEvent(sseEvent);

      // 通知对应的监听器
      const listeners = listenersRef.current.get(sseEvent.event as SSEEventType);
      if (listeners) {
        listeners.forEach((listener) => {
          try {
            listener(sseEvent.data);
          } catch (err) {
            console.error('[useSSE] Listener error:', err);
          }
        });
      }
    } catch (err) {
      console.error('[useSSE] Failed to parse SSE event:', err);
    }
  }, []);

  /**
   * 建立 SSE 连接
   */
  const connect = useCallback(() => {
    if (!url) return;

    // 清理旧连接
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setIsConnecting(true);
    setError(null);
    shouldReconnectRef.current = true;

    try {
      // 注意：原生 EventSource 不支持自定义 headers
      // 如果需要自定义 headers，应使用 fetch + ReadableStream
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setIsConnected(true);
        setIsConnecting(false);
        reconnectAttemptsRef.current = 0;
        console.log('[useSSE] Connected');
      };

      eventSource.onmessage = handleMessage;

      eventSource.onerror = () => {
        setIsConnected(false);
        setIsConnecting(false);

        eventSource.close();
        eventSourceRef.current = null;

        // 自动重连
        if (
          shouldReconnectRef.current &&
          reconnectAttemptsRef.current < maxReconnectAttempts
        ) {
          reconnectAttemptsRef.current++;
          const delay = reconnectInterval * reconnectAttemptsRef.current;

          console.log(
            `[useSSE] Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
          );

          reconnectTimerRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setError('连接失败，已达到最大重连次数');
        }
      };
    } catch (err) {
      setIsConnecting(false);
      setError(err instanceof Error ? err.message : '连接失败');
    }
  }, [url, handleMessage, reconnectInterval, maxReconnectAttempts]);

  /**
   * 断开 SSE 连接
   */
  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;

    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    setIsConnected(false);
    setIsConnecting(false);
  }, []);

  /**
   * 订阅特定事件类型
   */
  const on = useCallback(
    <T = unknown>(eventType: SSEEventType, listener: SSEEventListener<T>): (() => void) => {
      const typedListener = listener as SSEEventListener;

      if (!listenersRef.current.has(eventType)) {
        listenersRef.current.set(eventType, new Set());
      }

      listenersRef.current.get(eventType)!.add(typedListener);

      // 返回取消订阅函数
      return () => {
        listenersRef.current.get(eventType)?.delete(typedListener);
      };
    },
    []
  );

  /**
   * 自动连接
   */
  useEffect(() => {
    if (autoConnect && url) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [url, autoConnect, connect, disconnect]);

  return {
    isConnected,
    isConnecting,
    lastEvent,
    error,
    connect,
    disconnect,
    on,
  };
}

export default useSSE;
