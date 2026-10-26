import React from 'react';
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { ProcurementRiskResponse } from '../types';
import { AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';

interface RiskViewProps {
  data: ProcurementRiskResponse;
  cutoffTime: string;
}

export const RiskView: React.FC<RiskViewProps> = ({ data, cutoffTime }) => {
  const q = data.overallErrorQuantilesMW;

  return (
    <div className="space-y-6">
      {/* 1. Mandatory Risk Disclaimer Banner */}
      <div className="bg-amber-50 border border-amber-300/80 rounded-xl p-4 text-amber-900 shadow-sm flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div className="text-xs">
          <h4 className="font-bold text-amber-950 text-sm mb-0.5">{data.label}</h4>
          <p className="leading-relaxed text-amber-900/90 font-medium">
            {data.disclaimer}
          </p>
          <p className="text-[11px] text-amber-800/80 mt-1">
            Note: Quantiles represent empirical distribution of historical forecast errors (Forecast - Actual) for January 2026 under the {cutoffTime} D-1 cutoff.
            No bias correction has been applied to raw forecasts, and no external demand assumptions have been invented.
          </p>
        </div>
      </div>

      {/* 2. Empirical Quantile KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* P10 (Downside Error) */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <span className="text-[10px] font-bold uppercase text-slate-500 tracking-wider block mb-1">
            P10 Forecast Error
          </span>
          <div className="text-2xl font-black text-blue-700 tracking-tight font-mono">
            {q.quantileP10 > 0 ? '+' : ''}{q.quantileP10.toLocaleString()} MW
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            10% of periods have errors below this level (under-forecast or mild over-forecast).
          </p>
        </div>

        {/* P50 (Median Error) */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <span className="text-[10px] font-bold uppercase text-slate-500 tracking-wider block mb-1">
            P50 Median Error
          </span>
          <div className="text-2xl font-black text-amber-700 tracking-tight font-mono">
            +{q.quantileP50Median.toLocaleString()} MW
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            Empirical median forecast miss (50% above, 50% below).
          </p>
        </div>

        {/* P90 (Upside Overforecast) */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <span className="text-[10px] font-bold uppercase text-slate-500 tracking-wider block mb-1">
            P90 Forecast Error
          </span>
          <div className="text-2xl font-black text-rose-700 tracking-tight font-mono">
            +{q.quantileP90.toLocaleString()} MW
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            10% of periods see an overforecast miss exceeding this extreme value.
          </p>
        </div>

        {/* Over/Under Frequency */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <span className="text-[10px] font-bold uppercase text-slate-500 tracking-wider block mb-1">
            Directional Error Frequency
          </span>
          <div className="space-y-1.5 mt-2">
            <div className="flex justify-between text-xs">
              <span className="text-amber-800 font-semibold flex items-center gap-1">
                <TrendingUp className="w-3.5 h-3.5" /> Overforecast:
              </span>
              <span className="font-mono font-bold text-amber-800">{q.overforecastFrequencyPct}%</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden flex">
              <div className="bg-amber-500 h-full" style={{ width: `${q.overforecastFrequencyPct}%` }}></div>
              <div className="bg-blue-500 h-full" style={{ width: `${q.underforecastFrequencyPct}%` }}></div>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-blue-800 font-semibold flex items-center gap-1">
                <TrendingDown className="w-3.5 h-3.5" /> Underforecast:
              </span>
              <span className="font-mono font-bold text-blue-800">{q.underforecastFrequencyPct}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Diurnal Empirical Quantiles Profile Chart */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div className="mb-4">
          <h4 className="text-sm font-bold text-slate-900 tracking-tight">
            Diurnal Empirical Error Quantiles (P10, P50 Median, P90 in MW)
          </h4>
          <p className="text-xs text-slate-500 mt-0.5">
            Shows the empirical error spread by hour of day (00:00 to 23:00). Notice wide positive error bands overnight.
          </p>
        </div>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data.hourlyRiskProfile} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="hourLabel" tickLine={false} fontSize={10} stroke="#64748b" />
              <YAxis tickLine={false} fontSize={10} stroke="#64748b" unit=" MW" tickFormatter={(val) => `${val / 1000}k`} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                formatter={(val: any, name: any) => [`${Number(val).toLocaleString()} MW`, name]}
              />
              <Legend wrapperStyle={{ fontSize: '11px' }} />
              <Line type="monotone" dataKey="p90ErrorMW" name="P90 Error (MW)" stroke="#e11d48" strokeWidth={2} dot={false} strokeDasharray="3 3" />
              <Line type="monotone" dataKey="p50ErrorMW" name="P50 Median Error (MW)" stroke="#d97706" strokeWidth={2.5} dot={false} />
              <Line type="monotone" dataKey="p10ErrorMW" name="P10 Error (MW)" stroke="#2563eb" strokeWidth={2} dot={false} strokeDasharray="3 3" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 4. Table of Hourly Risk Profile */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <h4 className="text-sm font-bold text-slate-900 tracking-tight mb-3">
          Hourly Error Quantile Matrix
        </h4>
        <div className="overflow-x-auto max-h-72 overflow-y-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] tracking-wider border-b border-slate-200 sticky top-0 z-10">
              <tr>
                <th className="py-2.5 px-3">Hour of Day</th>
                <th className="py-2.5 px-3 text-right">Periods Evaluated</th>
                <th className="py-2.5 px-3 text-right">P10 Error</th>
                <th className="py-2.5 px-3 text-right">P50 Median Error</th>
                <th className="py-2.5 px-3 text-right">P90 Error</th>
                <th className="py-2.5 px-3 text-right">Overforecast Frequency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
              {data.hourlyRiskProfile.map((row) => (
                <tr key={row.hourOfDay} className="hover:bg-slate-50 transition-colors">
                  <td className="py-2 px-3 font-semibold font-sans text-slate-900">{row.hourLabel}</td>
                  <td className="py-2 px-3 text-right text-slate-600">{row.sampleCount}</td>
                  <td className="py-2 px-3 text-right text-blue-700 font-semibold">{row.p10ErrorMW > 0 ? '+' : ''}{row.p10ErrorMW.toLocaleString()} MW</td>
                  <td className="py-2 px-3 text-right text-amber-700 font-bold">+{row.p50ErrorMW.toLocaleString()} MW</td>
                  <td className="py-2 px-3 text-right text-rose-700 font-semibold">+{row.p90ErrorMW.toLocaleString()} MW</td>
                  <td className="py-2 px-3 text-right text-slate-800">{row.overforecastPct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
