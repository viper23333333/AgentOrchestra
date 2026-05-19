import type {
  Conversation,
  ConversationConfig,
  Task,
} from '@/types';
import { conversationApi, taskApi } from '@/lib/api';
import { generateId } from '@/lib/utils';

/**
 * 聊天服务层
 * 封装聊天相关的业务逻辑，连接 API 层和 Store 层
 */

/** 发送消息的请求参数 */
export interface SendMessageParams {
  conversationId: string;
  content: string;
  stream?: boolean;
}

/** 发送消息的响应 */
export interface SendMessageResult {
  success: boolean;
  messageId?: string;
  error?: string;
}

/**
 * 聊天服务类
 */
class ChatService {
  /**
   * 创建新对话
   */
  async createConversation(config?: Partial<ConversationConfig>): Promise<Conversation> {
    try {
      const response = await conversationApi.create(config);
      if (response.success && response.data) {
        return response.data;
      }
      throw new Error(response.error?.message || '创建对话失败');
    } catch (error) {
      // 如果后端不可用，创建本地对话
      console.warn('[ChatService] Backend unavailable, creating local conversation');
      const now = Date.now();
      return {
        id: generateId(),
        title: '新对话',
        messages: [],
        agents: [],
        tasks: [],
        config: {
          model: process.env.NEXT_PUBLIC_DEFAULT_MODEL || 'gpt-4',
          temperature: 0.7,
          maxTokens: 4096,
          enabledAgents: ['planner', 'researcher', 'coder', 'reviewer', 'summarizer'],
          autoExecute: true,
          stream: true,
          ...config,
        },
        createdAt: now,
        updatedAt: now,
      };
    }
  }

  /**
   * 获取对话列表
   */
  async getConversations(): Promise<Conversation[]> {
    try {
      const response = await conversationApi.list({ page: 1, pageSize: 50 });
      if (response.success && response.data) {
        return response.data.items;
      }
      return [];
    } catch (error) {
      console.error('[ChatService] Failed to fetch conversations:', error);
      return [];
    }
  }

  /**
   * 获取对话详情
   */
  async getConversation(id: string): Promise<Conversation | null> {
    try {
      const response = await conversationApi.get(id);
      if (response.success && response.data) {
        return response.data;
      }
      return null;
    } catch (error) {
      console.error('[ChatService] Failed to fetch conversation:', error);
      return null;
    }
  }

  /**
   * 删除对话
   */
  async deleteConversation(id: string): Promise<boolean> {
    try {
      const response = await conversationApi.delete(id);
      return response.success;
    } catch (error) {
      console.error('[ChatService] Failed to delete conversation:', error);
      return false;
    }
  }

  /**
   * 发送消息（普通模式）
   */
  async sendMessage(params: SendMessageParams): Promise<SendMessageResult> {
    try {
      const response = await conversationApi.sendMessage(
        params.conversationId,
        params.content
      );

      if (response.success && response.data) {
        return { success: true, messageId: response.data.id };
      }

      return { success: false, error: response.error?.message || '发送消息失败' };
    } catch (error) {
      console.error('[ChatService] Failed to send message:', error);
      return { success: false, error: '网络错误，请稍后重试' };
    }
  }

  /**
   * 发送消息（流式模式）
   * 使用 Server-Sent Events (SSE) 接收流式响应
   *
   * @param params - 发送参数
   * @param onToken - 接收到 token 时的回调
   * @param onComplete - 消息完成时的回调
   * @param onAgentStatus - Agent 状态变化时的回调
   * @param onError - 错误回调
   * @returns AbortController，用于取消请求
   */
  sendMessageStream(
    params: SendMessageParams,
    callbacks: {
      onToken?: (messageId: string, token: string) => void;
      onComplete?: (messageId: string, fullContent: string) => void;
      onAgentStatus?: (agentId: string, status: string, message?: string) => void;
      onError?: (error: string) => void;
    }
  ): AbortController {
    const controller = new AbortController();
    const { conversationId, content } = params;

    // 使用 fetch API 发送流式请求
    const apiBaseUrl =
      process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

    fetch(`${apiBaseUrl}/api/v1/conversations/${conversationId}/messages/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
      },
      body: JSON.stringify({ content, role: 'user' }),
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error('No response body');

        const decoder = new TextDecoder();
        let buffer = '';
        let currentMessageId = '';
        let fullContent = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // 解析 SSE 事件
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          let currentEvent = '';
          let currentData = '';

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              currentEvent = line.slice(7).trim();
            } else if (line.startsWith('data: ')) {
              currentData = line.slice(6);
            } else if (line === '' && currentEvent && currentData) {
              // 空行表示事件结束
              const parsedData = JSON.parse(currentData);

              switch (currentEvent) {
                case 'token':
                  currentMessageId = parsedData.message_id || currentMessageId;
                  fullContent += parsedData.content || '';
                  callbacks.onToken?.(currentMessageId, parsedData.content || '');
                  break;

                case 'message_complete':
                  callbacks.onComplete?.(
                    parsedData.message_id,
                    parsedData.content || fullContent
                  );
                  break;

                case 'agent_status_change':
                  callbacks.onAgentStatus?.(
                    parsedData.agent_id,
                    parsedData.status,
                    parsedData.message
                  );
                  break;

                case 'error':
                  callbacks.onError?.(parsedData.message || '未知错误');
                  break;
              }

              currentEvent = '';
              currentData = '';
            }
          }
        }
      })
      .catch((error) => {
        if (error.name !== 'AbortError') {
          console.error('[ChatService] Stream error:', error);
          callbacks.onError?.(error.message || '流式请求失败');
        }
      });

    return controller;
  }

  /**
   * 获取对话的任务列表
   */
  async getTasks(conversationId: string): Promise<Task[]> {
    try {
      const response = await taskApi.list(conversationId);
      if (response.success && response.data) {
        return response.data;
      }
      return [];
    } catch (error) {
      console.error('[ChatService] Failed to fetch tasks:', error);
      return [];
    }
  }
}

/** 聊天服务单例 */
export const chatService = new ChatService();
export default chatService;
