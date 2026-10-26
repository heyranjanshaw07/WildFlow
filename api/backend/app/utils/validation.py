"""
validation.py - Common parameter validation for WindScope API routes.
"""

import re
from datetime import datetime
from typing import Optional, Tuple
from fastapi import HTTPException


CUTOFF_REGEX = re.compile(r"^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$")
DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")

SCOPE_MIN_DATE = "2026-01-02"
SCOPE_MAX_DATE = "2026-02-01"


def parse_and_validate_cutoff(cutoff_time: Optional[str]) -> Tuple[int, int]:
    """
    Validate and parse cutoff time string in HH:MM format.
    Raises HTTPException(400) if format or values are invalid.
    """
    if not cutoff_time:
        return 9, 0

    cutoff_str = cutoff_time.strip()
    match = CUTOFF_REGEX.match(cutoff_str)
    if not match:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid cutoff format '{cutoff_time}'. Expected HH:MM in 24-hour format (e.g., '09:00', '12:00')."
        )

    hour = int(match.group(1))
    minute = int(match.group(2))
    return hour, minute


def validate_date_range(
    start_date: Optional[str],
    end_date: Optional[str],
    scope_min: str = SCOPE_MIN_DATE,
    scope_max: str = SCOPE_MAX_DATE
) -> None:
    """
    Validate ISO date strings and check they lie within the operational delivery scope.
    Raises HTTPException(400) on invalid dates or out-of-scope ranges.
    """
    if start_date:
        if not DATE_REGEX.match(start_date):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid start_date format '{start_date}'. Expected YYYY-MM-DD."
            )
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid calendar date for start_date '{start_date}'."
            )

    if end_date:
        if not DATE_REGEX.match(end_date):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid end_date format '{end_date}'. Expected YYYY-MM-DD."
            )
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid calendar date for end_date '{end_date}'."
            )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail=f"start_date '{start_date}' cannot be after end_date '{end_date}'."
        )

    if (start_date and start_date > scope_max) or (end_date and end_date < scope_min):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Requested date range ({start_date or '...'} to {end_date or '...'}) "
                f"is entirely outside the available delivery scope ({scope_min} to {scope_max})."
            )
        )
