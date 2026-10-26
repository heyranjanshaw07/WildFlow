"""
test_analytics.py - Unit tests for forecast selection, strict no look-ahead bias,
and accuracy metrics using hand-computed synthetic cases and real edge cases.
"""

import pytest
from datetime import datetime, date, timedelta, timezone
from zoneinfo import ZoneInfo
import pandas as pd
import numpy as np

from backend.app.analytics.selection import select_cutoff_forecasts, get_cutoff_for_delivery_day
from backend.app.analytics.metrics import (
    compute_summary_metrics,
    compute_daily_breakdown,
    compute_hourly_profile,
    compute_error_histogram,
    compute_lead_time_metrics
)

# ============================================================================
# 1. HAND-COMPUTED METRICS TESTS
# ============================================================================

def test_hand_computed_metrics():
    """
    Hand calculation:
    Forecasts: [100.0, 200.0, 300.0]
    Actuals:   [120.0, 180.0, 300.0]
    Errors (f - a):      [-20.0, +20.0, 0.0]
    Abs Errors |f - a|:  [ 20.0,  20.0, 0.0]
    MAE = (20 + 20 + 0) / 3 = 13.333... -> 13.33
    Squared errors: [400, 400, 0] -> Mean = 800 / 3 = 266.666...
    RMSE = sqrt(266.666...) = 16.3299... -> 16.33
    Sum abs error = 40.0
    Sum actual = 120 + 180 + 300 = 600.0
    WAPE = (40 / 600) * 100 = 6.666... -> 6.67%
    MBE = (-20 + 20 + 0) / 3 = 0.0
    """
    df = pd.DataFrame({
        "startTime": ["2026-01-02T00:00:00Z", "2026-01-02T01:00:00Z", "2026-01-02T02:00:00Z"],
        "actual": [120.0, 180.0, 300.0],
        "forecast": [100.0, 200.0, 300.0],
        "hasForecast": [True, True, True],
        "isHourlyPeriod": [True, True, True]
    })
    
    metrics = compute_summary_metrics(df, hourly_only=True)
    assert metrics["mae"] == 13.33
    assert metrics["rmse"] == 16.33
    assert metrics["wape"] == 6.67
    assert metrics["mbe"] == 0.0
    assert metrics["count"] == 3
    assert metrics["totalActualEnergyMWh"] == 600.0
    assert metrics["totalForecastEnergyMWh"] == 600.0


def test_zero_denominator_wape():
    """Verify that zero actual generation returns None for WAPE without ZeroDivisionError."""
    df = pd.DataFrame({
        "startTime": ["2026-01-02T00:00:00Z", "2026-01-02T01:00:00Z"],
        "actual": [0.0, 0.0],
        "forecast": [50.0, 50.0],
        "hasForecast": [True, True],
        "isHourlyPeriod": [True, True]
    })
    metrics = compute_summary_metrics(df)
    assert metrics["mae"] == 50.0
    assert metrics["wape"] is None  # Zero denominator handled explicitly


def test_empty_metrics():
    """Verify empty input returns None values and zero count."""
    df_empty = pd.DataFrame(columns=["actual", "forecast", "hasForecast", "isHourlyPeriod"])
    metrics = compute_summary_metrics(df_empty)
    assert metrics["count"] == 0
    assert metrics["mae"] is None
    assert metrics["rmse"] is None


# ============================================================================
# 2. VINTAGE SELECTION & NO LOOK-AHEAD BIAS TESTS
# ============================================================================

def test_vintage_selection_and_no_lookahead():
    """
    Delivery day: 2026-01-05
    Cutoff: 09:00 London on 2026-01-04 (2026-01-04T09:00:00Z)
    Candidate vintages for target 2026-01-05T12:00:00Z:
      - Run 1: 2026-01-04T07:30:00Z -> 1000 MW (Valid, older)
      - Run 2: 2026-01-04T08:59:00Z -> 1500 MW (Valid, latest before cutoff)
      - Run 3: 2026-01-04T09:00:01Z -> 9999 MW (Invalid, 1 second AFTER cutoff)
      - Run 4: 2026-01-04T11:30:00Z -> 8888 MW (Invalid, 2.5 hours AFTER cutoff)
    Expected selected vintage: Run 2 (1500 MW).
    """
    actuals = pd.DataFrame([{
        "startTime": "2026-01-05T12:00:00Z",
        "generation": 1400.0
    }])
    
    forecasts = pd.DataFrame([
        {"startTime": "2026-01-05T12:00:00Z", "publishTime": "2026-01-04T07:30:00Z", "generation": 1000.0, "leadTimeHours": 28.5},
        {"startTime": "2026-01-05T12:00:00Z", "publishTime": "2026-01-04T08:59:00Z", "generation": 1500.0, "leadTimeHours": 27.0},
        {"startTime": "2026-01-05T12:00:00Z", "publishTime": "2026-01-04T09:00:01Z", "generation": 9999.0, "leadTimeHours": 26.9},
        {"startTime": "2026-01-05T12:00:00Z", "publishTime": "2026-01-04T11:30:00Z", "generation": 8888.0, "leadTimeHours": 24.5},
    ])

    matched_df, meta = select_cutoff_forecasts(actuals, forecasts, cutoff_hour=9, cutoff_minute=0)
    assert len(matched_df) == 1
    selected = matched_df.iloc[0]
    
    # Must select Run 2
    assert selected["publishTime"] == "2026-01-04T08:59:00Z"
    assert selected["forecast"] == 1500.0
    assert selected["error"] == 100.0  # 1500 - 1400


def test_cutoff_boundary_exact_match():
    """Verify that a forecast published exactly AT the cutoff (publishTime == cutoff) is INCLUDED."""
    actuals = pd.DataFrame([{
        "startTime": "2026-01-05T12:00:00Z",
        "generation": 1400.0
    }])
    forecasts = pd.DataFrame([
        {"startTime": "2026-01-05T12:00:00Z", "publishTime": "2026-01-04T09:00:00Z", "generation": 2500.0, "leadTimeHours": 27.0}
    ])
    matched_df, _ = select_cutoff_forecasts(actuals, forecasts, cutoff_hour=9, cutoff_minute=0)
    assert matched_df.iloc[0]["publishTime"] == "2026-01-04T09:00:00Z"
    assert matched_df.iloc[0]["forecast"] == 2500.0


def test_cutoff_boundary_one_second_after():
    """Verify that a forecast published 1 second after the cutoff is strictly EXCLUDED."""
    actuals = pd.DataFrame([{
        "startTime": "2026-01-05T12:00:00Z",
        "generation": 1400.0
    }])
    forecasts = pd.DataFrame([
        # Published 1 second after 09:00:00
        {"startTime": "2026-01-05T12:00:00Z", "publishTime": "2026-01-04T09:00:01Z", "generation": 2500.0, "leadTimeHours": 27.0}
    ])
    matched_df, _ = select_cutoff_forecasts(actuals, forecasts, cutoff_hour=9, cutoff_minute=0)
    assert not matched_df.iloc[0]["hasForecast"]
    assert matched_df.iloc[0]["forecast"] is None or pd.isna(matched_df.iloc[0]["forecast"])


# ============================================================================
# 3. REAL EDGE CASE: 12:00Z PUBLICATION CUTOFF TEST
# ============================================================================

def test_real_edge_case_1200_cutoff():
    """
    Test real edge case from 15 Jan 2026 data:
    A run was published at 12:25Z on 15 Jan instead of the usual 11:30Z; the 12:00 cutoff therefore uses the 09:30Z run for 16 Jan.
    - Under a 12:00 cutoff (12:00:00 Europe/London), 12:25:00Z is after cutoff and must be EXCLUDED,
      falling back to the freshest eligible run: 2026-01-15T09:30:00Z.
    - Under a 12:30 cutoff (12:30:00 Europe/London), the 12:25:00Z run is INCLUDED.
    All timestamps and generation numbers below are authentic values from the processed Elexon datasets.
    """
    actuals = pd.DataFrame([{
        "startTime": "2026-01-16T15:00:00Z",
        "generation": 7659.0
    }])
    
    forecasts = pd.DataFrame([
        {"startTime": "2026-01-16T15:00:00Z", "publishTime": "2026-01-15T09:30:00Z", "generation": 7947.0, "leadTimeHours": 29.5},
        {"startTime": "2026-01-16T15:00:00Z", "publishTime": "2026-01-15T12:25:00Z", "generation": 8090.0, "leadTimeHours": 26.58},
    ])

    # Case 1: Cutoff at 12:00 Europe/London (12:00:00Z)
    # The 12:25:00Z run was published after 12:00:00Z, so it must be EXCLUDED, falling back to 09:30:00Z
    df_1200, _ = select_cutoff_forecasts(actuals, forecasts, cutoff_hour=12, cutoff_minute=0)
    assert df_1200.iloc[0]["publishTime"] == "2026-01-15T09:30:00Z"
    assert df_1200.iloc[0]["forecast"] == 7947.0

    # Case 2: Cutoff at 12:30 Europe/London (12:30:00Z)
    # The 12:25:00Z run was published before 12:30:00Z, so it must be INCLUDED
    df_1230, _ = select_cutoff_forecasts(actuals, forecasts, cutoff_hour=12, cutoff_minute=30)
    assert df_1230.iloc[0]["publishTime"] == "2026-01-15T12:25:00Z"
    assert df_1230.iloc[0]["forecast"] == 8090.0


# ============================================================================
# 4. HOURLY EVALUATION SET & NO FILLING ZERO
# ============================================================================

def test_hourly_evaluation_set_and_no_zero_filling():
    """
    Verify that:
    1. Hourly :00 actuals match with available forecasts.
    2. Half-hourly :30 actuals remain with hasForecast=False and forecast=None (NEVER filled with 0 or forward-filled).
    """
    actuals = pd.DataFrame([
        {"startTime": "2026-01-02T10:00:00Z", "generation": 15000.0},
        {"startTime": "2026-01-02T10:30:00Z", "generation": 15200.0},  # Half-hour period
        {"startTime": "2026-01-02T11:00:00Z", "generation": 15500.0},
    ])
    forecasts = pd.DataFrame([
        {"startTime": "2026-01-02T10:00:00Z", "publishTime": "2026-01-01T07:30:00Z", "generation": 14800.0, "leadTimeHours": 26.5},
        {"startTime": "2026-01-02T11:00:00Z", "publishTime": "2026-01-01T07:30:00Z", "generation": 15300.0, "leadTimeHours": 27.5},
    ])

    matched_df, meta = select_cutoff_forecasts(actuals, forecasts, cutoff_hour=9, cutoff_minute=0)
    assert len(matched_df) == 3
    
    row_1000 = matched_df[matched_df["startTime"] == "2026-01-02T10:00:00Z"].iloc[0]
    row_1030 = matched_df[matched_df["startTime"] == "2026-01-02T10:30:00Z"].iloc[0]
    row_1100 = matched_df[matched_df["startTime"] == "2026-01-02T11:00:00Z"].iloc[0]

    assert bool(row_1000["hasForecast"]) is True
    assert row_1000["forecast"] == 14800.0

    # 10:30 must NOT be zero-filled or forward-filled
    assert bool(row_1030["hasForecast"]) is False
    assert row_1030["forecast"] is None or pd.isna(row_1030["forecast"])
    assert row_1030["actual"] == 15200.0
    assert row_1030["error"] is None or pd.isna(row_1030["error"])

    assert bool(row_1100["hasForecast"]) is True
    assert row_1100["forecast"] == 15300.0


def test_duplicate_publication_flag():
    """Verify that multiple publications at the exact same max publishTime trigger a duplicate flag."""
    actuals = pd.DataFrame([{
        "startTime": "2026-01-02T10:00:00Z",
        "generation": 15000.0
    }])
    forecasts = pd.DataFrame([
        {"startTime": "2026-01-02T10:00:00Z", "publishTime": "2026-01-01T07:30:00Z", "generation": 14000.0, "leadTimeHours": 26.5},
        # Duplicate at same publishTime
        {"startTime": "2026-01-02T10:00:00Z", "publishTime": "2026-01-01T07:30:00Z", "generation": 14200.0, "leadTimeHours": 26.5},
    ])
    matched_df, meta = select_cutoff_forecasts(actuals, forecasts, cutoff_hour=9, cutoff_minute=0)
    assert bool(matched_df.iloc[0]["hasDuplicatePublication"]) is True
    assert meta["duplicatePublicationCount"] == 1
