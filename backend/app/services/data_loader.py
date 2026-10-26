"""
data_loader.py - In-memory caching and loading of processed Elexon datasets.
"""

from pathlib import Path
import json
from typing import Optional, Tuple, Dict, Any
import pandas as pd
from backend.app.config import settings

_ACTUALS_DF: Optional[pd.DataFrame] = None
_FORECASTS_DF: Optional[pd.DataFrame] = None
_COVERAGE_REPORT: Optional[Dict[str, Any]] = None


def get_data_paths() -> Tuple[Path, Path, Path]:
    """Get absolute paths to processed datasets and coverage report."""
    candidate_dirs = [
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "processed",
        Path(__file__).resolve().parent.parent.parent / "data" / "processed",
        Path.cwd() / "api" / "data" / "processed",
        Path.cwd() / "data" / "processed",
        Path("/var/task/api/data/processed"),
        Path("/var/task/data/processed"),
        settings.data_dir / "processed",
    ]
    for d in candidate_dirs:
        act = d / "actuals_jan2026.csv"
        fc = d / "forecasts_jan2026.csv"
        if act.exists() and fc.exists():
            rep = d / "coverage_report.json"
            return act, fc, rep

    # Recursive search fallback in case Lambda extracted to an unexpected directory
    for search_root in [Path(__file__).resolve().parent.parent.parent.parent, Path.cwd(), Path("/var/task")]:
        try:
            if search_root.exists():
                for found in search_root.rglob("actuals_jan2026.csv"):
                    p_dir = found.parent
                    fc = p_dir / "forecasts_jan2026.csv"
                    if fc.exists():
                        return found, fc, p_dir / "coverage_report.json"
        except Exception:
            pass

    # Fallback to configured settings.data_dir
    processed_dir = settings.data_dir / "processed"
    return (
        processed_dir / "actuals_jan2026.csv",
        processed_dir / "forecasts_jan2026.csv",
        processed_dir / "coverage_report.json"
    )



def load_datasets() -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Load and cache processed datasets in memory."""
    global _ACTUALS_DF, _FORECASTS_DF, _COVERAGE_REPORT

    if _ACTUALS_DF is not None and _FORECASTS_DF is not None and _COVERAGE_REPORT is not None:
        return _ACTUALS_DF, _FORECASTS_DF, _COVERAGE_REPORT

    actuals_path, forecasts_path, report_path = get_data_paths()

    if not actuals_path.exists() or not forecasts_path.exists():
        raise FileNotFoundError(
            f"Processed data files not found (checked: {actuals_path}, cwd: {Path.cwd()}). "
            "Please ensure data/processed is included in deployment."
        )

    _ACTUALS_DF = pd.read_csv(actuals_path)
    _FORECASTS_DF = pd.read_csv(forecasts_path)

    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            _COVERAGE_REPORT = json.load(f)
    else:
        _COVERAGE_REPORT = {}

    return _ACTUALS_DF, _FORECASTS_DF, _COVERAGE_REPORT


def get_actuals() -> pd.DataFrame:
    """Retrieve actuals DataFrame."""
    act, _, _ = load_datasets()
    return act


def get_forecasts() -> pd.DataFrame:
    """Retrieve forecasts DataFrame."""
    _, fc, _ = load_datasets()
    return fc


def get_coverage_report() -> Dict[str, Any]:
    """Retrieve coverage report dictionary."""
    _, _, rep = load_datasets()
    return rep
