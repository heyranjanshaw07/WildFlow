"""
vintages.py - Lead-time analysis across all positive-lead forecast vintages.
"""

from typing import Optional
from fastapi import APIRouter, Query
import pandas as pd
from backend.app.services.data_loader import get_actuals, get_forecasts
from backend.app.analytics.selection import select_cutoff_forecasts
from backend.app.analytics.metrics import compute_lead_time_metrics
from backend.app.models.schemas import LeadTimeResponse, LeadTimeBucketRecord
from backend.app.utils.validation import parse_and_validate_cutoff

router = APIRouter(tags=["Vintages"])


@router.get("/forecast-vintages", response_model=LeadTimeResponse)
def get_forecast_vintages_lead_time(
    cutoff_time: Optional[str] = Query(None, description="Cutoff time in HH:MM Europe/London on D-1"),
    cutoff: Optional[str] = Query(None, description="Alias for cutoff_time in HH:MM Europe/London on D-1")
) -> LeadTimeResponse:
    """
    Return accuracy metrics across all forecast vintages with positive lead time,
    along with the specific lead-time range utilized by cutoff-selected forecasts.
    """
    act_df = get_actuals()
    fc_df = get_forecasts()

    active_cutoff = cutoff or cutoff_time or "09:00"
    c_hour, c_min = parse_and_validate_cutoff(active_cutoff)

    # Calculate lead-time range for cutoff-selected forecasts
    matched_df, _ = select_cutoff_forecasts(act_df, fc_df, cutoff_hour=c_hour, cutoff_minute=c_min)
    valid_selected = matched_df[matched_df["hasForecast"] & matched_df["isHourlyPeriod"]]
    selected_lts = valid_selected["leadTimeHours"].dropna().tolist()
    
    sel_min = float(min(selected_lts)) if selected_lts else 0.0
    sel_max = float(max(selected_lts)) if selected_lts else 0.0
    sel_mean = float(sum(selected_lts) / len(selected_lts)) if selected_lts else 0.0

    # Bucketed lead-time accuracy across all positive-lead forecasts targeting January
    buckets_raw = compute_lead_time_metrics(fc_df, act_df)
    bucket_records = [LeadTimeBucketRecord(**b) for b in buckets_raw]

    return LeadTimeResponse(
        title="Error by forecast lead time (all forecast vintages with positive lead time)",
        description=(
            "Evaluates forecast accuracy across all available forecast vintages targeting January 2026 "
            "grouped by lead time (startTime - publishTime). Negative lead times (startTime < publishTime) "
            "are excluded from active forecasting analysis."
        ),
        cutoffSelectionLeadTimeRangeHours={
            "minLeadHours": round(sel_min, 1),
            "maxLeadHours": round(sel_max, 1),
            "meanLeadHours": round(sel_mean, 1)
        },
        buckets=bucket_records
    )
