import React from 'react';
import Button from 'components/ui/Button';

type EmptyStateProps = {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
};

const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'Nothing here yet',
  description = 'There is no data to display.',
  actionLabel,
  onAction,
}) => {
  return (
    <div className="rounded-lg border border-dashed border-gray-300 p-8 text-center">
      <div className="mx-auto mb-2 h-10 w-10 rounded-full bg-gray-100 text-gray-400">∅</div>
      <h3 className="text-sm font-medium text-gray-900">{title}</h3>
      <p className="mt-1 text-sm text-gray-600">{description}</p>
      {actionLabel && onAction && (
        <div className="mt-4">
          <Button onClick={onAction}>{actionLabel}</Button>
        </div>
      )}
    </div>
  );
};

export default React.memo(EmptyState);