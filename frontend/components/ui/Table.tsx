import React from 'react';
import clsx from 'clsx';

type TableRootProps = React.HTMLAttributes<HTMLTableElement> & { compact?: boolean };
export const Table: React.FC<TableRootProps> = ({ className, compact, ...props }) => (
  <table className={clsx('table-root', compact ? 'text-xs' : 'text-sm', className)} {...props} />
);

export const THead: React.FC<React.HTMLAttributes<HTMLTableSectionElement>> = ({
  className,
  ...props
}) => <thead className={clsx('table-head', className)} {...props} />;

export const TBody: React.FC<React.HTMLAttributes<HTMLTableSectionElement>> = ({
  className,
  ...props
}) => <tbody className={clsx(className)} {...props} />;

export const TR: React.FC<React.HTMLAttributes<HTMLTableRowElement>> = ({ className, ...props }) => (
  <tr className={clsx('table-row', className)} {...props} />
);

export const TH: React.FC<React.ThHTMLAttributes<HTMLTableCellElement>> = ({
  className,
  ...props
}) => <th className={clsx('px-3 py-2 font-medium', className)} {...props} />;

export const TD: React.FC<React.TdHTMLAttributes<HTMLTableCellElement>> = ({
  className,
  ...props
}) => <td className={clsx('px-3 py-2', className)} {...props} />;

export default Object.assign(Table, { Head: THead, Body: TBody, Row: TR, TH, TD });