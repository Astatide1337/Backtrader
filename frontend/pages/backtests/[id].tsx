import React from 'react';
import { useRouter } from 'next/router';
import { useBacktestDetail, useBacktests, formatLocalDateTime } from 'hooks/useBacktests';
import Card from 'components/ui/Card';
import { CardHeader, CardContent } from 'components/ui/Card';
import Skeleton from 'components/ui/Skeleton';
import ErrorState from 'components/ui/ErrorState';
import Button from 'components/ui/Button';

const BacktestDetailPage: React.FC = () => {
  const router = useRouter();
  const id = router.query.id as string | undefined;
  const { data, isLoading, error } = useBacktestDetail(id);

  // Fetch list to obtain metadata (created_at/status) if not present in detail payload
  const { data: list } = useBacktests();
  const meta = list?.find((b) => b.id === id);
  const { deleteBacktest } = useBacktests();

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="text-sm font-semibold text-gray-900">Backtest Detail</div>
        </CardHeader>
        <div className="px-4 pb-0 pt-3">
          <Button
            variant="secondary"
            className="px-3 py-1 text-sm"
            onClick={async () => {
              if (!id) return;
              if (!confirm('Delete this backtest? This action cannot be undone.')) return;
              try {
                await deleteBacktest(id);
                window.location.href = '/backtests';
              } catch (e: any) {
                alert(e?.message || 'Failed to delete backtest');
              }
            }}
          >
            Delete
          </Button>
        </div>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : error ? (
            <ErrorState message="Failed to load backtest." />
          ) : data ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <div>
                  <div className="text-xs text-gray-500">ID</div>
                  <div className="font-mono text-sm break-all">{id ?? '—'}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Created (UTC)</div>
                  <div className="text-sm">{formatLocalDateTime(meta?.created_at)}</div>
                </div>
                {/* Status removed per request */}
              </div>

              <div>
                <div className="mb-2 text-sm font-semibold text-gray-900">Result JSON</div>
                <pre className="overflow-auto rounded-md border border-gray-200 bg-gray-50 p-3 text-xs">
                  {JSON.stringify(data, null, 2)}
                </pre>
              </div>
            </div>
          ) : (
            <div className="text-sm text-gray-600">No data.</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default BacktestDetailPage;