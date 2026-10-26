"""
download_data.py - Download UK Wind actuals (FUELHH) and forecasts (WINDFOR) from Elexon BMRS API.

Scope:
- Actuals (FUELHH, fuelType=WIND): Delivery days 2026-01-02 to 2026-02-01.
- Forecasts (WINDFOR): Vintages published from 2025-12-30 to 2026-02-02.
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"
DEFAULT_RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

def fetch_with_retry(url: str, max_retries: int = 4, backoff_factor: float = 1.5, timeout: int = 45):
    """Fetch URL with exponential backoff and retry handling."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "WindScope-Platform/1.0 (Enterprise Energy Utility)",
            "Accept": "application/json",
        }
    )
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    data = resp.read()
                    return json.loads(data.decode("utf-8"))
                raise urllib.error.HTTPError(url, resp.status, f"Unexpected status {resp.status}", resp.headers, None)
        except urllib.error.HTTPError as e:
            print(f"  [Attempt {attempt}/{max_retries}] HTTP error {e.code} for {url}: {e.reason}")
            if attempt == max_retries:
                raise
            sleep_time = backoff_factor ** attempt
            time.sleep(sleep_time)
        except Exception as e:
            print(f"  [Attempt {attempt}/{max_retries}] Network error: {e}")
            if attempt == max_retries:
                raise
            sleep_time = backoff_factor ** attempt
            time.sleep(sleep_time)

def download_fuelhh(raw_dir: Path, force: bool = False):
    """Download FUELHH actuals with fuelType=WIND."""
    target_file = raw_dir / "fuelhh_wind_raw.json"
    if target_file.exists() and not force:
        print(f"[FUELHH] Raw file already exists at {target_file}. Skipping (use --force to re-download).")
        with open(target_file, "r", encoding="utf-8") as f:
            return json.load(f)

    print("\n[FUELHH] Starting download...")
    # Fetch from 2026-01-01T23:00:00Z to 2026-02-02T04:00:00Z to cover all settlement periods for Jan 2 to Feb 1
    params = {
        "publishDateTimeFrom": "2026-01-01T23:00:00Z",
        "publishDateTimeTo": "2026-02-02T04:00:00Z",
        "fuelType": "WIND"
    }
    url = f"{BASE_URL}/FUELHH/stream?{urllib.parse.urlencode(params)}"
    print(f"  URL: {url}")
    start_t = time.time()
    records = fetch_with_retry(url)
    elapsed = time.time() - start_t
    print(f"  Retrieved {len(records)} raw FUELHH records in {elapsed:.2f}s")

    raw_dir.mkdir(parents=True, exist_ok=True)
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"  Saved raw FUELHH to {target_file}")
    return records

def download_windfor(raw_dir: Path, force: bool = False):
    """Download WINDFOR forecasts in 7-day chunks."""
    target_file = raw_dir / "windfor_raw.json"
    if target_file.exists() and not force:
        print(f"[WINDFOR] Raw file already exists at {target_file}. Skipping (use --force to re-download).")
        with open(target_file, "r", encoding="utf-8") as f:
            return json.load(f)

    print("\n[WINDFOR] Starting chunked download...")
    chunks_dir = raw_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    date_windows = [
        ("2025-12-30T00:00:00Z", "2026-01-06T00:00:00Z"),
        ("2026-01-06T00:00:00Z", "2026-01-13T00:00:00Z"),
        ("2026-01-13T00:00:00Z", "2026-01-20T00:00:00Z"),
        ("2026-01-20T00:00:00Z", "2026-01-27T00:00:00Z"),
        ("2026-01-27T00:00:00Z", "2026-02-02T00:00:00Z"),
    ]

    all_records = []
    for idx, (p_from, p_to) in enumerate(date_windows, start=1):
        chunk_file = chunks_dir / f"windfor_chunk_{idx}.json"
        if chunk_file.exists() and not force:
            print(f"  [Chunk {idx}/{len(date_windows)}] Found cached chunk {chunk_file.name}")
            with open(chunk_file, "r", encoding="utf-8") as f:
                chunk_data = json.load(f)
        else:
            params = {
                "publishDateTimeFrom": p_from,
                "publishDateTimeTo": p_to,
            }
            url = f"{BASE_URL}/WINDFOR/stream?{urllib.parse.urlencode(params)}"
            print(f"  [Chunk {idx}/{len(date_windows)}] Fetching {p_from} to {p_to}...")
            start_t = time.time()
            chunk_data = fetch_with_retry(url)
            elapsed = time.time() - start_t
            print(f"    Retrieved {len(chunk_data)} records in {elapsed:.2f}s")
            with open(chunk_file, "w", encoding="utf-8") as f:
                json.dump(chunk_data, f)
            time.sleep(0.5)  # Respectful pacing between chunks

        all_records.extend(chunk_data)

    print(f"  Total raw WINDFOR records fetched across chunks: {len(all_records)}")
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(all_records, f)
    print(f"  Saved consolidated raw WINDFOR to {target_file}")
    return all_records

def main():
    parser = argparse.ArgumentParser(description="Download raw Elexon BMRS datasets for WindScope.")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR, help="Directory to save raw JSON files")
    parser.add_argument("--force", action="store_true", help="Force re-download even if files exist")
    args = parser.parse_args()

    args.raw_dir.mkdir(parents=True, exist_ok=True)
    print(f"WindScope Data Ingestion Starting...")
    print(f"Target raw directory: {args.raw_dir}")

    fuelhh_data = download_fuelhh(args.raw_dir, force=args.force)
    windfor_data = download_windfor(args.raw_dir, force=args.force)

    print("\nIngestion Summary:")
    print(f"  FUELHH (WIND) raw row count: {len(fuelhh_data)}")
    print(f"  WINDFOR raw row count:       {len(windfor_data)}")
    print("Done.")

if __name__ == "__main__":
    main()
