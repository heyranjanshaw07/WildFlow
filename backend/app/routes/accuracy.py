"""
accuracy.py - Accuracy analysis, daily breakdowns, worst days, and bias breakdowns.
"""

from typing import Optional, List
from fastapi import APIRouter, Query
import numpy as np
import pandas as pd
from backend.app.services.data_loader import get_actuals, get_forecasts
from backend.app.analytics.selection import select_cutoff_forecasts
from backend.app.analytics.metrics import (
    compute_summary_metrics,
    compute_daily_breakdown,
    compute_hourly_profile,
    compute_error_histogram
)
from backend.app.models.schemas import (
    AccuracyResponse,
    SummaryMetrics,
    DailyMetricRecord,
    HourlyProfileRecord,
    HistogramBin,
    ForecastLevelBiasRecord,
    CutoffSensitivityRecord
)
from backend.app.utils.validation import parse_and_validate_cutoff, validate_date_range

router = APIRouter(tags=["Accuracy"])


def compute_forecast_level_bias(df_eval: pd.DataFrame) -> List[ForecastLevelBiasRecord]:
    """
    Compute accuracy and bias conditional on the FORECAST level.
    Buckets: < 5,000 MW, 5,000 - 10,000 MW, 10,000 - 15,000 MW, > 15,000 MW.
    """
    if df_eval.empty:
        return []

    bins = [0, 5000, 10000, 15000, float("inf")]
    labels = ["< 5k MW", "5k - 10k MW", "10k - 15k MW", "> 15k MW"]
    df_eval = df_eval.copy()
    df_eval["bucket"] = pd.cut(df_eval["forecast"], bins=bins, labels=labels, right=False)

    records = []
    for label in labels:
        grp = df_eval[df_eval["bucket"] == label]
        if grp.empty:
            continue
        fc = grp["forecast"].to_numpy(dtype=float)
        act = grp["actual"].to_numpy(dtype=float)
        err = fc - act
        abs_err = np.abs(err)
        sum_act = float(np.sum(act))
        wape = (float(np.sum(abs_err)) / sum_act * 100.0) if sum_act > 0 else None

        records.append(ForecastLevelBiasRecord(
            bucket=label,
            count=len(grp),
            forecastMean=round(float(np.mean(fc)), 2),
            actualMean=round(float(np.mean(act)), 2),
            mae=round(float(np.mean(abs_err)), 2),
            mbe=round(float(np.mean(err)), 2),
            wape=round(wape, 2) if wape is not None else None,
            note="Evaluated conditional on the available forecast at cutoff time"
        ))
    return records


def compute_cutoff_sensitivity_comparison(
    act_df: pd.DataFrame,
    fc_df: pd.DataFrame,
    current_hour: int,
    current_minute: int
) -> List[CutoffSensitivityRecord]:
    """Compare selected cutoff against benchmark cutoffs (09:00 vs 12:00 vs 15:00)."""
    comparison_cutoffs = [
        (9, 0, "09:00 Europe/London (Default Cutoff)"),
        (12, 0, "12:00 Europe/London (Comparison Cutoff)"),
        (15, 0, "15:00 Europe/London (Afternoon Cutoff)")
    ]
    
    # If user selected a custom cutoff, include it
    user_tuple = (current_hour, current_minute, f"{current_hour:02d}:{current_minute:02d} Europe/London (Selected)")
    if not any(c[0] == current_hour and c[1] == current_minute for c in comparison_cutoffs):
        comparison_cutoffs.append(user_tuple)
        comparison_cutoffs.sort(key=lambda x: (x[0], x[1]))

    records = []
    for h, m, label in comparison_cutoffs:
        df_matched, meta = select_cutoff_forecasts(act_df, fc_df, cutoff_hour=h, cutoff_minute=m)
        m_stats = compute_summary_metrics(df_matched, hourly_only=True)
        valid_pts = df_matched["publishTime"].dropna().tolist()
        freshest_pt = max(valid_pts) if valid_pts else "None"

        records.append(CutoffSensitivityRecord(
            cutoffTimeUK=label,
            mae=m_stats["mae"] or 0.0,
            rmse=m_stats["rmse"] or 0.0,
            wape=m_stats["wape"],
            mbe=m_stats["mbe"] or 0.0,
            matchedHourlyPeriods=m_stats["count"],
            coveragePct=meta["hourlyCoveragePct"],
            freshestVintageUTC=freshest_pt
        ))
    return records


@router.get("/accuracy", response_model=AccuracyResponse)
def get_accuracy_metrics(
    cutoff_time: Optional[str] = Query(None, description="Cutoff time in HH:MM Europe/London on D-1"),
    cutoff: Optional[str] = Query(None, description="Alias for cutoff_time in HH:MM Europe/London on D-1"),
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD")
) -> AccuracyResponse:
    """Retrieve comprehensive forecast error metrics, distributions, and sensitivity analysis."""
    act_df = get_actuals()
    fc_df = get_forecasts()

    active_cutoff = cutoff or cutoff_time or "09:00"
    c_hour, c_min = parse_and_validate_cutoff(active_cutoff)
    validate_date_range(start_date, end_date)

    matched_df, meta = select_cutoff_forecasts(
        act_df, fc_df, cutoff_hour=c_hour, cutoff_minute=c_min, timezone_name="Europe/London"
    )

    if start_date:
        matched_df = matched_df[matched_df["deliveryDate"] >= start_date]
    if end_date:
        matched_df = matched_df[matched_df["deliveryDate"] <= end_date]

    # Overall metrics
    overall_raw = compute_summary_metrics(matched_df, hourly_only=True)
    overall_obj = SummaryMetrics(
        mae=overall_raw["mae"],
        rmse=overall_raw["rmse"],
        wape=overall_raw["wape"],
        mbe=overall_raw["mbe"],
        evaluatedHourlyPeriods=overall_raw["count"],
        expectedHourlyPeriods=meta["expectedHourlyPeriods"],
        hourlyCoveragePct=meta["hourlyCoveragePct"],
        unforecastedHalfHourPeriods=meta["halfHourPeriodsWithoutForecast"],
        approxTotalActualEnergyMWh=overall_raw["approxTotalActualEnergyMWh"],
        approxTotalForecastEnergyMWh=overall_raw["approxTotalForecastEnergyMWh"],
        energyNote=overall_raw["energyNote"]
    )

    # Daily breakdown
    daily_raw = compute_daily_breakdown(matched_df)
    daily_records = [DailyMetricRecord(**d) for d in daily_raw]

    # Worst days by WAPE (top 5) and by MAE (top 5)
    valid_daily = [d for d in daily_records if d.wape is not None]
    worst_wape = sorted(valid_daily, key=lambda x: x.wape, reverse=True)[:5]
    worst_mae = sorted(daily_records, key=lambda x: x.mae, reverse=True)[:5]

    # Histogram
    hist_raw = compute_error_histogram(matched_df, bin_width_mw=1000.0)
    hist_records = [HistogramBin(**b) for b in hist_raw["bins"]]

    # Diurnal profile
    diurnal_raw = compute_hourly_profile(matched_df)
    diurnal_records = [HourlyProfileRecord(**p) for p in diurnal_raw]

    # Bias by Forecast Level
    eval_df = matched_df[matched_df["hasForecast"] & matched_df["isHourlyPeriod"]].copy()
    forecast_bias_records = compute_forecast_level_bias(eval_df)

    # Cutoff Sensitivity
    sensitivity_records = compute_cutoff_sensitivity_comparison(act_df, fc_df, c_hour, c_min)

    return AccuracyResponse(
        cutoffUsed=f"{c_hour:02d}:{c_min:02d} Europe/London on D-1 (Assumed decision cutoff (configurable))",
        overall=overall_obj,
        dailyBreakdown=daily_records,
        worstDaysByWape=worst_wape,
        worstDaysByMae=worst_mae,
        errorDistribution=hist_records,
        diurnalProfile=diurnal_records,
        biasByForecastLevel=forecast_bias_records,
        cutoffSensitivity=sensitivity_records
    )
