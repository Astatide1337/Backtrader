import React, { useState, useMemo } from 'react';
import { Order } from '../../types/api';
import Input from '../ui/Input';
import Button from '../ui/Button';

type SortKey = 'id' | 'symbol' | 'side' | 'qty' | 'price' | 'timestamp';
type SortDirection = 'asc' | 'desc';

interface OrdersTableProps {
  orders: Order[];
}

export const OrdersTable: React.FC<OrdersTableProps> = ({ orders }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState<{ key: SortKey; direction: SortDirection } | null>(null);

  const filteredOrders = useMemo(() => {
    return orders.filter(order =>
      Object.values(order).some(value =>
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
        // Fallback for mixed types or other types
        return 0;
      });
    }
    return sortableOrders;
  }, [filteredOrders, sortConfig]);

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
      order.qty,
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
    <div className="flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <Input
          type="text"
          placeholder="Search orders..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full max-w-xs"
        />
        <Button onClick={handleDownloadCSV}>Download CSV</Button>
      </div>
      <div className="overflow-x-auto relative shadow-md sm:rounded-lg">
        <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
          <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
            <tr>
              <th scope="col" className="py-3 px-6 cursor-pointer" onClick={() => requestSort('id')}>
                Order ID
                <span className={getClassNamesFor('id')}></span>
              </th>
              <th scope="col" className="py-3 px-6 cursor-pointer" onClick={() => requestSort('symbol')}>
                Symbol
                <span className={getClassNamesFor('symbol')}></span>
              </th>
              <th scope="col" className="py-3 px-6 cursor-pointer" onClick={() => requestSort('side')}>
                Side
                <span className={getClassNamesFor('side')}></span>
              </th>
              <th scope="col" className="py-3 px-6 cursor-pointer" onClick={() => requestSort('qty')}>
                Quantity
                <span className={getClassNamesFor('qty')}></span>
              </th>
              <th scope="col" className="py-3 px-6 cursor-pointer" onClick={() => requestSort('price')}>
                Price
                <span className={getClassNamesFor('price')}></span>
              </th>
              <th scope="col" className="py-3 px-6 cursor-pointer" onClick={() => requestSort('timestamp')}>
                Timestamp
                <span className={getClassNamesFor('timestamp')}></span>
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedOrders.map((order) => (
              <tr key={order.id} className="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
                <td className="py-4 px-6">{order.id}</td>
                <td className="py-4 px-6">{order.symbol}</td>
                <td className="py-4 px-6">{order.side}</td>
                <td className="py-4 px-6">{order.qty}</td>
                <td className="py-4 px-6">{order.price}</td>
                <td className="py-4 px-6">{new Date(order.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
