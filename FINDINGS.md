# Empirical Analysis & Findings: January 2026 UK Wind Forecasts

This document synthesizes the empirical performance findings from the **WindScope** evaluation of National Wind Generation in Great Britain for January 2026. All figures are computed directly from the processed Elexon BMRS datasets (`FUELHH` actuals with `fuelType = 'WIND'` and `WINDFOR` forecast vintages).

---

## 1. Executive Summary & Core Accuracy Metrics

Under the assumed operational decision cutoff of **09:00 Europe/London on day $D - 1$**, day-ahead forecast accuracy over the **744 hourly delivery periods** of January 2026 was evaluated against actual outturn generation:

| Metric | 09:00 Cutoff (Default) | 12:00 Cutoff (Comparison) | Difference / Delta |
| :--- | :---: | :---: | :---: |
| **Mean Absolute Error (MAE)** | **2,022.47 MW** | **1,883.98 MW** | -138.49 MW (-6.85%) |
| **Root Mean Squared Error (RMSE)** | **2,497.41 MW** | **2,350.33 MW** | -147.08 MW (-5.89%) |
| **Weighted Absolute Percentage Error (WAPE)** | **17.92%** | **16.69%** | -1.23 percentage points |
| **Mean Bias Error (MBE)** | **+1,745.94 MW** | **+1,685.27 MW** | -60.67 MW |
| **Evaluated Hourly Periods ($N$)** | **744** | **744** | 100.0% coverage |
| **Approx Total Actual Generation** | **8,396,417 MWh** | **8,396,417 MWh** | Base actual energy |
| **Approx Total Forecast Generation** | **9,695,395 MWh** | **9,650,261 MWh** | -45,134 MWh over-procurement |

*Energy note: Sum of hourly-sampled MW $\times$ 1h over `:00` timestamps only.*

---

## 2. Persistent Positive Forecast Bias

The data reveals a large and persistent over-forecast across the evaluation window:
- **Mean Bias Error (MBE):** Under the 09:00 cutoff, the forecast exceeded actual outturn by an average of **+1,745.94 MW** per hourly period.
- **Over-Forecast Frequency:**
  - **84.68% of evaluated periods** (630 of 744 hours) had a forecast higher than actual outturn ($f > a$).
  - Only **15.32% of periods** (114 of 744 hours) were under-forecast ($f < a$).
- **Empirical Error Distribution Quantiles:**
  - **P10:** -426.4 MW
  - **P50 (Median Error):** +1,581.5 MW
  - **P90:** +4,154.4 MW
- **Diurnal Persistence:**
  - Positive bias persists throughout all 24 hours of the day.
  - Lowest hourly mean bias occurs at **15:00** (+1,277.35 MW).
  - Highest hourly mean bias occurs at **05:00** (+2,339.42 MW).
- **Unexplained Bias Statement:**
  > **Data Finding:** Forecasts exceeded actuals by roughly 1,415 to 1,900 MW in every lead-time bucket; the cause cannot be determined from these two datasets.

---

## 3. Lead-Time Horizon Degradation

### A. All Forecast Vintages with Positive Lead Time
Across all available forecast publications targeting delivery in January 2026 ($N = 14,383$ matched hourly vintage rows), forecast accuracy shows that error increases slightly as lead time expands:

| Lead-Time Horizon | Matched Rows ($N$) | MAE (MW) | RMSE (MW) | WAPE (%) | Mean Bias (MW) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **0h - 6h** | 1,488 | 1,654.09 MW | 2,114.02 MW | 14.71% | +1,428.50 MW |
| **6h - 10h** | 992 | 1,717.54 MW | 2,174.69 MW | 15.18% | +1,494.31 MW |
| **10h - 14h** | 992 | 1,746.23 MW | 2,217.27 MW | 15.40% | +1,539.63 MW |
| **14h - 18h** | 992 | 1,857.19 MW | 2,330.99 MW | 16.39% | +1,664.06 MW |
| **18h - 24h** | 1,488 | 1,936.52 MW | 2,417.16 MW | 17.24% | +1,768.27 MW |
| **24h - 30h** | 1,488 | 1,957.92 MW | 2,423.33 MW | 17.41% | +1,723.56 MW |
| **30h - 36h** | 1,488 | 2,050.41 MW | 2,523.76 MW | 18.11% | +1,714.56 MW |
| **36h - 48h** | 2,945 | 2,233.83 MW | 2,775.89 MW | 19.80% | +1,900.10 MW |
| **48h - 72h** | 2,510 | 2,307.40 MW | 2,922.80 MW | 20.28% | +1,415.05 MW |

### B. Cutoff-Selected Day-Ahead Lead Range
In contrast to the broader vintage pool, the day-ahead decision cutoff selects forecasts within a strictly constrained lead-time window:
- **09:00 London Cutoff:**
  - Selected forecasts have lead times ranging from **16.5 hours** (for 00:00 UTC delivery) to **39.5 hours** (for 23:00 UTC delivery), with a mean lead time of **28.0 hours**.
  - All 744 hourly delivery periods select the 07:30 UTC publication run from day $D - 1$.
- **12:00 London Cutoff:**
  - Selected forecasts have lead times ranging from **12.5 hours** to **37.5 hours**, with a mean lead time of **24.1 hours**.
  - 720 periods select the 11:30 UTC run; 24 periods select the 09:30 UTC run (explained below).
- **Intraday Exclusion ($0\text{h} - 14\text{h}$):** The 3,472 raw forecast rows with lead times between 0h and 14h represent intraday updates published after the assumed decision cutoff. They are excluded from day-ahead evaluation to prevent look-ahead bias.

---

## 4. Notable Days & Worst-Case Forecast Performance

Ranked by **Weighted Absolute Percentage Error (WAPE)**, the top 5 worst forecast days for January 2026 under the 09:00 cutoff were:

| Rank | Delivery Date | WAPE (%) | MAE (MW) | RMSE (MW) | Actual Mean (MW) | Forecast Mean (MW) | Mean Bias (MW) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | **2026-01-28** | **91.79%** | 5,328.96 MW | 5,355.71 MW | 5,805.62 MW | 11,134.58 MW | +5,328.96 MW |
| 2 | **2026-01-08** | **41.20%** | 1,852.71 MW | 2,053.33 MW | 4,496.88 MW | 5,372.83 MW | +875.96 MW |
| 3 | **2026-01-11** | **35.93%** | 4,853.00 MW | 4,907.31 MW | 13,506.00 MW | 18,359.00 MW | +4,853.00 MW |
| 4 | **2026-01-12** | **33.75%** | 4,875.42 MW | 5,137.56 MW | 14,445.04 MW | 19,320.46 MW | +4,875.42 MW |
| 5 | **2026-01-18** | **32.30%** | 1,594.50 MW | 1,654.67 MW | 4,937.29 MW | 6,531.79 MW | +1,594.50 MW |

Ranked by **Mean Absolute Error (MAE)**:

| Rank | Delivery Date | MAE (MW) | RMSE (MW) | WAPE (%) | Actual Mean (MW) | Forecast Mean (MW) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | **2026-01-28** | **5,328.96 MW** | 5,355.71 MW | 91.79% | 5,805.62 MW | 11,134.58 MW |
| 2 | **2026-01-12** | **4,875.42 MW** | 5,137.56 MW | 33.75% | 14,445.04 MW | 19,320.46 MW |
| 3 | **2026-01-11** | **4,853.00 MW** | 4,907.31 MW | 35.93% | 13,506.00 MW | 18,359.00 MW |
| 4 | **2026-01-21** | **3,677.12 MW** | 3,775.48 MW | 23.40% | 15,712.88 MW | 19,390.00 MW |
| 5 | **2026-01-27** | **3,418.62 MW** | 3,505.45 MW | 20.76% | 16,469.00 MW | 19,887.62 MW |

### Key Incident: 28 January 2026
Day **2026-01-28** represents the single largest forecast failure of the month:
- **WAPE:** 91.79%
- **MAE / MBE:** +5,328.96 MW
- **Actual Mean Outturn:** 5,805.62 MW
- **Forecast Mean:** 11,134.58 MW
- Over the 24 hours of 28 January, actual wind was less than half of the predicted generation throughout the entire day, reaching a peak over-prediction of +4,383 MW.

---

## 5. Dataset Resolution & Publication Cadence Observations

1. **Resolution Mismatch:**
   - `FUELHH` records 1,488 half-hourly settlement periods across January (48 periods/day).
   - `WINDFOR` publishes exclusively on the hour (:00 timestamps), generating 744 hourly forecasts.
   - The evaluation set is strictly the **744 matched hourly delivery periods**.
   - The 744 half-hour actuals at `:30` have no forecast by design and are left unforecasted without forward-filling or zero-filling.
2. **Publication Cadence on 15 January 2026:**
   - A run was published at 12:25Z on 15 Jan instead of the usual 11:30Z; the 12:00 cutoff therefore uses the 09:30Z run for 16 Jan.
   - This produces a maximum lead time of **37.5 hours** for 16 January under the 12:00 cutoff.
3. **Retrospective Initialization Rows (Negative Lead Times):**
   - Out of 19,856 raw forecast records, **4,081 rows (20.55%)** have negative lead times ($t_{\text{start}} < t_{\text{publish}}$).
   - These are tagged and excluded from active forward forecasting evaluation.

---

*Generated automatically by `scripts/generate_findings.py`. All numbers computed from source datasets.*
