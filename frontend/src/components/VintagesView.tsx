import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { LeadTimeResponse } from '../types';
import { Clock, Info, ShieldCheck } from 'lucide-react';

interface VintagesViewProps {
  data: LeadTimeResponse;
  cutoffTime: string;
}

export const VintagesView: React.FC<VintagesViewProps> = ({ data, cutoffTime }) => {
  return (
    <div className="space-y-6">
      {/* 1. Explanatory Context & Active Cutoff Lead Time Badge */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <Clock className="w-4 h-4 text-blue-600" />
              {data.title}
            </h3>
            <p className="text-xs text-slate-500 mt-1 max-w-2xl">
              {data.description}
            </p>
          </div>

          <div className="bg-blue-50/80 border border-blue-200 rounded-xl p-3.5 text-xs shrink-0">
            <span className="text-[10px] uppercase font-bold text-blue-800 tracking-wider block mb-1">
              Active Cutoff Horizon ({cutoffTime} on D-1)
            </span>
            <div className="flex items-baseline gap-3 text-slate-800">
              <div>
                <span className="text-slate-400 text-[10px] block">Min Lead:</span>
                <span className="text-sm font-bold font-mono text-blue-900">{data.cutoffSelectionLeadTimeRangeHours.minLeadHours}h</span>
              </div>
              <span className="text-slate-300">|</span>
              <div>
                <span className="text-slate-400 text-[10px] block">Mean Lead:</span>
                <span className="text-sm font-bold font-mono text-blue-900">{data.cutoffSelectionLeadTimeRangeHours.meanLeadHours}h</span>
              </div>
              <span className="text-slate-300">|</span>
              <div>
                <span className="text-slate-400 text-[10px] block">Max Lead:</span>
                <span className="text-sm font-bold font-mono text-blue-900">{data.cutoffSelectionLeadTimeRangeHours.maxLeadHours}h</span>
              </div>
            </div>
          </div>
        </div>

        {/* Why Day-Ahead Selection Starts at >= 15h */}
        <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-600">
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200/60">
            <h5 className="font-semibold text-slate-800 mb-1 flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-blue-600" />
              Cutoff Horizon Lead-Time Range:
            </h5>
            <p className="text-slate-500 text-[11px] leading-relaxed">
              For delivery day D, the assumed decision cutoff occurs on day D-1 at {cutoffTime} Europe/London.
              Under the default 09:00 cutoff, the freshest publication available is at 07:30 UTC on D-1, so actual lead times range from 16.5h (00:00 delivery) to 39.5h (23:00 delivery), with a mean of 28.0h.
              Under the 12:00 cutoff, the freshest publication is at 11:30 UTC (or 09:30 UTC), so lead times range from 12.5h to 37.5h, with a mean of 24.1h.
            </p>
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200/60">
            <h5 className="font-semibold text-slate-800 mb-1 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              Why 0h - 14h Vintages Are Excluded from Day-Ahead:
            </h5>
            <p className="text-slate-500 text-[11px] leading-relaxed">
              The 3,472 raw forecast records with lead times between 0h and 14h were published on D-1 afternoon or during day D itself (intraday updates). Using them for day-ahead purchase decisions would constitute an illegal look-ahead violation.
            </p>
          </div>
        </div>
      </div>

      {/* 2. Lead Time Horizon Chart */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div className="mb-4">
          <h4 className="text-sm font-bold text-slate-900 tracking-tight">
            Error by forecast lead time (all forecast vintages with positive lead time)
          </h4>
          <p className="text-xs text-slate-500 mt-0.5">
            Observes that forecast error increases slightly as lead time expands from 0h out to 72h.
          </p>
        </div>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.buckets} margin={{ top: 10, right: 10, left: 0, bottom: 25 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="bucket" tickLine={false} fontSize={10} stroke="#64748b" />
              <YAxis yAxisId="left" stroke="#1d4ed8" fontSize={10} tickLine={false} unit=" MW" />
              <YAxis yAxisId="right" orientation="right" stroke="#0d9488" fontSize={10} tickLine={false} unit="%" />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                formatter={(val: any, name: any) => [
                  name === 'WAPE (%)' ? `${val}%` : `${Number(val).toLocaleString()} MW`,
                  name
                ]}
              />
              <Legend wrapperStyle={{ fontSize: '11px' }} />
              <Bar yAxisId="left" dataKey="mae" name="MAE (MW)" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar yAxisId="right" dataKey="wape" name="WAPE (%)" fill="#14b8a6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 3. Comprehensive Lead-Time Table */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <h4 className="text-sm font-bold text-slate-900 tracking-tight mb-3">
          Lead-Time Horizon Performance Metrics
        </h4>
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Lead-Time Horizon</th>
                <th className="py-2.5 px-3 text-right">Matched Forecasts ($N$)</th>
                <th className="py-2.5 px-3 text-right">MAE</th>
                <th className="py-2.5 px-3 text-right">RMSE</th>
                <th className="py-2.5 px-3 text-right">WAPE</th>
                <th className="py-2.5 px-3 text-right">Mean Bias Error (MBE)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
              {data.buckets.map((b) => (
                <tr key={b.bucket} className="hover:bg-slate-50 transition-colors">
                  <td className="py-2.5 px-3 font-semibold font-sans text-slate-900">{b.bucket}</td>
                  <td className="py-2.5 px-3 text-right text-slate-600">{b.matchedCount.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-right font-semibold text-slate-900">{b.mae?.toLocaleString()} MW</td>
                  <td className="py-2.5 px-3 text-right text-slate-600">{b.rmse?.toLocaleString()} MW</td>
                  <td className="py-2.5 px-3 text-right font-bold text-teal-700">{b.wape}%</td>
                  <td className="py-2.5 px-3 text-right text-amber-700 font-semibold">+{b.mbe?.toLocaleString()} MW</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
