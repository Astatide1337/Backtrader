import React from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import Card, { CardContent, CardHeader } from 'components/ui/Card';
import Button from 'components/ui/Button';
import Skeleton from 'components/ui/Skeleton';
import ErrorState from 'components/ui/ErrorState';
import { useCustomStrategy } from 'hooks/useCustomStrategies';

const CustomStrategyDetailPage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query as { id?: string };
  const { data, error, isLoading } = useCustomStrategy(id);

  const useStrategy = React.useCallback(() => {
    if (!id) return;
    const qs = new URLSearchParams({ strategy: `custom:${id}` }).toString();
    router.push(`/backtests/new?${qs}`);
  }, [id, router]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-gray-900">Custom Strategy</h1>
          <p className="text-sm text-gray-600">Summary and JSON for your custom strategy.</p>
        </div>
        <div className="flex gap-2">
          <Link href="/strategies/new" className="hidden md:inline-block">
            <Button variant="secondary" size="sm">New Strategy</Button>
          </Link>
          <Button size="sm" onClick={useStrategy} disabled={!id}>
            Use Strategy
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="text-sm font-semibold text-gray-900">Summary</div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : error ? (
            <ErrorState message="Failed to load custom strategy." />
          ) : !data ? (
            <ErrorState message="Strategy not found." />
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="space-y-2 rounded-md border p-3 text-sm">
                <div><span className="font-medium">Name:</span> {data.strategy.basics.name || '—'}</div>
                <div><span className="font-medium">Status:</span> {data.status}</div>
                <div><span className="font-medium">Created:</span> {new Date(data.created_at).toLocaleString()}</div>
                <div><span className="font-medium">Updated:</span> {new Date(data.updated_at).toLocaleString()}</div>
                <div><span className="font-medium">Indicators:</span> {data.strategy.indicators.length}</div>
                <div><span className="font-medium">Entry groups:</span> {data.strategy.entry.groups.length}</div>
                <div><span className="font-medium">Exit groups:</span> {data.strategy.exit?.groups?.length ?? 0}</div>
                <div><span className="font-medium">Sizing:</span> {data.strategy.sizing.mode}</div>
                <div><span className="font-medium">Advanced exprs:</span> {data.strategy.advanced?.expressions?.length ?? 0}</div>
              </div>
              <div>
                <div className="mb-2 text-sm font-semibold text-gray-900">JSON</div>
                <pre className="max-h-[420px] overflow-auto rounded-md border p-3 text-xs">
{JSON.stringify(data.strategy, null, 2)}
                </pre>
                <div className="mt-3">
                  <Button onClick={useStrategy}>Use Strategy</Button>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CustomStrategyDetailPage;