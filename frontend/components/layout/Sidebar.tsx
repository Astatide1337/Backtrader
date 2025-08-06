import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

type SidebarProps = {
  onNavigate?: () => void;
};

const NavItem: React.FC<{ href: string; label: string; onClick?: () => void }> = ({
  href,
  label,
  onClick,
}) => {
  const router = useRouter();
  const active = router.pathname === href;
  return (
    <Link
      href={href}
      onClick={onClick}
      className={[
        'block rounded-md px-3 py-2 text-sm font-medium',
        active ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50',
      ].join(' ')}
    >
      {label}
    </Link>
  );
};

const Sidebar: React.FC<SidebarProps> = ({ onNavigate }) => {
  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b">
        <Link href="/" onClick={onNavigate} className="text-lg font-semibold text-gray-900">
          Backtrader
        </Link>
        <p className="mt-1 text-xs text-gray-500">Dashboard</p>
      </div>
      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        <NavItem href="/" label="Home" onClick={onNavigate} />
        <NavItem href="/backtests" label="Backtests" onClick={onNavigate} />
        <NavItem href="/orders" label="Orders" onClick={onNavigate} />
        <NavItem href="/strategies" label="Strategies" onClick={onNavigate} />
      </nav>
      <div className="p-4 border-t text-xs text-gray-500">
        v0.1.0 • Next.js • SWR
      </div>
    </div>
  );
};

export default React.memo(Sidebar);