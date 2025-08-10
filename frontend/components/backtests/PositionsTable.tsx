import React from 'react';
import { Card, CardContent, CardHeader } from 'components/ui/Card';
import { Table, THead, TBody, TR, TH, TD } from 'components/ui/Table';
import { Position } from 'types/api';
import clsx from 'clsx';

interface PositionsTableProps {
  positions: Position[];
}

const PositionsTable: React.FC<PositionsTableProps> = ({ positions }) => {
  const formatCurrency = (value: number | null) => value?.toLocaleString('en-US', { style: 'currency', currency: 'USD' }) ?? 'N/A';
  const formatDate = (value: string | null) => value ? new Date(value).toLocaleString() : 'N/A';

  return (
    <Card>
      <CardHeader>
        <h2 className="text-lg font-semibold">Positions</h2>
      </CardHeader>
      <CardContent>
        <Table>
          <THead>
            <TR>
              <TH>Symbol</TH>
              <TH>Side</TH>
              <TH>Quantity</TH>
              <TH>Entry Price</TH>
              <TH>Exit Price</TH>
              <TH>Entry Time</TH>
              <TH>Exit Time</TH>
              <TH>PNL</TH>
            </TR>
          </THead>
          <TBody>
            {positions.map((position, index) => (
              <TR key={index}>
                <TD>{position.symbol}</TD>
                <TD>
                  <span className={clsx(
                    'px-2 py-1 rounded-full text-xs font-semibold',
                    {
                      'bg-green-100 text-green-800': position.side === 'long',
                      'bg-red-100 text-red-800': position.side === 'short',
                    }
                  )}>
                    {position.side}
                  </span>
                </TD>
                <TD>{position.quantity}</TD>
                <TD>{formatCurrency(position.entry_price)}</TD>
                <TD>{formatCurrency(position.exit_price)}</TD>
                <TD>{formatDate(position.entry_time)}</TD>
                <TD>{formatDate(position.exit_time)}</TD>
                <TD className={clsx({
                  'text-green-600': position.pnl > 0,
                  'text-red-600': position.pnl < 0,
                })}>
                  {formatCurrency(position.pnl)}
                </TD>
              </TR>
            ))}
          </TBody>
        </Table>
      </CardContent>
    </Card>
  );
};

export default PositionsTable;
