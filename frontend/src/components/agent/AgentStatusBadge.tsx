'use client';

import { cn, getAgentStatusStyle } from '@/lib/utils';
import type { AgentStatus } from '@/types';

/**
 * Agent 状态徽章组件
 * - 显示 Agent 当前状态
 * - 支持不同尺寸
 * - 状态指示灯动画
 */

/** AgentStatusBadge 属性 */
interface AgentStatusBadgeProps {
  /** Agent 状态 */
  status: AgentStatus;
  /** 徽章尺寸 */
  size?: 'sm' | 'md';
  /** 是否显示标签文字 */
  showLabel?: boolean;
  /** 自定义类名 */
  className?: string;
}

/**
 * AgentStatusBadge 组件
 */
export default function AgentStatusBadge({
  status,
  size = 'md',
  showLabel = true,
  className,
}: AgentStatusBadgeProps) {
  const style = getAgentStatusStyle(status);

  const sizeStyles = {
    sm: 'px-1.5 py-0.5 text-xs gap-1',
    md: 'px-2 py-1 text-xs gap-1.5',
  };

  const dotSizes = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full font-medium',
        'bg-surface-100 dark:bg-surface-800',
        sizeStyles[size],
        className
      )}
      title={style.label}
    >
      {/* 状态指示灯 */}
      <span className={cn('rounded-full', dotSizes[size], style.dotClass)} />

      {/* 状态标签 */}
      {showLabel && (
        <span className={cn('leading-none', style.textClass)}>
          {style.label}
        </span>
      )}
    </span>
  );
}

export type { AgentStatusBadgeProps };
