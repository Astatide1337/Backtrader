import React from 'react';
import Button from 'components/ui/Button';

type ErrorStateProps = {
  title?: string;
  message?: string;
  onRetry?: () => void;
};

const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  message = 'An unexpected error occurred. Please try again.',
  onRetry,
}) => {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
      <div className="mx-auto mb-2 h-10 w-10 rounded-full bg-red-100 text-red-500">!</div>
      <h3 className="text-sm font-semibold text-red-700">{title}</h3>
      <p className="mt-1 text-sm text-red-600">{message}</p>
      {onRetry && (
        <div className="mt-4">
          <Button variant="secondary" onClick={onRetry}>
            Retry
          </Button>
        </div>
      )}
    </div>
  );
};

export default React.memo(ErrorState);