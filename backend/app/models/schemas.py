"""
schemas.py - Pydantic request and response schemas for WindScope.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str
    datasetsLoaded: bool
    actualsRowCount: int
    forecastsRowCount: int


class ProvenanceInfo(BaseModel):
    actualsSourceUrl: str
    forecastsSourceUrl: str
    dataSource: str
    units: str
    fetchDateUTC: str
    decisionDatesScope: str
    deliveryDaysScope: str
    evaluationSetDefinition: str
    cutoffAssumption: str
    selectedPublishTimeRange: str


class SummaryMetrics(BaseModel):
    mae: Optional[float]
    rmse: Optional[float]
    wape: Optional[float]
    mbe: Optional[float]
    evaluatedHourlyPeriods: int
    expectedHourlyPeriods: int
    hourlyCoveragePct: float
    unforecastedHalfHourPeriods: int
    approxTotalActualEnergyMWh: float
    approxTotalForecastEnergyMWh: float
    energyNote: str


class SummaryResponse(BaseModel):
    metrics: SummaryMetrics
    provenance: ProvenanceInfo
    dataAvailability: Dict[str, Any]


class ActualRecord(BaseModel):
    startTime: str
    startTimeUK: str
    settlementDate: str
    settlementPeriod: int
    fuelType: str
    generation: float
    publishTime: str


class MatchedPeriodRecord(BaseModel):
    startTime: str
    startTimeUK: str
    deliveryDate: str
    settlementPeriod: int
    isHourlyPeriod: bool
    actual: float
    forecast: Optional[float]
    error: Optional[float]
    absError: Optional[float]
    publishTime: Optional[str]
    leadTimeHours: Optional[float]
    hasForecast: bool
    hasDuplicatePublication: bool


class DailyMetricRecord(BaseModel):
    deliveryDate: str
    periodCount: int
    mae: float
    rmse: float
    wape: Optional[float]
    mbe: float
    actualMean: float
    forecastMean: float
    actualMax: float
    forecastMax: float


class HourlyProfileRecord(BaseModel):
    hourOfDay: int
    hourLabel: str
    count: int
    actualAvg: float
    forecastAvg: float
    mae: float
    mbe: float


class ForecastLevelBiasRecord(BaseModel):
    bucket: str
    count: int
    forecastMean: float
    actualMean: float
    mae: float
    mbe: float
    wape: Optional[float]
    note: str


class HistogramBin(BaseModel):
    binRange: str
    binMin: float
    binMax: float
    binMid: float
    count: int
    pct: float


class CutoffSensitivityRecord(BaseModel):
    cutoffTimeUK: str
    mae: float
    rmse: float
    wape: Optional[float]
    mbe: float
    matchedHourlyPeriods: int
    coveragePct: float
    freshestVintageUTC: str


class AccuracyResponse(BaseModel):
    cutoffUsed: str
    overall: SummaryMetrics
    dailyBreakdown: List[DailyMetricRecord]
    worstDaysByWape: List[DailyMetricRecord]
    worstDaysByMae: List[DailyMetricRecord]
    errorDistribution: List[HistogramBin]
    diurnalProfile: List[HourlyProfileRecord]
    biasByForecastLevel: List[ForecastLevelBiasRecord]
    cutoffSensitivity: List[CutoffSensitivityRecord]


class LeadTimeBucketRecord(BaseModel):
    bucket: str
    minLeadHours: float
    maxLeadHours: float
    matchedCount: int
    mae: Optional[float]
    rmse: Optional[float]
    wape: Optional[float]
    mbe: Optional[float]


class LeadTimeResponse(BaseModel):
    title: str
    description: str
    cutoffSelectionLeadTimeRangeHours: Dict[str, float]
    buckets: List[LeadTimeBucketRecord]


class DataQualityResponse(BaseModel):
    actualsCompleteness: Dict[str, Any]
    forecastAudit: Dict[str, Any]
    coverageSummary: Dict[str, Any]


class QuantileRecord(BaseModel):
    quantileP10: float
    quantileP50Median: float
    quantileP90: float
    overforecastFrequencyPct: float
    underforecastFrequencyPct: float
    sampleCount: int


class HourlyRiskProfileRecord(BaseModel):
    hourOfDay: int
    hourLabel: str
    p10ErrorMW: float
    p50ErrorMW: float
    p90ErrorMW: float
    overforecastPct: float
    sampleCount: int


class ProcurementRiskResponse(BaseModel):
    label: str
    disclaimer: str
    overallErrorQuantilesMW: QuantileRecord
    hourlyRiskProfile: List[HourlyRiskProfileRecord]
