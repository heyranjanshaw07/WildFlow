"""
actuals.py - Actual outturn records endpoint.
"""

from typing import Optional, List
from fastapi import APIRouter, Query
from backend.app.services.data_loader import get_actuals
from backend.app.models.schemas import ActualRecord
from backend.app.utils.validation import validate_date_range

router = APIRouter(tags=["Actuals"])


@router.get("/actuals", response_model=List[ActualRecord])
def get_actuals_series(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD")
) -> List[ActualRecord]:
    """Retrieve actual wind outturn generation records."""
    validate_date_range(start_date, end_date)
    df = get_actuals().copy()
    if start_date:
        df = df[df["settlementDate"] >= start_date]
    if end_date:
        df = df[df["settlementDate"] <= end_date]

    records = []
    for _, r in df.iterrows():
        records.append(ActualRecord(
            startTime=r["startTime"],
            startTimeUK=r["startTimeUK"],
            settlementDate=r["settlementDate"],
            settlementPeriod=int(r["settlementPeriod"]),
            fuelType=r["fuelType"],
            generation=float(r["generation"]),
            publishTime=r["publishTime"]
        ))
    return records
