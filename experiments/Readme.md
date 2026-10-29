# Experiments

This directory contains dataset preparation tools, validation evidence and protocols for experiments on agentic triage and analysis of network host contexts.
Raw captures, connection archives, enrichment feeds and generated contexts remain on the processing host; the paper repository contains tools and provenance rather than copies of operational traffic.

## Artifact layout

```text
experiments/
  Readme.md
  datasets/2025_LAN/
    dp_workbench.py
    WORKBENCH.md
    Readme.md
    scripts/inventory_connections.py
    scripts/check_connections.py
    inventory.json
    validation-september-01.json
    workbench-verification.json
  reports/wave-flow-check/
    ... original validation reports, checker patch and ISCX timestamp analysis
```

The files were moved here from the local `student-imeri` workspace.
Absolute paths embedded in generated evidence describe the original execution locations and are intentionally preserved.
The deployed tools remain at `/home/rysavy/lan-dataset-tools` on `supermicro-devbox`.

## Available datasets

All three collections are under `/mnt/data/2026_MAESTRO/Datasets` on `supermicro-devbox`.
This CIFS mount is read-only; create reports and derived inputs under the user's home directory.
Inventory and verification below were collected on 29 October 2026.

| Directory | What it represents | Extent | Experimental role and limitations |
| --- | --- | --- | --- |
| `2025_LAN` | Packet-derived bidirectional connections from an operational office LAN | 19,802 gzip NDJSON files; 139 populated days, 6 May–23 September 2025; 2,712,412,661 compressed bytes | Host behaviour and operational context analysis; no established benign/malicious ground truth |
| `2026_PUB_FLOW_MTA-Exercises` | Connections derived from ten Malware-Traffic-Analysis.net exercises, including background traffic | 4,306 records in ten JSONL files, exercise dates July 2024–September 2026 | Small infection investigations; no flow labels in the JSONL; scenario/answer material must be curated separately |
| `2026_PUB_FLOW_ISCX-Botnet` | Connections derived from the ISCX Botnet 2014 overlaid captures | 445,915 records; testing 235,023 and training 210,892, across 32 JSONL shards | Scale and artifact-robustness experiments; endpoint attribution is not a malicious-flow label; timestamps require part-aware replay |

The records provide connection timestamps, durations, endpoints, directional byte/packet counters and optional DNS, TLS, HTTP or HTTP/2 observations.
They contain packet/header metadata rather than packet payload bytes.
Identifiers, internal addresses and application metadata can nevertheless reveal operational information.
Protocol coverage varies by corpus; optional protocol fields must not be interpreted as universally available.

Read the remote datasets' `AGENTS.md` and README files before deriving features or labels.
The LAN-specific [README](datasets/2025_LAN/Readme.md) and [workbench guide](datasets/2025_LAN/WORKBENCH.md) describe the archive layout and command parameters in detail.

## Prepare the experimental inputs

### 1. Select and record the scope

Record the dataset, selected days/exercises/ISCX parts, research question, intended ground truth, train/test split and evaluation procedure before processing.
Do not claim office traffic is benign merely because it came from a stable office network.
Keep public-dataset answer keys and ISCX endpoint attribution outside agent-visible evidence when measuring independent triage performance.
Use host/capture-aware splits where appropriate; randomly splitting connections can put the same hosts and neighbouring activity into both training and evaluation.

Preserve source archives unchanged.
Use the dataset-relative filename and line number as a raw-record reference; a producer's `id` is not globally unique.
For ISCX, preserve `cid` and `part` in a provenance sidecar if they are removed from derived WAVE input.

### 2. Inventory the LAN archive

The deployed layout is:

```text
2025_LAN/2025/<MM>/<DD>/capture_<YYYYMMDD>T<HHMM>.ndjson.gz
```

The driver discovers populated day directories and passes all matching files within each day in filename order as one stream.
Boundary days are partial and filenames need not be aligned to exact ten-minute boundaries.
The measured archive is missing 9–10 July and contains 60 zero-byte files, listed in [inventory.json](datasets/2025_LAN/inventory.json).
A zero-byte file may represent an incomplete export or placeholder; its cause has not been established.
Do not replace missing data with fabricated empty observations.

Run the metadata inventory separately from connection validation:

```bash
ssh supermicro-devbox
cd /home/rysavy/lan-dataset-tools
./dp_workbench.py inspect
```

`inspect` reports the entire archive and exits nonzero for empty or malformed archive entries.
It does not decompress every file or establish record validity.

### 3. Validate the actual replay selection

```bash
./dp_workbench.py validate --day 2025-09-01
./dp_workbench.py validate \
  --from-date 2025-08-01 --to-date 2025-08-31 --keep-going
```

Each day receives an independent watermark, matching the daily `run` command.
Schema failures and late records fail validation; declared context-array truncation alone does not.
Zero-byte files are blocked by default.
Use `--allow-empty-files` only to acknowledge the collection gaps explicitly; their paths remain in the report, and an entirely empty day always fails.

For a genuinely continuous multi-day replay, check cross-day ordering separately with the companion driver:

```bash
python3 scripts/check_connections.py \
  /mnt/data/2026_MAESTRO/Datasets/2025_LAN \
  --wave-repo /home/rysavy/lan-dataset-tools/maestro-helena-wave \
  --from-date 2025-09-01 --to-date 2025-09-07 \
  --scope continuous --output /home/rysavy/lan-check-continuous-week
```

The workbench itself deliberately runs each day independently and closes its final window at that day's end.
It does not establish continuous host contexts across midnight.

### 4. Handle public datasets according to their capture scope

MTA exercises are independently processable JSONL files.
All ten passed the original preflight, with 169 predicted contexts in total across separate runs and no late records or predicted truncation.
Their scenarios and available answer pages reside in the source Datalake; the 13 June 2025 exercise has no upstream answer page according to the dataset documentation.
Maintain a reviewed label/evidence mapping separately rather than inferring labels from filenames.

ISCX requires a separate preparation stage before strict WAVE ingestion.
Its `cid`, `part` and `botnet` annotations are additional fields rejected by the strict schema in the checked WAVE revision.
Project them into a sidecar, preserving the mapping to the original record, and validate the derived records again.
The checker-only [patch](reports/wave-flow-check/ignore-additional-fields.patch) tolerates extensions but does not change `wave-offline` ingestion.

Every ISCX part was already nondecreasing by connection `ts`.
The measured late-record loss came from concatenating overlapping, nonchronological parts under one watermark: 115,171 late testing records and 151,620 late training records.
Prepare a replay per part, or explicitly justify a chronological merge; do not reset by shard filename because shards cross part boundaries.
Part-aware replay does not repair epoch-zero timestamps, backward packet timestamps or invalid durations.
See the [timestamp analysis](reports/wave-flow-check/iscx-timestamp-analysis.md) before defining filters or temporal features.
The LAN workbench's date-directory discovery does not directly support the MTA or ISCX layouts; use WAVE directly on their prepared file selections.

## Prepare the remote processor

The processor is [maestro-helena-wave](https://github.com/rysavy-ondrej/maestro-helena-wave).
The verified checkout was commit `926fa20278ce5aab3d0a5ab953517bff0efa371b`, with RisingWave 3.0.3 and Python 3.12.14.
A future `init` cloning main can obtain a different revision; always record the actual commit and checker checksum written to the operation status.

The tools are already installed on `supermicro-devbox`.
To deploy this repository's copies to another compatible host, run from the paper repository root:

```bash
ssh supermicro-devbox 'mkdir -p /home/rysavy/lan-dataset-tools/scripts'
scp experiments/datasets/2025_LAN/dp_workbench.py \
    experiments/datasets/2025_LAN/WORKBENCH.md \
    supermicro-devbox:/home/rysavy/lan-dataset-tools/
scp experiments/datasets/2025_LAN/scripts/*.py \
    supermicro-devbox:/home/rysavy/lan-dataset-tools/scripts/
ssh supermicro-devbox \
  'chmod +x /home/rysavy/lan-dataset-tools/dp_workbench.py'
```

Then initialize remotely:

```bash
ssh supermicro-devbox
cd /home/rysavy/lan-dataset-tools
./dp_workbench.py init --smoke-test
```

`init` creates the WAVE checkout and its locked virtual environment, installs a checksum-verified RisingWave binary and copies a compatible Python 3.12 shared library locally.
It records the shared library's actual hash and whether it matches the upstream artifact pin; the installed uv-managed library differs from that pin and passed the demo.
No Kafka broker or system service is installed.
System prerequisites are Linux x86_64, git, unshare, ip and hostname; missing system packages require administrator installation.
The host was verified to support `unshare --user --map-root-user`, allowing WAVE's nested isolation without sudo.
`--runtime-mode auto` tests direct isolation and then user namespaces; sudo is used only when explicitly selected.

Initialization is repeatable and does not update an existing checkout automatically.
Use `init --update --ref main` for an intentional update, then revalidate inputs and refresh experimental evidence.
For a fixed revision, provision and retain an appropriate local checkout and supply `--repo PATH`; record its exact commit.

## Run remote daily context processing

Start with one day and explicitly supplied enrichment inputs:

```bash
cd /home/rysavy/lan-dataset-tools
./dp_workbench.py run --day 2025-09-01 \
  --threatfox /path/to/threatfox \
  --netify /path/to/netify \
  --public-suffix-list /path/to/public_suffix_list.dat \
  --tenant lan --sensor office-lan \
  --evaluated-at 2025-09-02T00:00:00Z \
  --timeout 1800
```

Replace the feed paths with actual source directories; feeds are not downloaded by the workbench.
The example evaluation clock is illustrative and must be chosen for the experiment's historical-enrichment policy.
A current indicator match does not establish what was known when the traffic was captured.
Omitting feed parameters produces contexts without claims from those sources.

`run` validates the selected day, passes the predicted context count to WAVE as `--expect`, and invokes `bin/wave-offline` once for that whole day.
WAVE owns engine startup, SQL setup, enrichment upload, ingestion, context export and teardown.
Never launch one engine invocation per ten-minute file when the intent is one daily stream.

Other useful invocations are:

```bash
# Full environment preflight without starting an engine:
./dp_workbench.py run --day 2025-09-01 --check-only

# Separate daily runs over an interval:
./dp_workbench.py run \
  --from-date 2025-09-01 --to-date 2025-09-07 \
  --threatfox /path/to/threatfox --netify /path/to/netify \
  --timeout 1800 --keep-going

# Installation and recorded operation states:
./dp_workbench.py status --limit 10
```

Each command also accepts `--dataset`, `--repo` and `--state-dir` after its command name.
`run` requires a date selection or explicit `--all-days`.
Use the same state directory when requesting status for an operation.
The script prevents concurrent workbench mutations within one state directory; do not bypass that isolation by running simultaneous jobs against the same checkout without evaluating resource and lifecycle interactions.
For long jobs, run inside an existing terminal multiplexer on the remote host to survive SSH disconnection.

## Outputs, provenance and current evidence

Outputs are stored under `/home/rysavy/lan-dataset-tools/.workbench/operations/<operation-id>/`.
Each day's directory contains validation JSON/stderr, WAVE summary/stderr, `contexts/` and quarantine records when applicable.
Operation `status.json` records dates, exit codes, repository commit, checker checksum and the invoked processing command.
Status is recorded evidence rather than a live engine monitor; a forcibly terminated operation can retain a stale running status.
Workbench results are retained until manually removed and are separate from WAVE's internal runtime retention.

The real 1 September LAN subset passed strict WAVE validation: 177,494 records, no late records, 10,991 predicted contexts and 35 predicted truncated contexts.
The full multi-month collection has been inventoried, not fully validated or processed.
The synthetic smoke test actually exported six contexts with zero rejected/withheld contexts; its ownership manifest confirmed all owned processes stopped and state was removed.
These are tool-verification results, not downstream triage-performance results.
See [verification evidence](datasets/2025_LAN/workbench-verification.json) and [LAN validation](reports/wave-flow-check/2025_LAN-results.json).

For each published experiment, retain the research question, input manifest and hashes, labels and their provenance, split, configurations, feed snapshots, evaluation clock, WAVE/model/tool versions, prompts, random seeds where applicable, execution date, raw outputs and analysis commands.
Record missing or rejected records, temporal loss, truncation and withheld contexts rather than silently excluding them.
Copy only reviewed, appropriately redacted summaries into the paper repository; raw contexts and reports may contain sensitive addresses and identifiers.
Existing generated reports were moved intact and require review before publication.
