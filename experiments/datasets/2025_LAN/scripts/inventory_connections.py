#!/usr/bin/env python3
"""Inventory the LAN archive without decompressing it. No third-party dependencies."""
import argparse
import collections
import datetime as dt
import json
from pathlib import Path
import re

NAME = re.compile(r"capture_(\d{8})T(\d{4})\.ndjson\.gz$")


def inventory(root):
    months = collections.defaultdict(lambda: {"files": 0, "bytes": 0})
    dates = set()
    stamps = []
    misplaced = []
    unexpected = []
    zero_bytes = []
    for path in sorted(root.rglob("*.ndjson.gz")):
        relative = str(path.relative_to(root))
        match = NAME.fullmatch(path.name)
        if not match:
            unexpected.append(relative)
            continue
        try:
            stamp = dt.datetime.strptime("".join(match.groups()), "%Y%m%d%H%M")
        except ValueError:
            unexpected.append(relative)
            continue
        expected = Path(stamp.strftime("%Y/%m/%d")) / path.name
        if path.relative_to(root) != expected:
            misplaced.append(relative)
        size = path.stat().st_size
        if size == 0:
            zero_bytes.append(relative)
        dates.add(stamp.date())
        stamps.append(stamp)
        row = months[stamp.strftime("%Y-%m")]
        row["files"] += 1
        row["bytes"] += size
    missing = []
    if dates:
        day = min(dates)
        while day <= max(dates):
            if day not in dates:
                missing.append(day.isoformat())
            day += dt.timedelta(days=1)
    return dict(root=str(root), files=sum(v["files"] for v in months.values()),
                compressed_bytes=sum(v["bytes"] for v in months.values()),
                days=len(dates), months=dict(sorted(months.items())),
                first_filename_time=min(stamps).isoformat() if stamps else None,
                last_filename_time=max(stamps).isoformat() if stamps else None,
                missing_days=missing, misplaced_files=misplaced,
                unexpected_filenames=unexpected, zero_byte_files=zero_bytes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error("root must be an existing dataset directory")
    result = inventory(args.root.resolve())
    print(json.dumps(result, indent=2))
    return int(not result["files"] or bool(result["misplaced_files"] or
               result["unexpected_filenames"] or result["zero_byte_files"]))


if __name__ == "__main__":
    raise SystemExit(main())
