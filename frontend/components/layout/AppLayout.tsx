import React, { useState, useCallback } from 'react';
import Sidebar from 'components/layout/Sidebar';
import Topbar from 'components/layout/Topbar';

type Props = {
  children: React.ReactNode;
};

const AppLayout: React.FC<Props> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const toggleSidebar = useCallback(() => setSidebarOpen((s) => !s), []);
  const closeSidebar = useCallback(() => setSidebarOpen(false), []);

  return (
    <div className="layout-root">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/30 lg:hidden"
          onClick={closeSidebar}
          aria-hidden="true"
        />
      )}

      <aside
        className={[
          'sidebar fixed inset-y-0 left-0 z-40 w-64 transform bg-white transition-transform duration-200 ease-in-out',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full',
          'lg:translate-x-0 lg:static lg:inset-auto',
        ].join(' ')}
        aria-label="Sidebar"
      >
        <Sidebar onNavigate={closeSidebar} />
      </aside>

      <div className="lg:pl-64">
        <header className="topbar sticky top-0 z-20">
          <Topbar onMenuClick={toggleSidebar} />
        </header>
        <main className="container-responsive py-6">{children}</main>
      </div>
    </div>
  );
};

export default React.memo(AppLayout);