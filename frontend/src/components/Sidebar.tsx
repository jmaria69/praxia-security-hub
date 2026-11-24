import React from 'react';
import { 
  Shield, 
  Lock, 
  Layers, 
  EyeOff, 
  FileText, 
  Settings as SettingsIcon, 
  Server
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab }) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: Shield },
    { id: 'projects', label: 'Project Security', icon: Layers },
    { id: 'bla', label: 'BLA Manager', icon: Lock },
    { id: 'privacy', label: 'Privacy Center', icon: EyeOff },
    { id: 'audit', label: 'Audit Center', icon: FileText },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 bg-[#0F172A] text-white flex flex-col min-h-screen border-r border-slate-800 shadow-xl">
      <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-[#0A66C2] flex items-center justify-center font-bold text-white shadow-lg shadow-blue-500/30">
          P
        </div>
        <div>
          <h1 className="font-bold text-lg leading-tight tracking-wide">PRAXIA LABS</h1>
          <p className="text-xs text-blue-400 font-mono tracking-wider">SECURITY HUB</p>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-[#0A66C2] text-white shadow-md shadow-blue-600/30'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800 text-xs text-slate-400">
        <div className="flex items-center space-x-2 mb-1">
          <Server className="w-3.5 h-3.5 text-[#10B981]" />
          <span className="text-slate-300 font-medium">Gateway 127.0.0.1:8888</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-[#10B981]"></div>
          <span>OmniRoute & Headroom Linked</span>
        </div>
      </div>
    </aside>
  );
};
