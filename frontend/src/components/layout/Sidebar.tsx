'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  MessageSquare,
  Trash2,
  PanelLeftClose,
  Search,
} from 'lucide-react';
import { cn, formatRelativeTime } from '@/lib/utils';
import { useChatStore } from '@/store/chat-store';
import type { Conversation } from '@/types';

/**
 * 侧边栏组件
 * - 显示对话历史列表
 * - 创建新对话
 * - 删除对话
 * - 搜索对话
 * - 可折叠
 */

/** Sidebar 属性 */
interface SidebarProps {
  /** 是否展开 */
  isExpanded: boolean;
  /** 切换展开/折叠 */
  onToggle: () => void;
  /** 创建新对话回调 */
  onNewConversation?: () => void;
  /** 自定义类名 */
  className?: string;
}

/**
 * 对话列表项组件
 */
function ConversationItem({
  conversation,
  isActive,
  onClick,
  onDelete,
}: {
  conversation: Conversation;
  isActive: boolean;
  onClick: () => void;
  onDelete: () => void;
}) {
  const [showActions, setShowActions] = useState(false);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -5 }}
      transition={{ duration: 0.15 }}
      className="group relative"
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <button
        onClick={onClick}
        className={cn(
          'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left',
          'transition-colors duration-150',
          isActive
            ? 'bg-surface-700/50 text-white'
            : 'text-surface-300 hover:bg-surface-700/30 hover:text-white'
        )}
      >
        {/* 对话图标 */}
        <MessageSquare className="w-4 h-4 flex-shrink-0 opacity-60" />

        {/* 对话信息 */}
        <div className="flex-1 min-w-0">
          <p className={cn('text-sm font-medium truncate', isActive ? 'text-white' : 'text-surface-200')}>
            {conversation.title}
          </p>
          <p className="text-xs text-surface-500 mt-0.5">
            {conversation.messages.length} 条消息
            {conversation.updatedAt && (
              <span className="ml-2">{formatRelativeTime(conversation.updatedAt)}</span>
            )}
          </p>
        </div>

        {/* 操作按钮 */}
        <AnimatePresence>
          {showActions && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              onClick={(e) => {
                e.stopPropagation();
                onDelete();
              }}
              className="p-1 rounded text-surface-500 hover:text-red-400 hover:bg-surface-700/50 transition-colors"
              aria-label="删除对话"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </motion.button>
          )}
        </AnimatePresence>
      </button>
    </motion.div>
  );
}

/**
 * Sidebar 组件
 */
export default function Sidebar({
  isExpanded,
  onToggle,
  onNewConversation,
  className,
}: SidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const {
    conversations,
    activeConversationId,
    setActiveConversation,
    deleteConversation,
  } = useChatStore();

  /** 过滤对话列表 */
  const filteredConversations = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  /** 按更新时间排序（最新在前） */
  const sortedConversations = [...filteredConversations].sort(
    (a, b) => b.updatedAt - a.updatedAt
  );

  return (
    <>
      {/* 移动端遮罩 */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-30 lg:hidden"
            onClick={onToggle}
          />
        )}
      </AnimatePresence>

      {/* 侧边栏 */}
      <motion.aside
        initial={false}
        animate={{ width: isExpanded ? 280 : 0 }}
        transition={{ duration: 0.2, ease: 'easeInOut' }}
        className={cn(
          'h-full flex-shrink-0 overflow-hidden',
          'bg-surface-900 dark:bg-surface-950',
          'border-r border-surface-800 dark:border-surface-800',
          'flex flex-col',
          // 移动端定位
          'fixed lg:relative z-40 lg:z-auto',
          'top-0 left-0 lg:top-auto lg:left-auto',
          className
        )}
      >
        <div className="w-[280px] h-full flex flex-col">
          {/* 头部 */}
          <div className="flex items-center justify-between p-4 pb-2">
            <h2 className="text-sm font-semibold text-surface-200 uppercase tracking-wider">
              对话历史
            </h2>
            <button
              onClick={onToggle}
              className="p-1.5 rounded-lg text-surface-400 hover:text-surface-200 hover:bg-surface-800 transition-colors lg:hidden"
              aria-label="关闭侧边栏"
            >
              <PanelLeftClose className="w-4 h-4" />
            </button>
          </div>

          {/* 新建对话按钮 */}
          <div className="px-3 pb-3">
            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              onClick={onNewConversation}
              className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium transition-colors shadow-glow"
            >
              <Plus className="w-4 h-4" />
              新建对话
            </motion.button>
          </div>

          {/* 搜索框 */}
          {conversations.length > 3 && (
            <div className="px-3 pb-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-surface-500" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="搜索对话..."
                  className="w-full pl-9 pr-3 py-2 rounded-lg bg-surface-800 border border-surface-700 text-sm text-surface-200 placeholder-surface-500 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                />
              </div>
            </div>
          )}

          {/* 对话列表 */}
          <div className="flex-1 overflow-y-auto px-3 pb-3 scrollbar-hidden">
            <AnimatePresence mode="popLayout">
              {sortedConversations.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-surface-500">
                  <MessageSquare className="w-8 h-8 mb-3 opacity-40" />
                  <p className="text-sm">
                    {searchQuery ? '没有找到匹配的对话' : '暂无对话'}
                  </p>
                  <p className="text-xs mt-1 text-surface-600">
                    点击上方按钮开始新对话
                  </p>
                </div>
              ) : (
                <div className="space-y-1">
                  {sortedConversations.map((conversation) => (
                    <ConversationItem
                      key={conversation.id}
                      conversation={conversation}
                      isActive={conversation.id === activeConversationId}
                      onClick={() => setActiveConversation(conversation.id)}
                      onDelete={() => deleteConversation(conversation.id)}
                    />
                  ))}
                </div>
              )}
            </AnimatePresence>
          </div>

          {/* 底部信息 */}
          <div className="px-4 py-3 border-t border-surface-800">
            <p className="text-xs text-surface-600 text-center">
              AgentOrchestra v0.1.0
            </p>
          </div>
        </div>
      </motion.aside>
    </>
  );
}

export type { SidebarProps };
