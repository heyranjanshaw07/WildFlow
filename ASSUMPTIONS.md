# WindScope — Engineering & Domain Assumptions

This document records all methodological decisions, data modeling assumptions, and engineering judgment calls made during the design and development of WindScope.

---

## 1. Scope Definition (Decision Window vs. Delivery Window)
- **Business Rule:** Decisions are made on day $D - 1$ for electricity delivery on day $D$.
- **Temporal Scope:** The mandate is strictly limited to purchase decisions made in **January 2026** (1 January 2026 to 31 January 2026).
- **Resulting Delivery Range:** 
  - First delivery day: **2 January 2026** (decided on 1 January 2026).
  - Last delivery day: **1 February 2026** (decided on 31 January 2026).
  - 1 January 2026 delivery is excluded because its purchase decision was made in December 2025 (out of scope).
- **Total Delivery Days:** Exactly 31 days (2 January 2026 00:00 UTC to 1 February 2026 23:30 UTC).

---

## 2. Assumed Decision Cutoff (Configurable Assumption)
- **Cutoff Rule:** For delivery day $D$, the decision cutoff is assumed to be **09:00 Europe/London on day $D - 1$**.
- **Market Context:** This is an operational assumption for wholesale market workflow modelling, not a statutory market gate closure. The platform provides a single configuration parameter (`CUTOFF_HOUR`, `CUTOFF_MINUTE`, `CUTOFF_TIMEZONE`) exposed via environment variables and interactive UI controls.
- **Strict Anti-Lookahead Guarantee:** For any delivery period $t$ on day $D$, only forecast vintages with `publishTime <= Cutoff(D-1)` are eligible for selection. Forecasts published after the cutoff are strictly barred.
- **Selected Vintage Rule:** Among all eligible forecasts for period $t$, the system selects the one with the maximum `publishTime` (the freshest available forecast at decision time).

---

## 3. Dataset Resolution & The Evaluation Set
- **Data Source Reality:**
  - `FUELHH` (Actual outturn generation) is recorded at **half-hourly resolution** (48 settlement periods per day: `:00` and `:30`).
  - `WINDFOR` (Forecast generation) is published at **hourly resolution** (24 periods per day: `:00`).
- **Evaluation Set Definition:**
  - The evaluation set is defined strictly as the **744 hourly delivery periods** (`:00` timestamps) that exist across both datasets in January 2026 (31 days $\times$ 24 hours = 744).
  - In all reporting, coverage is calculated as `Matched Hourly Periods / 744 (100.0%)`.
  - The **744 half-hour actuals at `:30` have no matching forecast by design**.
- **No Synthetic Resampling / Zero-Filling:**
  - In strict compliance with domain requirements, forecasts are **NEVER** forward-filled, interpolated, or zero-filled for the `:30` periods.
  - `:30` periods remain unforecasted in the database with `hasForecast: False` and `forecast: null`.

---

## 4. WINDFOR Horizon Spans & Negative Lead Times
- **Horizon Observations:**
  - Each WINDFOR publication run contains **73 hourly rows** spanning a 72.0-hour window ($T_{\text{max}} - T_{\text{min}} = 72.0\text{ hours}$).
  - Runs are observed to anchor to 21:00 UTC target boundaries across runs.
  - Across the entire raw dataset, lead times (`startTime - publishTime`) range from **-25.5 hours to +66.5 hours**.
  - No single run has a 92-hour span: early morning runs (e.g. 02:30Z) span from -5.5h to +66.5h, while late evening runs (e.g. 22:30Z) span from -25.5h to +46.5h.
- **Negative Lead Times (`startTime < publishTime`):**
  - **Empirical Observation:** Approximately 20.5% (4,081 out of 19,856 rows) have target `startTime` earlier than `publishTime`. The cause of these retrospective rows is not documented by the Elexon BMRS API.
  - **Handling:** In processed files, negative lead-time rows are tagged with `isNegativeLeadTime: True`. For forward day-ahead procurement analysis, all periods where `startTime < publishTime` are excluded.

---

## 5. Lead-Time Horizons & Excluded Intraday Rows
- **Plain Lead Ranges:** Lead-time analysis uses plain lead-time bins (e.g. `0h - 6h`, `6h - 10h`, `10h - 14h`, `14h - 18h`, `18h - 24h`, `24h - 30h`, `30h - 36h`, `36h - 48h`, `48h - 72h`).
- **Exact Cutoff Lead-Time Ranges (startTime - publishTime):**
  - **09:00 London Cutoff:** The freshest forecast available on D-1 before 09:00 was published at 07:30 UTC. The actual lead times of selected forecasts range from **16.5 hours** (00:00 UTC delivery) to **39.5 hours** (23:00 UTC delivery), with a mean lead time of **28.0 hours**.
  - **12:00 London Cutoff:** The freshest forecast available on D-1 before 12:00 was published at 11:30 UTC (or 09:30 UTC on 15 Jan). The actual lead times range from **12.5 hours** to **37.5 hours**, with a mean lead time of **24.1 hours**.
  - *Observation on Publication Cadence for 16 Jan Delivery:* A run was published at 12:25Z on 15 Jan instead of the usual 11:30Z; the 12:00 cutoff therefore uses the 09:30Z run for 16 Jan (producing a maximum lead time of 37.5 hours).
- **Why 0h - 14h Vintages Are Excluded from Day-Ahead Selection:**
  - The **3,472 positive-lead forecast rows** in the raw stream that have lead times between `0h` and `14h` were published on $D - 1$ afternoon/evening or during day $D$ itself (intraday updates).
  - In day-ahead decision making, these 3,472 rows are excluded from the 09:00 cutoff selection to prevent look-ahead bias (they were published after the assumed decision cutoff).

---

## 6. Energy Totals & Metric Precision
- **Approximate Energy Totals:**
  - Energy figures are explicitly presented as approximate: $\sum (\text{hourly MW}) \times 1\text{h}$ over the 744 `:00` hourly samples only.
  - They are not presented as exact integrated settlement MWh because `:30` periods are excluded from the forecast evaluation set.
- **Formulations:**
  - **Mean Absolute Error (MAE):** $\frac{1}{N} \sum_{i=1}^N |f_i - a_i|$ (MW)
  - **Root Mean Squared Error (RMSE):** $\sqrt{\frac{1}{N} \sum_{i=1}^N (f_i - a_i)^2}$ (MW)
  - **Weighted Absolute Percentage Error (WAPE):** $\frac{\sum_{i=1}^N |f_i - a_i|}{\sum_{i=1}^N |a_i|} \times 100$ (%)
    - *Zero Denominator Protection:* If $\sum |a_i| = 0$, WAPE explicitly returns `None` (or `null` in JSON), avoiding `ZeroDivisionError`.
  - **Mean Bias Error (MBE):** $\frac{1}{N} \sum_{i=1}^N (f_i - a_i)$ (MW)
- **Positive Bias Observation:**
  - A systematic positive bias ($\text{MBE} \approx +1,746\text{ MW}$) is observed across all hours of the day and across all lead times.
  - A time-shift analysis (-3h to +3h) confirms this is not an hourly clock/timezone alignment artifact.
  - Potential causes (such as commercial wind curtailment, transmission losses, or differences between transmission-system-metered outturn and total installed capacity) remain unverified hypotheses that cannot be confirmed or tested with Elexon BMRS FUELHH/WINDFOR data alone.
