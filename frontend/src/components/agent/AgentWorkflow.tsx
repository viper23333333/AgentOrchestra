'use client';

import { motion } from 'framer-motion';
import {
  Brain,
  Search,
  Code2,
  FileCheck,
  FileText,
  ArrowRight,
} from 'lucide-react';
import { cn, getAgentColorClass, getAgentBgColorClass, getAgentStatusStyle } from '@/lib/utils';
import { AGENT_TYPE_LABELS, type AgentType, type AgentStatus, type Workflow } from '@/types';
import AgentStatusBadge from './AgentStatusBadge';

/**
 * Agent 工作流可视化组件
 * - 展示 Agent 协作流程图
 * - 显示各 Agent 的当前状态
 * - 动画过渡效果
 * - 响应式布局
 */

/** AgentWorkflow 属性 */
interface AgentWorkflowProps {
  /** 工作流数据 */
  workflow: Workflow | null;
  /** Agent 状态映射（ID -> 状态信息） */
  agentStates?: Map<
    string,
    { status: AgentStatus; message?: string; progress?: number }
  >;
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

/** 工作流步骤定义 */
const WORKFLOW_STEPS: { type: AgentType; label: string; description: string }[] = [
  {
    type: 'planner',
    label: '规划',
    description: '分析需求，制定执行计划',
  },
  {
    type: 'researcher',
    label: '研究',
    description: '收集信息，调研技术方案',
  },
  {
    type: 'coder',
    label: '编码',
    description: '实现功能，编写代码',
  },
  {
    type: 'reviewer',
    label: '审查',
    description: '代码审查，质量检查',
  },
  {
    type: 'summarizer',
    label: '总结',
    description: '汇总结果，生成报告',
  },
];

/**
 * 单个工作流节点
 */
function WorkflowNode({
  step,
  index,
  isActive,
  isCompleted,
  status,
  message,
}: {
  step: (typeof WORKFLOW_STEPS)[number];
  index: number;
  isActive: boolean;
  isCompleted: boolean;
  status?: AgentStatus;
  message?: string;
}) {
  const IconComponent = AGENT_ICONS[step.type];
  const colorClass = getAgentColorClass(step.type);
  const bgClass = getAgentBgColorClass(step.type);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      className="flex flex-col items-center"
    >
      {/* 节点圆圈 */}
      <motion.div
        animate={
          isActive
            ? { scale: [1, 1.05, 1], boxShadow: ['0 0 0 0 rgba(99,102,241,0.4)', '0 0 0 8px rgba(99,102,241,0)', '0 0 0 0 rgba(99,102,241,0)'] }
            : {}
        }
        transition={isActive ? { duration: 2, repeat: Infinity } : {}}
        className={cn(
          'w-14 h-14 rounded-2xl flex items-center justify-center relative',
          'border-2 transition-all duration-300',
          isActive
            ? `${bgClass} ${colorClass.replace('text-', 'border-')}`
            : isCompleted
              ? 'bg-accent-50 dark:bg-accent-950/30 border-accent-200 dark:border-accent-800'
              : 'bg-surface-100 dark:bg-surface-800 border-surface-200 dark:border-surface-700'
        )}
      >
        <IconComponent
          className={cn(
            'w-6 h-6',
            isActive
              ? colorClass
              : isCompleted
                ? 'text-accent-500'
                : 'text-surface-400'
          )}
        />

        {/* 完成勾选标记 */}
        {isCompleted && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute -top-1 -right-1 w-5 h-5 bg-accent-500 rounded-full flex items-center justify-center"
          >
            <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </motion.div>
        )}

        {/* 步骤序号 */}
        <div
          className={cn(
            'absolute -top-2 -left-2 w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold',
            isActive
              ? 'bg-primary-500 text-white'
              : isCompleted
                ? 'bg-accent-500 text-white'
                : 'bg-surface-200 dark:bg-surface-700 text-surface-500'
          )}
        >
          {index + 1}
        </div>
      </motion.div>

      {/* 标签 */}
      <div className="mt-3 text-center">
        <p
          className={cn(
            'text-sm font-semibold',
            isActive
              ? colorClass
              : isCompleted
                ? 'text-accent-600 dark:text-accent-400'
                : 'text-surface-600 dark:text-surface-400'
          )}
        >
          {step.label}
        </p>
        <p className="text-xs text-surface-400 dark:text-surface-500 mt-0.5 max-w-[100px]">
          {step.description}
        </p>
      </div>

      {/* 状态消息 */}
      {isActive && message && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-xs text-primary-500 mt-2 max-w-[120px] text-center"
        >
          {message}
        </motion.p>
      )}
    </motion.div>
  );
}

/**
 * 连接线组件
 */
function ConnectionLine({ isActive }: { isActive: boolean }) {
  return (
    <div className="flex items-center justify-center px-2 self-start mt-7">
      <div className="relative w-12 h-0.5">
        <div
          className={cn(
            'absolute inset-0 rounded-full',
            isActive ? 'bg-primary-300 dark:bg-primary-700' : 'bg-surface-200 dark:bg-surface-700'
          )}
        />
        {isActive && (
          <motion.div
            className="absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-primary-500"
            animate={{ x: [0, 40] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          />
        )}
        <ArrowRight
          className={cn(
            'absolute -right-1 top-1/2 -translate-y-1/2 w-3 h-3',
            isActive ? 'text-primary-400' : 'text-surface-300 dark:text-surface-600'
          )}
        />
      </div>
    </div>
  );
}

/**
 * AgentWorkflow 组件
 */
export default function AgentWorkflow({
  workflow,
  agentStates,
  className,
}: AgentWorkflowProps) {
  /** 确定每个步骤的状态 */
  const getStepStatus = (agentType: AgentType): { isActive: boolean; isCompleted: boolean; status?: AgentStatus; message?: string } => {
    if (!agentStates) return { isActive: false, isCompleted: false };

    for (const [agentId, state] of agentStates.entries()) {
      if (agentId.includes(agentType)) {
        return {
          isActive: state.status === 'thinking' || state.status === 'working',
          isCompleted: state.status === 'completed',
          status: state.status,
          message: state.message,
        };
      }
    }

    return { isActive: false, isCompleted: false };
  };

  return (
    <div className={cn('p-6 rounded-2xl bg-white dark:bg-surface-800/50 border border-surface-200 dark:border-surface-700', className)}>
      {/* 标题 */}
      <div className="mb-6">
        <h3 className="text-base font-semibold text-surface-900 dark:text-white">
          Agent 工作流
        </h3>
        <p className="text-sm text-surface-500 dark:text-surface-400 mt-1">
          多 Agent 协作执行流程
        </p>
      </div>

      {/* 工作流图 */}
      <div className="flex items-start overflow-x-auto pb-4 scrollbar-hidden">
        {WORKFLOW_STEPS.map((step, index) => {
          const { isActive, isCompleted, status, message } = getStepStatus(step.type);

          return (
            <div key={step.type} className="flex items-start">
              <WorkflowNode
                step={step}
                index={index}
                isActive={isActive}
                isCompleted={isCompleted}
                status={status}
                message={message}
              />

              {/* 连接线（最后一个节点不需要） */}
              {index < WORKFLOW_STEPS.length - 1 && (
                <ConnectionLine isActive={isActive || isCompleted} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export type { AgentWorkflowProps };
