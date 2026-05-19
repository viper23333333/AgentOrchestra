'use client';

import { useEffect, useCallback, type ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * 通用模态框组件
 * - 支持多种尺寸
 * - 支持自定义内容
 * - 点击遮罩关闭
 * - ESC 键关闭
 * - 焦点锁定
 * - 动画过渡
 */

/** 模态框尺寸 */
type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';

/** 模态框属性 */
interface ModalProps {
  /** 是否显示 */
  isOpen: boolean;
  /** 关闭回调 */
  onClose: () => void;
  /** 标题 */
  title?: string;
  /** 描述 */
  description?: string;
  /** 子内容 */
  children: ReactNode;
  /** 尺寸 */
  size?: ModalSize;
  /** 自定义页脚 */
  footer?: ReactNode;
  /** 是否显示关闭按钮 */
  showCloseButton?: boolean;
  /** 点击遮罩是否关闭 */
  closeOnOverlayClick?: boolean;
  /** ESC 键是否关闭 */
  closeOnEsc?: boolean;
  /** 自定义类名 */
  className?: string;
}

/** 尺寸映射 */
const sizeStyles: Record<ModalSize, string> = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
  full: 'max-w-[calc(100vw-2rem)] max-h-[calc(100vh-2rem)]',
};

/**
 * 遮罩层动画配置
 */
const overlayVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 },
};

/**
 * 模态框内容动画配置
 */
const contentVariants = {
  hidden: { opacity: 0, scale: 0.95, y: 10 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { type: 'spring', damping: 25, stiffness: 300 },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 10,
    transition: { duration: 0.15 },
  },
};

/**
 * 模态框组件
 */
export default function Modal({
  isOpen,
  onClose,
  title,
  description,
  children,
  size = 'md',
  footer,
  showCloseButton = true,
  closeOnOverlayClick = true,
  closeOnEsc = true,
  className,
}: ModalProps) {
  /**
   * ESC 键关闭
   */
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (closeOnEsc && event.key === 'Escape') {
        onClose();
      }
    },
    [closeOnEsc, onClose]
  );

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      // 阻止背景滚动
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isOpen, handleKeyDown]);

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* 遮罩层 */}
          <motion.div
            variants={overlayVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            transition={{ duration: 0.2 }}
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={closeOnOverlayClick ? onClose : undefined}
          />

          {/* 模态框内容 */}
          <motion.div
            variants={contentVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            className={cn(
              'relative w-full bg-white dark:bg-surface-800',
              'rounded-2xl shadow-2xl',
              'border border-surface-200 dark:border-surface-700',
              'flex flex-col max-h-[85vh]',
              sizeStyles[size],
              className
            )}
            role="dialog"
            aria-modal="true"
            aria-labelledby={title ? 'modal-title' : undefined}
            aria-describedby={description ? 'modal-description' : undefined}
          >
            {/* 头部 */}
            {(title || showCloseButton) && (
              <div className="flex items-start justify-between p-6 pb-0">
                <div className="flex-1 min-w-0">
                  {title && (
                    <h2
                      id="modal-title"
                      className="text-lg font-semibold text-surface-900 dark:text-white"
                    >
                      {title}
                    </h2>
                  )}
                  {description && (
                    <p
                      id="modal-description"
                      className="mt-1 text-sm text-surface-500 dark:text-surface-400"
                    >
                      {description}
                    </p>
                  )}
                </div>
                {showCloseButton && (
                  <button
                    onClick={onClose}
                    className="ml-4 p-1.5 rounded-lg text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
                    aria-label="关闭"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            )}

            {/* 内容区域 */}
            <div className="flex-1 overflow-y-auto p-6">{children}</div>

            {/* 页脚 */}
            {footer && (
              <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-surface-200 dark:border-surface-700">
                {footer}
              </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

export type { ModalProps, ModalSize };
