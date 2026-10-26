import React from 'react';
import { CheckCircle2 } from 'lucide-react';
import { SummaryMetrics } from '../types';

interface MetricCardsProps {
  metrics: SummaryMetrics | null;
  cutoffTime?: string;
}

export const MetricCards: React.FC<MetricCardsProps> = ({ metrics }) => {
  if (!metrics) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white border border-slate-200 rounded-xl p-4 animate-pulse h-24"></div>
        ))}
      </div>
    );
  }

  const isOverforecast = (metrics.mbe || 0) > 0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
      {/* 1. MAE */}
      <div className="bg-white border border-slate-200 rounded-xl p-3.5 shadow-sm hover:border-slate-300 transition-colors">
        <div className="flex items-center justify-between text-slate-500 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">MAE</span>
          <span className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-mono">MW</span>
        </div>
        <div className="text-xl font-bold text-slate-900 tracking-tight">
          {metrics.mae !== null ? `${metrics.mae.toLocaleString()}` : '—'}
        </div>
        <p className="text-[11px] text-slate-500 mt-1 truncate">Mean absolute error</p>
      </div>

      {/* 2. RMSE */}
      <div className="bg-white border border-slate-200 rounded-xl p-3.5 shadow-sm hover:border-slate-300 transition-colors">
        <div className="flex items-center justify-between text-slate-500 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">RMSE</span>
          <span className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-mono">MW</span>
        </div>
        <div className="text-xl font-bold text-slate-900 tracking-tight">
          {metrics.rmse !== null ? `${metrics.rmse.toLocaleString()}` : '—'}
        </div>
        <p className="text-[11px] text-slate-500 mt-1 truncate">Penalizes large misses</p>
      </div>

      {/* 3. WAPE */}
      <div className="bg-white border border-slate-200 rounded-xl p-3.5 shadow-sm hover:border-slate-300 transition-colors">
        <div className="flex items-center justify-between text-slate-500 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">WAPE</span>
          <span className="text-[10px] bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded font-mono">%</span>
        </div>
        <div className="text-xl font-bold text-blue-700 tracking-tight">
          {metrics.wape !== null ? `${metrics.wape}%` : '—'}
        </div>
        <p className="text-[11px] text-slate-500 mt-1 truncate">Weighted error rate</p>
      </div>

      {/* 4. Mean Bias Error (MBE) */}
      <div className="bg-white border border-slate-200 rounded-xl p-3.5 shadow-sm hover:border-slate-300 transition-colors">
        <div className="flex items-center justify-between text-slate-500 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Mean Bias</span>
          <span className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${isOverforecast ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800'}`}>
            {isOverforecast ? 'OVER' : 'UNDER'}
          </span>
        </div>
        <div className={`text-xl font-bold tracking-tight ${isOverforecast ? 'text-amber-800' : 'text-blue-800'}`}>
          {metrics.mbe !== null ? `${metrics.mbe > 0 ? '+' : ''}${metrics.mbe.toLocaleString()}` : '—'}
          <span className="text-xs font-normal text-slate-500 ml-1">MW</span>
        </div>
        <p className="text-[11px] text-slate-500 mt-1 truncate">Forecast minus actual</p>
      </div>

      {/* 5. Hourly Evaluation Coverage */}
      <div className="bg-white border border-slate-200 rounded-xl p-3.5 shadow-sm hover:border-slate-300 transition-colors">
        <div className="flex items-center justify-between text-slate-500 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Evaluation Set</span>
          <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-semibold flex items-center gap-0.5">
            <CheckCircle2 className="w-2.5 h-2.5" />
            {metrics.hourlyCoveragePct}%
          </span>
        </div>
        <div className="text-xl font-bold text-slate-900 tracking-tight">
          {metrics.evaluatedHourlyPeriods}
          <span className="text-xs font-normal text-slate-400 ml-1">/ {metrics.expectedHourlyPeriods}</span>
        </div>
        <p className="text-[11px] text-slate-500 mt-1 truncate" title="744 hourly periods matched; 744 :30 periods unforecasted by design">
          744 hourly periods matched
        </p>
      </div>

      {/* 6. Approximate Energy Volume */}
      <div className="bg-white border border-slate-200 rounded-xl p-3.5 shadow-sm hover:border-slate-300 transition-colors">
        <div className="flex items-center justify-between text-slate-500 mb-1">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Total Energy (approx.)</span>
          <span className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-mono">GWh*</span>
        </div>
        <div className="text-xl font-bold text-slate-900 tracking-tight">
          {Math.round(metrics.approxTotalActualEnergyMWh / 1000).toLocaleString()}
          <span className="text-xs font-normal text-slate-500 ml-1">GWh actual</span>
        </div>
        <p className="text-[11px] text-slate-500 mt-1 truncate" title="Approximate: sum of hourly-sampled MW x 1h, :00 samples only">
          vs {Math.round(metrics.approxTotalForecastEnergyMWh / 1000).toLocaleString()} GWh forecast
        </p>
        <div className="text-[10px] text-slate-400 mt-1 pt-1 border-t border-slate-100 truncate" title="*Footnote: Sum of hourly MW × 1h (:00 samples only; excludes :30 periods)">
          *Footnote: :00 MW × 1h only
        </div>
      </div>
    </div>
  );
};
