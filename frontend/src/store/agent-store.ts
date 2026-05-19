import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { Agent, AgentState, AgentStatus, Workflow, AgentType } from '@/types';

/**
 * Agent 状态管理 Store
 * 管理 Agent 列表、工作流状态和 Agent 配置
 */

/** Agent Store 状态接口 */
interface AgentStoreState {
  // ==========================================
  // 状态
  // ==========================================

  /** Agent 列表 */
  agents: Agent[];
  /** 当前对话的 Agent 实时状态 */
  agentStates: AgentState[];
  /** 工作流可视化数据 */
  workflow: Workflow | null;
  /** 是否正在加载 */
  isLoading: boolean;
  /** 错误信息 */
  error: string | null;
  /** 选中的 Agent ID */
  selectedAgentId: string | null;

  // ==========================================
  // Getters
  // ==========================================

  /** 根据 ID 获取 Agent */
  getAgentById: (id: string) => Agent | undefined;
  /** 根据类型获取 Agent */
  getAgentByType: (type: AgentType) => Agent | undefined;
  /** 获取指定 Agent 的实时状态 */
  getAgentState: (agentId: string) => AgentState | undefined;
  /** 获取选中的 Agent */
  getSelectedAgent: () => Agent | undefined;
  /** 获取当前活跃的 Agent 列表 */
  getActiveAgents: () => AgentState[];
  /** 检查是否有 Agent 正在工作 */
  hasActiveAgents: () => boolean;

  // ==========================================
  // Actions
  // ==========================================

  /** 设置 Agent 列表 */
  setAgents: (agents: Agent[]) => void;
  /** 更新单个 Agent */
  updateAgent: (id: string, updates: Partial<Agent>) => void;
  /** 设置 Agent 实时状态 */
  setAgentStates: (states: AgentState[]) => void;
  /** 更新单个 Agent 状态 */
  updateAgentState: (agentId: string, updates: Partial<AgentState>) => void;
  /** 设置工作流 */
  setWorkflow: (workflow: Workflow | null) => void;
  /** 设置加载状态 */
  setLoading: (isLoading: boolean) => void;
  /** 设置错误 */
  setError: (error: string | null) => void;
  /** 选中 Agent */
  selectAgent: (id: string | null) => void;
  /** 重置状态 */
  reset: () => void;
}

/**
 * Agent Store
 */
export const useAgentStore = create<AgentStoreState>()(
  devtools(
    (set, get) => ({
      // ==========================================
      // 初始状态
      // ==========================================
      agents: [],
      agentStates: [],
      workflow: null,
      isLoading: false,
      error: null,
      selectedAgentId: null,

      // ==========================================
      // Getters
      // ==========================================
      getAgentById: (id) => {
        return get().agents.find((a) => a.id === id);
      },

      getAgentByType: (type) => {
        return get().agents.find((a) => a.type === type);
      },

      getAgentState: (agentId) => {
        return get().agentStates.find((s) => s.id === agentId);
      },

      getSelectedAgent: () => {
        const { agents, selectedAgentId } = get();
        return agents.find((a) => a.id === selectedAgentId);
      },

      getActiveAgents: () => {
        const activeStatuses: AgentStatus[] = ['thinking', 'working', 'waiting'];
        return get().agentStates.filter((s) => activeStatuses.includes(s.status));
      },

      hasActiveAgents: () => {
        const activeStatuses: AgentStatus[] = ['thinking', 'working', 'waiting'];
        return get().agentStates.some((s) => activeStatuses.includes(s.status));
      },

      // ==========================================
      // Actions
      // ==========================================
      setAgents: (agents) => {
        set({ agents, error: null });
      },

      updateAgent: (id, updates) => {
        set((state) => ({
          agents: state.agents.map((a) =>
            a.id === id ? { ...a, ...updates, lastActiveAt: Date.now() } : a
          ),
        }));
      },

      setAgentStates: (states) => {
        set({ agentStates: states });
      },

      updateAgentState: (agentId, updates) => {
        set((state) => {
          const existingIndex = state.agentStates.findIndex((s) => s.id === agentId);
          let updatedStates: AgentState[];

          if (existingIndex >= 0) {
            updatedStates = [...state.agentStates];
            updatedStates[existingIndex] = { ...updatedStates[existingIndex], ...updates };
          } else {
            updatedStates = [
              ...state.agentStates,
              { id: agentId, type: 'planner', status: 'idle', ...updates } as AgentState,
            ];
          }

          return { agentStates: updatedStates };
        });
      },

      setWorkflow: (workflow) => {
        set({ workflow });
      },

      setLoading: (isLoading) => {
        set({ isLoading });
      },

      setError: (error) => {
        set({ error });
      },

      selectAgent: (id) => {
        set({ selectedAgentId: id });
      },

      reset: () => {
        set({
          agentStates: [],
          workflow: null,
          isLoading: false,
          error: null,
          selectedAgentId: null,
        });
      },
    }),
    { name: 'AgentStore' }
  )
);
