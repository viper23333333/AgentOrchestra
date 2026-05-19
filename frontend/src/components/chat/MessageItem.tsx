'use client';

import { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check, User, Bot, AlertCircle } from 'lucide-react';
import { useState, useCallback } from 'react';
import { cn, formatRelativeTime, getAgentColorClass, getAgentBgColorClass } from '@/lib/utils';
import { AGENT_TYPE_LABELS } from '@/types';
import type { Message } from '@/types';

/**
 * 单条消息组件
 * - 支持 Markdown 渲染
 * - 支持代码高亮和复制
 * - 区分用户消息和 Agent 消息
 * - 显示发送者信息和时间
 */

/** MessageItem 属性 */
interface MessageItemProps {
  /** 消息数据 */
  message: Message;
  /** 自定义类名 */
  className?: string;
}

/**
 * 代码块组件（带复制功能）
 */
function CodeBlock({
  language,
  code,
}: {
  language: string;
  code: string;
}) {
  const [copied, setCopied] = useState(false);

  /** 复制代码 */
  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // 降级方案
      const textarea = document.createElement('textarea');
      textarea.value = code;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [code]);

  return (
    <div className="code-block group relative my-3">
      {/* 代码头部 */}
      <div className="flex items-center justify-between px-4 py-2 bg-surface-800 border-b border-surface-700">
        <span className="text-xs text-surface-400 font-mono">{language || 'code'}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2 py-1 rounded text-xs text-surface-400 hover:text-surface-200 hover:bg-surface-700 transition-colors"
          aria-label="复制代码"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-accent-500" />
              <span className="text-accent-500">已复制</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>复制</span>
            </>
          )}
        </button>
      </div>

      {/* 代码内容 */}
      <SyntaxHighlighter
        language={language || 'text'}
        style={oneDark}
        customStyle={{
          margin: 0,
          padding: '1rem',
          background: 'transparent',
          fontSize: '0.8125rem',
          lineHeight: '1.6',
        }}
        showLineNumbers={code.split('\n').length > 3}
        lineNumberStyle={{
          color: '#4a5568',
          fontSize: '0.75rem',
          minWidth: '2.5em',
        }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}

/**
 * MessageItem 组件
 */
const MessageItem = memo(function MessageItem({ message, className }: MessageItemProps) {
  const isUser = message.role === 'user';
  const isError = message.status === 'error';
  const isStreaming = message.status === 'streaming';

  /** Agent 类型对应的颜色 */
  const agentType = message.sender?.agentType;
  const agentColorClass = agentType ? getAgentColorClass(agentType) : 'text-primary-500';
  const agentBgClass = agentType ? getAgentBgColorClass(agentType) : 'bg-primary-500/10';

  return (
    <div
      className={cn(
        'flex gap-3',
        isUser ? 'flex-row-reverse' : 'flex-row',
        className
      )}
    >
      {/* 头像 */}
      <div
        className={cn(
          'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
          isUser
            ? 'bg-primary-500 text-white'
            : `${agentBgClass} ${agentColorClass}`
        )}
      >
        {isUser ? (
          <User className="w-4 h-4" />
        ) : (
          <Bot className="w-4 h-4" />
        )}
      </div>

      {/* 消息内容 */}
      <div className={cn('flex-1 min-w-0 max-w-[80%] md:max-w-[75%]', isUser && 'flex flex-col items-end')}>
        {/* 发送者信息 */}
        <div className={cn('flex items-center gap-2 mb-1', isUser && 'flex-row-reverse')}>
          <span className="text-sm font-medium text-surface-700 dark:text-surface-300">
            {isUser ? '你' : message.sender?.name || 'Agent'}
          </span>
          {!isUser && agentType && (
            <span className={cn('text-xs px-1.5 py-0.5 rounded', agentBgClass, agentColorClass)}>
              {AGENT_TYPE_LABELS[agentType]}
            </span>
          )}
          <span className="text-xs text-surface-400">
            {formatRelativeTime(message.timestamp)}
          </span>
        </div>

        {/* 消息气泡 */}
        <div
          className={cn(
            'rounded-2xl px-4 py-3',
            isUser
              ? 'message-bubble-user'
              : 'message-bubble-agent',
            isError && 'border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/30',
            isStreaming && !isUser && 'animate-pulse'
          )}
        >
          {/* 错误提示 */}
          {isError && (
            <div className="flex items-center gap-2 mb-2 text-red-500">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm font-medium">发送失败</span>
            </div>
          )}

          {/* 消息内容 - Markdown 渲染 */}
          {isUser ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="markdown-content text-sm text-surface-800 dark:text-surface-200">
              {message.content ? (
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '');
                      const codeString = String(children).replace(/\n$/, '');

                      // 判断是否为代码块（有语言标识或多行）
                      if (match || codeString.includes('\n')) {
                        return (
                          <CodeBlock language={match?.[1] || ''} code={codeString} />
                        );
                      }

                      // 行内代码
                      return (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    },
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              ) : isStreaming ? (
                <span className="inline-block w-2 h-4 bg-surface-400 animate-pulse rounded-sm" />
              ) : null}
            </div>
          )}
        </div>

        {/* Token 使用统计 */}
        {message.usage && (
          <div className="mt-1 flex items-center gap-3 text-xs text-surface-400">
            <span>
              输入: {message.usage.promptTokens} tokens
            </span>
            <span>
              输出: {message.usage.completionTokens} tokens
            </span>
          </div>
        )}
      </div>
    </div>
  );
});

export default MessageItem;
export type { MessageItemProps };
