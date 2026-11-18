#!/usr/bin/env python3
"""Push blood pressure from omramin's SQLite store to intervals.icu wellness.

intervals.icu does not get blood pressure from Garmin Connect, so this sends it
directly: for each day, the last reading of that day (in the reading's own
timezone) becomes the day's systolic/diastolic. Days whose values already match
are left alone. Standard library only.

    ./bp2intervals.py --db omron.db3              # last 7 days
    ./bp2intervals.py --db omron.db3 --dry-run    # show what would change
    ./bp2intervals.py --db omron.db3 --days 365 --fill-only   # backfill empty days

The API key comes from $INTERVALS_API_KEY or --key-file.
"""

import argparse
import base64
import json
import os
import pathlib
import re
import sqlite3
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

API = "https://intervals.icu/api/v1/athlete/0/wellness"


def local_time(ts_ms: int, tz: str) -> datetime:
    # storage.py keeps str(pytz tz): "pytz.FixedOffset(600)", or "UTC" for zero offset
    m = re.search(r"FixedOffset\((-?\d+)\)", tz)
    offset = int(m.group(1)) if m else 0
    return datetime.fromtimestamp(ts_ms / 1000, timezone(timedelta(minutes=offset)))


def daily_bp(db_path: str, days: int) -> dict:
    since = datetime.now(timezone.utc) - timedelta(days=days + 1)
    rows = sqlite3.connect(db_path).execute(
        "SELECT timestamp_utc, systolic, diastolic, timezone FROM bp_measurements"
        " WHERE timestamp_utc >= ? ORDER BY timestamp_utc",
        (int(since.timestamp() * 1000),),
    )
    out = {}
    for ts, systolic, diastolic, tz in rows:
        out[local_time(ts, tz).date().isoformat()] = (systolic, diastolic)  # later readings win
    return out


def call(method: str, url: str, key: str, body=None):
    auth = base64.b64encode(f"API_KEY:{key}".encode()).decode()
    req = urllib.request.Request(
        url,
        method=method,
        data=None if body is None else json.dumps(body).encode(),
        # intervals.icu answers 403 to urllib's default "Python-urllib/x.y" User-Agent
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json", "User-Agent": "bp2intervals"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", default="omron.db3", help="omramin SQLite file (default: %(default)s)")
    ap.add_argument("--days", type=int, default=7, help="days back to push (default: %(default)s)")
    ap.add_argument("--key-file", default="~/.config/intervals/api_key")
    ap.add_argument("--fill-only", action="store_true", help="only write days with no BP in intervals")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    readings = daily_bp(args.db, args.days)
    if not readings:
        print(f"intervals BP: no readings in the last {args.days} days")
        return 0

    key = os.environ.get("INTERVALS_API_KEY") or pathlib.Path(args.key_file).expanduser().read_text().strip()
    existing = {
        r["id"]: (r.get("systolic"), r.get("diastolic"))
        for r in call("GET", f"{API}?oldest={min(readings)}&newest={max(readings)}", key)
    }

    pushed, same = [], 0
    for day, bp in sorted(readings.items()):
        current = existing.get(day, (None, None))
        if current == bp or (args.fill_only and current != (None, None)):
            same += 1
            continue
        if not args.dry_run:
            call("PUT", f"{API}/{day}", key, {"systolic": bp[0], "diastolic": bp[1]})
        pushed.append(f"{day} {bp[0]}/{bp[1]}")

    verb = "would push" if args.dry_run else "pushed"
    print(f"intervals BP: {verb} {len(pushed)} day(s){': ' + ', '.join(pushed) if pushed else ''}; {same} unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
