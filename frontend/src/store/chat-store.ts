import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type {
  Conversation,
  Message,
  AgentState,
  Task,
  ConversationConfig,
  AgentType,
} from '@/types';
import { generateId, generateConversationTitle } from '@/lib/utils';

/**
 * 聊天状态管理 Store
 * 使用 Zustand 管理对话、消息和聊天相关状态
 * - 支持持久化（localStorage）
 * - 支持开发工具调试
 */

/** 聊天 Store 状态接口 */
interface ChatStoreState {
  // ==========================================
  // 状态
  // ==========================================

  /** 对话列表 */
  conversations: Conversation[];
  /** 当前激活的对话 ID */
  activeConversationId: string | null;
  /** 是否正在加载 */
  isLoading: boolean;
  /** 是否正在发送消息 */
  isSending: boolean;
  /** 错误信息 */
  error: string | null;
  /** 当前正在输入的 Agent ID 列表 */
  typingAgentIds: string[];

  // ==========================================
  // 计算属性（Getters）
  // ==========================================

  /** 获取当前激活的对话 */
  getActiveConversation: () => Conversation | null;
  /** 获取当前对话的消息列表 */
  getActiveMessages: () => Message[];
  /** 获取当前对话的 Agent 状态列表 */
  getActiveAgents: () => AgentState[];

  // ==========================================
  // Actions
  // ==========================================

  /** 创建新对话 */
  createConversation: (config?: Partial<ConversationConfig>) => string;
  /** 删除对话 */
  deleteConversation: (id: string) => void;
  /** 切换激活的对话 */
  setActiveConversation: (id: string | null) => void;
  /** 更新对话标题 */
  updateConversationTitle: (id: string, title: string) => void;
  /** 更新对话配置 */
  updateConversationConfig: (id: string, config: Partial<ConversationConfig>) => void;

  /** 添加消息到对话 */
  addMessage: (conversationId: string, message: Message) => void;
  /** 更新消息内容（用于流式更新） */
  updateMessage: (conversationId: string, messageId: string, updates: Partial<Message>) => void;
  /** 追加消息内容（流式） */
  appendMessageContent: (conversationId: string, messageId: string, content: string) => void;
  /** 删除消息 */
  deleteMessage: (conversationId: string, messageId: string) => void;

  /** 更新 Agent 状态 */
  updateAgentState: (conversationId: string, agentState: AgentState) => void;
  /** 添加/更新任务 */
  upsertTask: (conversationId: string, task: Task) => void;

  /** 设置加载状态 */
  setLoading: (isLoading: boolean) => void;
  /** 设置发送状态 */
  setSending: (isSending: boolean) => void;
  /** 设置错误 */
  setError: (error: string | null) => void;

  /** 添加正在输入的 Agent */
  addTypingAgent: (agentId: string) => void;
  /** 移除正在输入的 Agent */
  removeTypingAgent: (agentId: string) => void;
  /** 清空正在输入的 Agent 列表 */
  clearTypingAgents: () => void;

  /** 清空所有状态 */
  reset: () => void;
}

/** 默认对话配置 */
const DEFAULT_CONVERSATION_CONFIG: ConversationConfig = {
  model: process.env.NEXT_PUBLIC_DEFAULT_MODEL || 'gpt-4',
  temperature: 0.7,
  maxTokens: 4096,
  enabledAgents: ['planner', 'researcher', 'coder', 'reviewer', 'summarizer'] as AgentType[],
  autoExecute: true,
  stream: true,
};

/**
 * 聊天 Store
 */
export const useChatStore = create<ChatStoreState>()(
  devtools(
    persist(
      (set, get) => ({
        // ==========================================
        // 初始状态
        // ==========================================
        conversations: [],
        activeConversationId: null,
        isLoading: false,
        isSending: false,
        error: null,
        typingAgentIds: [],

        // ==========================================
        // Getters
        // ==========================================
        getActiveConversation: () => {
          const { conversations, activeConversationId } = get();
          return conversations.find((c) => c.id === activeConversationId) || null;
        },

        getActiveMessages: () => {
          const conversation = get().getActiveConversation();
          return conversation?.messages || [];
        },

        getActiveAgents: () => {
          const conversation = get().getActiveConversation();
          return conversation?.agents || [];
        },

        // ==========================================
        // 对话 Actions
        // ==========================================
        createConversation: (config) => {
          const id = generateId();
          const now = Date.now();

          const newConversation: Conversation = {
            id,
            title: '新对话',
            messages: [],
            agents: [],
            tasks: [],
            config: { ...DEFAULT_CONVERSATION_CONFIG, ...config },
            createdAt: now,
            updatedAt: now,
          };

          set((state) => ({
            conversations: [newConversation, ...state.conversations],
            activeConversationId: id,
            error: null,
          }));

          return id;
        },

        deleteConversation: (id) => {
          set((state) => ({
            conversations: state.conversations.filter((c) => c.id !== id),
            activeConversationId:
              state.activeConversationId === id ? null : state.activeConversationId,
          }));
        },

        setActiveConversation: (id) => {
          set({ activeConversationId: id, error: null });
        },

        updateConversationTitle: (id, title) => {
          set((state) => ({
            conversations: state.conversations.map((c) =>
              c.id === id ? { ...c, title, updatedAt: Date.now() } : c
            ),
          }));
        },

        updateConversationConfig: (id, config) => {
          set((state) => ({
            conversations: state.conversations.map((c) =>
              c.id === id
                ? { ...c, config: { ...c.config, ...config }, updatedAt: Date.now() }
                : c
            ),
          }));
        },

        // ==========================================
        // 消息 Actions
        // ==========================================
        addMessage: (conversationId, message) => {
          set((state) => ({
            conversations: state.conversations.map((c) => {
              if (c.id !== conversationId) return c;

              const updatedMessages = [...c.messages, message];

              // 如果是第一条用户消息，自动生成标题
              let title = c.title;
              if (message.role === 'user' && c.messages.length === 0) {
                title = generateConversationTitle(message.content);
              }

              return {
                ...c,
                messages: updatedMessages,
                title,
                updatedAt: Date.now(),
              };
            }),
          }));
        },

        updateMessage: (conversationId, messageId, updates) => {
          set((state) => ({
            conversations: state.conversations.map((c) => {
              if (c.id !== conversationId) return c;

              return {
                ...c,
                messages: c.messages.map((m) =>
                  m.id === messageId ? { ...m, ...updates } : m
                ),
                updatedAt: Date.now(),
              };
            }),
          }));
        },

        appendMessageContent: (conversationId, messageId, content) => {
          set((state) => ({
            conversations: state.conversations.map((c) => {
              if (c.id !== conversationId) return c;

              return {
                ...c,
                messages: c.messages.map((m) =>
                  m.id === messageId
                    ? { ...m, content: m.content + content }
                    : m
                ),
                updatedAt: Date.now(),
              };
            }),
          }));
        },

        deleteMessage: (conversationId, messageId) => {
          set((state) => ({
            conversations: state.conversations.map((c) => {
              if (c.id !== conversationId) return c;
              return {
                ...c,
                messages: c.messages.filter((m) => m.id !== messageId),
                updatedAt: Date.now(),
              };
            }),
          }));
        },

        // ==========================================
        // Agent 状态 Actions
        // ==========================================
        updateAgentState: (conversationId, agentState) => {
          set((state) => ({
            conversations: state.conversations.map((c) => {
              if (c.id !== conversationId) return c;

              const existingIndex = c.agents.findIndex((a) => a.id === agentState.id);
              let updatedAgents: AgentState[];

              if (existingIndex >= 0) {
                updatedAgents = [...c.agents];
                updatedAgents[existingIndex] = { ...updatedAgents[existingIndex], ...agentState };
              } else {
                updatedAgents = [...c.agents, agentState];
              }

              return { ...c, agents: updatedAgents, updatedAt: Date.now() };
            }),
          }));
        },

        // ==========================================
        // 任务 Actions
        // ==========================================
        upsertTask: (conversationId, task) => {
          set((state) => ({
            conversations: state.conversations.map((c) => {
              if (c.id !== conversationId) return c;

              const existingIndex = c.tasks.findIndex((t) => t.id === task.id);
              let updatedTasks: Task[];

              if (existingIndex >= 0) {
                updatedTasks = [...c.tasks];
                updatedTasks[existingIndex] = { ...updatedTasks[existingIndex], ...task };
              } else {
                updatedTasks = [...c.tasks, task];
              }

              return { ...c, tasks: updatedTasks, updatedAt: Date.now() };
            }),
          }));
        },

        // ==========================================
        // UI 状态 Actions
        // ==========================================
        setLoading: (isLoading) => set({ isLoading }),
        setSending: (isSending) => set({ isSending }),
        setError: (error) => set({ error }),

        addTypingAgent: (agentId) => {
          set((state) => ({
            typingAgentIds: state.typingAgentIds.includes(agentId)
              ? state.typingAgentIds
              : [...state.typingAgentIds, agentId],
          }));
        },

        removeTypingAgent: (agentId) => {
          set((state) => ({
            typingAgentIds: state.typingAgentIds.filter((id) => id !== agentId),
          }));
        },

        clearTypingAgents: () => set({ typingAgentIds: [] }),

        // ==========================================
        // 重置
        // ==========================================
        reset: () =>
          set({
            conversations: [],
            activeConversationId: null,
            isLoading: false,
            isSending: false,
            error: null,
            typingAgentIds: [],
          }),
      }),
      {
        name: 'agent-orchestra-chat',
        // 只持久化对话数据，不持久化 UI 状态
        partialize: (state) => ({
          conversations: state.conversations,
          activeConversationId: state.activeConversationId,
        }),
      }
    ),
    { name: 'ChatStore' }
  )
);
