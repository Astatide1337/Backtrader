import React from 'react';
import clsx from 'clsx';

export type SelectOption = { value: string; label: string };

export type SelectProps = React.SelectHTMLAttributes<HTMLSelectElement> & {
  label?: string;
  error?: string;
  options?: SelectOption[];
};

const Select: React.FC<SelectProps> = ({ className, label, error, id, options, children, ...props }) => {
  const selectId = id || props.name || undefined;
  return (
    <div className="w-full">
      {label && (
        <label htmlFor={selectId} className="mb-1 block text-sm font-medium text-gray-700">
          {label}
        </label>
      )}
      <select id={selectId} className={clsx('select', className)} {...props}>
        {options
          ? options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))
          : children}
      </select>
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
};

export default React.memo(Select);