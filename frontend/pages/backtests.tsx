import React, { useMemo, useState } from 'react';
import { useBacktests } from 'hooks/useBacktests';
import Button from 'components/ui/Button';
import Card from 'components/ui/Card';
import { CardHeader, CardContent } from 'components/ui/Card';
import Skeleton from 'components/ui/Skeleton';
import EmptyState from 'components/ui/EmptyState';
import ErrorState from 'components/ui/ErrorState';
import Table from 'components/ui/Table';
import { THead, TBody, TR, TH, TD } from 'components/ui/Table';

const PAGE_SIZE = 10;

const BacktestsPage: React.FC = () => {
  const { data, isLoading, error, deleteBacktest, mutate } = useBacktests();

  async function onDelete(id: string) {
    if (!confirm('Delete this backtest? This action cannot be undone.')) return;
    try {
      // optimistic UI: remove from current page immediately
      // Note: keeping simple; rely on mutate after server delete to refresh canonical data
      await deleteBacktest(id);
    } catch (e: any) {
      alert(e?.message || 'Failed to delete backtest');
    }
  }
  const [page, setPage] = useState(1);

  const paged = useMemo(() => {
    if (!data) return [];
    const start = (page - 1) * PAGE_SIZE;
    return data.slice(start, start + PAGE_SIZE);
  }, [data, page]);

  const totalPages = data ? Math.max(1, Math.ceil(data.length / PAGE_SIZE)) : 1;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex w-full items-center justify-between">
            <div className="text-sm font-semibold text-gray-900">Backtests</div>
            <a href="/backtests/new" className="btn btn-primary px-3 py-1 text-sm">New Backtest</a>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : error ? (
            <ErrorState message="Failed to load backtests." />
          ) : data && data.length > 0 ? (
            <>
              <Table compact>
                <THead>
                  <TR>
                    <TH>Created (UTC)</TH>
                    <TH>Strategy</TH>
                    <TH>Symbol</TH>
                    <TH>Period</TH>
                    <TH className="text-right">Initial Capital</TH>
                    <TH className="w-40 text-right">Actions</TH>
                  </TR>
                </THead>
                <TBody>
                  {paged.map((b) => (
                    <TR
                      key={b.id}
                      className="group hover:bg-gray-50 cursor-pointer"
                      onClick={() => (window.location.href = `/backtests/${b.id}`)}
                    >
                      <TD className="whitespace-nowrap text-gray-500">
                        {new Intl.DateTimeFormat(undefined, {
                          year: 'numeric',
                          month: 'short',
                          day: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit',
                          hour12: false,
                          timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
                        }).format(new Date(b.created_at))}
                      </TD>
                      <TD className="font-medium">
                        <a
                          className="text-blue-700 underline-offset-2 hover:underline focus:underline"
                          href={`/backtests/${b.id}`}
                          onClick={(e) => e.stopPropagation()}
                        >
                          {b.strategy_name}
                        </a>
                      </TD>
                      <TD className="">{b.symbol}</TD>
                      <TD className="whitespace-nowrap">
                        {b.start_date} → {b.end_date}
                      </TD>
                      <TD className="text-right">${b.initial_capital.toLocaleString()}</TD>
                      <TD className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="secondary"
                            className="px-2 py-1 text-xs"
                            onClick={(e) => {
                              e.stopPropagation();
                              onDelete(b.id);
                            }}
                          >
                            Delete
                          </Button>
                        </div>
                      </TD>
                    </TR>
                  ))}
                </TBody>
              </Table>

              {/* Pagination */}
              <div className="mt-4 flex items-center justify-between">
                <div className="text-sm text-gray-600">
                  Page {page} of {totalPages}
                </div>
                <div className="flex gap-2">
                  <button
                    className="btn btn-secondary px-3 py-1"
                    disabled={page <= 1}
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                  >
                    Previous
                  </button>
                  <button
                    className="btn btn-secondary px-3 py-1"
                    disabled={page >= totalPages}
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  >
                    Next
                  </button>
                </div>
              </div>
            </>
          ) : (
            <EmptyState title="No backtests" description="No backtests found." />
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default BacktestsPage;
