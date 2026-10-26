import React, { useState } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { MatchedPeriodRecord } from '../types';
import { Layers, Info } from 'lucide-react';

interface MainChartProps {
  data: MatchedPeriodRecord[];
  cutoffTime: string;
}

export const MainChart: React.FC<MainChartProps> = ({ data, cutoffTime }) => {
  const [showActual] = useState(true);
  const [showForecast] = useState(true);
  const [showAbsError, setShowAbsError] = useState(false);
  const [hourlyOnly, setHourlyOnly] = useState(true);

  const displayData = hourlyOnly ? data.filter((d) => d.isHourlyPeriod) : data;

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;
    const record: MatchedPeriodRecord = payload[0].payload;

    return (
      <div className="custom-tooltip min-w-[240px]">
        <div className="font-semibold text-slate-100 border-b border-slate-700 pb-1 mb-2">
          {record.startTimeUK} <span className="text-[10px] text-slate-400 font-normal">(UK Local Time)</span>
        </div>
        <div className="space-y-1">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400 flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-sm bg-blue-500 inline-block"></span>
              Actual Wind:
            </span>
            <span className="font-semibold text-white font-mono">
              {record.actual.toLocaleString()} MW
            </span>
          </div>

          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400 flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-sm bg-teal-400 inline-block"></span>
              Cutoff Forecast:
            </span>
            <span className="font-semibold text-teal-300 font-mono">
              {record.forecast !== null && record.forecast !== undefined
                ? `${record.forecast.toLocaleString()} MW`
                : 'No forecast (hourly WINDFOR, :30 actual only)'}
            </span>
          </div>

          {record.error !== null && (
            <div className="flex justify-between items-center text-xs pt-1 border-t border-slate-700/60">
              <span className="text-slate-400">Forecast Error:</span>
              <span className={`font-mono font-semibold ${record.error > 0 ? 'text-amber-400' : 'text-blue-300'}`}>
                {record.error > 0 ? '+' : ''}{record.error.toLocaleString()} MW
              </span>
            </div>
          )}

          {record.absError !== null && (
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400">Absolute Error:</span>
              <span className="font-mono text-slate-200">
                {record.absError.toLocaleString()} MW
              </span>
            </div>
          )}

          {record.publishTime && (
            <div className="pt-1.5 border-t border-slate-700/60 text-[10px] text-slate-400 space-y-0.5">
              <div className="flex justify-between">
                <span>Selected Vintage:</span>
                <span className="font-mono text-slate-300">{record.publishTime.replace('Z', ' UTC')}</span>
              </div>
              {record.leadTimeHours !== null && (
                <div className="flex justify-between">
                  <span>Forecast Lead Time:</span>
                  <span className="font-mono text-slate-300">{record.leadTimeHours} hrs</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
            National Wind Generation: Actual vs Cutoff Forecast
            <span className="text-[11px] font-normal text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full border border-slate-200">
              {displayData.length} periods plotted
            </span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Compares outturn generation with the latest forecast vintage published before {cutoffTime} Europe/London on D-1.
          </p>
        </div>

        {/* Chart View & Series Toggles */}
        <div className="flex items-center gap-2 text-xs flex-wrap">
          <button
            onClick={() => setHourlyOnly(!hourlyOnly)}
            className={`px-2.5 py-1 rounded-md font-medium text-xs border transition-colors flex items-center gap-1.5 ${
              hourlyOnly
                ? 'bg-blue-50 border-blue-300 text-blue-800'
                : 'bg-slate-100 border-slate-200 text-slate-600'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            {hourlyOnly ? 'Hourly Evaluation Set (:00)' : 'All Periods (incl :30)'}
          </button>

          <button
            onClick={() => setShowAbsError(!showAbsError)}
            className={`px-2.5 py-1 rounded-md font-medium text-xs border transition-colors ${
              showAbsError
                ? 'bg-amber-50 border-amber-300 text-amber-800'
                : 'bg-slate-100 border-slate-200 text-slate-600'
            }`}
          >
            {showAbsError ? 'Hide Error Bars' : 'Show Error Bars'}
          </button>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={displayData}
            margin={{ top: 10, right: 10, left: 0, bottom: 25 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis
              dataKey="startTimeUK"
              tickLine={false}
              stroke="#64748b"
              fontSize={10}
              tickFormatter={(val) => {
                // val is 'YYYY-MM-DD HH:MM:SS'
                return val ? val.slice(5, 16) : '';
              }}
              minTickGap={40}
            />
            <YAxis
              domain={[0, 20000]}
              ticks={[0, 5000, 10000, 15000, 20000]}
              stroke="#64748b"
              fontSize={10}
              tickLine={false}
              tickFormatter={(val) => (val === 0 ? '0' : `${val / 1000}k`)}
              unit=" MW"
              width={65}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="top"
              align="right"
              wrapperStyle={{ paddingBottom: '10px', fontSize: '11px' }}
            />

            {showAbsError && (
              <Bar
                dataKey="absError"
                name="Absolute Error (MW)"
                fill="#fde68a"
                opacity={0.7}
              />
            )}

            {showActual && (
              <Line
                type="monotone"
                dataKey="actual"
                name="Actual Wind Outturn (MW)"
                stroke="#1d4ed8"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, strokeWidth: 1, stroke: '#ffffff' }}
              />
            )}

            {showForecast && (
              <Line
                type="stepAfter"
                dataKey="forecast"
                name="Hourly forecast (held flat across the hour for display only; no :30 forecast exists)"
                stroke="#0d9488"
                strokeWidth={2}
                strokeDasharray="4 2"
                dot={{ r: 2.5, fill: '#0d9488', stroke: '#ffffff', strokeWidth: 1 }}
                connectNulls={true}
                activeDot={{ r: 5, strokeWidth: 2, stroke: '#ffffff' }}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-2 text-[11px] text-slate-400 flex items-center justify-between border-t border-slate-100 pt-2">
        <span className="flex items-center gap-1">
          <Info className="w-3.5 h-3.5 text-slate-400" />
          Y-Axis units: Megawatts (MW). Delivery timestamps rendered in Europe/London local time.
        </span>
        <span className="font-mono text-[10px]">Elexon FUELHH & WINDFOR</span>
      </div>
    </div>
  );
};
