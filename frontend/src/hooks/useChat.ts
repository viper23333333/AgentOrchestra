'use client';

import { useCallback, useRef, useEffect } from 'react';
import { useChatStore } from '@/store/chat-store';
import { useAgentStore } from '@/store/agent-store';
import { chatService } from '@/services/chat-service';
import { generateId } from '@/lib/utils';
import type { Message, ConversationConfig, AgentState } from '@/types';

/**
 * 聊天 Hook
 * 封装消息发送、接收、流式处理等聊天核心功能
 * - 管理对话生命周期
 * - 处理消息发送和接收
 * - 支持流式响应
 * - 自动管理 Agent 状态
 */

/** useChat Hook 返回值 */
interface UseChatReturn {
  /** 当前激活的对话 ID */
  activeConversationId: string | null;
  /** 消息列表 */
  messages: Message[];
  /** 是否正在发送 */
  isSending: boolean;
  /** 是否正在加载 */
  isLoading: boolean;
  /** 错误信息 */
  error: string | null;
  /** 当前正在输入的 Agent ID 列表 */
  typingAgentIds: string[];
  /** 发送消息 */
  sendMessage: (content: string) => Promise<void>;
  /** 创建新对话 */
  createNewConversation: (config?: Partial<ConversationConfig>) => string;
  /** 停止生成 */
  stopGeneration: () => void;
  /** 清除错误 */
  clearError: () => void;
}

/**
 * 聊天 Hook
 */
export function useChat(): UseChatReturn {
  const {
    activeConversationId,
    isSending,
    isLoading,
    error,
    typingAgentIds,
    createConversation,
    addMessage,
    updateMessage,
    appendMessageContent,
    setSending,
    setError,
    addTypingAgent,
    removeTypingAgent,
    clearTypingAgents,
    updateAgentState,
    getActiveMessages,
    getActiveConversation,
  } = useChatStore();

  const { updateAgentState: updateGlobalAgentState } = useAgentStore();

  /** 用于取消流式请求的 AbortController */
  const abortControllerRef = useRef<AbortController | null>(null);

  /** 当前激活对话的消息列表 */
  const messages = getActiveMessages();

  /**
   * 创建新对话
   */
  const handleCreateConversation = useCallback(
    (config?: Partial<ConversationConfig>): string => {
      const id = createConversation(config);
      return id;
    },
    [createConversation]
  );

  /**
   * 发送消息
   */
  const handleSendMessage = useCallback(
    async (content: string) => {
      // 验证输入
      if (!content.trim()) return;

      // 获取或创建对话
      let conversationId = activeConversationId;
      if (!conversationId) {
        conversationId = handleCreateConversation();
      }

      const conversation = getActiveConversation();
      if (!conversation) return;

      // 创建用户消息
      const userMessage: Message = {
        id: generateId(),
        role: 'user',
        content: content.trim(),
        timestamp: Date.now(),
        status: 'sent',
      };

      // 添加用户消息到 store
      addMessage(conversationId, userMessage);

      // 创建 Agent 占位消息（用于流式填充）
      const assistantMessageId = generateId();
      const assistantMessage: Message = {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
        status: 'streaming',
        sender: {
          id: 'orchestrator',
          name: 'AgentOrchestra',
          agentType: 'planner',
        },
      };

      addMessage(conversationId, assistantMessage);
      setSending(true);
      setError(null);

      try {
        // 使用流式模式发送消息
        const controller = chatService.sendMessageStream(
          { conversationId, content: content.trim(), stream: true },
          {
            onToken: (_messageId, token) => {
              appendMessageContent(conversationId, assistantMessageId, token);
            },

            onComplete: (_messageId, fullContent) => {
              updateMessage(conversationId, assistantMessageId, {
                status: 'sent',
                content: fullContent,
              });
              setSending(false);
              clearTypingAgents();
            },

            onAgentStatus: (agentId, status, message) => {
              const agentState: AgentState = {
                id: agentId,
                type: agentId.includes('planner')
                  ? 'planner'
                  : agentId.includes('researcher')
                    ? 'researcher'
                    : agentId.includes('coder')
                      ? 'coder'
                      : agentId.includes('reviewer')
                        ? 'reviewer'
                        : 'summarizer',
                status: status as AgentState['status'],
                message,
              };

              // 更新聊天 store 中的 Agent 状态
              updateAgentState(conversationId, agentState);

              // 更新全局 Agent store
              updateGlobalAgentState(agentId, {
                status: status as AgentState['status'],
                message,
              });

              // 管理正在输入的 Agent 列表
              if (status === 'working' || status === 'thinking') {
                addTypingAgent(agentId);
              } else {
                removeTypingAgent(agentId);
              }
            },

            onError: (errorMessage) => {
              updateMessage(conversationId, assistantMessageId, {
                status: 'error',
                content: `抱歉，处理过程中出现错误：${errorMessage}`,
              });
              setSending(false);
              clearTypingAgents();
              setError(errorMessage);
            },
          }
        );

        // 保存 AbortController 用于取消
        abortControllerRef.current = controller;
      } catch (error) {
        console.error('[useChat] Send message error:', error);
        updateMessage(conversationId, assistantMessageId, {
          status: 'error',
          content: '发送消息失败，请检查网络连接后重试。',
        });
        setSending(false);
        setError('发送消息失败');
      }
    },
    [
      activeConversationId,
      handleCreateConversation,
      getActiveConversation,
      addMessage,
      updateMessage,
      appendMessageContent,
      setSending,
      setError,
      updateAgentState,
      updateGlobalAgentState,
      addTypingAgent,
      removeTypingAgent,
      clearTypingAgents,
    ]
  );

  /**
   * 停止生成
   */
  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    if (activeConversationId) {
      const messages = getActiveMessages();
      const lastMessage = messages[messages.length - 1];
      if (lastMessage && lastMessage.status === 'streaming') {
        updateMessage(activeConversationId, lastMessage.id, {
          status: 'sent',
        });
      }
    }

    setSending(false);
    clearTypingAgents();
  }, [activeConversationId, getActiveMessages, updateMessage, setSending, clearTypingAgents]);

  /**
   * 清除错误
   */
  const clearError = useCallback(() => {
    setError(null);
  }, [setError]);

  /**
   * 组件卸载时清理
   */
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    activeConversationId,
    messages,
    isSending,
    isLoading,
    error,
    typingAgentIds,
    sendMessage: handleSendMessage,
    createNewConversation: handleCreateConversation,
    stopGeneration,
    clearError,
  };
}

export default useChat;
