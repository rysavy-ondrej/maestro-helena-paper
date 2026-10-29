#!/usr/bin/env python3
"""Run WAVE's connection preflight per day or over a continuous date selection.

Uses the Python environment of --wave-repo/.venv by default. Raw input is read
only. Reports go to a separate, required output directory. Exit: 0 pass, 1
refused/late records, 2 execution/input failure. Truncation alone is not failure.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="2025_LAN dataset root")
    parser.add_argument("--wave-repo", type=Path, required=True)
    parser.add_argument("--python", help="WAVE Python executable; default REPO/.venv/bin/python")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--from-date", type=dt.date.fromisoformat)
    parser.add_argument("--to-date", type=dt.date.fromisoformat)
    parser.add_argument("--scope", choices=("day", "continuous"), default="day",
                        help="day resets watermark per day; continuous checks cross-day order")
    args = parser.parse_args()
    root = args.root.resolve()
    tool = args.wave_repo.resolve() / "scripts/check_flows.py"
    python = args.python or str(args.wave_repo.resolve() / ".venv/bin/python")
    if not root.is_dir() or not tool.is_file():
        parser.error("dataset root and WAVE scripts/check_flows.py must exist")
    if args.from_date and args.to_date and args.from_date > args.to_date:
        parser.error("--from-date must not exceed --to-date")
    days = []
    for folder in sorted(root.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]")):
        try:
            date = dt.date(*map(int, folder.relative_to(root).parts))
        except ValueError:
            continue
        if ((not args.from_date or date >= args.from_date) and
                (not args.to_date or date <= args.to_date) and
                any(folder.glob("*.ndjson.gz"))):
            days.append((date.isoformat(), folder))
    if not days:
        parser.error("no daily connection directories match the selection")
    output = args.output.resolve()
    if output == root or root in output.parents:
        parser.error("--output must be outside the raw dataset directory")
    output.mkdir(parents=True, exist_ok=True)
    groups = [(label, [folder]) for label, folder in days]
    if args.scope == "continuous":
        groups = [(days[0][0] + "_to_" + days[-1][0], [p for _, p in days])]
    summary = {"dataset": str(root), "wave_repo": str(args.wave_repo.resolve()),
               "scope": args.scope, "selected_days": [d for d, _ in days],
               "runs": [], "totals": {}}
    status = 0
    for index, (label, folders) in enumerate(groups, 1):
        print(f"[{index}/{len(groups)}] {label}", file=sys.stderr, flush=True)
        command = [python, str(tool), *map(str, folders), "--json"]
        try:
            result = subprocess.run(command, capture_output=True, text=True)
        except OSError as error:
            summary["runs"].append(dict(label=label, error=str(error), exit_code=2))
            status = 2
            break
        (output / (label + ".stderr")).write_text(result.stderr)
        (output / (label + ".json")).write_text(result.stdout)
        try:
            report = json.loads(result.stdout)
        except ValueError:
            summary["runs"].append(dict(label=label, exit_code=2,
                                        error="checker produced no valid JSON; inspect stderr"))
            status = 2
            break
        row = {k: report[k] for k in ("lines", "accepted", "refused", "late", "contexts",
               "truncated_contexts", "connections_outside_the_arrays")}
        row.update(label=label, exit_code=result.returncode)
        summary["runs"].append(row)
        for key in ("lines", "accepted", "late", "contexts", "truncated_contexts",
                    "connections_outside_the_arrays"):
            summary["totals"][key] = summary["totals"].get(key, 0) + row[key]
        summary["totals"]["refused"] = summary["totals"].get("refused", 0) + sum(row["refused"].values())
        status = max(status, result.returncode if result.returncode in (0, 1) else 2)
        # Save progress after every completed day, including unsuccessful checks.
        (output / "summary.json").write_text(json.dumps(summary, indent=2))
    summary["exit_code"] = status
    (output / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
