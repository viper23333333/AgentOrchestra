'use client';

import { motion } from 'framer-motion';
import { cn, getAgentColorClass, getAgentBgColorClass } from '@/lib/utils';
import { AGENT_TYPE_LABELS, type AgentType } from '@/types';

/**
 * Agent 正在输入的动画指示器
 * - 显示哪些 Agent 正在工作
 * - 跳动的点动画
 * - 支持 Agent 类型颜色区分
 */

/** TypingIndicator 属性 */
interface TypingIndicatorProps {
  /** 正在输入的 Agent ID 列表 */
  agentIds: string[];
  /** 自定义类名 */
  className?: string;
}

/**
 * 从 Agent ID 推断 Agent 类型
 */
function inferAgentType(agentId: string): AgentType {
  if (agentId.includes('planner')) return 'planner';
  if (agentId.includes('researcher')) return 'researcher';
  if (agentId.includes('coder')) return 'coder';
  if (agentId.includes('reviewer')) return 'reviewer';
  if (agentId.includes('summarizer')) return 'summarizer';
  return 'planner';
}

/**
 * 单个 Agent 的输入指示器
 */
function AgentTypingDot({ agentId }: { agentId: string }) {
  const agentType = inferAgentType(agentId);
  const colorClass = getAgentColorClass(agentType);
  const bgClass = getAgentBgColorClass(agentType);

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 10 }}
      className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700 shadow-sm"
    >
      {/* Agent 名称 */}
      <span className={cn('text-xs font-medium', colorClass)}>
        {AGENT_TYPE_LABELS[agentType]}
      </span>

      {/* 跳动的点 */}
      <div className="flex items-center gap-0.5">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className={cn('w-1.5 h-1.5 rounded-full', colorClass.replace('text-', 'bg-'))}
            animate={{
              y: [0, -4, 0],
              opacity: [0.4, 1, 0.4],
            }}
            transition={{
              duration: 0.8,
              repeat: Infinity,
              delay: i * 0.15,
              ease: 'easeInOut',
            }}
          />
        ))}
      </div>
    </motion.div>
  );
}

/**
 * TypingIndicator 组件
 */
export default function TypingIndicator({
  agentIds,
  className,
}: TypingIndicatorProps) {
  if (agentIds.length === 0) return null;

  return (
    <div className={cn('px-4 pb-2', className)}>
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 pl-11">
          {/* 提示文字 */}
          <span className="text-xs text-surface-400 flex-shrink-0">正在处理</span>

          {/* Agent 指示器列表 */}
          <div className="flex items-center gap-2 overflow-x-auto scrollbar-hidden">
            {agentIds.map((agentId) => (
              <AgentTypingDot key={agentId} agentId={agentId} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export type { TypingIndicatorProps };
