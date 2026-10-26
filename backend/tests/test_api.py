"""
test_api.py - Integration tests for all FastAPI backend endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["actualsRowCount"] == 1488
    assert data["forecastsRowCount"] == 19856


def test_summary_default():
    response = client.get("/api/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["metrics"]["evaluatedHourlyPeriods"] == 744
    assert data["metrics"]["hourlyCoveragePct"] == 100.0
    assert data["metrics"]["unforecastedHalfHourPeriods"] == 744
    assert "744 hourly delivery periods" in data["provenance"]["evaluationSetDefinition"]
    assert "09:00" in data["provenance"]["cutoffAssumption"]
    assert data["metrics"]["mae"] > 0


def test_summary_date_filtered():
    response = client.get("/api/summary?start_date=2026-01-05&end_date=2026-01-10")
    assert response.status_code == 200
    data = response.json()
    assert data["metrics"]["evaluatedHourlyPeriods"] == 6 * 24  # 144 periods


def test_actuals():
    response = client.get("/api/actuals")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1488
    assert data[0]["fuelType"] == "WIND"
    assert data[0]["generation"] >= 0


def test_actuals_filtered():
    response = client.get("/api/actuals?start_date=2026-01-02&end_date=2026-01-03")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2 * 48  # 96 half-hour periods


def test_forecasts_time_series():
    response = client.get("/api/forecasts?cutoff_time=09:00")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1488
    # Count how many have forecast
    hourly_with_forecast = [d for d in data if d["hasForecast"]]
    assert len(hourly_with_forecast) == 744


def test_accuracy_metrics():
    response = client.get("/api/accuracy?cutoff_time=09:00")
    assert response.status_code == 200
    data = response.json()
    assert "09:00 Europe/London on D-1" in data["cutoffUsed"]
    assert "Assumed decision cutoff (configurable)" in data["cutoffUsed"]
    assert len(data["dailyBreakdown"]) == 31
    assert len(data["worstDaysByWape"]) == 5
    assert len(data["worstDaysByMae"]) == 5
    assert len(data["diurnalProfile"]) == 24
    assert len(data["biasByForecastLevel"]) > 0
    assert len(data["cutoffSensitivity"]) >= 3


def test_vintages_lead_time():
    response = client.get("/api/forecast-vintages?cutoff_time=09:00")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Error by forecast lead time (all forecast vintages with positive lead time)"
    assert len(data["buckets"]) >= 6
    assert data["cutoffSelectionLeadTimeRangeHours"]["minLeadHours"] == 16.5
    assert data["cutoffSelectionLeadTimeRangeHours"]["maxLeadHours"] == 39.5


def test_invalid_requests():
    # Bad cutoff format
    resp_bad_cutoff = client.get("/api/accuracy?cutoff=99:99")
    assert resp_bad_cutoff.status_code == 400
    assert "Invalid cutoff format" in resp_bad_cutoff.json()["detail"]

    # Date range outside scope
    resp_bad_date = client.get("/api/accuracy?start_date=2025-01-01&end_date=2025-01-10")
    assert resp_bad_date.status_code == 400
    assert "outside the available delivery scope" in resp_bad_date.json()["detail"]

    # Inverted date range
    resp_inverted = client.get("/api/summary?start_date=2026-01-20&end_date=2026-01-10")
    assert resp_inverted.status_code == 400
    assert "cannot be after end_date" in resp_inverted.json()["detail"]


def test_data_quality():
    response = client.get("/api/data-quality")
    assert response.status_code == 200
    data = response.json()
    assert data["actualsCompleteness"]["completenessPct"] == 100.0
    assert data["coverageSummary"]["hourlyPeriodsMatched"] == 744
    assert data["forecastAudit"]["negativeLeadTimeCount"] > 0


def test_procurement_risk():
    response = client.get("/api/procurement-risk?cutoff_time=09:00")
    assert response.status_code == 200
    data = response.json()
    assert "not a trading recommendation" in data["disclaimer"]
    quantiles = data["overallErrorQuantilesMW"]
    assert quantiles["sampleCount"] == 744
    assert quantiles["quantileP10"] < quantiles["quantileP90"]
    assert quantiles["overforecastFrequencyPct"] > 50.0  # Demonstrating positive bias
    assert len(data["hourlyRiskProfile"]) == 24
