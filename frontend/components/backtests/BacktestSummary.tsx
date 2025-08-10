import React from 'react';
import { Card, CardContent, CardHeader } from 'components/ui/Card';
import { BacktestDetail } from 'types/api';

interface BacktestSummaryProps {
  data: BacktestDetail;
}

const BacktestSummary: React.FC<BacktestSummaryProps> = ({ data }) => {
  const { performance, positions } = data;

  const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;
  const formatNumber = (value: number) => value?.toFixed(2) ?? 'N/A';
  const formatCurrency = (value: number) => value?.toLocaleString('en-US', { style: 'currency', currency: 'USD' }) ?? 'N/A';

  const metrics = [
    { label: 'Total Return', value: formatPercent(performance.total_return) },
    { label: 'Annualized Return', value: formatPercent(performance.annualized_return) },
    { label: 'Annualized Volatility', value: formatPercent(performance.annualized_volatility) },
    { label: 'Sharpe Ratio', value: formatNumber(performance.sharpe_ratio) },
    { label: 'Sortino Ratio', value: formatNumber(performance.sortino_ratio) },
    { label: 'Calmar Ratio', value: formatNumber(performance.calmar_ratio) },
    { label: 'Max Drawdown', value: formatPercent(performance.max_drawdown) },
    { label: 'Win Rate', value: formatPercent(performance.win_rate) },
    { label: 'Profit Factor', value: formatNumber(performance.profit_factor) },
    { label: 'Avg. Trade', value: formatCurrency(performance.avg_trade) },
    { label: 'Avg. Win', value: formatCurrency(performance.avg_win) },
    { label: 'Avg. Loss', value: formatCurrency(performance.avg_loss) },
    { label: 'Total Trades', value: positions.length },
  ];

  return (
    <Card>
      <CardHeader>
        <h2 className="text-lg font-semibold">Performance Summary</h2>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          {metrics.map((metric) => (
            <div key={metric.label} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg text-center">
              <div className="text-sm text-gray-500 dark:text-gray-400">{metric.label}</div>
              <div className="text-xl font-bold">{metric.value}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default BacktestSummary;
