import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  CreditCard, 
  MessageSquare,
  Radio,
  Settings
} from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard', exact: true },
    { path: '/users', icon: Users, label: 'User Management' },
    { path: '/payments', icon: CreditCard, label: 'Payments' },
    { path: '/broadcast', icon: MessageSquare, label: 'Broadcast' },
  ];

  return (
    <div className="h-screen w-64 bg-gradient-to-b from-blue-900 via-blue-800 to-indigo-900 text-white fixed left-0 top-0 shadow-2xl">
      {/* Logo/Brand */}
      <div className="p-6 border-b border-blue-700/50">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
            <Radio className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold">OTT Bot Admin</h1>
            <p className="text-xs text-blue-300">Management Dashboard</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.exact}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                isActive
                  ? 'bg-blue-600 shadow-lg'
                  : 'hover:bg-blue-800/50'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-blue-700/50">
        <div className="flex items-center space-x-2 text-sm text-blue-300">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span>Bot Active</span>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
