import React from 'react';
import clsx from 'clsx';

type SkeletonProps = {
  className?: string;
};

const Skeleton: React.FC<SkeletonProps> = ({ className }) => {
  return <div className={clsx('skeleton', className)} aria-hidden="true" />;
};

export default React.memo(Skeleton);