"""
summary.py - Dashboard overview and data provenance endpoint.
"""

from typing import Optional
from fastapi import APIRouter, Query
from backend.app.services.data_loader import get_actuals, get_forecasts, get_coverage_report
from backend.app.analytics.selection import select_cutoff_forecasts
from backend.app.analytics.metrics import compute_summary_metrics
from backend.app.models.schemas import SummaryResponse, SummaryMetrics, ProvenanceInfo
from backend.app.utils.validation import parse_and_validate_cutoff, validate_date_range

router = APIRouter(tags=["Summary"])


@router.get("/summary", response_model=SummaryResponse)
def get_summary(
    cutoff_time: Optional[str] = Query(None, description="Cutoff time in HH:MM Europe/London on D-1"),
    cutoff: Optional[str] = Query(None, description="Alias for cutoff_time in HH:MM Europe/London on D-1"),
    start_date: Optional[str] = Query(None, description="Start delivery date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End delivery date YYYY-MM-DD")
) -> SummaryResponse:
    """Return KPI summary metrics, data provenance, and dataset coverage."""
    act_df = get_actuals()
    fc_df = get_forecasts()
    report = get_coverage_report()

    # Validate inputs
    active_cutoff = cutoff or cutoff_time or "09:00"
    c_hour, c_min = parse_and_validate_cutoff(active_cutoff)
    validate_date_range(start_date, end_date)

    matched_df, meta = select_cutoff_forecasts(
        act_df, fc_df, cutoff_hour=c_hour, cutoff_minute=c_min, timezone_name="Europe/London"
    )

    # Date filter if requested
    if start_date:
        matched_df = matched_df[matched_df["deliveryDate"] >= start_date]
    if end_date:
        matched_df = matched_df[matched_df["deliveryDate"] <= end_date]

    metrics_raw = compute_summary_metrics(matched_df, hourly_only=True)

    # Determine selected publishTime range
    valid_pub_times = matched_df["publishTime"].dropna().tolist()
    pub_range_str = (
        f"{min(valid_pub_times)} to {max(valid_pub_times)}"
        if valid_pub_times
        else "None"
    )

    metrics_obj = SummaryMetrics(
        mae=metrics_raw["mae"],
        rmse=metrics_raw["rmse"],
        wape=metrics_raw["wape"],
        mbe=metrics_raw["mbe"],
        evaluatedHourlyPeriods=metrics_raw["count"],
        expectedHourlyPeriods=meta["expectedHourlyPeriods"],
        hourlyCoveragePct=meta["hourlyCoveragePct"],
        unforecastedHalfHourPeriods=meta["halfHourPeriodsWithoutForecast"],
        approxTotalActualEnergyMWh=metrics_raw["approxTotalActualEnergyMWh"],
        approxTotalForecastEnergyMWh=metrics_raw["approxTotalForecastEnergyMWh"],
        energyNote=metrics_raw["energyNote"]
    )

    provenance_obj = ProvenanceInfo(
        actualsSourceUrl="https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream?fuelType=WIND",
        forecastsSourceUrl="https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream",
        dataSource="Elexon BMRS National Wind Generation Stream (FUELHH & WINDFOR)",
        units="Megawatts (MW) for instantaneous power; MWh for hourly energy estimates",
        fetchDateUTC="2026-10-25T08:18:00Z",
        decisionDatesScope="1 Jan 2026 to 31 Jan 2026",
        deliveryDaysScope="2 Jan 2026 00:00 UTC to 1 Feb 2026 23:30 UTC",
        evaluationSetDefinition=(
            "744 hourly delivery periods (:00 timestamps) matched with 100% completeness. "
            "744 half-hour actuals at :30 have no forecast by design because WINDFOR is published at hourly resolution."
        ),
        cutoffAssumption=f"{c_hour:02d}:{c_min:02d} Europe/London on D-1 (Assumed decision cutoff (configurable))",
        selectedPublishTimeRange=pub_range_str
    )

    return SummaryResponse(
        metrics=metrics_obj,
        provenance=provenance_obj,
        dataAvailability={
            "deliveryDaysCount": 31,
            "totalActualsRecorded": len(act_df),
            "hourlyEvaluationPeriods": meta["expectedHourlyPeriods"],
            "matchedHourlyPeriods": meta["matchedHourlyPeriods"],
            "halfHourPeriodsWithoutForecast": meta["halfHourPeriodsWithoutForecast"],
            "status": "Available & Fully Cached"
        }
    )
