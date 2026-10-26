import React, { useState, useEffect, useCallback } from 'react';
import { api } from './services/api';
import {
  ActiveTab,
  SummaryResponse,
  MatchedPeriodRecord,
  AccuracyResponse,
  LeadTimeResponse,
  ProcurementRiskResponse,
  DataQualityResponse,
} from './types';
import { Header } from './components/Header';
import { Controls } from './components/Controls';
import { MetricCards } from './components/MetricCards';
import { MainChart } from './components/MainChart';
import { AccuracyView } from './components/AccuracyView';
import { VintagesView } from './components/VintagesView';
import { RiskView } from './components/RiskView';
import { DataQualityView } from './components/DataQualityView';
import { LoadingView, ErrorView, EmptyView } from './components/StateViews';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('overview');
  const [cutoffTime, setCutoffTime] = useState<string>('09:00');
  const [startDate, setStartDate] = useState<string>('2026-01-02');
  const [endDate, setEndDate] = useState<string>('2026-02-01');

  // Loading & error states
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Data states
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [timeSeries, setTimeSeries] = useState<MatchedPeriodRecord[]>([]);
  const [accuracy, setAccuracy] = useState<AccuracyResponse | null>(null);
  const [vintages, setVintages] = useState<LeadTimeResponse | null>(null);
  const [risk, setRisk] = useState<ProcurementRiskResponse | null>(null);
  const [quality, setQuality] = useState<DataQualityResponse | null>(null);

  // Load primary dashboard data
  const loadData = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      // Parallel requests for core dashboard data
      const [sumRes, tsRes, accRes] = await Promise.all([
        api.getSummary(cutoffTime, startDate, endDate),
        api.getForecasts(cutoffTime, startDate, endDate),
        api.getAccuracy(cutoffTime, startDate, endDate),
      ]);

      setSummary(sumRes);
      setTimeSeries(tsRes);
      setAccuracy(accRes);

      // Lazy/background load tab-specific views if requested or preload
      api.getForecastVintages(cutoffTime).then(setVintages).catch(console.error);
      api.getProcurementRisk(cutoffTime, startDate, endDate).then(setRisk).catch(console.error);
      api.getDataQuality().then(setQuality).catch(console.error);
    } catch (err: any) {
      console.error('Failed to fetch dashboard data:', err);
      setErrorMessage(err.message || 'An unexpected error occurred while communicating with the backend.');
    } finally {
      setIsLoading(false);
    }
  }, [cutoffTime, startDate, endDate]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handle CSV export of current matched time series
  const handleExportCsv = () => {
    if (!timeSeries.length) return;

    const headers = [
      'startTimeUTC',
      'startTimeUK',
      'deliveryDate',
      'settlementPeriod',
      'isHourlyPeriod',
      'actualMW',
      'forecastMW',
      'errorMW',
      'absErrorMW',
      'selectedPublishTimeUTC',
      'leadTimeHours',
      'hasForecast',
    ];

    const rows = timeSeries.map((r) => [
      r.startTime,
      `"${r.startTimeUK}"`,
      r.deliveryDate,
      r.settlementPeriod,
      r.isHourlyPeriod,
      r.actual,
      r.forecast !== null ? r.forecast : '',
      r.error !== null ? r.error : '',
      r.absError !== null ? r.absError : '',
      r.publishTime || '',
      r.leadTimeHours !== null ? r.leadTimeHours : '',
      r.hasForecast,
    ]);

    const csvContent = [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `windscope_actuals_vs_forecasts_${startDate}_to_${endDate}_cutoff_${cutoffTime.replace(':', '')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleResetFilters = () => {
    setCutoffTime('09:00');
    setStartDate('2026-01-02');
    setEndDate('2026-02-01');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Header
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        fetchDate={summary?.provenance.fetchDateUTC}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Top Controls Bar */}
        <Controls
          cutoffTime={cutoffTime}
          onCutoffChange={setCutoffTime}
          startDate={startDate}
          endDate={endDate}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
          onResetFilters={handleResetFilters}
          onExportCsv={handleExportCsv}
          isLoading={isLoading}
        />

        {/* Global KPI Cards */}
        <MetricCards metrics={summary?.metrics || null} cutoffTime={cutoffTime} />

        {/* Tab Content Display */}
        {isLoading && !summary ? (
          <LoadingView />
        ) : errorMessage ? (
          <ErrorView message={errorMessage} onRetry={loadData} />
        ) : (
          <div>
            {activeTab === 'overview' && (
              <div>
                {timeSeries.length > 0 ? (
                  <MainChart data={timeSeries} cutoffTime={cutoffTime} />
                ) : (
                  <EmptyView onReset={handleResetFilters} />
                )}
              </div>
            )}

            {activeTab === 'accuracy' && (
              <div>
                {accuracy ? (
                  <AccuracyView data={accuracy} />
                ) : (
                  <LoadingView message="Computing accuracy metrics & daily breakdowns..." />
                )}
              </div>
            )}

            {activeTab === 'vintages' && (
              <div>
                {vintages ? (
                  <VintagesView data={vintages} cutoffTime={cutoffTime} />
                ) : (
                  <LoadingView message="Loading lead-time horizon metrics..." />
                )}
              </div>
            )}

            {activeTab === 'risk' && (
              <div>
                {risk ? (
                  <RiskView data={risk} cutoffTime={cutoffTime} />
                ) : (
                  <LoadingView message="Evaluating empirical error quantiles & risk profile..." />
                )}
              </div>
            )}

            {activeTab === 'quality' && (
              <div>
                {quality && summary ? (
                  <DataQualityView quality={quality} provenance={summary.provenance} />
                ) : (
                  <LoadingView message="Loading data quality audit..." />
                )}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-800">WindScope UK</span>
            <span>•</span>
            <span>Elexon BMRS Verified Datasets (FUELHH & WINDFOR)</span>
          </div>
          <div className="text-slate-400 text-center sm:text-right">
            <span>Operational decision cutoff default: 09:00 Europe/London (D-1)</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
