'use client';

import { useState, useCallback } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import { cn } from '@/lib/utils';

/**
 * 主布局组件
 * - 组合 Header、Sidebar 和内容区域
 * - 管理侧边栏展开/折叠状态
 * - 响应式布局
 */

/** MainLayout 属性 */
interface MainLayoutProps {
  /** 主内容区域 */
  children: React.ReactNode;
  /** 自定义类名 */
  className?: string;
}

/**
 * MainLayout 组件
 */
export default function MainLayout({ children, className }: MainLayoutProps) {
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(true);
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  const [isDark, setIsDark] = useState(false);

  /** 切换侧边栏 */
  const toggleSidebar = useCallback(() => {
    setIsSidebarExpanded((prev) => !prev);
  }, []);

  /** 切换主题 */
  const toggleTheme = useCallback(() => {
    setIsDark((prev) => {
      const newValue = !prev;
      // 更新 DOM class
      if (typeof document !== 'undefined') {
        document.documentElement.classList.toggle('dark', newValue);
      }
      return newValue;
    });
  }, []);

  return (
    <div className={cn('h-screen flex flex-col bg-surface-50 dark:bg-surface-950', className)}>
      {/* 顶部导航 */}
      <Header
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
        onToggleTheme={toggleTheme}
        isDark={isDark}
        onSettingsClick={() => {
          // TODO: 打开设置面板
        }}
      />

      {/* 主体区域 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 侧边栏 */}
        <Sidebar
          isExpanded={isSidebarExpanded}
          onToggle={toggleSidebar}
          onNewConversation={() => {
            // TODO: 创建新对话
          }}
        />

        {/* 主内容区域 */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* 侧边栏折叠按钮（桌面端） */}
          {!isSidebarExpanded && (
            <button
              onClick={toggleSidebar}
              className="absolute top-20 left-2 z-20 p-1.5 rounded-lg bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700 text-surface-500 hover:text-surface-700 dark:hover:text-surface-300 shadow-sm transition-colors hidden lg:flex"
              aria-label="展开侧边栏"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <rect width="18" height="18" x="3" y="3" rx="2" />
                <path d="M9 3v18" />
              </svg>
            </button>
          )}

          {children}
        </main>
      </div>
    </div>
  );
}

export type { MainLayoutProps };
