'use client';

import { cn } from '@/lib/utils';

/**
 * 加载动画组件
 * - 支持多种尺寸和变体
 * - 支持自定义颜色
 * - 可作为全屏遮罩使用
 */

/** Spinner 变体 */
type SpinnerVariant = 'default' | 'dots' | 'pulse';

/** Spinner 尺寸 */
type SpinnerSize = 'sm' | 'md' | 'lg' | 'xl';

/** Spinner 属性 */
interface SpinnerProps {
  /** 变体 */
  variant?: SpinnerVariant;
  /** 尺寸 */
  size?: SpinnerSize;
  /** 自定义颜色类名 */
  colorClass?: string;
  /** 全屏遮罩模式 */
  fullscreen?: boolean;
  /** 遮罩文字 */
  label?: string;
  /** 自定义类名 */
  className?: string;
}

/** 尺寸映射 */
const sizeStyles: Record<SpinnerSize, string> = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
  xl: 'w-12 h-12',
};

const dotSizeStyles: Record<SpinnerSize, string> = {
  sm: 'w-1 h-1',
  md: 'w-1.5 h-1.5',
  lg: 'w-2 h-2',
  xl: 'w-3 h-3',
};

/**
 * 默认旋转 Spinner
 */
function DefaultSpinner({ size, colorClass, className }: Omit<SpinnerProps, 'variant' | 'fullscreen' | 'label'>) {
  return (
    <svg
      className={cn(
        'animate-spin',
        sizeStyles[size || 'md'],
        colorClass || 'text-primary-500',
        className
      )}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

/**
 * 跳动点 Spinner
 */
function DotsSpinner({ size, colorClass, className }: Omit<SpinnerProps, 'variant' | 'fullscreen' | 'label'>) {
  const dotSize = dotSizeStyles[size || 'md'];
  const gap = size === 'sm' ? 'gap-1' : size === 'md' ? 'gap-1.5' : 'gap-2';

  return (
    <div className={cn('flex items-center', gap, className)}>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={cn(
            dotSize,
            'rounded-full',
            colorClass || 'bg-primary-500',
            'animate-bounce'
          )}
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </div>
  );
}

/**
 * 脉冲 Spinner
 */
function PulseSpinner({ size, colorClass, className }: Omit<SpinnerProps, 'variant' | 'fullscreen' | 'label'>) {
  return (
    <div
      className={cn(
        'relative',
        sizeStyles[size || 'md'],
        className
      )}
    >
      <div
        className={cn(
          'absolute inset-0 rounded-full',
          colorClass || 'bg-primary-500',
          'animate-ping opacity-20'
        )}
      />
      <div
        className={cn(
          'relative rounded-full',
          colorClass || 'bg-primary-500',
        )}
        style={{
          width: size === 'sm' ? '8px' : size === 'md' ? '12px' : size === 'lg' ? '16px' : '24px',
          height: size === 'sm' ? '8px' : size === 'md' ? '12px' : size === 'lg' ? '16px' : '24px',
        }}
      />
    </div>
  );
}

/**
 * Spinner 组件
 */
export default function Spinner({
  variant = 'default',
  size = 'md',
  colorClass,
  fullscreen = false,
  label,
  className,
}: SpinnerProps) {
  const spinnerElement = (
    <>
      {variant === 'default' && (
        <DefaultSpinner size={size} colorClass={colorClass} className={className} />
      )}
      {variant === 'dots' && (
        <DotsSpinner size={size} colorClass={colorClass} className={className} />
      )}
      {variant === 'pulse' && (
        <PulseSpinner size={size} colorClass={colorClass} className={className} />
      )}
      {label && (
        <span className="ml-2 text-sm text-surface-500 dark:text-surface-400">{label}</span>
      )}
    </>
  );

  // 全屏遮罩模式
  if (fullscreen) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/80 dark:bg-surface-950/80 backdrop-blur-sm">
        <div className="flex items-center">{spinnerElement}</div>
      </div>
    );
  }

  return <div className="inline-flex items-center">{spinnerElement}</div>;
}

export type { SpinnerProps, SpinnerVariant, SpinnerSize };
