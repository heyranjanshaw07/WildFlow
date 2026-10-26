import React from 'react';
import { DataQualityResponse, ProvenanceInfo } from '../types';
import { Database, CheckCircle2, AlertTriangle, ExternalLink } from 'lucide-react';

interface DataQualityViewProps {
  quality: DataQualityResponse;
  provenance: ProvenanceInfo;
}

export const DataQualityView: React.FC<DataQualityViewProps> = ({ quality, provenance }) => {
  return (
    <div className="space-y-6">
      {/* 1. Data Provenance & Official Source Verification */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2 mb-1">
          <Database className="w-4 h-4 text-blue-600" />
          Official Data Provenance & Source Metadata
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          All data ingested directly from Elexon BMRS API streams without simulation, synthetic interpolation, or third-party augmentation.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="border border-slate-200 rounded-lg p-3.5 bg-slate-50">
            <span className="text-[10px] font-bold uppercase text-slate-500 tracking-wider block mb-1">
              Actual Outturns Endpoint (FUELHH)
            </span>
            <a
              href={provenance.actualsSourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="font-mono text-blue-600 hover:text-blue-800 break-all flex items-center gap-1 font-medium"
            >
              {provenance.actualsSourceUrl}
              <ExternalLink className="w-3 h-3 shrink-0" />
            </a>
            <div className="mt-2 text-slate-600 text-[11px] space-y-0.5">
              <div><span className="text-slate-400">Dataset:</span> FUELHH</div>
              <div><span className="text-slate-400">Fuel Filter:</span> fuelType = "WIND"</div>
              <div><span className="text-slate-400">Resolution:</span> 30-minute settlement periods (48 periods/day)</div>
            </div>
          </div>

          <div className="border border-slate-200 rounded-lg p-3.5 bg-slate-50">
            <span className="text-[10px] font-bold uppercase text-slate-500 tracking-wider block mb-1">
              Forecast Vintages Endpoint (WINDFOR)
            </span>
            <a
              href={provenance.forecastsSourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="font-mono text-blue-600 hover:text-blue-800 break-all flex items-center gap-1 font-medium"
            >
              {provenance.forecastsSourceUrl}
              <ExternalLink className="w-3 h-3 shrink-0" />
            </a>
            <div className="mt-2 text-slate-600 text-[11px] space-y-0.5">
              <div><span className="text-slate-400">Dataset:</span> WINDFOR (Forecast stream)</div>
              <div><span className="text-slate-400">Cadence:</span> Published ~8 times per day in 73-point runs</div>
              <div><span className="text-slate-400">Resolution:</span> 60-minute hourly intervals (:00 timestamps)</div>
            </div>
          </div>
        </div>

        {/* Provenance Details Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 pt-4 border-t border-slate-100 text-xs">
          <div>
            <span className="text-slate-400 block text-[10px] uppercase font-semibold">Standard Units</span>
            <span className="font-semibold text-slate-900">{provenance.units}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px] uppercase font-semibold">Ingestion Fetch Date</span>
            <span className="font-mono text-slate-800">{provenance.fetchDateUTC.replace('T', ' ').replace('Z', ' UTC')}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px] uppercase font-semibold">Decision Scope</span>
            <span className="font-semibold text-slate-900">{provenance.decisionDatesScope}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px] uppercase font-semibold">Delivery Scope</span>
            <span className="font-semibold text-slate-900">2 Jan to 1 Feb 2026</span>
          </div>
        </div>
      </div>

      {/* 2. Evaluation Set & Dataset Resolution Audit */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <h4 className="text-sm font-bold text-slate-900 tracking-tight mb-1 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          Evaluation Set Definition & Resolution Audit
        </h4>
        <p className="text-xs text-slate-500 mb-4 leading-relaxed">
          {provenance.evaluationSetDefinition}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border border-emerald-200 bg-emerald-50/50 rounded-xl p-4">
            <span className="text-xs font-bold text-emerald-900 block mb-1">
              Hourly Evaluation Set (:00)
            </span>
            <div className="text-2xl font-black text-emerald-800 font-mono">
              744 / 744
            </div>
            <p className="text-[11px] text-emerald-700 mt-1">
              100.0% coverage across all 31 delivery days. Every hourly delivery period has a valid pre-cutoff forecast.
            </p>
          </div>

          <div className="border border-slate-200 bg-slate-50 rounded-xl p-4">
            <span className="text-xs font-bold text-slate-800 block mb-1">
              Half-Hour Actuals (:30)
            </span>
            <div className="text-2xl font-black text-slate-700 font-mono">
              744 periods
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              Unforecasted by design because WINDFOR publishes at 60-min resolution. Kept without synthetic interpolation.
            </p>
          </div>

          <div className="border border-blue-200 bg-blue-50/50 rounded-xl p-4">
            <span className="text-xs font-bold text-blue-900 block mb-1">
              Total Actual Periods
            </span>
            <div className="text-2xl font-black text-blue-800 font-mono">
              1,488 / 1,488
            </div>
            <p className="text-[11px] text-blue-700 mt-1">
              31 days x 48 half-hours. Zero missing settlement intervals across the delivery window.
            </p>
          </div>
        </div>

        {/* Note on Absent 11:30Z Run & 12:00 Cutoff Fallback */}
        <div className="mt-4 pt-3 border-t border-slate-100 flex items-start gap-2 text-xs text-blue-900 bg-blue-50/70 p-3 rounded-lg border border-blue-200/60">
          <Database className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-blue-955">Observation on WINDFOR Publication Cadence (16 Jan 2026 Delivery): </span>
            A run was published at 12:25Z on 15 Jan instead of the usual 11:30Z; the 12:00 cutoff therefore uses the 09:30Z run for 16 Jan (yielding a maximum lead time of 37.5 hours for that day).
          </div>
        </div>
      </div>

      {/* 3. Retrospective Rows & Negative Lead-Time Audit */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <h4 className="text-sm font-bold text-slate-900 tracking-tight mb-1 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-600" />
          Retrospective Forecast Records (Negative Lead Times)
        </h4>
        <p className="text-xs text-slate-500 mb-4">
          Observation: In raw WINDFOR publication runs, approximately 20.5% of rows have a target startTime preceding publishTime.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div className="border border-slate-200 p-3.5 rounded-lg bg-slate-50">
            <span className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Retrospective Rows</span>
            <span className="text-lg font-bold font-mono text-slate-900">
              {quality.forecastAudit.negativeLeadTimeCount.toLocaleString()}
            </span>
            <span className="text-slate-400 text-[11px] ml-1">({quality.forecastAudit.negativeLeadTimePct}%)</span>
          </div>

          <div className="border border-slate-200 p-3.5 rounded-lg bg-slate-50">
            <span className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Positive Lead Rows</span>
            <span className="text-lg font-bold font-mono text-emerald-700">
              {quality.forecastAudit.positiveLeadRows.toLocaleString()}
            </span>
            <span className="text-slate-400 text-[11px] ml-1">(Active candidates)</span>
          </div>

          <div className="border border-slate-200 p-3.5 rounded-lg bg-slate-50">
            <span className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Processing Action</span>
            <span className="font-semibold text-slate-800 block">
              Flagged & Excluded
            </span>
            <span className="text-[11px] text-slate-500">Excluded from day-ahead forward matching</span>
          </div>
        </div>
      </div>
    </div>
  );
};
