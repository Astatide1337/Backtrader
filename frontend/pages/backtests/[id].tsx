import React from 'react';
import { useRouter } from 'next/router';
import { useBacktestDetail, useBacktests, formatLocalDateTime } from 'hooks/useBacktests';
import Card from 'components/ui/Card';
import { CardHeader, CardContent } from 'components/ui/Card';
import Skeleton from 'components/ui/Skeleton';
import ErrorState from 'components/ui/ErrorState';
import Button from 'components/ui/Button';
import BacktestSummary from 'components/backtests/BacktestSummary';
import EquityCurveChart from 'components/backtests/EquityCurveChart';
import PositionsTable from 'components/backtests/PositionsTable';
import OrdersLog from 'components/backtests/OrdersLog';

const BacktestDetailPage: React.FC = () => {
  const router = useRouter();
  const id = router.query.id as string | undefined;
  const { data, isLoading, error } = useBacktestDetail(id);

  const { deleteBacktest } = useBacktests();

  return (
    <div className="space-y-6">
      {isLoading ? (
        <Skeleton className="h-24 w-full" />
      ) : error ? (
        <ErrorState message="Failed to load backtest." />
      ) : data ? (
        <>
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold">Backtest Results</h1>
            <div>
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
          </div>
          <BacktestSummary data={data} />
          <EquityCurveChart equityCurve={data.equity_curve} priceCurve={data.price_curve} />
          <PositionsTable positions={data.positions} />
          <OrdersLog orders={data.orders} />
        </>
      ) : (
        <div className="text-sm text-gray-600">No data.</div>
      )}
    </div>
  );
};

export default BacktestDetailPage;
