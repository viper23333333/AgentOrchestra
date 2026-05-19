/* ===========================================
   AgentOrchestra 前端类型定义
   =========================================== */

// ==========================================
// 消息相关类型
// ==========================================

/** 消息角色 */
export type MessageRole = 'user' | 'assistant' | 'system' | 'agent';

/** 消息状态 */
export type MessageStatus = 'sending' | 'streaming' | 'sent' | 'error';

/** 消息内容块 - 支持多模态 */
export interface MessageContent {
  type: 'text' | 'code' | 'image' | 'thinking';
  text?: string;
  language?: string;
  url?: string;
}

/** 消息实体 */
export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  /** 结构化内容块（可选） */
  contentBlocks?: MessageContent[];
  /** 发送者信息 */
  sender?: {
    id: string;
    name: string;
    avatar?: string;
    agentType?: AgentType;
  };
  /** 时间戳 */
  timestamp: number;
  /** 消息状态 */
  status: MessageStatus;
  /** 关联的 Agent ID */
  agentId?: string;
  /** 关联的任务 ID */
  taskId?: string;
  /** Token 使用统计 */
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  /** 元数据 */
  metadata?: Record<string, unknown>;
}

// ==========================================
// Agent 相关类型
// ==========================================

/** Agent 类型枚举 */
export type AgentType = 'planner' | 'researcher' | 'coder' | 'reviewer' | 'summarizer';

/** Agent 状态 */
export type AgentStatus = 'idle' | 'thinking' | 'working' | 'waiting' | 'completed' | 'error';

/** Agent 配置 */
export interface AgentConfig {
  model: string;
  temperature: number;
  maxTokens: number;
  systemPrompt?: string;
  tools?: string[];
}

/** Agent 实体 */
export interface Agent {
  id: string;
  name: string;
  type: AgentType;
  description: string;
  status: AgentStatus;
  config: AgentConfig;
  /** Agent 能力标签 */
  capabilities: string[];
  /** 当前正在处理的任务 */
  currentTaskId?: string;
  /** 统计信息 */
  stats: {
    tasksCompleted: number;
    totalTokensUsed: number;
    averageResponseTime: number;
  };
  /** 创建时间 */
  createdAt: number;
  /** 最后活跃时间 */
  lastActiveAt: number;
}

/** Agent 状态信息（轻量级，用于实时更新） */
export interface AgentState {
  id: string;
  type: AgentType;
  status: AgentStatus;
  currentTaskId?: string;
  progress?: number;
  message?: string;
}

// ==========================================
// 任务相关类型
// ==========================================

/** 任务状态 */
export type TaskStatus = 'pending' | 'assigned' | 'in_progress' | 'completed' | 'failed' | 'cancelled';

/** 任务优先级 */
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

/** 任务实体 */
export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  /** 分配的 Agent ID */
  assignedAgentId?: string;
  /** 父任务 ID（子任务关系） */
  parentId?: string;
  /** 子任务 ID 列表 */
  subtaskIds?: string[];
  /** 依赖任务 ID 列表 */
  dependencies?: string[];
  /** 任务输入 */
  input?: Record<string, unknown>;
  /** 任务输出 */
  output?: Record<string, unknown>;
  /** 执行时间统计 */
  timing?: {
    startedAt?: number;
    completedAt?: number;
    duration?: number;
  };
  /** 关联消息 ID */
  messageId?: string;
  /** 创建时间 */
  createdAt: number;
  /** 更新时间 */
  updatedAt: number;
}

// ==========================================
// 对话相关类型
// ==========================================

/** 对话实体 */
export interface Conversation {
  id: string;
  title: string;
  /** 对话摘要 */
  summary?: string;
  /** 消息列表 */
  messages: Message[];
  /** 参与的 Agent 列表 */
  agents: AgentState[];
  /** 任务列表 */
  tasks: Task[];
  /** 对话配置 */
  config: ConversationConfig;
  /** 创建时间 */
  createdAt: number;
  /** 最后更新时间 */
  updatedAt: number;
}

/** 对话配置 */
export interface ConversationConfig {
  /** 使用的 LLM 模型 */
  model: string;
  /** 温度参数 */
  temperature: number;
  /** 最大 Token 数 */
  maxTokens: number;
  /** 启用的 Agent 类型 */
  enabledAgents: AgentType[];
  /** 是否自动执行 */
  autoExecute: boolean;
  /** 流式输出 */
  stream: boolean;
}

// ==========================================
// 工作流相关类型
// ==========================================

/** 工作流节点 */
export interface WorkflowNode {
  id: string;
  agentId: string;
  agentType: AgentType;
  status: AgentStatus;
  position: { x: number; y: number };
}

/** 工作流连线 */
export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

/** 工作流 */
export interface Workflow {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

// ==========================================
// API 相关类型
// ==========================================

/** API 通用响应 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  message?: string;
}

/** API 错误 */
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

/** 分页参数 */
export interface PaginationParams {
  page: number;
  pageSize: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

/** 分页响应 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// ==========================================
// WebSocket 相关类型
// ==========================================

/** WebSocket 消息类型 */
export type WSMessageType =
  | 'message'
  | 'message_stream'
  | 'agent_status'
  | 'task_update'
  | 'workflow_update'
  | 'error'
  | 'pong';

/** WebSocket 消息 */
export interface WSMessage<T = unknown> {
  type: WSMessageType;
  payload: T;
  timestamp: number;
  conversationId?: string;
}

/** Agent 状态更新事件 */
export interface AgentStatusEvent {
  agentId: string;
  status: AgentStatus;
  message?: string;
  progress?: number;
}

/** 消息流式事件 */
export interface MessageStreamEvent {
  messageId: string;
  content: string;
  isComplete: boolean;
  agentId?: string;
}

// ==========================================
// SSE 相关类型
// ==========================================

/** SSE 事件类型 */
export type SSEEventType =
  | 'token'
  | 'message_complete'
  | 'agent_status_change'
  | 'task_status_change'
  | 'error';

/** SSE 事件 */
export interface SSEEvent<T = unknown> {
  event: SSEEventType;
  data: T;
}

// ==========================================
// UI 相关类型
// ==========================================

/** 主题模式 */
export type ThemeMode = 'light' | 'dark' | 'system';

/** 侧边栏状态 */
export type SidebarState = 'expanded' | 'collapsed' | 'mobile-hidden';

/** 通知类型 */
export type NotificationType = 'info' | 'success' | 'warning' | 'error';

/** 通知 */
export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: number;
  dismissed?: boolean;
}

/** 模型选项 */
export interface ModelOption {
  id: string;
  name: string;
  provider: string;
  description?: string;
  maxTokens: number;
  supportsStreaming: boolean;
}

// ==========================================
// Store 相关类型
// ==========================================

/** 聊天 Store 状态 */
export interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  isLoading: boolean;
  error: string | null;
}

/** Agent Store 状态 */
export interface AgentStoreState {
  agents: Agent[];
  workflow: Workflow | null;
  isLoading: boolean;
  error: string | null;
}

// ==========================================
// 常量
// ==========================================

/** Agent 类型到中文名称的映射 */
export const AGENT_TYPE_LABELS: Record<AgentType, string> = {
  planner: '规划者',
  researcher: '研究者',
  coder: '编码者',
  reviewer: '审查者',
  summarizer: '总结者',
};

/** Agent 类型到颜色的映射 */
export const AGENT_TYPE_COLORS: Record<AgentType, string> = {
  planner: '#6366f1',
  researcher: '#8b5cf6',
  coder: '#06b6d4',
  reviewer: '#f59e0b',
  summarizer: '#10b981',
};

/** Agent 状态到中文名称的映射 */
export const AGENT_STATUS_LABELS: Record<AgentStatus, string> = {
  idle: '空闲',
  thinking: '思考中',
  working: '工作中',
  waiting: '等待中',
  completed: '已完成',
  error: '错误',
};

/** 任务状态到中文名称的映射 */
export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  pending: '待处理',
  assigned: '已分配',
  in_progress: '进行中',
  completed: '已完成',
  failed: '已失败',
  cancelled: '已取消',
};

/** 可用的 LLM 模型列表 */
export const AVAILABLE_MODELS: ModelOption[] = [
  {
    id: 'gpt-4',
    name: 'GPT-4',
    provider: 'OpenAI',
    description: '最强大的推理模型，适合复杂任务',
    maxTokens: 8192,
    supportsStreaming: true,
  },
  {
    id: 'gpt-4-turbo',
    name: 'GPT-4 Turbo',
    provider: 'OpenAI',
    description: '更快的 GPT-4，支持 128K 上下文',
    maxTokens: 4096,
    supportsStreaming: true,
  },
  {
    id: 'gpt-3.5-turbo',
    name: 'GPT-3.5 Turbo',
    provider: 'OpenAI',
    description: '快速高效的模型，适合简单任务',
    maxTokens: 4096,
    supportsStreaming: true,
  },
  {
    id: 'claude-3-opus',
    name: 'Claude 3 Opus',
    provider: 'Anthropic',
    description: 'Anthropic 最强大的模型',
    maxTokens: 4096,
    supportsStreaming: true,
  },
  {
    id: 'claude-3-sonnet',
    name: 'Claude 3 Sonnet',
    provider: 'Anthropic',
    description: '平衡性能和速度的模型',
    maxTokens: 4096,
    supportsStreaming: true,
  },
];
