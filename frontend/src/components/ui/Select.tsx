'use client';

import { forwardRef, useState, useRef, useEffect, type SelectHTMLAttributes } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * 通用下拉选择组件
 * - 支持自定义样式
 * - 支持分组选项
 * - 支持占位符
 * - 键盘导航友好
 */

/** 选项定义 */
export interface SelectOption {
  value: string;
  label: string;
  description?: string;
  disabled?: boolean;
  icon?: React.ReactNode;
}

/** 选项分组 */
export interface SelectGroup {
  label: string;
  options: SelectOption[];
}

/** Select 属性 */
interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'size'> {
  /** 选项列表 */
  options: SelectOption[];
  /** 分组选项（优先于 options） */
  groups?: SelectGroup[];
  /** 占位符 */
  placeholder?: string;
  /** 尺寸 */
  size?: 'sm' | 'md' | 'lg';
  /** 是否显示错误状态 */
  error?: boolean;
  /** 左侧图标 */
  leftIcon?: React.ReactNode;
  /** 自定义渲染选项 */
  renderOption?: (option: SelectOption) => React.ReactNode;
}

/** 尺寸样式映射 */
const sizeStyles = {
  sm: 'px-3 py-1.5 text-sm rounded-lg',
  md: 'px-4 py-2 text-sm rounded-lg',
  lg: 'px-4 py-3 text-base rounded-xl',
};

/**
 * Select 组件
 */
const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      options = [],
      groups,
      placeholder,
      size = 'md',
      error = false,
      leftIcon,
      className,
      value,
      onChange,
      renderOption,
      ...props
    },
    ref
  ) => {
    return (
      <div className="relative">
        {/* 左侧图标 */}
        {leftIcon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none">
            {leftIcon}
          </div>
        )}

        {/* Select 元素 */}
        <select
          ref={ref}
          value={value}
          onChange={onChange}
          className={cn(
            // 基础样式
            'w-full appearance-none bg-white dark:bg-surface-800',
            'border rounded-lg',
            'text-surface-900 dark:text-surface-100',
            'transition-colors duration-150',
            'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-1',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            // 尺寸
            sizeStyles[size],
            // 图标间距
            leftIcon && 'pl-10',
            // 右侧箭头间距
            'pr-10',
            // 错误状态
            error
              ? 'border-red-300 dark:border-red-700 focus:ring-red-500'
              : 'border-surface-200 dark:border-surface-700 hover:border-surface-300 dark:hover:border-surface-600',
            className
          )}
          {...props}
        >
          {/* 占位符 */}
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}

          {/* 分组选项 */}
          {groups ? (
            groups.map((group) => (
              <optgroup key={group.label} label={group.label}>
                {group.options.map((option) => (
                  <option
                    key={option.value}
                    value={option.value}
                    disabled={option.disabled}
                  >
                    {option.label}
                  </option>
                ))}
              </optgroup>
            ))
          ) : (
            /* 普通选项 */
            options.map((option) => (
              <option key={option.value} value={option.value} disabled={option.disabled}>
                {option.label}
              </option>
            ))
          )}
        </select>

        {/* 下拉箭头 */}
        <div className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none">
          <ChevronDown className="w-4 h-4" />
        </div>
      </div>
    );
  }
);

Select.displayName = 'Select';

export default Select;
export type { SelectProps, SelectOption, SelectGroup };
