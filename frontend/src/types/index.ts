/**
 * TypeScript interfaces matching backend models.
 */

export interface ProvenanceInfo {
  actualsSourceUrl: string;
  forecastsSourceUrl: string;
  dataSource: string;
  units: string;
  fetchDateUTC: string;
  decisionDatesScope: string;
  deliveryDaysScope: string;
  evaluationSetDefinition: string;
  cutoffAssumption: string;
  selectedPublishTimeRange: string;
}

export interface SummaryMetrics {
  mae: number | null;
  rmse: number | null;
  wape: number | null;
  mbe: number | null;
  evaluatedHourlyPeriods: number;
  expectedHourlyPeriods: number;
  hourlyCoveragePct: number;
  unforecastedHalfHourPeriods: number;
  approxTotalActualEnergyMWh: number;
  approxTotalForecastEnergyMWh: number;
  energyNote: string;
}

export interface SummaryResponse {
  metrics: SummaryMetrics;
  provenance: ProvenanceInfo;
  dataAvailability: {
    deliveryDaysCount: number;
    totalActualsRecorded: number;
    hourlyEvaluationPeriods: number;
    matchedHourlyPeriods: number;
    halfHourPeriodsWithoutForecast: number;
    status: string;
  };
}

export interface MatchedPeriodRecord {
  startTime: string;
  startTimeUK: string;
  deliveryDate: string;
  settlementPeriod: number;
  isHourlyPeriod: boolean;
  actual: number;
  forecast: number | null;
  error: number | null;
  absError: number | null;
  publishTime: string | null;
  leadTimeHours: number | null;
  hasForecast: boolean;
  hasDuplicatePublication: boolean;
}

export interface DailyMetricRecord {
  deliveryDate: string;
  periodCount: number;
  mae: number;
  rmse: number;
  wape: number | null;
  mbe: number;
  actualMean: number;
  forecastMean: number;
  actualMax: number;
  forecastMax: number;
}

export interface HourlyProfileRecord {
  hourOfDay: number;
  hourLabel: string;
  count: number;
  actualAvg: number;
  forecastAvg: number;
  mae: number;
  mbe: number;
}

export interface ForecastLevelBiasRecord {
  bucket: string;
  count: number;
  forecastMean: number;
  actualMean: number;
  mae: number;
  mbe: number;
  wape: number | null;
  note: string;
}

export interface HistogramBin {
  binRange: string;
  binMin: number;
  binMax: number;
  binMid: number;
  count: number;
  pct: number;
}

export interface CutoffSensitivityRecord {
  cutoffTimeUK: string;
  mae: number;
  rmse: number;
  wape: number | null;
  mbe: number;
  matchedHourlyPeriods: number;
  coveragePct: number;
  freshestVintageUTC: string;
}

export interface AccuracyResponse {
  cutoffUsed: string;
  overall: SummaryMetrics;
  dailyBreakdown: DailyMetricRecord[];
  worstDaysByWape: DailyMetricRecord[];
  worstDaysByMae: DailyMetricRecord[];
  errorDistribution: HistogramBin[];
  diurnalProfile: HourlyProfileRecord[];
  biasByForecastLevel: ForecastLevelBiasRecord[];
  cutoffSensitivity: CutoffSensitivityRecord[];
}

export interface LeadTimeBucketRecord {
  bucket: string;
  minLeadHours: number;
  maxLeadHours: number;
  matchedCount: number;
  mae: number | null;
  rmse: number | null;
  wape: number | null;
  mbe: number | null;
}

export interface LeadTimeResponse {
  title: string;
  description: string;
  cutoffSelectionLeadTimeRangeHours: {
    minLeadHours: number;
    maxLeadHours: number;
    meanLeadHours: number;
  };
  buckets: LeadTimeBucketRecord[];
}

export interface DataQualityResponse {
  actualsCompleteness: Record<string, any>;
  forecastAudit: Record<string, any>;
  coverageSummary: Record<string, any>;
}

export interface QuantileRecord {
  quantileP10: number;
  quantileP50Median: number;
  quantileP90: number;
  overforecastFrequencyPct: number;
  underforecastFrequencyPct: number;
  sampleCount: number;
}

export interface HourlyRiskProfileRecord {
  hourOfDay: number;
  hourLabel: string;
  p10ErrorMW: number;
  p50ErrorMW: number;
  p90ErrorMW: number;
  overforecastPct: number;
  sampleCount: number;
}

export interface ProcurementRiskResponse {
  label: string;
  disclaimer: string;
  overallErrorQuantilesMW: QuantileRecord;
  hourlyRiskProfile: HourlyRiskProfileRecord[];
}

export type ActiveTab = 'overview' | 'accuracy' | 'vintages' | 'risk' | 'quality';
