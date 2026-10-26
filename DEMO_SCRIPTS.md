# WindScope — Phase 6: Video Demonstration Scripts & Recording Guide

This document contains two complete, production-ready demo video scripts and a technical recording checklist for **WindScope (UK Wind Forecast Intelligence Platform)**.

---

# Part 1: Client Pitch Script (Utility Day-Ahead Trading Desk)

- **Target Audience:** Day-ahead power buying team at a UK energy utility.
- **Goal:** Present the pilot, walk through the dashboard, demonstrate forecast performance at decision time, and explain how to account for quantified error.
- **Estimated Duration:** ~4 minutes (~550 spoken words).
- **Core Principle:** Only claims supported by the data or repo. No price, cash-out, or demand claims.

---

### [00:00 - 00:50] Introduction & Scope Definition
- **On Screen:** Full-screen browser displaying [WindScope Dashboard (https://wild-flow.vercel.app)](https://wild-flow.vercel.app). Smooth cursor hovering over the title, navigation tabs, and top metric cards.
- **Spoken Audio:**  
  "Good morning. Today I am presenting the pilot of **WindScope**, an intelligence platform built to evaluate national wind generation forecast performance for Great Britain.

  Our evaluation is grounded strictly in authentic Elexon BMRS data for January 2026, comparing half-hourly actual outturn against published wind forecast vintages.

  Before we look at the numbers, two boundaries are important. First, this platform evaluates intermittent generation supply only; no customer demand data was used in this study. 

  Second, the decision cutoff we model—09:00 London time on Day D minus 1—is an operational workflow assumption for wholesale trading analysis, not a statutory market gate closure. The platform allows this cutoff to be configured based on your desk's specific schedule."

---

### [00:50 - 01:50] Decision-Time Forecast Selection
- **On Screen:** Zoom into the **D-1 Cutoff dropdown** showing `09:00 London (Default Cutoff)`. Open the dropdown to show `12:00 London`, then return to `09:00`. Scroll down to view the main time series chart.
- **Spoken Audio:**  
  "When evaluating forecast performance, looking at forecasts published after your team makes commitments introduces look-ahead bias. 

  WindScope enforces strict anti-lookahead vintage selection. For any delivery day D, it isolates the latest forecast published on or before the 09:00 cutoff on Day D minus 1. For January 2026, that corresponds to the 07:30 UTC publication run. 

  This means our selected forecasts have lead times ranging from 16.5 hours to 39.5 hours, with an average lead time of 28.0 hours across the month. 

  Our evaluation set consists of the 744 hourly delivery periods where both actuals and forecasts exist. The 744 half-hourly periods at minute 30 have no forecast by design and are left unforecasted without synthetic filling."

---

### [01:50 - 02:50] Accuracy Metrics & Systematic Bias
- **On Screen:** Hover over the KPI cards: **MAE (2,022.47 MW)**, **RMSE (2,497.41 MW)**, **WAPE (17.92%)**, and **MBE (+1,745.94 MW)**. Switch to the **Accuracy & Bias** tab.
- **Spoken Audio:**  
  "Across January's 744 evaluated hours, the Mean Absolute Error was 2,022.47 MW, and the Weighted Absolute Percentage Error was 17.92%. 

  The most notable pattern in the data is a persistent positive bias. The Mean Bias Error is positive 1,745.94 MW. In fact, forecasts exceeded actual outturn in 84.68% of evaluated periods—that is 630 out of 744 hours. 

  Total forecast energy reached approximately 9.70 million MWh compared to 8.40 million MWh of actual outturn, representing a difference of 1.30 million MWh across hourly samples. 

  Forecasts exceeded actuals by roughly 1,415 to 1,900 MW in every lead-time bucket; the cause cannot be determined from these two datasets."

---

### [02:50 - 03:45] Extreme Variance: 28 January 2026
- **On Screen:** Set date picker to `2026-01-28` to `2026-01-28`. Hover over the time series showing actual mean (5,805.62 MW) versus forecast mean (11,134.58 MW).
- **Spoken Audio:**  
  "The platform allows you to inspect specific delivery days. January 28th exhibited the highest percentage error of the month. 

  On this day, the Weighted Absolute Percentage Error reached 91.79%. The forecast mean was 11,134.58 MW, whereas actual mean generation was only 5,805.62 MW. 

  On average across the day, the forecast over-predicted outturn by 5,328.96 MW. Actual generation remained below half of the predicted level across all twenty-four delivery hours."

---

### [03:45 - 04:30] Accounting for Quantified Error
- **On Screen:** Switch to the **Forecast Risk (Uncertainty)** tab showing P10 (-426.4 MW), P50 (+1,581.5 MW), and P90 (+4,154.4 MW). Then toggle the cutoff control to `12:00 London`.
- **Spoken Audio:**  
  "How can a buying team account for this quantified error? 

  Our empirical error distribution provides exact non-parametric quantiles: a P10 error of minus 426.4 MW, a median P50 error of positive 1,581.5 MW, and a P90 error of positive 4,154.4 MW. A trading desk could use the error quantiles to size its uncertainty, not as a recommendation.

  Furthermore, testing workflow assumptions is immediate. Shifting the assumed decision cutoff from 09:00 to 12:00 selects the 11:30 UTC run, reducing Mean Absolute Error by 138.49 MW, or 6.85%. 

  WindScope provides your team with empirical visibility into forecast uncertainty before commitments are made. Thank you."

---
---

# Part 2: Tech Lead Review Script (Engineering & Architecture Audit)

- **Target Audience:** Technical Lead, Engineering Manager, and Code Reviewers.
- **Goal:** Walk through system architecture, data pipeline, anti-lookahead selection logic, metric computations, test suites, deployment configuration, and development practices.
- **Estimated Duration:** ~4 minutes (~547 spoken words).
- **Core Principle:** Grounded strictly in repository files, real implementations, and verified test results.

---

### [00:00 - 00:50] Architecture & Repository Structure
- **On Screen:** Split screen showing the repository directory tree in [VS Code](file:///f:/WindScope) on the left and [WindScope Live](https://wild-flow.vercel.app) on the right. Highlight [`backend/app/main.py`](file:///f:/WindScope/backend/app/main.py) and [`frontend/src/App.tsx`](file:///f:/WindScope/frontend/src/App.tsx).
- **Spoken Audio:**  
  "Hello. In this technical walkthrough, I will review the architecture, data pipeline, analytical logic, and testing suite of WindScope.

  The project is a decoupled full-stack application. The backend runs on Python 3.12 using FastAPI, and the frontend is built with React 18.3.1, TypeScript, and Vite.

  Looking at the repository structure, the core application code is maintained in [`backend/`](file:///f:/WindScope/backend/). Note that [`api/backend/`](file:///f:/WindScope/api/backend/) also exists as a bundled mirror specifically to package backend dependencies for Vercel serverless deployment. The canonical source of truth for development, tests, and local builds is [`backend/`](file:///f:/WindScope/backend/).

  The API entrypoint in [`backend/app/main.py`](file:///f:/WindScope/backend/app/main.py) mounts modular routers for health, summary metrics, time series, accuracy, and uncertainty."

---

### [00:50 - 01:50] Data Pipeline & Selection Logic
- **On Screen:** Open [`scripts/process_data.py`](file:///f:/WindScope/scripts/process_data.py) and [`backend/app/analytics/selection.py`](file:///f:/WindScope/backend/app/analytics/selection.py).
- **Spoken Audio:**  
  "The data ingestion pipeline in [`scripts/process_data.py`](file:///f:/WindScope/scripts/process_data.py) processes two Elexon BMRS streams: half-hourly `FUELHH` actuals with 1,488 rows and hourly `WINDFOR` forecasts with 19,856 rows. 

  Because WINDFOR publishes only on the hour, our evaluation set is defined strictly as the 744 matched hourly delivery periods. Half-hour actuals at minute 30 remain unforecasted; we do not forward-fill or zero-fill them.

  In [`backend/app/analytics/selection.py`](file:///f:/WindScope/backend/app/analytics/selection.py), function `select_cutoff_forecasts()` enforces anti-lookahead rules. For delivery day D, it establishes a cutoff of 09:00 London on Day D minus 1. 

  It filters for forecasts where `publishTime` is less than or equal to the cutoff, selecting the record with maximum `publishTime`. Additionally, 4,081 retrospective rows with negative lead times are flagged and excluded from forward analysis."

---

### [01:50 - 02:45] Analytical Formulations & Metrics
- **On Screen:** Open [`backend/app/analytics/metrics.py`](file:///f:/WindScope/backend/app/analytics/metrics.py), scrolling through `calculate_summary_metrics()`.
- **Spoken Audio:**  
  "All statistical logic is centralized in [`backend/app/analytics/metrics.py`](file:///f:/WindScope/backend/app/analytics/metrics.py).

  We compute Mean Absolute Error, Root Mean Squared Error, and Mean Bias Error. For Weighted Absolute Percentage Error, we calculate the sum of absolute errors divided by total actual outturn. A zero-denominator guard returns `None` if actual generation is zero, preventing division-by-zero exceptions.

  The module also calculates empirical P10, P50, and P90 error quantiles across the month and by delivery hour. 

  Our energy totals are explicitly documented as approximate: the sum of hourly megawatt values multiplied by one hour over the 744 evaluated hourly samples."

---

### [02:45 - 03:40] Testing Approach
- **On Screen:** Switch to the terminal. Run `python -m pytest backend/tests -v`. Show all 27 unit tests passing. Then open [`backend/tests/test_api.py`](file:///f:/WindScope/backend/tests/test_api.py).
- **Spoken Audio:**  
  "Reliability is enforced through an automated test suite containing 27 unit tests across three test modules in [`backend/tests/`](file:///f:/WindScope/backend/tests/).

  In [`test_analytics.py`](file:///f:/WindScope/backend/tests/test_analytics.py), we validate metric edge cases including perfect accuracy, constant bias, zero-denominator protection, and selection filtering. 

  In [`test_data_processing.py`](file:///f:/WindScope/backend/tests/test_data_processing.py), we verify row counts, ensuring 31 delivery days contain 1,488 actual records and 744 matched evaluation periods.

  In [`test_api.py`](file:///f:/WindScope/backend/tests/test_api.py), endpoints are tested using Starlette's synchronous `TestClient` from `fastapi.testclient`. We verify HTTP 200 responses and validate payload schemas defined in [`backend/app/models/schemas.py`](file:///f:/WindScope/backend/app/models/schemas.py)."

---

### [03:40 - 04:30] Deployment & Development Practices
- **On Screen:** Open [`vercel.json`](file:///f:/WindScope/vercel.json) and [`api/index.py`](file:///f:/WindScope/api/index.py).
- **Spoken Audio:**  
  "Regarding infrastructure: Docker configuration is included and documented; the live deployment is on Vercel. 

  In [`vercel.json`](file:///f:/WindScope/vercel.json), we configure route rewrites, routing API calls to [`api/index.py`](file:///f:/WindScope/api/index.py). We added `tzdata` to `requirements.txt` to support `Europe/London` timezone calculations in serverless execution.

  In terms of development practices, we utilized AI-assisted engineering with Google Antigravity. The AI was used for scaffolding, drafting API route boilerplate, and generating test fixtures. 

  For verification, rather than relying on ungrounded generation, we spot-checked five timestamps against raw API rows, and all 27 automated tests were executed locally. 

  This completes our technical architecture overview."

---
---

# Technical Recording Checklist

Before hitting record, follow this checklist to guarantee a smooth recording:

### 1. Screen Layout & System Setup
- [ ] **Display Resolution:** Set screen to **1920 x 1080 (1080p)** at 100% DPI scaling (no 125% or 150% Windows scaling) so dashboard cards and charts render without clipping.
- [ ] **Browser Window:** Maximize Google Chrome or Microsoft Edge. Hide bookmarks bar (`Ctrl + Shift + B`) and extensions.
- [ ] **Editor Theme:** In VS Code, use a clean dark theme (*GitHub Dark Default* or *Dark+*) with font size set to **15px or 16px** for crystal-clear readability.
- [ ] **Notifications:** Enable Windows **Focus Assist / Do Not Disturb** to block system popups.

### 2. Browser Tabs Order (Left to Right)
1. **Tab 1 (Primary Live UI):** `https://wild-flow.vercel.app` (Preload the dashboard, set cutoff to `09:00 London`).
2. **Tab 2 (Interactive API Docs):** `https://wild-flow.vercel.app/docs` (Swagger UI preloaded).
3. **Tab 3 (GitHub Repository):** `<REPO_URL>` (Repository root showing clean tree and documentation).
4. **Tab 4 (Data Provenance / Elexon Portal):** `https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR` (Reference tab).

### 3. Preparation Before Each Recording
- **For Part 1 (Client Pitch):**
  - Reset dashboard date range to full month (`2 Jan 2026` to `1 Feb 2026`).
  - Pre-test the date filter for `2026-01-28` so you can type or select it quickly.
  - Hover smoothly over charts; avoid fast or erratic mouse jerks.
- **For Part 2 (Tech Lead Review):**
  - In VS Code terminal, pre-type `python -m pytest backend/tests -v` so you only have to press `Enter`.
  - Open the key files in VS Code tabs:
    1. [`backend/app/analytics/selection.py`](file:///f:/WindScope/backend/app/analytics/selection.py)
    2. [`backend/app/analytics/metrics.py`](file:///f:/WindScope/backend/app/analytics/metrics.py)
    3. [`backend/tests/test_api.py`](file:///f:/WindScope/backend/tests/test_api.py)
    4. [`vercel.json`](file:///f:/WindScope/vercel.json)

### 4. Critical Things to AVOID
- ❌ **Do NOT use trading outcome claims:** Do not mention cash-out prices, imbalance settlements, margins, or being "short" (as demand data was not used).
- ❌ **Do NOT state 09:00 is a statutory gate closure:** Clarify it is an *assumed operational trading cutoff* and is configurable.
- ❌ **Do NOT claim 1,488 hourly periods:** Remember that `FUELHH` is half-hourly (1,488 rows), but the evaluation set is strictly the **744 matched `:00` hourly periods**.
- ❌ **Do NOT invent numbers:** Stick strictly to **MAE 2,022.47 MW**, **RMSE 2,497.41 MW**, **WAPE 17.92%**, **MBE +1,745.94 MW**, and **28 Jan average difference of 5,328.96 MW**.
