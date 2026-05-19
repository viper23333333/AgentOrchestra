'use client';

import { motion } from 'framer-motion';
import {
  Bot,
  Brain,
  Code2,
  Search,
  FileCheck,
  FileText,
  ArrowRight,
  Sparkles,
  Zap,
  Shield,
} from 'lucide-react';

/**
 * Agent 功能介绍数据
 */
const AGENT_FEATURES = [
  {
    icon: Brain,
    name: 'Planner',
    color: 'text-agent-planner',
    bgColor: 'bg-agent-planner/10',
    borderColor: 'border-agent-planner/20',
    description: '智能任务分解与规划，将复杂需求拆解为可执行的子任务',
  },
  {
    icon: Search,
    name: 'Researcher',
    color: 'text-agent-researcher',
    bgColor: 'bg-agent-researcher/10',
    borderColor: 'border-agent-researcher/20',
    description: '深度信息检索与知识收集，为任务提供全面的信息支撑',
  },
  {
    icon: Code2,
    name: 'Coder',
    color: 'text-agent-coder',
    bgColor: 'bg-agent-coder/10',
    borderColor: 'border-agent-coder/20',
    description: '高质量代码生成与实现，支持多种编程语言和框架',
  },
  {
    icon: FileCheck,
    name: 'Reviewer',
    color: 'text-agent-reviewer',
    bgColor: 'bg-agent-reviewer/10',
    borderColor: 'border-agent-reviewer/20',
    description: '严格的代码审查与质量把控，确保输出符合最佳实践',
  },
  {
    icon: FileText,
    name: 'Summarizer',
    color: 'text-agent-summarizer',
    bgColor: 'bg-agent-summarizer/10',
    borderColor: 'border-agent-summarizer/20',
    description: '智能总结与报告生成，将复杂结果提炼为清晰摘要',
  },
];

/**
 * 平台特性数据
 */
const PLATFORM_FEATURES = [
  {
    icon: Zap,
    title: '实时协作',
    description: '多 Agent 并行工作，实时同步状态，高效完成复杂任务',
  },
  {
    icon: Shield,
    title: '质量保障',
    description: '内置审查机制，每一步输出都经过严格的质量检查',
  },
  {
    icon: Sparkles,
    title: '智能编排',
    description: '自动选择最优 Agent 组合和执行路径，最大化效率',
  },
];

/**
 * 动画容器变体
 */
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: 'easeOut' },
  },
};

/**
 * 首页组件
 * 展示 AgentOrchestra 项目介绍、Agent 能力和快速开始入口
 */
export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-surface-50 via-white to-surface-50 dark:from-surface-950 dark:via-surface-900 dark:to-surface-950">
      {/* 顶部导航 */}
      <header className="fixed top-0 left-0 right-0 z-50 glass">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold text-surface-900 dark:text-white">
                AgentOrchestra
              </span>
            </div>
            <div className="flex items-center gap-4">
              <a
                href="#features"
                className="text-sm text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-white transition-colors"
              >
                功能特性
              </a>
              <a
                href="#agents"
                className="text-sm text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-white transition-colors"
              >
                Agent 团队
              </a>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium rounded-lg transition-colors shadow-glow"
                onClick={() => (window.location.href = '/chat')}
              >
                开始使用
              </motion.button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero 区域 */}
      <main className="pt-16">
        <section className="relative overflow-hidden">
          {/* 背景装饰 */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-500/10 rounded-full blur-3xl" />
            <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-accent-500/5 rounded-full blur-3xl" />
          </div>

          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32 lg:py-40">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
              className="text-center max-w-4xl mx-auto"
            >
              {/* 标签 */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2, duration: 0.5 }}
                className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-50 dark:bg-primary-950/50 border border-primary-200 dark:border-primary-800 mb-8"
              >
                <Sparkles className="w-4 h-4 text-primary-500" />
                <span className="text-sm font-medium text-primary-700 dark:text-primary-300">
                  Multi-Agent Collaboration Platform
                </span>
              </motion.div>

              {/* 标题 */}
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-surface-900 dark:text-white mb-6">
                让 AI Agent 团队
                <br />
                <span className="gradient-text">协同解决复杂问题</span>
              </h1>

              {/* 副标题 */}
              <p className="text-lg sm:text-xl text-surface-600 dark:text-surface-400 max-w-2xl mx-auto mb-10 leading-relaxed">
                AgentOrchestra 编排多个专业化 AI Agent 协同工作，
                通过智能规划、研究、编码、审查和总结，高效完成复杂任务。
              </p>

              {/* CTA 按钮 */}
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full sm:w-auto px-8 py-3.5 bg-primary-500 hover:bg-primary-600 text-white font-semibold rounded-xl transition-colors shadow-lg shadow-primary-500/25 flex items-center justify-center gap-2"
                  onClick={() => (window.location.href = '/chat')}
                >
                  开始对话
                  <ArrowRight className="w-4 h-4" />
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full sm:w-auto px-8 py-3.5 bg-white dark:bg-surface-800 text-surface-700 dark:text-surface-300 font-semibold rounded-xl border border-surface-200 dark:border-surface-700 hover:border-surface-300 dark:hover:border-surface-600 transition-colors"
                  onClick={() =>
                    document.getElementById('agents')?.scrollIntoView({ behavior: 'smooth' })
                  }
                >
                  了解更多
                </motion.button>
              </div>
            </motion.div>
          </div>
        </section>

        {/* 平台特性 */}
        <section id="features" className="py-20 sm:py-28">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-3xl sm:text-4xl font-bold text-surface-900 dark:text-white mb-4">
                平台核心能力
              </h2>
              <p className="text-lg text-surface-600 dark:text-surface-400 max-w-2xl mx-auto">
                构建于先进的 Agent 编排架构，提供强大的多智能体协作能力
              </p>
            </motion.div>

            <motion.div
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              className="grid grid-cols-1 md:grid-cols-3 gap-8"
            >
              {PLATFORM_FEATURES.map((feature) => (
                <motion.div
                  key={feature.title}
                  variants={itemVariants}
                  className="group p-6 rounded-2xl bg-white dark:bg-surface-800/50 border border-surface-200 dark:border-surface-700/50 hover:border-primary-200 dark:hover:border-primary-800 transition-all card-hover"
                >
                  <div className="w-12 h-12 rounded-xl bg-primary-50 dark:bg-primary-950/50 flex items-center justify-center mb-4 group-hover:shadow-glow transition-shadow">
                    <feature.icon className="w-6 h-6 text-primary-500" />
                  </div>
                  <h3 className="text-lg font-semibold text-surface-900 dark:text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-surface-600 dark:text-surface-400 leading-relaxed">
                    {feature.description}
                  </p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Agent 团队介绍 */}
        <section id="agents" className="py-20 sm:py-28 bg-surface-100/50 dark:bg-surface-900/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-3xl sm:text-4xl font-bold text-surface-900 dark:text-white mb-4">
                专业化 Agent 团队
              </h2>
              <p className="text-lg text-surface-600 dark:text-surface-400 max-w-2xl mx-auto">
                每个 Agent 都经过专门训练，在各自领域拥有卓越能力
              </p>
            </motion.div>

            <motion.div
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {AGENT_FEATURES.map((agent) => (
                <motion.div
                  key={agent.name}
                  variants={itemVariants}
                  className={`group p-6 rounded-2xl bg-white dark:bg-surface-800/50 border ${agent.borderColor} hover:shadow-lg transition-all card-hover`}
                >
                  <div
                    className={`w-12 h-12 rounded-xl ${agent.bgColor} flex items-center justify-center mb-4`}
                  >
                    <agent.icon className={`w-6 h-6 ${agent.color}`} />
                  </div>
                  <h3 className={`text-lg font-semibold ${agent.color} mb-2`}>{agent.name}</h3>
                  <p className="text-surface-600 dark:text-surface-400 leading-relaxed text-sm">
                    {agent.description}
                  </p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* 底部 CTA */}
        <section className="py-20 sm:py-28">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl sm:text-4xl font-bold text-surface-900 dark:text-white mb-4">
                准备好体验多 Agent 协作了吗？
              </h2>
              <p className="text-lg text-surface-600 dark:text-surface-400 mb-8">
                立即开始，让专业 Agent 团队为您解决复杂问题
              </p>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-8 py-3.5 bg-primary-500 hover:bg-primary-600 text-white font-semibold rounded-xl transition-colors shadow-lg shadow-primary-500/25 inline-flex items-center gap-2"
                onClick={() => (window.location.href = '/chat')}
              >
                开始使用
                <ArrowRight className="w-4 h-4" />
              </motion.button>
            </motion.div>
          </div>
        </section>
      </main>

      {/* 页脚 */}
      <footer className="border-t border-surface-200 dark:border-surface-800 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Bot className="w-5 h-5 text-primary-500" />
              <span className="text-sm font-medium text-surface-600 dark:text-surface-400">
                AgentOrchestra
              </span>
            </div>
            <p className="text-sm text-surface-500 dark:text-surface-500">
              Multi-Agent Collaboration Platform
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
