import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';

/**
 * 字体配置
 * - Inter: 主 UI 字体，现代几何无衬线体
 * - JetBrains Mono: 代码字体，专为开发者设计
 */
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-mono',
});

/**
 * 应用 Metadata
 * 用于 SEO 和浏览器标签页信息
 */
export const metadata: Metadata = {
  title: {
    default: 'AgentOrchestra - Multi-Agent Collaboration Platform',
    template: '%s | AgentOrchestra',
  },
  description:
    'A powerful multi-agent collaboration platform that orchestrates specialized AI agents to solve complex tasks through intelligent cooperation.',
  keywords: ['AI', 'Multi-Agent', 'LLM', 'Collaboration', 'Orchestration', 'Agent'],
  authors: [{ name: 'AgentOrchestra Team' }],
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0f172a' },
  ],
};

/**
 * 根布局组件
 * - 提供全局字体、样式和 metadata
 * - 包含 QueryClientProvider 用于数据请求管理
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} font-sans min-h-screen bg-surface-50 dark:bg-surface-950`}
      >
        {children}
      </body>
    </html>
  );
}
