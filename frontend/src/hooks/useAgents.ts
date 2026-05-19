'use client';

import { useCallback, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useAgentStore } from '@/store/agent-store';
import { agentService } from '@/services/agent-service';
import type { Agent, AgentConfig, Workflow } from '@/types';

/**
 * Agent 管理 Hook
 * 封装 Agent 列表获取、配置更新和工作流管理
 */

/** useAgents Hook 返回值 */
interface UseAgentsReturn {
  /** Agent 列表 */
  agents: Agent[];
  /** 工作流数据 */
  workflow: Workflow | null;
  /** 是否正在加载 */
  isLoading: boolean;
  /** 错误信息 */
  error: string | null;
  /** 选中的 Agent ID */
  selectedAgentId: string | null;
  /** 是否有活跃 Agent */
  hasActiveAgents: boolean;
  /** 获取 Agent 列表 */
  fetchAgents: () => Promise<void>;
  /** 获取工作流 */
  fetchWorkflow: (conversationId?: string) => Promise<void>;
  /** 更新 Agent 配置 */
  updateAgentConfig: (agentId: string, config: Partial<AgentConfig>) => Promise<void>;
  /** 选中 Agent */
  selectAgent: (id: string | null) => void;
}

/** React Query Keys */
const AGENT_KEYS = {
  all: ['agents'] as const,
  list: () => [...AGENT_KEYS.all, 'list'] as const,
  detail: (id: string) => [...AGENT_KEYS.all, 'detail', id] as const,
  workflow: (conversationId?: string) =>
    [...AGENT_KEYS.all, 'workflow', conversationId] as const,
};

/**
 * Agent 管理 Hook
 */
export function useAgents(conversationId?: string): UseAgentsReturn {
  const queryClient = useQueryClient();
  const {
    agents,
    workflow,
    isLoading,
    error,
    selectedAgentId,
    setAgents,
    setWorkflow,
    setLoading,
    setError,
    selectAgent,
    updateAgent,
    hasActiveAgents,
  } = useAgentStore();

  /**
   * 获取 Agent 列表
   */
  const fetchAgents = useCallback(async () => {
    setLoading(true);
    try {
      const agentList = await agentService.getAgents();
      setAgents(agentList);
    } catch (error) {
      console.error('[useAgents] Failed to fetch agents:', error);
      setError('获取 Agent 列表失败');
    } finally {
      setLoading(false);
    }
  }, [setAgents, setLoading, setError]);

  /**
   * 获取工作流
   */
  const fetchWorkflow = useCallback(
    async (convId?: string) => {
      try {
        const wf = await agentService.getWorkflow(convId);
        setWorkflow(wf);
      } catch (error) {
        console.error('[useAgents] Failed to fetch workflow:', error);
      }
    },
    [setWorkflow]
  );

  /**
   * 更新 Agent 配置
   */
  const handleUpdateAgentConfig = useCallback(
    async (agentId: string, config: Partial<AgentConfig>) => {
      try {
        const updatedAgent = await agentService.updateAgentConfig(agentId, config);
        if (updatedAgent) {
          updateAgent(agentId, { config: { ...updatedAgent.config, ...config } });
        }
        // 刷新缓存
        queryClient.invalidateQueries({ queryKey: AGENT_KEYS.detail(agentId) });
      } catch (error) {
        console.error('[useAgents] Failed to update agent config:', error);
        setError('更新 Agent 配置失败');
      }
    },
    [updateAgent, setError, queryClient]
  );

  /**
   * 初始加载 Agent 列表
   */
  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  /**
   * 当对话 ID 变化时加载工作流
   */
  useEffect(() => {
    fetchWorkflow(conversationId);
  }, [conversationId, fetchWorkflow]);

  return {
    agents,
    workflow,
    isLoading,
    error,
    selectedAgentId,
    hasActiveAgents: hasActiveAgents(),
    fetchAgents,
    fetchWorkflow,
    updateAgentConfig: handleUpdateAgentConfig,
    selectAgent,
  };
}

export default useAgents;
