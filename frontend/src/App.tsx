import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Overview } from './pages/Overview';
import { ProjectSecurity } from './pages/ProjectSecurity';
import { BLAManager } from './pages/BLAManager';
import { PrivacyCenter } from './pages/PrivacyCenter';
import { AuditCenter } from './pages/AuditCenter';
import { Settings } from './pages/Settings';
import { ShieldCheck, UserCheck } from 'lucide-react';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState('overview');

  const renderContent = () => {
    switch (currentTab) {
      case 'overview':
        return <Overview />;
      case 'projects':
        return <ProjectSecurity />;
      case 'bla':
        return <BLAManager />;
      case 'privacy':
        return <PrivacyCenter />;
      case 'audit':
        return <AuditCenter />;
      case 'settings':
        return <Settings />;
      default:
        return <Overview />;
    }
  };

  return (
    <div className="flex min-h-screen bg-[#F3F6F8]">
      <Sidebar currentTab={currentTab} onSelectTab={setCurrentTab} />
      
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-10 shadow-sm">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-blue-50 text-[#0A66C2] border border-blue-200">
              PRAXIA SECURITY HUB
            </span>
            <span className="text-xs text-slate-400">|</span>
            <span className="text-xs text-slate-500 font-medium">WSL2 Ubuntu • NVIDIA RTX 5080 • OmniRoute • Headroom</span>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-xs text-slate-600 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span className="font-semibold text-slate-800">SecOps Ready</span>
            </div>
            <div className="flex items-center space-x-2 text-xs text-slate-600">
              <div className="w-7 h-7 rounded-full bg-[#0A66C2] text-white flex items-center justify-center font-bold text-xs">
                PL
              </div>
              <span className="font-semibold text-slate-800">Admin</span>
            </div>
          </div>
        </header>

        {/* Main Content Body */}
        <main className="flex-1 p-8 max-w-7xl w-full mx-auto">
          {renderContent()}
        </main>
      </div>
    </div>
  );
};

export default App;
