import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const navItems = [
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Live Feed', path: '/posts' },
  { name: 'Analytics', path: '/analytics' },
  { name: 'Test AI', path: '/test' },
];

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-200 transition-transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0`}>
        <nav className="p-4 space-y-2">
          {navItems.map(({ name, path }) => (
            <Link
              key={name}
              to={path}
              className={`block px-3 py-2 rounded ${location.pathname === path ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`}
              onClick={() => setSidebarOpen(false)}
            >
              {name}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && <div className="fixed inset-0 bg-black bg-opacity-25 md:hidden" onClick={() => setSidebarOpen(false)}></div>}

      {/* Main content */}
      <div className="flex-1 ml-0 md:ml-64">
        <header className="flex items-center justify-between p-4 bg-white border-b border-gray-200">
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="md:hidden p-2 rounded border border-gray-300">Menu</button>
          <h1 className="text-xl font-bold">VIP Threat Monitor</h1>
        </header>
        <main className="p-4">{children}</main>
      </div>
    </div>
  );
}
