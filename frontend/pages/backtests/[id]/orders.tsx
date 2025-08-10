import { useRouter } from 'next/router';
import useOrders from '../../../hooks/useOrders';
import Card from '../../../components/ui/Card';
import EmptyState from '../../../components/ui/EmptyState';
import ErrorState from '../../../components/ui/ErrorState';
import { OrdersTable } from '../../../components/orders/OrdersTable';

export default function BacktestOrdersPage() {
  const router = useRouter();
  const { id } = router.query;
  const backtestId = typeof id === 'string' ? id : '';

  const { data: orders, isLoading, error } = useOrders(backtestId);

  if (isLoading) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Orders for Backtest {backtestId}</h1>
        <Card>
          <p>Loading orders...</p>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Orders for Backtest {backtestId}</h1>
        <ErrorState title="Error" message="Failed to load orders." />
      </div>
    );
  }

  if (!orders || orders.length === 0) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Orders for Backtest {backtestId}</h1>
        <EmptyState title="No Orders" description="No orders were found for this backtest." />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Orders for Backtest {backtestId}</h1>
      <Card>
        <OrdersTable orders={orders} />
      </Card>
    </div>
  );
}
