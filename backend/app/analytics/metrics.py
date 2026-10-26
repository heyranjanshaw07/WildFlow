"""
metrics.py - Energy-data forecast accuracy metrics and lead-time analysis.

Metrics implemented:
- Mean Absolute Error (MAE): (1/N) * sum(|f - a|)
- Root Mean Squared Error (RMSE): sqrt((1/N) * sum((f - a)^2))
- Weighted Absolute Percentage Error (WAPE): (sum(|f - a|) / sum(|a|)) * 100
- Mean Bias Error (MBE): (1/N) * sum(f - a)
- Error distribution histogram
- Daily breakdowns
- Lead-time bucketed error analysis
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import numpy as np
import pandas as pd


def compute_summary_metrics(
    df_matched: pd.DataFrame,
    hourly_only: bool = True
) -> Dict[str, Any]:
    """
    Compute overall forecast error metrics over the evaluation set.
    
    Args:
        df_matched: DataFrame containing ['actual', 'forecast', 'hasForecast', 'isHourlyPeriod', ...]
        hourly_only: If True, evaluates only hourly periods where both forecast and actual exist.

    Returns:
        Dictionary with MAE, RMSE, WAPE, MBE, total periods, and coverage statistics.
    """
    if df_matched.empty:
        return {
            "mae": None,
            "rmse": None,
            "wape": None,
            "mbe": None,
            "count": 0,
            "totalActualEnergyMWh": 0.0,
            "totalForecastEnergyMWh": 0.0
        }

    # Filter to valid evaluation periods
    eval_df = df_matched[df_matched["hasForecast"] & df_matched["forecast"].notna()].copy()
    if hourly_only:
        eval_df = eval_df[eval_df["isHourlyPeriod"]].copy()

    n = len(eval_df)
    if n == 0:
        return {
            "mae": None,
            "rmse": None,
            "wape": None,
            "mbe": None,
            "count": 0,
            "totalActualEnergyMWh": 0.0,
            "totalForecastEnergyMWh": 0.0
        }

    actuals = eval_df["actual"].to_numpy(dtype=float)
    forecasts = eval_df["forecast"].to_numpy(dtype=float)

    errors = forecasts - actuals
    abs_errors = np.abs(errors)
    squared_errors = errors ** 2

    # MAE
    mae = float(np.mean(abs_errors))

    # RMSE
    rmse = float(np.sqrt(np.mean(squared_errors)))

    # Mean Bias Error (MBE)
    mbe = float(np.mean(errors))

    # WAPE (zero denominator handled)
    sum_abs_actual = float(np.sum(np.abs(actuals)))
    sum_abs_error = float(np.sum(abs_errors))
    if sum_abs_actual > 0:
        wape = float((sum_abs_error / sum_abs_actual) * 100.0)
    else:
        wape = None  # Explicit zero denominator handling

    # Approximate energy calculation (sum of hourly-sampled MW x 1h, :00 samples only)
    approx_actual_mwh = float(np.sum(actuals))
    approx_forecast_mwh = float(np.sum(forecasts))

    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "wape": round(wape, 2) if wape is not None else None,
        "mbe": round(mbe, 2),
        "count": n,
        "approxTotalActualEnergyMWh": round(approx_actual_mwh, 2),
        "approxTotalForecastEnergyMWh": round(approx_forecast_mwh, 2),
        "totalActualEnergyMWh": round(approx_actual_mwh, 2),
        "totalForecastEnergyMWh": round(approx_forecast_mwh, 2),
        "energyNote": "Approximate: sum of hourly-sampled MW x 1h, :00 samples only"
    }


def compute_daily_breakdown(df_matched: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Compute daily accuracy metrics and stats for each delivery day in scope.
    """
    if df_matched.empty:
        return []

    eval_df = df_matched[df_matched["hasForecast"] & df_matched["isHourlyPeriod"]].copy()
    if eval_df.empty:
        return []

    daily_results = []
    for day, group in eval_df.groupby("deliveryDate", sort=True):
        actuals = group["actual"].to_numpy(dtype=float)
        forecasts = group["forecast"].to_numpy(dtype=float)
        errors = forecasts - actuals
        abs_errors = np.abs(errors)

        sum_actual = float(np.sum(np.abs(actuals)))
        sum_err = float(np.sum(abs_errors))
        wape = (sum_err / sum_actual * 100.0) if sum_actual > 0 else None

        daily_results.append({
            "deliveryDate": str(day),
            "periodCount": len(group),
            "mae": round(float(np.mean(abs_errors)), 2),
            "rmse": round(float(np.sqrt(np.mean(errors ** 2))), 2),
            "wape": round(wape, 2) if wape is not None else None,
            "mbe": round(float(np.mean(errors)), 2),
            "actualMean": round(float(np.mean(actuals)), 2),
            "forecastMean": round(float(np.mean(forecasts)), 2),
            "actualMax": round(float(np.max(actuals)), 2),
            "forecastMax": round(float(np.max(forecasts)), 2)
        })

    return daily_results


def compute_hourly_profile(df_matched: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Compute the average diurnal profile by hour of the day (00:00 to 23:00).
    """
    if df_matched.empty:
        return []

    eval_df = df_matched[df_matched["hasForecast"] & df_matched["isHourlyPeriod"]].copy()
    if eval_df.empty:
        return []

    eval_df["hourOfDay"] = eval_df["startTime"].apply(lambda s: int(s[11:13]))

    profile = []
    for hour, group in eval_df.groupby("hourOfDay", sort=True):
        actuals = group["actual"].to_numpy(dtype=float)
        forecasts = group["forecast"].to_numpy(dtype=float)
        errors = forecasts - actuals
        abs_errors = np.abs(errors)

        profile.append({
            "hourOfDay": int(hour),
            "hourLabel": f"{hour:02d}:00",
            "count": len(group),
            "actualAvg": round(float(np.mean(actuals)), 2),
            "forecastAvg": round(float(np.mean(forecasts)), 2),
            "mae": round(float(np.mean(abs_errors)), 2),
            "mbe": round(float(np.mean(errors)), 2)
        })

    return profile


def compute_error_histogram(
    df_matched: pd.DataFrame,
    bin_width_mw: float = 500.0
) -> Dict[str, Any]:
    """
    Compute histogram of forecast errors (forecast - actual) in MW.
    """
    eval_df = df_matched[df_matched["hasForecast"] & df_matched["isHourlyPeriod"]].copy()
    if eval_df.empty:
        return {"bins": [], "minError": 0.0, "maxError": 0.0, "totalCount": 0}

    errors = (eval_df["forecast"] - eval_df["actual"]).to_numpy(dtype=float)
    min_err = float(np.min(errors))
    max_err = float(np.max(errors))

    # Construct bins rounded to nearest bin_width_mw
    start_edge = np.floor(min_err / bin_width_mw) * bin_width_mw
    end_edge = np.ceil(max_err / bin_width_mw) * bin_width_mw
    if start_edge == end_edge:
        end_edge += bin_width_mw

    bin_edges = np.arange(start_edge, end_edge + bin_width_mw, bin_width_mw)
    counts, _ = np.histogram(errors, bins=bin_edges)

    bins_data = []
    for i in range(len(counts)):
        b_min = float(bin_edges[i])
        b_max = float(bin_edges[i + 1])
        cnt = int(counts[i])
        bins_data.append({
            "binRange": f"{int(b_min)} to {int(b_max)} MW",
            "binMin": b_min,
            "binMax": b_max,
            "binMid": (b_min + b_max) / 2.0,
            "count": cnt,
            "pct": round((cnt / len(errors)) * 100.0, 2)
        })

    return {
        "bins": bins_data,
        "minError": round(min_err, 2),
        "maxError": round(max_err, 2),
        "totalCount": len(errors)
    }


def compute_lead_time_metrics(
    df_forecasts: pd.DataFrame,
    df_actuals: pd.DataFrame,
    lead_time_buckets: Optional[List[Tuple[float, float, str]]] = None
) -> List[Dict[str, Any]]:
    """
    Evaluate forecast accuracy across different forecast lead-time horizons.
    Lead time = startTime - publishTime (in hours).
    """
    if lead_time_buckets is None:
        lead_time_buckets = [
            (0.0, 6.0, "0h - 6h"),
            (6.0, 10.0, "6h - 10h"),
            (10.0, 14.0, "10h - 14h"),
            (14.0, 18.0, "14h - 18h"),
            (18.0, 24.0, "18h - 24h"),
            (24.0, 30.0, "24h - 30h"),
            (30.0, 36.0, "30h - 36h"),
            (36.0, 48.0, "36h - 48h"),
            (48.0, 72.0, "48h - 72h")
        ]

    # Pre-map actuals by startTime
    actual_map = {row["startTime"]: float(row["generation"]) for _, row in df_actuals.iterrows()}

    # Clean forward forecasts with non-negative lead time
    clean_f = df_forecasts[df_forecasts["leadTimeHours"] >= 0].copy()

    results = []
    for min_h, max_h, label in lead_time_buckets:
        sub = clean_f[(clean_f["leadTimeHours"] >= min_h) & (clean_f["leadTimeHours"] < max_h)].copy()
        
        # Join with actuals
        matched_pairs = []
        for _, f_row in sub.iterrows():
            st = f_row["startTime"]
            if st in actual_map:
                matched_pairs.append((float(f_row["generation"]), actual_map[st]))

        if not matched_pairs:
            results.append({
                "bucket": label,
                "minLeadHours": min_h,
                "maxLeadHours": max_h,
                "count": 0,
                "matchedCount": 0,
                "mae": None,
                "rmse": None,
                "wape": None,
                "mbe": None
            })
            continue

        forecast_arr = np.array([p[0] for p in matched_pairs], dtype=float)
        actual_arr = np.array([p[1] for p in matched_pairs], dtype=float)
        err = forecast_arr - actual_arr
        abs_err = np.abs(err)

        sum_act = float(np.sum(actual_arr))
        wape = (float(np.sum(abs_err)) / sum_act * 100.0) if sum_act > 0 else None

        results.append({
            "bucket": label,
            "minLeadHours": min_h,
            "maxLeadHours": max_h,
            "count": len(matched_pairs),
            "matchedCount": len(matched_pairs),
            "mae": round(float(np.mean(abs_err)), 2),
            "rmse": round(float(np.sqrt(np.mean(err ** 2))), 2),
            "wape": round(wape, 2) if wape is not None else None,
            "mbe": round(float(np.mean(err)), 2)
        })

    return results
