import React from 'react';
import Link from 'next/link';
import useSWR from 'swr';
import useStrategies from 'hooks/useStrategies';
import Card from 'components/ui/Card';
import { CardHeader, CardContent } from 'components/ui/Card';
import Skeleton from 'components/ui/Skeleton';
import EmptyState from 'components/ui/EmptyState';
import ErrorState from 'components/ui/ErrorState';
import Table from 'components/ui/Table';
import { THead, TBody, TR, TH, TD } from 'components/ui/Table';
import Button from 'components/ui/Button';
import { deleteCustomStrategy } from 'lib/customStrategies';

const StrategiesPage: React.FC = () => {
  const { data, isLoading, error, mutate } = useStrategies();

  React.useEffect(() => {
    if (data) {
      console.log('Available strategies:', data);
    }
  }, [data]);

  async function handleDelete(id: string) {
    if (window.confirm('Are you sure you want to delete this strategy?')) {
      try {
        await deleteCustomStrategy(id);
        mutate();
      } catch (error) {
        console.error('Failed to delete strategy:', error);
      }
    }
  }

  function useStrategy(name: string) {
    // simplest approach: navigate to /backtests/new with preselected strategy via query string
    const params = new URLSearchParams({ strategy: name }).toString();
    window.location.href = `/backtests/new?${params}`;
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex w-full items-center justify-between">
            <div className="text-sm font-semibold text-gray-900">Strategies</div>
            <Link href="/strategies/new">
              <Button size="sm">New Strategy</Button>
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : error ? (
            <ErrorState message="Failed to load strategies." />
          ) : data && data.length > 0 ? (
            <Table compact>
              <THead>
                <TR>
                  <TH>Name</TH>
                  <TH>Description</TH>
                  <TH className="w-48 text-center">Action</TH>
                </TR>
              </THead>
              <TBody>
                {data.map((s) => (
                  <TR key={(s as any).id ?? s.name}>
                    <TD className="font-medium">{s.name}</TD>
                    <TD className="text-gray-600">{s.description ?? '—'}</TD>
                    <TD className="text-right">
                      <div className="flex items-center justify-end space-x-2">
                        {(s as any).is_custom ? (
                          <>
                            <Link href={`/strategies/custom/${(s as any).id}`}>
                              <Button variant="secondary" className="px-3 py-1 text-xs">
                                View
                              </Button>
                            </Link>
                            <Button
                              variant="secondary"
                              className="px-3 py-1 text-xs"
                              onClick={() => handleDelete((s as any).id)}
                            >
                              Delete
                            </Button>
                          </>
                        ) : (
                          <Button
                            variant="secondary"
                            className="px-3 py-1 text-xs"
                            onClick={() => useStrategy(s.name)}
                          >
                            Use Strategy
                          </Button>
                        )}
                      </div>
                    </TD>
                  </TR>
                ))}
              </TBody>
            </Table>
          ) : (
            <EmptyState title="No strategies" description="No strategies available." />
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default StrategiesPage;
