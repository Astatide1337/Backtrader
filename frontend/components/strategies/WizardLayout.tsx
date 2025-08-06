import React from 'react';
import clsx from 'clsx';

export type WizardStep = {
  key: string;
  title: string;
  description?: string;
};

type WizardLayoutProps = {
  steps: WizardStep[];
  activeIndex: number;
  onSelectStep?: (index: number) => void;
  children: React.ReactNode;
};

const WizardLayout: React.FC<WizardLayoutProps> = ({ steps, activeIndex, onSelectStep, children }) => {
  return (
    <div className="w-full">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-[260px_1fr]">
        {/* Left step nav */}
        <aside className="md:sticky md:top-4">
          <ol className="flex overflow-auto md:block md:space-y-1">
            {steps.map((s, idx) => {
              const active = idx === activeIndex;
              return (
                <li key={s.key} className={clsx('mr-2 md:mr-0')}>
                  <button
                    type="button"
                    onClick={() => onSelectStep && onSelectStep(idx)}
                    className={clsx(
                      'w-full rounded-md px-3 py-2 text-left text-sm transition-colors',
                      active
                        ? 'bg-blue-50 text-blue-700 ring-1 ring-inset ring-blue-200'
                        : 'text-gray-700 hover:bg-gray-50',
                    )}
                    aria-current={active ? 'step' : undefined}
                  >
                    <div className="font-medium">{idx + 1}. {s.title}</div>
                    {s.description && <div className="text-xs text-gray-500">{s.description}</div>}
                  </button>
                </li>
              );
            })}
          </ol>
        </aside>
        {/* Main content */}
        <section className="min-w-0">{children}</section>
      </div>
    </div>
  );
};

export default React.memo(WizardLayout);