'use client';

import { memo } from 'react';
import { motion } from 'framer-motion';
import {
  Brain,
  Search,
  Code2,
  FileCheck,
  FileText,
  CheckCircle2,
  Clock,
  Zap,
} from 'lucide-react';
import { cn, getAgentColorClass, getAgentBgColorClass, getAgentBorderColorClass, formatRelativeTime } from '@/lib/utils';
import { AGENT_TYPE_LABELS, type Agent, type AgentType } from '@/types';
import AgentStatusBadge from './AgentStatusBadge';

/**
 * Agent 卡片组件
 * - 显示 Agent 状态和信息
 * - 支持选中状态
 * - 显示 Agent 统计信息
 * - 响应式设计
 */

/** AgentCard 属性 */
interface AgentCardProps {
  /** Agent 数据 */
  agent: Agent;
  /** 是否选中 */
  isSelected?: boolean;
  /** 点击回调 */
  onClick?: () => void;
  /** 自定义类名 */
  className?: string;
}

/** Agent 类型到图标的映射 */
const AGENT_ICONS: Record<AgentType, React.ComponentType<{ className?: string }>> = {
  planner: Brain,
  researcher: Search,
  coder: Code2,
  reviewer: FileCheck,
  summarizer: FileText,
};

/**
 * AgentCard 组件
 */
const AgentCard = memo(function AgentCard({
  agent,
  isSelected = false,
  onClick,
  className,
}: AgentCardProps) {
  const IconComponent = AGENT_ICONS[agent.type];
  const colorClass = getAgentColorClass(agent.type);
  const bgClass = getAgentBgColorClass(agent.type);
  const borderClass = getAgentBorderColorClass(agent.type);

  return (
    <motion.div
      whileHover={{ scale: 1.01, y: -2 }}
      whileTap={{ scale: 0.99 }}
      onClick={onClick}
      className={cn(
        'relative p-4 rounded-xl cursor-pointer transition-all duration-200',
        'bg-white dark:bg-surface-800/50',
        'border',
        isSelected
          ? `${borderClass} shadow-glow`
          : 'border-surface-200 dark:border-surface-700 hover:border-surface-300 dark:hover:border-surface-600',
        className
      )}
    >
      {/* 选中指示器 */}
      {isSelected && (
        <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-primary-500 to-purple-500 rounded-t-xl" />
      )}

      {/* 头部：图标和名称 */}
      <div className="flex items-start gap-3">
        {/* Agent 图标 */}
        <div
          className={cn(
            'w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0',
            bgClass
          )}
        >
          <IconComponent className={cn('w-5 h-5', colorClass)} />
        </div>

        {/* 名称和状态 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-surface-900 dark:text-white">
              {agent.name}
            </h3>
            <AgentStatusBadge status={agent.status} size="sm" />
          </div>
          <p className="text-xs text-surface-500 dark:text-surface-400 mt-0.5">
            {AGENT_TYPE_LABELS[agent.type]}
          </p>
        </div>
      </div>

      {/* 描述 */}
      <p className="text-xs text-surface-600 dark:text-surface-400 mt-3 line-clamp-2 leading-relaxed">
        {agent.description}
      </p>

      {/* 能力标签 */}
      <div className="flex flex-wrap gap-1.5 mt-3">
        {agent.capabilities.slice(0, 3).map((cap) => (
          <span
            key={cap}
            className={cn(
              'text-xs px-2 py-0.5 rounded-full',
              bgClass,
              colorClass
            )}
          >
            {cap}
          </span>
        ))}
        {agent.capabilities.length > 3 && (
          <span className="text-xs px-2 py-0.5 rounded-full bg-surface-100 dark:bg-surface-700 text-surface-500">
            +{agent.capabilities.length - 3}
          </span>
        )}
      </div>

      {/* 统计信息 */}
      <div className="flex items-center gap-4 mt-3 pt-3 border-t border-surface-100 dark:border-surface-700/50">
        <div className="flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-accent-500" />
          <span className="text-xs text-surface-500">
            {agent.stats.tasksCompleted} 任务
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <Zap className="w-3.5 h-3.5 text-primary-400" />
          <span className="text-xs text-surface-500">
            {agent.stats.averageResponseTime > 0
              ? `${(agent.stats.averageResponseTime / 1000).toFixed(1)}s`
              : '--'}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-surface-400" />
          <span className="text-xs text-surface-500">
            {formatRelativeTime(agent.lastActiveAt)}
          </span>
        </div>
      </div>
    </motion.div>
  );
});

export default AgentCard;
export type { AgentCardProps };
