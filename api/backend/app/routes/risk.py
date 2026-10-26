"""
risk.py - Empirical uncertainty and procurement risk distributions.
"""

from typing import Optional, List
from fastapi import APIRouter, Query
import numpy as np
import pandas as pd
from backend.app.services.data_loader import get_actuals, get_forecasts
from backend.app.analytics.selection import select_cutoff_forecasts
from backend.app.models.schemas import (
    ProcurementRiskResponse,
    QuantileRecord,
    HourlyRiskProfileRecord
)
from backend.app.utils.validation import parse_and_validate_cutoff, validate_date_range

router = APIRouter(tags=["Procurement Risk"])


@router.get("/procurement-risk", response_model=ProcurementRiskResponse)
def get_procurement_risk(
    cutoff_time: Optional[str] = Query(None, description="Cutoff time in HH:MM Europe/London on D-1"),
    cutoff: Optional[str] = Query(None, description="Alias for cutoff_time in HH:MM Europe/London on D-1"),
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD")
) -> ProcurementRiskResponse:
    """
    Return empirical forecast error quantiles (P10/P50/P90) and over/under-forecast frequencies.
    Labeled as an indicative forecast-error distribution, not a trading recommendation.
    """
    act_df = get_actuals()
    fc_df = get_forecasts()

    active_cutoff = cutoff or cutoff_time or "09:00"
    c_hour, c_min = parse_and_validate_cutoff(active_cutoff)
    validate_date_range(start_date, end_date)

    matched_df, _ = select_cutoff_forecasts(
        act_df, fc_df, cutoff_hour=c_hour, cutoff_minute=c_min, timezone_name="Europe/London"
    )

    if start_date:
        matched_df = matched_df[matched_df["deliveryDate"] >= start_date]
    if end_date:
        matched_df = matched_df[matched_df["deliveryDate"] <= end_date]

    eval_df = matched_df[matched_df["hasForecast"] & matched_df["isHourlyPeriod"]].copy()

    if eval_df.empty:
        empty_quantile = QuantileRecord(
            quantileP10=0.0,
            quantileP50Median=0.0,
            quantileP90=0.0,
            overforecastFrequencyPct=0.0,
            underforecastFrequencyPct=0.0,
            sampleCount=0
        )
        return ProcurementRiskResponse(
            label="Indicative Wind-Generation Forecast Risk",
            disclaimer="Indicative forecast-error distribution, not a trading recommendation.",
            overallErrorQuantilesMW=empty_quantile,
            hourlyRiskProfile=[]
        )

    errors = (eval_df["forecast"] - eval_df["actual"]).to_numpy(dtype=float)
    p10 = float(np.percentile(errors, 10))
    p50 = float(np.percentile(errors, 50))
    p90 = float(np.percentile(errors, 90))

    over_count = int(np.sum(errors > 0))
    under_count = int(np.sum(errors < 0))
    n = len(errors)

    over_pct = round((over_count / n) * 100.0, 2)
    under_pct = round((under_count / n) * 100.0, 2)

    overall_quantile = QuantileRecord(
        quantileP10=round(p10, 2),
        quantileP50Median=round(p50, 2),
        quantileP90=round(p90, 2),
        overforecastFrequencyPct=over_pct,
        underforecastFrequencyPct=under_pct,
        sampleCount=n
    )

    # Hourly diurnal profile
    eval_df["hourOfDay"] = eval_df["startTime"].apply(lambda s: int(s[11:13]))
    hourly_profiles = []

    for h, group in eval_df.groupby("hourOfDay", sort=True):
        h_errors = (group["forecast"] - group["actual"]).to_numpy(dtype=float)
        h_p10 = float(np.percentile(h_errors, 10))
        h_p50 = float(np.percentile(h_errors, 50))
        h_p90 = float(np.percentile(h_errors, 90))
        h_over = round(float(np.sum(h_errors > 0) / len(h_errors) * 100.0), 2)

        hourly_profiles.append(HourlyRiskProfileRecord(
            hourOfDay=int(h),
            hourLabel=f"{h:02d}:00",
            p10ErrorMW=round(h_p10, 2),
            p50ErrorMW=round(h_p50, 2),
            p90ErrorMW=round(h_p90, 2),
            overforecastPct=h_over,
            sampleCount=len(group)
        ))

    return ProcurementRiskResponse(
        label="Indicative Wind-Generation Forecast Risk",
        disclaimer=(
            "Indicative forecast-error distribution based on empirical historical errors, "
            "not a trading recommendation or advice. No bias correction has been applied."
        ),
        overallErrorQuantilesMW=overall_quantile,
        hourlyRiskProfile=hourly_profiles
    )
