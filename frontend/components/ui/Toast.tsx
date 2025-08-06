import React, { useEffect } from 'react';
import clsx from 'clsx';

export type ToastProps = {
  open: boolean;
  title?: string;
  description?: string;
  onClose: () => void;
  variant?: 'info' | 'success' | 'error' | 'warning';
  duration?: number; // ms
  className?: string;
};

const tone: Record<NonNullable<ToastProps['variant']>, string> = {
  info: 'bg-blue-600',
  success: 'bg-emerald-600',
  error: 'bg-red-600',
  warning: 'bg-amber-600',
};

const Toast: React.FC<ToastProps> = ({
  open,
  title,
  description,
  onClose,
  duration = 3000,
  variant = 'info',
  className,
}) => {
  useEffect(() => {
    if (!open) return;
    const id = window.setTimeout(onClose, duration);
    return () => window.clearTimeout(id);
  }, [open, onClose, duration]);

  if (!open) return null;

  return (
    <div className="pointer-events-none fixed inset-0 z-50 flex items-start justify-end p-4">
      <div
        className={clsx(
          'pointer-events-auto inline-flex min-w-[260px] max-w-md gap-3 rounded-md bg-white p-3 shadow-lg ring-1 ring-black/5',
          className
        )}>
        <span className={clsx('mt-1 inline-block h-2 w-2 rounded-full', tone[variant])} />
        <div className="flex-1">
          {title && <div className="text-sm font-medium text-gray-900">{title}</div>}
          {description && <div className="text-xs text-gray-600">{description}</div>}
        </div>
        <button
          onClick={onClose}
          className="rounded p-1 text-gray-500 hover:bg-gray-100 hover:text-gray-700"
          aria-label="Close notification"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default React.memo(Toast);