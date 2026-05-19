'use client';

import { useEffect, useRef } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import MessageItem from './MessageItem';
import type { Message } from '@/types';

/**
 * 消息列表组件
 * - 渲染消息列表
 * - 自动滚动到最新消息
 * - 支持虚拟滚动（预留）
 */

/** MessageList 属性 */
interface MessageListProps {
  /** 消息列表 */
  messages: Message[];
  /** 是否正在发送 */
  isSending?: boolean;
  /** 自定义类名 */
  className?: string;
}

/**
 * MessageList 组件
 */
export default function MessageList({
  messages,
  isSending = false,
  className,
}: MessageListProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  /**
   * 自动滚动到底部
   * 当有新消息或消息内容更新时触发
   */
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, messages.length > 0 ? messages[messages.length - 1]?.content : null]);

  /**
   * 初始加载时滚动到底部
   */
  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, []);

  return (
    <div
      ref={scrollContainerRef}
      className={`flex-1 overflow-y-auto px-4 py-6 scrollbar-hidden ${className || ''}`}
    >
      <div className="max-w-4xl mx-auto space-y-6">
        <AnimatePresence mode="popLayout">
          {messages.map((message, index) => (
            <motion.div
              key={message.id}
              layout
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{
                duration: 0.3,
                delay: message.role === 'user' ? 0 : 0.1,
              }}
            >
              <MessageItem message={message} />
            </motion.div>
          ))}
        </AnimatePresence>

        {/* 滚动锚点 */}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}

export type { MessageListProps };
