'use client';

import { useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot } from 'lucide-react';
import { useChat } from '@/hooks/useChat';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import TypingIndicator from './TypingIndicator';
import { cn } from '@/lib/utils';

/**
 * 聊天面板主组件
 * - 整合消息列表、输入框和状态指示器
 * - 管理聊天交互流程
 * - 空状态展示
 */

/** ChatPanel 属性 */
interface ChatPanelProps {
  /** 自定义类名 */
  className?: string;
}

/**
 * ChatPanel 组件
 */
export default function ChatPanel({ className }: ChatPanelProps) {
  const {
    messages,
    isSending,
    error,
    typingAgentIds,
    sendMessage,
    stopGeneration,
    clearError,
  } = useChat();

  /** 是否有空消息 */
  const isEmpty = messages.length === 0;

  /** 发送消息处理 */
  const handleSend = useCallback(
    async (content: string) => {
      await sendMessage(content);
    },
    [sendMessage]
  );

  return (
    <div className={cn('flex-1 flex flex-col overflow-hidden', className)}>
      {/* 错误提示 */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mx-4 mt-3 px-4 py-3 rounded-lg bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 flex items-center justify-between"
          >
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            <button
              onClick={clearError}
              className="text-red-400 hover:text-red-600 text-sm font-medium ml-4"
            >
              关闭
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 消息列表区域 */}
      {isEmpty ? (
        /* 空状态 */
        <div className="flex-1 flex items-center justify-center p-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-md"
          >
            {/* Logo */}
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center mx-auto mb-6 shadow-glow-lg">
              <Bot className="w-8 h-8 text-white" />
            </div>

            {/* 标题 */}
            <h2 className="text-2xl font-bold text-surface-900 dark:text-white mb-2">
              AgentOrchestra
            </h2>
            <p className="text-surface-500 dark:text-surface-400 mb-8">
              多 Agent 协作平台，让专业 AI 团队为您解决复杂问题
            </p>

            {/* 快捷提示 */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {[
                { icon: '💡', text: '帮我分析这个技术方案的优劣' },
                { icon: '🔍', text: '调研最新的前端框架趋势' },
                { icon: '💻', text: '用 Python 实现一个快速排序算法' },
                { icon: '📝', text: '总结今天的会议要点' },
              ].map((item) => (
                <button
                  key={item.text}
                  onClick={() => handleSend(item.text)}
                  className="flex items-start gap-3 p-3 rounded-xl bg-white dark:bg-surface-800/50 border border-surface-200 dark:border-surface-700 hover:border-primary-200 dark:hover:border-primary-800 hover:shadow-glow transition-all text-left group"
                >
                  <span className="text-lg">{item.icon}</span>
                  <span className="text-sm text-surface-600 dark:text-surface-400 group-hover:text-surface-900 dark:group-hover:text-surface-200 transition-colors">
                    {item.text}
                  </span>
                </button>
              ))}
            </div>
          </motion.div>
        </div>
      ) : (
        /* 消息列表 */
        <MessageList messages={messages} isSending={isSending} />
      )}

      {/* 正在输入指示器 */}
      <AnimatePresence>
        {typingAgentIds.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <TypingIndicator agentIds={typingAgentIds} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* 输入区域 */}
      <ChatInput
        onSend={handleSend}
        onStop={stopGeneration}
        isSending={isSending}
        disabled={false}
      />
    </div>
  );
}

export type { ChatPanelProps };
