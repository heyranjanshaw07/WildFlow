import React from 'react';
import { Wind, Activity, Clock, ShieldCheck, BarChart2, Layers } from 'lucide-react';
import { ActiveTab } from '../types';
import { formatFetchDate } from '../utils/formatters';

interface HeaderProps {
  activeTab: ActiveTab;
  onSelectTab: (tab: ActiveTab) => void;
  statusText?: string;
  fetchDate?: string;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onSelectTab,
  fetchDate
}) => {
  const tabs: { id: ActiveTab; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Dashboard & Time Series', icon: <Activity className="w-4 h-4" /> },
    { id: 'accuracy', label: 'Accuracy & Bias', icon: <BarChart2 className="w-4 h-4" /> },
    { id: 'vintages', label: 'Lead-Time & Vintages', icon: <Clock className="w-4 h-4" /> },
    { id: 'risk', label: 'Forecast Risk (Uncertainty)', icon: <ShieldCheck className="w-4 h-4" /> },
    { id: 'quality', label: 'Data Quality & Provenance', icon: <Layers className="w-4 h-4" /> },
  ];

  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-30 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Platform Info (Clicking navigates to Home / Overview) */}
          <button
            onClick={() => onSelectTab('overview')}
            className="flex items-center gap-3 text-left focus:outline-none focus:ring-2 focus:ring-blue-500/50 rounded-lg p-1 -ml-1 transition-all hover:opacity-90 cursor-pointer group"
            title="Go to Home / Dashboard"
          >
            <div className="w-9 h-9 bg-blue-600 group-hover:bg-blue-500 rounded-lg flex items-center justify-center text-white shadow-inner transition-colors">
              <Wind className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-base tracking-tight text-white group-hover:text-blue-200 transition-colors">WindScope</span>
                <span className="text-[10px] font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30 px-1.5 py-0.5 rounded tracking-wide uppercase">
                  UK Day-Ahead
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Renewable Generation Forecast Intelligence Platform
              </p>
            </div>
          </button>

          {/* Status Badge */}
          <div className="flex items-center gap-2 text-xs text-slate-300 bg-slate-800/80 border border-slate-700/60 px-3 py-1.5 rounded-full">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shrink-0"></span>
            <span className="font-medium text-slate-200">
              Historical data · Elexon, fetched {formatFetchDate(fetchDate)} · Decisions: Jan 2026
            </span>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 overflow-x-auto no-scrollbar border-t border-slate-800/80 pt-1 -mb-px">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onSelectTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2.5 text-xs font-medium border-b-2 whitespace-nowrap transition-colors ${
                  isActive
                    ? 'border-blue-500 text-blue-400 bg-blue-500/10'
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-600'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
