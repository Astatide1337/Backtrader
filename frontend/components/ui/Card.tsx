import React from 'react';
import clsx from 'clsx';

type CardProps = {
  className?: string;
  children: React.ReactNode;
};

export const Card: React.FC<CardProps> = ({ className, children }) => {
  return <div className={clsx('card', className)}>{children}</div>;
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => {
  return (
    <div className={clsx('card-header', className)} {...props}>
      {children}
    </div>
  );
};

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => {
  return (
    <div className={clsx('card-content', className)} {...props}>
      {children}
    </div>
  );
};

export default Object.assign(Card, { Header: CardHeader, Content: CardContent });