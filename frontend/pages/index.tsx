import React from 'react';
import usePortfolio from 'hooks/usePortfolio';
import useOrders from 'hooks/useOrders';
import { useBacktests } from 'hooks/useBacktests';
import useMarketData from 'hooks/useMarketData';
import Card from 'components/ui/Card';
import { CardHeader, CardContent } from 'components/ui/Card';
import Skeleton from 'components/ui/Skeleton';
import EmptyState from 'components/ui/EmptyState';
import ErrorState from 'components/ui/ErrorState';
import Table from 'components/ui/Table';
import { THead, TBody, TR, TH, TD } from 'components/ui/Table';

const NumberText: React.FC<{ value: number | undefined; suffix?: string }> = ({ value, suffix }) => {
  if (typeof value !== 'number') return <span>—</span>;
  const formatted = value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  return (
    <span className={value >= 0 ? 'text-emerald-600' : 'text-red-600'}>
      {formatted}
      {suffix ?? ''}
    </span>
  );
};

const DashboardPage: React.FC = () => {
  const { data: portfolio, isLoading: portfolioLoading, error: portfolioError, mutate: refetchPortfolio } =
    usePortfolio();
  const { data: orders, isLoading: ordersLoading, error: ordersError } = useOrders();
  const { data: backtests, isLoading: backtestsLoading, error: backtestsError } = useBacktests();
  const { data: candles, isLoading: mdLoading, error: mdError } = useMarketData('AAPL', 100);

  const lastClose = candles && candles.length > 0 ? candles[candles.length - 1].close : undefined;

  return (
    <div className="space-y-6">
      {/* Portfolio summary */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Card>
          <CardHeader>
            <div className="text-sm font-medium text-gray-600">Equity</div>
          </CardHeader>
          <CardContent>
            {portfolioLoading ? (
              <Skeleton className="h-6 w-24" />
            ) : portfolioError ? (
              <ErrorState message="Failed to load portfolio." onRetry={refetchPortfolio} />
            ) : portfolio ? (
              <div className="text-2xl font-semibold text-gray-900">
                <NumberText value={portfolio.equity} />
              </div>
            ) : (
              <EmptyState title="No portfolio data" description="No snapshot available." />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="text-sm font-medium text-gray-600">Cash</div>
          </CardHeader>
          <CardContent>
            {portfolioLoading ? (
              <Skeleton className="h-6 w-24" />
            ) : portfolioError ? (
              <ErrorState message="Failed to load portfolio." onRetry={refetchPortfolio} />
            ) : portfolio ? (
              <div className="text-2xl font-semibold text-gray-900">
                <NumberText value={portfolio.cash} />
              </div>
            ) : (
              <EmptyState title="No portfolio data" description="No snapshot available." />
            )}
          </CardContent>
        </Card>

        <Card className="sm:col-span-2 xl:col-span-1">
          <CardHeader>
            <div className="text-sm font-medium text-gray-600">PnL</div>
          </CardHeader>
          <CardContent>
            {portfolioLoading ? (
              <Skeleton className="h-6 w-24" />
            ) : portfolioError ? (
              <ErrorState message="Failed to load portfolio." onRetry={refetchPortfolio} />
            ) : portfolio ? (
              <div className="text-2xl font-semibold">
                <NumberText value={portfolio.pnl} />
              </div>
            ) : (
              <EmptyState title="No portfolio data" description="No snapshot available." />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="text-sm font-medium text-gray-600">AAPL Last Close</div>
          </CardHeader>
          <CardContent>
            {mdLoading ? (
              <Skeleton className="h-6 w-24" />
            ) : mdError ? (
              <ErrorState message="Failed to load ticker." />
            ) : typeof lastClose === 'number' ? (
              <div className="text-2xl font-semibold text-gray-900">
                <NumberText value={lastClose} />
              </div>
            ) : (
              <EmptyState title="No data" description="Ticker not available." />
            )}
            <div className="mt-2 text-xs text-gray-500">Chart coming soon</div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Orders */}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="text-sm font-semibold text-gray-900">Recent Orders</div>
          </CardHeader>
          <CardContent>
            {ordersLoading ? (
              <Skeleton className="h-24 w-full" />
            ) : ordersError ? (
              <ErrorState message="Failed to load orders." />
            ) : orders && orders.length > 0 ? (
              <Table compact>
                <THead>
                  <TR>
                    <TH>Time</TH>
                    <TH>Symbol</TH>
                    <TH>Side</TH>
                    <TH>Qty</TH>
                    <TH>Price</TH>
                    <TH>Status</TH>
                  </TR>
                </THead>
                <TBody>
                  {orders.slice(0, 5).map((o) => (
                    <TR key={o.id}>
                      <TD className="whitespace-nowrap text-gray-500">
                        {new Date(o.timestamp).toLocaleString()}
                      </TD>
                      <TD className="font-medium">{o.symbol}</TD>
                      <TD className={o.side === 'buy' ? 'text-emerald-600' : 'text-red-600'}>
                        {o.side.toUpperCase()}
                      </TD>
                      <TD>{o.qty}</TD>
                      <TD>{o.price.toFixed(2)}</TD>
                      <TD className="text-gray-600">{o.status ?? '—'}</TD>
                    </TR>
                  ))}
                </TBody>
              </Table>
            ) : (
              <EmptyState title="No orders" description="No recent orders." />
            )}
          </CardContent>
        </Card>

        {/* Recent Backtests */}
        <Card>
          <CardHeader>
            <div className="text-sm font-semibold text-gray-900">Recent Backtests</div>
          </CardHeader>
          <CardContent>
            {backtestsLoading ? (
              <Skeleton className="h-24 w-full" />
            ) : backtestsError ? (
              <ErrorState message="Failed to load backtests." />
            ) : backtests && backtests.length > 0 ? (
              <Table compact>
                <THead>
                  <TR>
                    <TH>Created (UTC)</TH>
                    <TH>Strategy</TH>
                    <TH>Symbol</TH>
                  </TR>
                </THead>
                <TBody>
                  {backtests.slice(0, 5).map((b) => (
                    <TR key={b.id} className="group hover:bg-gray-50">
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
                        <a className="text-blue-700 underline-offset-2 hover:underline focus:underline" href={`/backtests/${b.id}`}>
                          {b.strategy_name}
                        </a>
                      </TD>
                      <TD className="">{b.symbol}</TD>
                    </TR>
                  ))}
                </TBody>
              </Table>
            ) : (
              <EmptyState title="No backtests" description="No recent backtests." />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;