import React from 'react';
import Link from 'next/link';
import Card from 'components/ui/Card';
import { CardContent } from 'components/ui/Card';
import Button from 'components/ui/Button';

const ErrorPage: React.FC = () => {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <Card className="max-w-md w-full">
        <CardContent>
          <div className="text-center">
            <div className="text-7xl font-bold text-gray-200">500</div>
            <h1 className="mt-2 text-lg font-semibold text-gray-900">Internal Server Error</h1>
            <p className="mt-1 text-sm text-gray-600">
              An unexpected error occurred. Please try again or return home.
            </p>
            <div className="mt-4 flex justify-center gap-3">
              <button className="btn btn-secondary" onClick={() => location.reload()}>
                Reload
              </button>
              <Link href="/">
                <Button>Go back home</Button>
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ErrorPage;