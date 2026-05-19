'use client';

import { useState } from 'react';
import { Bot, Settings, Moon, Sun, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Select from '@/components/ui/Select';
import { cn } from '@/lib/utils';
import { AVAILABLE_MODELS } from '@/types';
import type { ModelOption } from '@/types';

/**
 * 顶部导航栏组件
 * - Logo 和品牌标识
 * - 模型选择器
 * - 主题切换
 * - 设置按钮
 */

/** Header 属性 */
interface HeaderProps {
  /** 当前选中的模型 */
  selectedModel?: string;
  /** 模型切换回调 */
  onModelChange?: (modelId: string) => void;
  /** 主题切换回调 */
  onToggleTheme?: () => void;
  /** 是否为暗色主题 */
  isDark?: boolean;
  /** 设置按钮点击回调 */
  onSettingsClick?: () => void;
  /** 自定义类名 */
  className?: string;
}

/**
 * Header 组件
 */
export default function Header({
  selectedModel = 'gpt-4',
  onModelChange,
  onToggleTheme,
  isDark = false,
  onSettingsClick,
  className,
}: HeaderProps) {
  const [isModelSelectorOpen, setIsModelSelectorOpen] = useState(false);

  /** 当前选中的模型信息 */
  const currentModel = AVAILABLE_MODELS.find((m) => m.id === selectedModel);

  /** 按模型提供商分组 */
  const modelGroups = AVAILABLE_MODELS.reduce(
    (acc, model) => {
      if (!acc[model.provider]) {
        acc[model.provider] = { label: model.provider, options: [] };
      }
      acc[model.provider].options.push({
        value: model.id,
        label: model.name,
        description: model.description,
      });
      return acc;
    },
    {} as Record<string, { label: string; options: { value: string; label: string; description?: string }[] }>
  );

  return (
    <header
      className={cn(
        'h-16 flex items-center justify-between px-4 sm:px-6',
        'bg-white/80 dark:bg-surface-900/80 backdrop-blur-xl',
        'border-b border-surface-200 dark:border-surface-800',
        'z-30',
        className
      )}
    >
      {/* 左侧：Logo */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center shadow-glow">
          <Bot className="w-5 h-5 text-white" />
        </div>
        <div className="hidden sm:block">
          <h1 className="text-base font-bold text-surface-900 dark:text-white leading-tight">
            AgentOrchestra
          </h1>
          <p className="text-xs text-surface-400 dark:text-surface-500 leading-tight">
            Multi-Agent Platform
          </p>
        </div>
      </div>

      {/* 中间：模型选择器 */}
      <div className="flex items-center gap-3">
        <div className="relative">
          <Select
            value={selectedModel}
            onChange={(e) => onModelChange?.(e.target.value)}
            groups={Object.values(modelGroups)}
            size="sm"
            className="w-44 sm:w-56 bg-surface-50 dark:bg-surface-800/50"
          />
        </div>
      </div>

      {/* 右侧：操作按钮 */}
      <div className="flex items-center gap-1">
        {/* 主题切换 */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onToggleTheme}
          className="p-2 rounded-lg text-surface-500 dark:text-surface-400 hover:text-surface-700 dark:hover:text-surface-200 hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
          aria-label={isDark ? '切换到亮色模式' : '切换到暗色模式'}
        >
          <AnimatePresence mode="wait">
            {isDark ? (
              <motion.div
                key="sun"
                initial={{ rotate: -90, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                exit={{ rotate: 90, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <Sun className="w-5 h-5" />
              </motion.div>
            ) : (
              <motion.div
                key="moon"
                initial={{ rotate: 90, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                exit={{ rotate: -90, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <Moon className="w-5 h-5" />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.button>

        {/* 设置按钮 */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onSettingsClick}
          className="p-2 rounded-lg text-surface-500 dark:text-surface-400 hover:text-surface-700 dark:hover:text-surface-200 hover:bg-surface-100 dark:hover:bg-surface-800 transition-colors"
          aria-label="设置"
        >
          <Settings className="w-5 h-5" />
        </motion.button>
      </div>
    </header>
  );
}

export type { HeaderProps };
