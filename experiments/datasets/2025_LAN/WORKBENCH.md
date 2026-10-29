# Daily processing workbench

Installed entry point on `supermicro-devbox`:
`/home/rysavy/lan-dataset-tools/dp_workbench.py`.
It has five commands: **init, inspect, validate, run, status**. Each command has
`--help`. Options follow the command, for example `dp_workbench.py run --day ...`.

## init

```bash
cd /home/rysavy/lan-dataset-tools
./dp_workbench.py init --smoke-test
```

Clones `maestro-helena-wave` under the tools directory, installs its locked
dependencies into `.venv` using uv and Python 3.12, downloads RisingWave from its
official release and verifies the binary against the checkout's SHA-256 pin.
It copies the Python 3.12 shared library from the uv-managed interpreter and
records its actual hash and whether it matches WAVE's library pin. Its engine
version probe must pass. This avoids the upstream installer's `/root` copy
paths and unnecessary Java/Kafka artifacts. No broker or system daemon is
installed or started. Kafka's Python package is still part of WAVE's lockfile.

`--smoke-test` runs the committed synthetic demo with its six-context assertion.
An existing checkout stays unchanged; `init --update --ref main` explicitly
fetches main and refuses tracked modifications. Other options:

- `--repo PATH`: use a different local checkout.
- `--ref BRANCH_OR_TAG`: initial clone branch/tag, default main.
- `--risingwave-binary PATH`: supply a binary instead of downloading it; the
  checkout's checksum is still mandatory.
- `--libpython PATH`: override the Python 3.12 shared library.
- `--runtime-mode auto|direct|userns|sudo`: auto tries direct isolation, then
  an unprivileged outer user namespace. It never silently selects sudo.

System prerequisites are Linux x86_64, git, unshare (util-linux), ip (iproute2)
and hostname. The script reports missing system tools; an administrator must
install them. uv is reused when available, otherwise installed in a local
bootstrap venv through pip. A failed partial download is not used as an archive.
`--runtime-mode sudo` uses `sudo -n`; authenticate/authorize sudo separately.
No system namespace policy or permissions are modified.

## inspect

```bash
./dp_workbench.py inspect
./dp_workbench.py inspect --from-date 2025-09-01 --to-date 2025-09-07
```

Runs the file-metadata inventory, including missing days and zero-byte files.
It does not decompress or validate records. The inventory is corpus-wide;
date arguments additionally list selected populated days. The known 60 empty
files cause exit 1. The archive remains untouched.

## validate

```bash
./dp_workbench.py validate --day 2025-09-01
./dp_workbench.py validate --from-date 2025-08-01 --to-date 2025-08-31 --keep-going
```

Reads every connection with the selected checkout's `scripts/check_flows.py`.
All files within a day are passed in filename order as one stream. Each day
has a fresh watermark. Schema refusals and late records fail the check;
context-array truncation is reported without failing it. The fresh checkout
uses upstream's strict schema, not the separately modified experimental checker.

No date arguments selects all available days for validation. Missing calendar
days are not synthesized. Zero-byte files fail before WAVE starts; use
`--allow-empty-files` only to acknowledge gaps and continue with the other files.
The empty paths are recorded even when acknowledged. A day containing only
zero-byte files always fails. `--keep-going` continues after a failed day;
otherwise processing stops at the first failure.

## run

```bash
./dp_workbench.py run --day 2025-09-01 \
  --threatfox /path/to/threatfox --netify /path/to/netify \
  --public-suffix-list /path/to/public_suffix_list.dat \
  --evaluated-at 2025-09-02T00:00:00Z --timeout 1800

# Validate the input and run full WAVE environment preflight, without an engine:
./dp_workbench.py run --day 2025-09-01 --check-only

# Independent daily jobs for a selected interval:
./dp_workbench.py run --from-date 2025-09-01 --to-date 2025-09-07 \
  --threatfox /path/to/threatfox --netify /path/to/netify --keep-going
```

Requires an explicit day/date boundary or `--all-days`. Each selected day first
passes validation, then invokes `bin/wave-offline` once with its whole directory.
WAVE creates and tears down a private engine **per day**. Do not invoke it
separately per ten-minute file: EOF advances event time and would make later
files late if they shared that engine. Daily processing also closes the final
window independently; it is not a continuous replay across midnight.

Optional parameters include `--tenant` (default lan), `--sensor` (office-lan),
`--expect N` (override expected contexts per day; by default the validator's
prediction is passed to WAVE), `--timeout SECONDS` (WAVE export timeout,
default 180), `--runtime-mode`, `--allow-empty-files` and `--keep-going`.
`--evaluated-at` is passed directly to WAVE; it is an explicit enrichment
evaluation clock, not a rewrite of capture timestamps. Feed arguments are
optional; without them, contexts have no claims from those feeds. Feeds are not
downloaded by this workbench. Supply the intended source directories.

`run --check-only` still scans records and checks the full WAVE environment; it
does not certify the resulting engine computation or export. Large daily inputs
can require much more engine state than their compressed size suggests. Start
with a day, inspect logs and disk usage, then scale the date selection.

## status and outputs

```bash
./dp_workbench.py status --limit 10
```

Common options on every command: `--dataset PATH`, `--repo PATH`,
`--state-dir PATH`. State and repository paths must be outside the raw dataset.
Defaults are the deployed LAN dataset, `./maestro-helena-wave` beside the script,
and `.workbench` beside the script. They do not depend on the caller's cwd.

Each operation gets a unique `.workbench/operations/<UTC-time>-<command>-<id>/`
directory. Status includes the repository commit and checker checksum for
validate/run. Each day keeps:

- `validation.json` and `validation.stderr`.
- `wave-summary.json` and `wave.stderr` when WAVE runs.
- `contexts/` and `quarantine.jsonl` from the processor.
- A durable operation `status.json`, updated between days and at completion.

A workspace lock prevents concurrent mutation by two workbench commands.
`status` reads recorded evidence without taking that lock. It is not an engine
health monitor: after a forced kill, a record can remain `running`; inspect its
PID and WAVE ownership manifest before deciding whether it is still alive.
Use the same `--state-dir` with status that was used for the operation.
Workbench outputs are retained until the operator removes them; they are outside
WAVE's internal run-directory retention. No automatic resume or overwrite occurs.
Ctrl-C waits for the foreground child to finish its teardown.

Exit codes: 0 success, 1 data-validation/processor failure, 2 setup or execution
error, 130 interrupted. A multi-day operation stops at the first failed day unless
`--keep-going` is specified; the overall exit remains nonzero when any day fails.
