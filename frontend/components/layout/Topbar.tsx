import React from 'react';
import Button from 'components/ui/Button';

type TopbarProps = {
  onMenuClick?: () => void;
};

const Topbar: React.FC<TopbarProps> = ({ onMenuClick }) => {
  return (
    <div className="container-responsive flex h-14 items-center justify-between">
      <div className="flex items-center gap-2">
        <Button variant="secondary" className="lg:hidden" onClick={onMenuClick} aria-label="Toggle sidebar">
          ☰
        </Button>
        <span className="hidden text-sm text-gray-500 sm:inline">Backtrader Dashboard</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-600">v0.1.0</span>
      </div>
    </div>
  );
};

export default React.memo(Topbar);