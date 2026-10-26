import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend
} from 'recharts';
import { AccuracyResponse, DailyMetricRecord } from '../types';
import { AlertTriangle, ArrowUpDown } from 'lucide-react';
import { formatUnambiguousDate } from '../utils/formatters';

interface AccuracyViewProps {
  data: AccuracyResponse;
}

export const AccuracyView: React.FC<AccuracyViewProps> = ({ data }) => {
  const [sortField, setSortField] = useState<keyof DailyMetricRecord>('wape');
  const [sortAsc, setSortAsc] = useState<boolean>(false);

  const handleSort = (field: keyof DailyMetricRecord) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const sortedDaily = [...data.dailyBreakdown].sort((a, b) => {
    const valA = a[sortField];
    const valB = b[sortField];
    if (valA === null || valA === undefined) return 1;
    if (valB === null || valB === undefined) return -1;
    if (typeof valA === 'number' && typeof valB === 'number') {
      return sortAsc ? valA - valB : valB - valA;
    }
    return sortAsc ? String(valA).localeCompare(String(valB)) : String(valB).localeCompare(String(valA));
  });

  return (
    <div className="space-y-6">
      {/* 1. Worst Days Callout Cards */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            Top 3 High-Error Days (By WAPE)
          </h3>
          <span className="text-xs text-slate-500">Days requiring highest thermal balancing</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {data.worstDaysByWape.slice(0, 3).map((day, idx) => (
            <div key={day.deliveryDate} className="bg-white border border-amber-200/80 rounded-xl p-4 shadow-sm relative overflow-hidden">
              <div className="absolute top-0 right-0 bg-amber-500/10 text-amber-800 text-[10px] font-bold px-2 py-0.5 rounded-bl">
                Rank #{idx + 1}
              </div>
              <div className="text-xs font-bold text-slate-900 mb-1">{formatUnambiguousDate(day.deliveryDate)}</div>
              <div className="flex items-baseline gap-2 mb-3">
                <span className="text-2xl font-black text-amber-700 tracking-tight">{day.wape}%</span>
                <span className="text-xs font-medium text-slate-500">WAPE</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs border-t border-slate-100 pt-2 text-slate-600">
                <div>
                  <span className="text-[10px] text-slate-400 block">Actual Wind:</span>
                  <span className="font-semibold">{day.actualMean.toLocaleString()} MW</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Cutoff Forecast:</span>
                  <span className="font-semibold text-teal-700">{day.forecastMean.toLocaleString()} MW</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">MAE:</span>
                  <span className="font-mono">{day.mae.toLocaleString()} MW</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Overforecast:</span>
                  <span className="font-mono text-amber-700">+{day.mbe.toLocaleString()} MW</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 2. Charts Row: Error Histogram & Diurnal Profile */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Error Distribution Histogram */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="mb-4">
            <h4 className="text-sm font-bold text-slate-900 tracking-tight">
              Forecast Error Distribution (1,000 MW Bins)
            </h4>
            <p className="text-xs text-slate-500 mt-0.5">
              Distribution of (Forecast - Actual). Note heavy skew to positive errors (over-forecasting).
            </p>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.errorDistribution} margin={{ top: 10, right: 10, left: 0, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis
                  dataKey="binMin"
                  tickLine={false}
                  fontSize={9}
                  stroke="#64748b"
                  tickFormatter={(val) => `${val / 1000}k`}
                />
                <YAxis
                  tickLine={false}
                  fontSize={10}
                  stroke="#64748b"
                  unit=" pts"
                />
                <Tooltip
                  formatter={(value: any, _name: any, item: any) => [
                    `${value} periods (${item.payload.pct}%)`,
                    'Count'
                  ]}
                  labelFormatter={(val, items) => {
                    if (items && items[0]) {
                      return items[0].payload.binRange;
                    }
                    return `${val} MW`;
                  }}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                />
                <Bar
                  dataKey="count"
                  name="Periods"
                  fill="#0284c7"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Diurnal 24h Profile Chart */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="mb-4">
            <h4 className="text-sm font-bold text-slate-900 tracking-tight">
              Diurnal Hourly Generation & Error Profile
            </h4>
            <p className="text-xs text-slate-500 mt-0.5">
              Average actual outturn vs day-ahead forecast by hour of the day (00:00 to 23:00).
            </p>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.diurnalProfile} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="hourLabel" tickLine={false} fontSize={10} stroke="#64748b" />
                <YAxis tickLine={false} fontSize={10} stroke="#64748b" tickFormatter={(val) => `${val / 1000}k`} unit=" MW" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                  formatter={(val: any) => [`${Number(val).toLocaleString()} MW`]}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line type="monotone" dataKey="actualAvg" name="Average Actual (MW)" stroke="#1d4ed8" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="forecastAvg" name="Average Forecast (MW)" stroke="#0d9488" strokeWidth={2} strokeDasharray="3 3" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 3. Bias by Forecast Level Buckets */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div className="mb-3">
          <h4 className="text-sm font-bold text-slate-900 tracking-tight">
            Forecast Bias Categorized by Forecast Magnitude
          </h4>
          <p className="text-xs text-slate-500 mt-0.5">
            Evaluates forecast accuracy conditional on the forecasted wind level available at cutoff time.
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Forecast Level</th>
                <th className="py-2.5 px-3 text-right">Periods ($N$)</th>
                <th className="py-2.5 px-3 text-right">Mean Forecast</th>
                <th className="py-2.5 px-3 text-right">Mean Actual</th>
                <th className="py-2.5 px-3 text-right">MAE</th>
                <th className="py-2.5 px-3 text-right">Mean Bias Error (MBE)</th>
                <th className="py-2.5 px-3 text-right">WAPE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.biasByForecastLevel.map((row) => (
                <tr key={row.bucket} className="hover:bg-slate-50 transition-colors">
                  <td className="py-2.5 px-3 font-semibold text-slate-900">{row.bucket}</td>
                  <td className="py-2.5 px-3 text-right font-mono text-slate-600">{row.count}</td>
                  <td className="py-2.5 px-3 text-right font-mono text-teal-700">{row.forecastMean.toLocaleString()} MW</td>
                  <td className="py-2.5 px-3 text-right font-mono text-blue-700">{row.actualMean.toLocaleString()} MW</td>
                  <td className="py-2.5 px-3 text-right font-mono text-slate-800">{row.mae.toLocaleString()} MW</td>
                  <td className={`py-2.5 px-3 text-right font-mono font-bold ${row.mbe > 0 ? 'text-amber-700' : 'text-blue-700'}`}>
                    {row.mbe > 0 ? '+' : ''}{row.mbe.toLocaleString()} MW
                  </td>
                  <td className="py-2.5 px-3 text-right font-mono font-semibold text-slate-900">
                    {row.wape !== null ? `${row.wape}%` : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. Cutoff Sensitivity Comparison */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div className="mb-3">
          <h4 className="text-sm font-bold text-slate-900 tracking-tight">
            Decision Cutoff Sensitivity: Assumed decision cutoff (configurable) (09:00 vs 12:00 vs 15:00)
          </h4>
          <p className="text-xs text-slate-500 mt-0.5">
            Quantifies the reduction in forecast error gained by holding the purchase decision closer to delivery.
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Cutoff Assumption</th>
                <th className="py-2.5 px-3 text-right">Periods Evaluated</th>
                <th className="py-2.5 px-3 text-right">Coverage</th>
                <th className="py-2.5 px-3 text-right">MAE</th>
                <th className="py-2.5 px-3 text-right">RMSE</th>
                <th className="py-2.5 px-3 text-right">WAPE</th>
                <th className="py-2.5 px-3 text-right">Mean Bias</th>
                <th className="py-2.5 px-3">Latest Vintage Selected</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.cutoffSensitivity.map((row) => (
                <tr key={row.cutoffTimeUK} className="hover:bg-slate-50 transition-colors">
                  <td className="py-2.5 px-3 font-semibold text-slate-900">{row.cutoffTimeUK}</td>
                  <td className="py-2.5 px-3 text-right font-mono text-slate-600">{row.matchedHourlyPeriods} / 744</td>
                  <td className="py-2.5 px-3 text-right font-semibold text-emerald-700">{row.coveragePct}%</td>
                  <td className="py-2.5 px-3 text-right font-mono font-medium text-slate-900">{row.mae.toLocaleString()} MW</td>
                  <td className="py-2.5 px-3 text-right font-mono text-slate-700">{row.rmse.toLocaleString()} MW</td>
                  <td className="py-2.5 px-3 text-right font-mono font-bold text-blue-700">{row.wape}%</td>
                  <td className="py-2.5 px-3 text-right font-mono text-amber-700">+{row.mbe.toLocaleString()} MW</td>
                  <td className="py-2.5 px-3 font-mono text-[11px] text-slate-500">{row.freshestVintageUTC.replace('Z', ' UTC')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Complete Daily Metrics Table */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
          <div>
            <h4 className="text-sm font-bold text-slate-900 tracking-tight">
              Daily Accuracy Breakdown (All 31 Delivery Days)
            </h4>
            <p className="text-xs text-slate-500 mt-0.5">Click column headers to sort ascending or descending.</p>
          </div>
          <span className="text-xs text-slate-400 font-mono">Sorted by {String(sortField)} ({sortAsc ? 'asc' : 'desc'})</span>
        </div>

        <div className="overflow-x-auto max-h-96 overflow-y-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] tracking-wider border-b border-slate-200 sticky top-0 z-10 shadow-sm">
              <tr>
                <th
                  onClick={() => handleSort('deliveryDate')}
                  className="py-2.5 px-3 cursor-pointer hover:text-slate-900"
                >
                  <div className="flex items-center gap-1">Date <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('periodCount')} className="py-2.5 px-3 text-right cursor-pointer hover:text-slate-900">
                  Hours
                </th>
                <th onClick={() => handleSort('actualMean')} className="py-2.5 px-3 text-right cursor-pointer hover:text-slate-900">
                  Actual Mean
                </th>
                <th onClick={() => handleSort('forecastMean')} className="py-2.5 px-3 text-right cursor-pointer hover:text-slate-900">
                  Forecast Mean
                </th>
                <th onClick={() => handleSort('mae')} className="py-2.5 px-3 text-right cursor-pointer hover:text-slate-900">
                  <div className="flex items-center justify-end gap-1">MAE <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('rmse')} className="py-2.5 px-3 text-right cursor-pointer hover:text-slate-900">
                  RMSE
                </th>
                <th onClick={() => handleSort('wape')} className="py-2.5 px-3 text-right cursor-pointer hover:text-slate-900">
                  <div className="flex items-center justify-end gap-1">WAPE <ArrowUpDown className="w-3 h-3 text-blue-600" /></div>
                </th>
                <th onClick={() => handleSort('mbe')} className="py-2.5 px-3 text-right cursor-pointer hover:text-slate-900">
                  Mean Bias
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
              {sortedDaily.map((row) => (
                <tr key={row.deliveryDate} className="hover:bg-slate-50 transition-colors">
                  <td className="py-2 px-3 font-semibold font-sans text-slate-900" title={row.deliveryDate}>
                    {formatUnambiguousDate(row.deliveryDate)}
                  </td>
                  <td className="py-2 px-3 text-right text-slate-600">{row.periodCount}</td>
                  <td className="py-2 px-3 text-right text-blue-800">{row.actualMean.toLocaleString()}</td>
                  <td className="py-2 px-3 text-right text-teal-800">{row.forecastMean.toLocaleString()}</td>
                  <td className="py-2 px-3 text-right text-slate-900 font-semibold">{row.mae.toLocaleString()}</td>
                  <td className="py-2 px-3 text-right text-slate-600">{row.rmse.toLocaleString()}</td>
                  <td className="py-2 px-3 text-right font-bold text-blue-700">{row.wape}%</td>
                  <td className={`py-2 px-3 text-right ${row.mbe > 0 ? 'text-amber-700' : 'text-blue-600'}`}>
                    {row.mbe > 0 ? '+' : ''}{row.mbe.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
