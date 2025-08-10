import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader } from 'components/ui/Card';
import { Table, THead, TBody, TR, TH, TD } from 'components/ui/Table';
import Input from 'components/ui/Input';
import Button from 'components/ui/Button';

type SortKey = 'id' | 'symbol' | 'side' | 'qty' | 'price' | 'timestamp';
type SortDirection = 'asc' | 'desc';

interface OrdersLogProps {
  orders: any[];
}

const PAGE_SIZE = 10;

const OrdersLog: React.FC<OrdersLogProps> = ({ orders }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState<{ key: SortKey; direction: SortDirection } | null>(null);
  const [page, setPage] = useState(1);

  const filteredOrders = useMemo(() => {
    return orders.filter(order =>
      Object.values({
        ...order,
        quantity: String(order.qty), // Convert quantity to string
      }).some(value =>
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  }, [orders, searchTerm]);

  const sortedOrders = useMemo(() => {
    let sortableOrders = [...filteredOrders];
    if (sortConfig !== null) {
      sortableOrders.sort((a, b) => {
        const aValue = a[sortConfig.key];
        const bValue = b[sortConfig.key];

        if (typeof aValue === 'string' && typeof bValue === 'string') {
          return sortConfig.direction === 'asc'
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue);
        }
        if (typeof aValue === 'number' && typeof bValue === 'number') {
          return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
        }
        return 0;
      });
    }
    return sortableOrders;
  }, [filteredOrders, sortConfig]);

  const pagedOrders = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return sortedOrders.slice(start, start + PAGE_SIZE);
  }, [sortedOrders, page]);

  const totalPages = Math.max(1, Math.ceil(sortedOrders.length / PAGE_SIZE));

  const requestSort = (key: SortKey) => {
    let direction: SortDirection = 'asc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const getClassNamesFor = (name: SortKey) => {
    if (!sortConfig) {
      return;
    }
    return sortConfig.key === name ? sortConfig.direction : undefined;
  };

  const handleDownloadCSV = () => {
    const headers = ['Order ID', 'Symbol', 'Side', 'Quantity', 'Price', 'Timestamp'];
    const rows = sortedOrders.map(order => [
      order.id,
      order.symbol,
      order.side,
      order.quantity,
      order.price,
      order.timestamp,
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(',')),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', 'orders.csv');
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <Card>
      <CardHeader>
        <h2 className="text-lg font-semibold">Orders Log</h2>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between items-center mb-4">
          <Input
            type="text"
            placeholder="Search orders..."
            value={searchTerm}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
            className="w-full max-w-xs"
          />
          <Button onClick={handleDownloadCSV} variant="secondary">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            CSV
          </Button>
        </div>
        <Table>
          <THead>
            <TR>
              <TH className="cursor-pointer" onClick={() => requestSort('id')}>
                Order ID <span className={getClassNamesFor('id')}></span>
              </TH>
              <TH className="cursor-pointer" onClick={() => requestSort('symbol')}>
                Symbol <span className={getClassNamesFor('symbol')}></span>
              </TH>
              <TH className="cursor-pointer" onClick={() => requestSort('side')}>
                Side <span className={getClassNamesFor('side')}></span>
              </TH>
              <TH className="cursor-pointer" onClick={() => requestSort('qty')}>
                Quantity <span className={getClassNamesFor('qty')}></span>
              </TH>
              <TH className="cursor-pointer" onClick={() => requestSort('price')}>
                Price <span className={getClassNamesFor('price')}></span>
              </TH>
              <TH className="cursor-pointer" onClick={() => requestSort('timestamp')}>
                Timestamp <span className={getClassNamesFor('timestamp')}></span>
              </TH>
            </TR>
          </THead>
          <TBody>
            {pagedOrders.map((order) => (
              <TR key={order.id}>
                <TD>{order.id}</TD>
                <TD>{order.symbol}</TD>
                <TD>{order.side}</TD>
                <TD>{order.qty}</TD>
                <TD>{order.price.toFixed(2)}</TD>
                <TD>{new Date(order.timestamp).toLocaleString()}</TD>
              </TR>
            ))}
          </TBody>
        </Table>
        <div className="mt-4 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Page {page} of {totalPages}
          </div>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            >
              Next
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default OrdersLog;
