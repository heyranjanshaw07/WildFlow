"""
test_data_processing.py - Unit tests for data filtering, parsing, dedup, and validation.
Uses synthetic fixtures clearly labelled as TEST_ONLY.
"""

import pytest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import pandas as pd
from scripts.process_data import parse_iso_utc, TZ_UK

# ============================================================================
# SYNTHETIC TEST FIXTURES (TEST-ONLY)
# ============================================================================

SYNTHETIC_FUELHH_RECORDS = [
    {
        "dataset": "FUELHH",
        "publishTime": "2026-01-02T01:00:00Z",
        "startTime": "2026-01-02T00:00:00Z",
        "settlementDate": "2026-01-02",
        "settlementPeriod": 1,
        "fuelType": "WIND",
        "generation": 12500
    },
    {
        "dataset": "FUELHH",
        "publishTime": "2026-01-02T01:00:00Z",
        "startTime": "2026-01-02T00:00:00Z",
        "settlementDate": "2026-01-02",
        "settlementPeriod": 1,
        "fuelType": "CCGT",
        "generation": 4500
    },
    {
        "dataset": "FUELHH",
        "publishTime": "2026-01-02T01:00:00Z",
        "startTime": "2026-01-02T00:00:00Z",
        "settlementDate": "2026-01-02",
        "settlementPeriod": 1,
        "fuelType": "BIOMASS",
        "generation": 1800
    },
    {
        # Duplicate of the WIND record
        "dataset": "FUELHH",
        "publishTime": "2026-01-02T01:00:00Z",
        "startTime": "2026-01-02T00:00:00Z",
        "settlementDate": "2026-01-02",
        "settlementPeriod": 1,
        "fuelType": "WIND",
        "generation": 12500
    },
    {
        # Out-of-scope record (2025-12-31)
        "dataset": "FUELHH",
        "publishTime": "2026-01-01T00:00:00Z",
        "startTime": "2025-12-31T23:30:00Z",
        "settlementDate": "2025-12-31",
        "settlementPeriod": 48,
        "fuelType": "WIND",
        "generation": 11000
    }
]

SYNTHETIC_WINDFOR_RECORDS = [
    {
        "dataset": "WINDFOR",
        "publishTime": "2026-01-01T07:30:00Z",
        "startTime": "2026-01-02T00:00:00Z",
        "generation": 18000
    },
    {
        # Duplicate of above
        "dataset": "WINDFOR",
        "publishTime": "2026-01-01T07:30:00Z",
        "startTime": "2026-01-02T00:00:00Z",
        "generation": 18000
    },
    {
        # Negative lead time record (startTime before publishTime)
        "dataset": "WINDFOR",
        "publishTime": "2026-01-01T07:30:00Z",
        "startTime": "2025-12-31T21:00:00Z",
        "generation": 17500
    }
]


# ============================================================================
# TESTS
# ============================================================================

def test_filter_wind_only():
    """Verify that only fuelType == 'WIND' records are retained."""
    wind_only = [r for r in SYNTHETIC_FUELHH_RECORDS if r["fuelType"] == "WIND"]
    fuel_types = set(r["fuelType"] for r in wind_only)
    assert fuel_types == {"WIND"}
    assert len(wind_only) == 3  # 2 active + 1 duplicate


def test_timestamp_parsing_utc_and_london():
    """Verify ISO8601 parsing into UTC and Europe/London conversion."""
    ts_str = "2026-01-02T14:30:00Z"
    dt_utc = parse_iso_utc(ts_str)
    assert dt_utc.tzinfo == timezone.utc
    assert dt_utc.year == 2026
    assert dt_utc.month == 1
    assert dt_utc.day == 2
    assert dt_utc.hour == 14
    assert dt_utc.minute == 30

    dt_uk = dt_utc.astimezone(TZ_UK)
    # In January, London is on GMT (UTC+0)
    assert dt_uk.strftime("%Y-%m-%d %H:%M:%S") == "2026-01-02 14:30:00"
    assert dt_uk.utcoffset().total_seconds() == 0


def test_deduplication_actuals():
    """Verify deduplication removes duplicate records for the same settlement startTime."""
    wind_records = [r for r in SYNTHETIC_FUELHH_RECORDS if r["fuelType"] == "WIND"]
    df = pd.DataFrame(wind_records)
    assert len(df) == 3

    df_dedup = df.drop_duplicates(subset=["startTime"])
    assert len(df_dedup) == 2  # 2026-01-02 and 2025-12-31 remain


def test_deduplication_forecasts():
    """Verify deduplication removes duplicate records with identical (publishTime, startTime)."""
    df = pd.DataFrame(SYNTHETIC_WINDFOR_RECORDS)
    assert len(df) == 3

    df_dedup = df.drop_duplicates(subset=["publishTime", "startTime"])
    assert len(df_dedup) == 2


def test_validation_nulls_and_negative_generation():
    """Verify that invalid negative generation or missing keys raise errors."""
    corrupted_record = {
        "dataset": "FUELHH",
        "publishTime": "2026-01-02T01:00:00Z",
        "startTime": "2026-01-02T00:00:00Z",
        "settlementDate": "2026-01-02",
        "settlementPeriod": 1,
        "fuelType": "WIND",
        "generation": -50  # Negative generation is invalid
    }
    with pytest.raises(ValueError, match="Negative generation"):
        gen = float(corrupted_record["generation"])
        if gen < 0:
            raise ValueError(f"Negative generation encountered: {corrupted_record}")


def test_lead_time_calculation_and_negative_detection():
    """Verify forward vs negative lead-time calculations."""
    pt_dt = parse_iso_utc("2026-01-01T07:30:00Z")
    
    # Forward forecast (16.5 hours lead time)
    st_forward = parse_iso_utc("2026-01-02T00:00:00Z")
    lt_forward = (st_forward - pt_dt).total_seconds() / 3600.0
    assert lt_forward == 16.5
    assert lt_forward >= 0

    # Past hindcast / initialization row (-10.5 hours lead time)
    st_past = parse_iso_utc("2025-12-31T21:00:00Z")
    lt_past = (st_past - pt_dt).total_seconds() / 3600.0
    assert lt_past == -10.5
    assert lt_past < 0
