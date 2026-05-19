'use client';

import { useState, useRef, useCallback, type KeyboardEvent, type ChangeEvent } from 'react';
import { Send, Square, Paperclip, Mic } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

/**
 * 聊天输入框组件
 * - 支持多行输入（自动扩展高度）
 * - Enter 发送，Shift+Enter 换行
 * - 发送/停止按钮切换
 * - 附件和语音按钮（预留）
 */

/** ChatInput 属性 */
interface ChatInputProps {
  /** 发送消息回调 */
  onSend: (content: string) => void;
  /** 停止生成回调 */
  onStop: () => void;
  /** 是否正在发送 */
  isSending?: boolean;
  /** 是否禁用 */
  disabled?: boolean;
  /** 占位符文本 */
  placeholder?: string;
  /** 自定义类名 */
  className?: string;
}

/** 最小/最大高度 */
const MIN_HEIGHT = 44;
const MAX_HEIGHT = 200;

/**
 * ChatInput 组件
 */
export default function ChatInput({
  onSend,
  onStop,
  isSending = false,
  disabled = false,
  placeholder = '输入消息，按 Enter 发送...',
  className,
}: ChatInputProps) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /** 是否可以发送（有内容且未在发送中） */
  const canSend = value.trim().length > 0 && !isSending && !disabled;

  /**
   * 自动调整 textarea 高度
   */
  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, MAX_HEIGHT);
    textarea.style.height = `${Math.max(newHeight, MIN_HEIGHT)}px`;
  }, []);

  /**
   * 处理输入变化
   */
  const handleChange = useCallback(
    (e: ChangeEvent<HTMLTextAreaElement>) => {
      setValue(e.target.value);
      adjustHeight();
    },
    [adjustHeight]
  );

  /**
   * 处理键盘事件
   * - Enter: 发送消息
   * - Shift+Enter: 换行
   */
  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();

        if (canSend) {
          handleSend();
        }
      }
    },
    [canSend] // eslint-disable-line react-hooks/exhaustive-deps
  );

  /**
   * 发送消息
   */
  const handleSend = useCallback(() => {
    if (!canSend) return;

    const content = value.trim();
    onSend(content);
    setValue('');

    // 重置 textarea 高度
    if (textareaRef.current) {
      textareaRef.current.style.height = `${MIN_HEIGHT}px`;
    }
  }, [value, canSend, onSend]);

  return (
    <div
      className={cn(
        'border-t border-surface-200 dark:border-surface-800',
        'bg-white/80 dark:bg-surface-900/80 backdrop-blur-xl',
        'px-4 py-3',
        className
      )}
    >
      <div className="max-w-4xl mx-auto">
        {/* 输入区域 */}
        <div
          className={cn(
            'flex items-end gap-2 p-2 rounded-2xl',
            'bg-surface-100 dark:bg-surface-800',
            'border border-surface-200 dark:border-surface-700',
            'focus-within:border-primary-300 dark:focus-within:border-primary-600',
            'focus-within:ring-2 focus-within:ring-primary-500/20',
            'transition-all duration-200'
          )}
        >
          {/* 附件按钮（预留） */}
          <button
            className="p-2 rounded-lg text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors flex-shrink-0"
            aria-label="添加附件"
            title="添加附件（即将推出）"
          >
            <Paperclip className="w-5 h-5" />
          </button>

          {/* 文本输入区域 */}
          <textarea
            ref={textareaRef}
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled || isSending}
            rows={1}
            className={cn(
              'flex-1 resize-none bg-transparent',
              'text-sm text-surface-900 dark:text-surface-100',
              'placeholder-surface-400 dark:placeholder-surface-500',
              'focus:outline-none',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'py-2 px-1',
              'scrollbar-hidden'
            )}
            style={{ minHeight: `${MIN_HEIGHT}px`, maxHeight: `${MAX_HEIGHT}px` }}
          />

          {/* 语音按钮（预留） */}
          <button
            className="p-2 rounded-lg text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors flex-shrink-0"
            aria-label="语音输入"
            title="语音输入（即将推出）"
          >
            <Mic className="w-5 h-5" />
          </button>

          {/* 发送/停止按钮 */}
          <div className="flex-shrink-0">
            {isSending ? (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onStop}
                className="p-2.5 rounded-xl bg-red-500 hover:bg-red-600 text-white transition-colors shadow-sm"
                aria-label="停止生成"
              >
                <Square className="w-4 h-4" />
              </motion.button>
            ) : (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSend}
                disabled={!canSend}
                className={cn(
                  'p-2.5 rounded-xl transition-all duration-200',
                  canSend
                    ? 'bg-primary-500 hover:bg-primary-600 text-white shadow-sm shadow-primary-500/20'
                    : 'bg-surface-200 dark:bg-surface-700 text-surface-400 cursor-not-allowed'
                )}
                aria-label="发送消息"
              >
                <Send className="w-4 h-4" />
              </motion.button>
            )}
          </div>
        </div>

        {/* 底部提示 */}
        <p className="text-xs text-surface-400 dark:text-surface-500 text-center mt-2">
          AgentOrchestra 可能会出错，请核实重要信息。按 Shift+Enter 换行。
        </p>
      </div>
    </div>
  );
}

export type { ChatInputProps };
