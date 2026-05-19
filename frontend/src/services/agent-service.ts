import type { Agent, AgentState, Workflow, AgentType } from '@/types';
import { agentApi } from '@/lib/api';

/**
 * Agent 服务层
 * 封装 Agent 管理相关的业务逻辑
 */

/** Agent 服务类 */
class AgentService {
  /**
   * 获取所有 Agent 列表
   */
  async getAgents(): Promise<Agent[]> {
    try {
      const response = await agentApi.list();
      if (response.success && response.data) {
        return response.data;
      }
      return [];
    } catch (error) {
      console.error('[AgentService] Failed to fetch agents:', error);
      return this.getDefaultAgents();
    }
  }

  /**
   * 获取单个 Agent 详情
   */
  async getAgent(id: string): Promise<Agent | null> {
    try {
      const response = await agentApi.get(id);
      if (response.success && response.data) {
        return response.data;
      }
      return null;
    } catch (error) {
      console.error('[AgentService] Failed to fetch agent:', error);
      return null;
    }
  }

  /**
   * 更新 Agent 配置
   */
  async updateAgentConfig(
    id: string,
    config: Partial<Agent['config']>
  ): Promise<Agent | null> {
    try {
      const response = await agentApi.updateConfig(id, config);
      if (response.success && response.data) {
        return response.data;
      }
      return null;
    } catch (error) {
      console.error('[AgentService] Failed to update agent config:', error);
      return null;
    }
  }

  /**
   * 获取工作流状态
   */
  async getWorkflow(conversationId?: string): Promise<Workflow | null> {
    try {
      const response = await agentApi.getWorkflow(conversationId);
      if (response.success && response.data) {
        return response.data as Workflow;
      }
      return null;
    } catch (error) {
      console.error('[AgentService] Failed to fetch workflow:', error);
      return this.getDefaultWorkflow();
    }
  }

  /**
   * 获取默认 Agent 列表（后端不可用时使用）
   */
  getDefaultAgents(): Agent[] {
    const now = Date.now();
    return [
      {
        id: 'agent-planner',
        name: 'Planner',
        type: 'planner',
        description: '智能任务分解与规划 Agent，负责将复杂需求拆解为可执行的子任务',
        status: 'idle',
        config: {
          model: 'gpt-4',
          temperature: 0.7,
          maxTokens: 4096,
        },
        capabilities: ['任务分解', '需求分析', '执行规划', '依赖管理'],
        stats: {
          tasksCompleted: 0,
          totalTokensUsed: 0,
          averageResponseTime: 0,
        },
        createdAt: now,
        lastActiveAt: now,
      },
      {
        id: 'agent-researcher',
        name: 'Researcher',
        type: 'researcher',
        description: '深度信息检索与知识收集 Agent，为任务提供全面的信息支撑',
        status: 'idle',
        config: {
          model: 'gpt-4',
          temperature: 0.5,
          maxTokens: 4096,
        },
        capabilities: ['信息检索', '知识收集', '数据分析', '来源验证'],
        stats: {
          tasksCompleted: 0,
          totalTokensUsed: 0,
          averageResponseTime: 0,
        },
        createdAt: now,
        lastActiveAt: now,
      },
      {
        id: 'agent-coder',
        name: 'Coder',
        type: 'coder',
        description: '高质量代码生成与实现 Agent，支持多种编程语言和框架',
        status: 'idle',
        config: {
          model: 'gpt-4',
          temperature: 0.3,
          maxTokens: 8192,
        },
        capabilities: ['代码生成', '代码重构', 'Bug 修复', '单元测试'],
        stats: {
          tasksCompleted: 0,
          totalTokensUsed: 0,
          averageResponseTime: 0,
        },
        createdAt: now,
        lastActiveAt: now,
      },
      {
        id: 'agent-reviewer',
        name: 'Reviewer',
        type: 'reviewer',
        description: '严格的代码审查与质量把控 Agent，确保输出符合最佳实践',
        status: 'idle',
        config: {
          model: 'gpt-4',
          temperature: 0.2,
          maxTokens: 4096,
        },
        capabilities: ['代码审查', '质量评估', '安全检查', '性能分析'],
        stats: {
          tasksCompleted: 0,
          totalTokensUsed: 0,
          averageResponseTime: 0,
        },
        createdAt: now,
        lastActiveAt: now,
      },
      {
        id: 'agent-summarizer',
        name: 'Summarizer',
        type: 'summarizer',
        description: '智能总结与报告生成 Agent，将复杂结果提炼为清晰摘要',
        status: 'idle',
        config: {
          model: 'gpt-4',
          temperature: 0.5,
          maxTokens: 4096,
        },
        capabilities: ['内容总结', '报告生成', '关键点提取', '格式化输出'],
        stats: {
          tasksCompleted: 0,
          totalTokensUsed: 0,
          averageResponseTime: 0,
        },
        createdAt: now,
        lastActiveAt: now,
      },
    ];
  }

  /**
   * 获取默认工作流（后端不可用时使用）
   */
  getDefaultWorkflow(): Workflow {
    const agentTypes: AgentType[] = [
      'planner',
      'researcher',
      'coder',
      'reviewer',
      'summarizer',
    ];

    const nodes = agentTypes.map((type, index) => ({
      id: `agent-${type}`,
      agentId: `agent-${type}`,
      agentType: type,
      status: 'idle' as const,
      position: {
        x: index * 200,
        y: 100,
      },
    }));

    const edges = agentTypes.slice(0, -1).map((type, index) => ({
      id: `edge-${type}-${agentTypes[index + 1]}`,
      source: `agent-${type}`,
      target: `agent-${agentTypes[index + 1]}`,
    }));

    return { nodes, edges };
  }

  /**
   * 根据 Agent 类型列表生成 Agent 状态
   */
  createAgentStates(types: AgentType[]): AgentState[] {
    return types.map((type) => ({
      id: `agent-${type}`,
      type,
      status: 'idle',
    }));
  }
}

/** Agent 服务单例 */
export const agentService = new AgentService();
export default agentService;
