import React from 'react';
import { Calendar, Clock, Download, RefreshCw, AlertTriangle } from 'lucide-react';

import { formatUnambiguousDate } from '../utils/formatters';

interface ControlsProps {
  cutoffTime: string;
  onCutoffChange: (time: string) => void;
  startDate: string;
  endDate: string;
  onStartDateChange: (date: string) => void;
  onEndDateChange: (date: string) => void;
  onResetFilters: () => void;
  onExportCsv: () => void;
  isLoading: boolean;
}

export const Controls: React.FC<ControlsProps> = ({
  cutoffTime,
  onCutoffChange,
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  onResetFilters,
  onExportCsv,
  isLoading
}) => {
  const cutoffOptions = [
    { value: '09:00', label: '09:00 London (Default Cutoff)' },
    { value: '12:00', label: '12:00 London (Comparison Cutoff)' },
    { value: '15:00', label: '15:00 London (Afternoon Cutoff)' },
  ];

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm mb-6">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left: Interactive Filter Controls */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Decision Cutoff Selector */}
          <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs">
            <Clock className="w-3.5 h-3.5 text-slate-500" />
            <span className="font-semibold text-slate-700">D-1 Cutoff:</span>
            <select
              value={cutoffTime}
              onChange={(e) => onCutoffChange(e.target.value)}
              className="bg-transparent font-medium text-slate-900 border-none outline-none cursor-pointer focus:ring-0 text-xs py-0 pl-1 pr-6"
            >
              {cutoffOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Date Range Selectors */}
          <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs">
            <Calendar className="w-3.5 h-3.5 text-slate-500" />
            <span className="font-semibold text-slate-700">Delivery:</span>
            <span className="font-semibold text-blue-900 bg-blue-100/70 px-2 py-0.5 rounded border border-blue-200/60">
              "{formatUnambiguousDate(startDate)}" to "{formatUnambiguousDate(endDate)}"
            </span>
            <span className="text-slate-400">|</span>
            <input
              type="date"
              min="2026-01-02"
              max="2026-02-01"
              value={startDate}
              onChange={(e) => onStartDateChange(e.target.value)}
              className="bg-transparent text-slate-600 border-none outline-none text-xs p-0 w-24 cursor-pointer"
              title="Change start date"
            />
            <span className="text-slate-400">to</span>
            <input
              type="date"
              min="2026-01-02"
              max="2026-02-01"
              value={endDate}
              onChange={(e) => onEndDateChange(e.target.value)}
              className="bg-transparent text-slate-600 border-none outline-none text-xs p-0 w-24 cursor-pointer"
              title="Change end date"
            />
          </div>

          {/* Quick Filter Reset */}
          <button
            onClick={onResetFilters}
            className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
            title="Reset to full January scope (Jan 2 to Feb 1 at 09:00 cutoff)"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            Reset
          </button>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-3">
          <button
            onClick={onExportCsv}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            Export Filtered CSV
          </button>
        </div>
      </div>

      {/* Assumption Alert Banner */}
      <div className="mt-3.5 pt-3 border-t border-slate-100 flex items-start gap-2 text-xs text-amber-800 bg-amber-50/70 p-2.5 rounded-lg border border-amber-200/60">
        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-amber-900">Assumed decision cutoff (configurable): </span>
          For delivery day D, decisions are modelled using the latest forecast available on or before {cutoffTime} Europe/London on day D-1.
          This is an operational workflow assumption for wholesale procurement modelling, not a statutory market gate closure.
          Strict anti-lookahead rules guarantee that forecasts published after {cutoffTime} on D-1 are never selected.
        </div>
      </div>
    </div>
  );
};
