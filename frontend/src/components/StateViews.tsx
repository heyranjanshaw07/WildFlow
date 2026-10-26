import React from 'react';
import { AlertCircle, RefreshCw, Database } from 'lucide-react';

interface LoadingProps {
  message?: string;
}

export const LoadingView: React.FC<LoadingProps> = ({ message = "Loading energy forecast data..." }) => (
  <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
    <div className="relative w-12 h-12 mb-4">
      <div className="absolute inset-0 rounded-full border-4 border-slate-200"></div>
      <div className="absolute inset-0 rounded-full border-4 border-blue-600 border-t-transparent animate-spin"></div>
    </div>
    <p className="text-sm font-medium text-slate-600">{message}</p>
    <p className="text-xs text-slate-400 mt-1">Grounded directly in Elexon BMRS January 2026 data</p>
  </div>
);

interface ErrorProps {
  message: string;
  onRetry?: () => void;
}

export const ErrorView: React.FC<ErrorProps> = ({ message, onRetry }) => (
  <div className="bg-white border border-red-200 rounded-xl p-8 text-center max-w-lg mx-auto my-12 shadow-sm">
    <div className="w-12 h-12 bg-red-50 text-red-600 rounded-full flex items-center justify-center mx-auto mb-4">
      <AlertCircle className="w-6 h-6" />
    </div>
    <h3 className="text-base font-semibold text-slate-900 mb-1">Failed to load data</h3>
    <p className="text-xs text-slate-500 mb-6 font-mono bg-slate-50 p-2.5 rounded border border-slate-200 text-left overflow-x-auto">
      {message}
    </p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition-colors shadow-sm"
      >
        <RefreshCw className="w-3.5 h-3.5" />
        Retry Request
      </button>
    )}
  </div>
);

interface EmptyProps {
  title?: string;
  description?: string;
  onReset?: () => void;
}

export const EmptyView: React.FC<EmptyProps> = ({
  title = "No data available",
  description = "No settlement records matched the selected date filter or cutoff parameters.",
  onReset
}) => (
  <div className="bg-white border border-slate-200 rounded-xl p-12 text-center max-w-md mx-auto my-12">
    <div className="w-12 h-12 bg-slate-100 text-slate-500 rounded-full flex items-center justify-center mx-auto mb-3">
      <Database className="w-6 h-6" />
    </div>
    <h3 className="text-sm font-semibold text-slate-800 mb-1">{title}</h3>
    <p className="text-xs text-slate-500 mb-5">{description}</p>
    {onReset && (
      <button
        onClick={onReset}
        className="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium rounded-lg transition-colors"
      >
        Reset Filters
      </button>
    )}
  </div>
);
