/**
 * api.ts - Type-safe API client for WindScope backend.
 */

import {
  SummaryResponse,
  MatchedPeriodRecord,
  AccuracyResponse,
  LeadTimeResponse,
  DataQualityResponse,
  ProcurementRiskResponse,
} from '../types';

const RAW_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
// Strip trailing slash if present to avoid double-slashes when constructing endpoint paths
export const API_BASE_URL = RAW_BASE_URL.replace(/\/+$/, '');

async function fetchJson<T>(url: string): Promise<T> {
  const fullUrl = `${API_BASE_URL}${url}`;
  const response = await fetch(fullUrl, {
    headers: {
      'Accept': 'application/json',
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    let readableMessage = errorText;
    try {
      const errJson = JSON.parse(errorText);
      if (Array.isArray(errJson.detail)) {
        // FastAPI 422 validation error array
        readableMessage = errJson.detail
          .map((e: any) => {
            const field = Array.isArray(e.loc) ? e.loc.filter((x: string) => x !== 'query' && x !== 'body').join('.') : 'field';
            return `${field ? field + ': ' : ''}${e.msg}`;
          })
          .join(' | ');
      } else if (typeof errJson.detail === 'string') {
        readableMessage = errJson.detail;
      } else if (errJson.error && typeof errJson.error.message === 'string') {
        readableMessage = errJson.error.message;
      } else if (typeof errJson.message === 'string') {
        readableMessage = errJson.message;
      }
    } catch {
      // Use raw errorText if not JSON
    }
    throw new Error(`API Error ${response.status}: ${readableMessage || response.statusText}`);
  }

  return response.json();
}

export const api = {
  getSummary: (cutoffTime: string, startDate?: string, endDate?: string) => {
    const params = new URLSearchParams({ cutoff_time: cutoffTime });
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    return fetchJson<SummaryResponse>(`/api/summary?${params.toString()}`);
  },

  getForecasts: (cutoffTime: string, startDate?: string, endDate?: string, hourlyOnly: boolean = false) => {
    const params = new URLSearchParams({
      cutoff_time: cutoffTime,
      hourly_only: String(hourlyOnly)
    });
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    return fetchJson<MatchedPeriodRecord[]>(`/api/forecasts?${params.toString()}`);
  },

  getAccuracy: (cutoffTime: string, startDate?: string, endDate?: string) => {
    const params = new URLSearchParams({ cutoff_time: cutoffTime });
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    return fetchJson<AccuracyResponse>(`/api/accuracy?${params.toString()}`);
  },

  getForecastVintages: (cutoffTime: string) => {
    const params = new URLSearchParams({ cutoff_time: cutoffTime });
    return fetchJson<LeadTimeResponse>(`/api/forecast-vintages?${params.toString()}`);
  },

  getDataQuality: () => {
    return fetchJson<DataQualityResponse>('/api/data-quality');
  },

  getProcurementRisk: (cutoffTime: string, startDate?: string, endDate?: string) => {
    const params = new URLSearchParams({ cutoff_time: cutoffTime });
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    return fetchJson<ProcurementRiskResponse>(`/api/procurement-risk?${params.toString()}`);
  },
};
