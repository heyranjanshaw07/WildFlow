"""
forecasts.py - Forecast matching and time-series endpoint for interactive charts.
"""

from typing import Optional, List
from fastapi import APIRouter, Query
import pandas as pd
from backend.app.services.data_loader import get_actuals, get_forecasts
from backend.app.analytics.selection import select_cutoff_forecasts
from backend.app.models.schemas import MatchedPeriodRecord
from backend.app.utils.validation import parse_and_validate_cutoff, validate_date_range

router = APIRouter(tags=["Forecasts"])


@router.get("/forecasts", response_model=List[MatchedPeriodRecord])
def get_matched_forecasts(
    cutoff_time: Optional[str] = Query(None, description="Cutoff time in HH:MM Europe/London on D-1"),
    cutoff: Optional[str] = Query(None, description="Alias for cutoff_time in HH:MM Europe/London on D-1"),
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    hourly_only: bool = Query(False, description="If True, filters to hourly :00 periods only")
) -> List[MatchedPeriodRecord]:
    """Retrieve actual vs cutoff forecast time-series for charts and tables."""
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
    if hourly_only:
        matched_df = matched_df[matched_df["isHourlyPeriod"]]

    results = []
    for _, r in matched_df.iterrows():
        f_val = float(r["forecast"]) if pd.notna(r["forecast"]) else None
        err_val = float(r["error"]) if pd.notna(r["error"]) else None
        abs_err_val = float(r["absError"]) if pd.notna(r["absError"]) else None
        lt_val = float(r["leadTimeHours"]) if pd.notna(r["leadTimeHours"]) else None
        pt_val = str(r["publishTime"]) if pd.notna(r["publishTime"]) else None

        results.append(MatchedPeriodRecord(
            startTime=r["startTime"],
            startTimeUK=r["startTimeUK"],
            deliveryDate=r["deliveryDate"],
            settlementPeriod=int(r["settlementPeriod"]),
            isHourlyPeriod=bool(r["isHourlyPeriod"]),
            actual=float(r["actual"]),
            forecast=f_val,
            error=err_val,
            absError=abs_err_val,
            publishTime=pt_val,
            leadTimeHours=lt_val,
            hasForecast=bool(r["hasForecast"]),
            hasDuplicatePublication=bool(r["hasDuplicatePublication"])
        ))

    return results
