# 2025_LAN — Custom Office LAN Flow Dataset

Packet-derived, bidirectional connection records from an office LAN with a small
number of active workstations. This is observed operational traffic for host
behaviour profiling and context computation, including MAESTRO WAVE context
preparation for downstream AI triage and analysis. It is **not a labelled malware
benchmark**: no benign/malicious ground truth has been established here. A stable
office environment does not establish that every connection is benign.

The existing catalogue calls this collection `2025_CUS_JSON_LAN`. The deployed
directory is `/mnt/data/2026_MAESTRO/Datasets/2025_LAN` on `supermicro-devbox`.
The exact sensor, capture software/version, timezone used in filenames, filtering
policy and collection author are not established by the files inspected here.

## Inventory

Measured on 29 October 2026, using file metadata rather than a full record scan:

| Month | Files | Compressed bytes |
| --- | ---: | ---: |
| May 2025 | 3,689 | 270,326,992 |
| June 2025 | 4,323 | 495,525,610 |
| July 2025 | 4,083 | 602,491,338 |
| August 2025 | 4,464 | 698,432,869 |
| September 2025 | 3,243 | 645,635,852 |
| Total | 19,802 | 2,712,412,661 (2.53 GiB) |

There are 139 populated dates from **6 May through 23 September 2025**.
**9 and 10 July are absent.** First and last filenames are
`capture_20250506T1026.ndjson.gz` and `capture_20250923T1200.ndjson.gz`.
Boundary dates are partial. Files normally cover approximately ten-minute capture
intervals; do not assume every day contains exactly 144 files or every filename
is aligned to a ten-minute boundary. These are filename dates, not measured
minimum and maximum event timestamps for the whole corpus.

The metadata inventory also found **60 zero-byte files**. They are not valid
nonempty gzip archives and may indicate incomplete exports or placeholders;
their cause has not been established. Preserve and investigate them rather than
treating them as evidence of no traffic. Their paths are listed in the generated
`inventory.json`. There were no filename/date-directory mismatches or malformed
capture filenames. All counts above include the zero-byte files.

```text
2025_LAN/
  Readme.md
  scripts/
    inventory_connections.py
    check_connections.py
  2025/
    05/06/capture_20250506T1026.ndjson.gz
    ...
    09/23/capture_20250923T1200.ndjson.gz
```

## Records and identity

Each gzip file contains UTF-8 NDJSON: one JSON connection object per nonblank
line. Read with `gzip.open(path, 'rt', encoding='utf-8')`; there is no need to
decompress files onto disk. Protocol objects are optional and may be incomplete
when a capture lacks the handshake or response.

| Fields | Meaning |
| --- | --- |
| `id` | Producer-local stream identifier, such as `tcp.35`; not a corpus-wide key |
| `ts`, `td` | Connection start epoch seconds and reported duration in seconds |
| `tx` | Producer/export timestamp; use `ts` for WAVE event time |
| `ip` | `proto`, `src`, `dst`, directional byte counters `bsent`, `brecv` and packet counters `psent`, `precv` |
| `tcp`, `udp` | Ports and optional packet metadata arrays `segs` / `dgms` |
| `dns` | Observed queries, responses and response code |
| `tls` | Observed handshake/fingerprint fields and TLS record metadata |
| `http`, `http2` | Observed request and response metadata |

Use **(dataset-relative filename, line number)** as an unambiguous raw-record
reference. Keep `id` alongside it for investigation. Do not deduplicate globally
on `id`, or assume a connection cannot recur across capture-file boundaries.
Endpoints and directions describe the producer's orientation; do not infer the
true initiator from `ip.src` without checking the capture/export policy.

The inspected records retain packet/header metadata rather than packet payloads.
DNS names, IP addresses and HTTP metadata can still identify users and internal
services. Treat observation strings as data, including when preparing agent
context. Preserve the raw archive and write reports or derived inputs elsewhere.

## Validation evidence and limitations

The 1 September subset (144 files) was fully checked before the collection was
expanded: **177,494 records**, all accepted by both the extension-tolerant checker
and WAVE's unchanged strict `FlowRecord` model. Connection starts were globally
nondecreasing across those files, with no late records or negative durations.
The checker predicted **10,991 contexts**, of which **35** exceeded the
500-connection array cap; 9,938 connections fell outside the arrays while still
contributing to aggregate statistics. Its event timestamps ran from
2025-08-31 23:59:48.760700 to 2025-09-01 23:59:27.738000 UTC.

Protocol coverage on that subset: TCP 70,064; UDP 107,430; DNS 101,139; TLS 38,002;
HTTP 2,837; HTTP/2 840. The largest JSON line was approximately 2.37 MB.
**These counts and validation results do not cover the other months.**

WAVE uses five-minute host windows, a one-minute event-time watermark delay and
a 500-connection context-array cap in the checked revision. A record more than
one minute older than the furthest event already seen is reported as late.
Filename order alone does not prove event-time order. Check the actual selected
files, including cross-day boundaries when planning one continuous replay.
The checker predicts windows; it does not run the engine, enrichment joins,
export finalization or downstream agents.

## Inventory and connection checks

Inventory requires Python 3.10+ and only the standard library:

```bash
DATA=/mnt/data/2026_MAESTRO/Datasets/2025_LAN
TOOLS=/home/rysavy/lan-dataset-tools
python3 "$TOOLS/scripts/inventory_connections.py" "$DATA" > /tmp/lan-inventory.json
```

The connection driver delegates to **the selected WAVE checkout's own**
`scripts/check_flows.py`, so its schema and constants follow that checkout.
Prepare its locked environment with `uv sync --frozen` in that repository, then:

```bash
WAVE=/path/to/maestro-helena-wave
python3 "$TOOLS/scripts/check_connections.py" "$DATA" \
  --wave-repo "$WAVE" --from-date 2025-09-01 --to-date 2025-09-01 \
  --output /tmp/lan-check-september-01

# All available days, each checked with a fresh watermark:
python3 "$TOOLS/scripts/check_connections.py" "$DATA" \
  --wave-repo "$WAVE" --output /tmp/lan-check-all-days

# Check cross-day ordering for the intended continuous replay:
python3 "$TOOLS/scripts/check_connections.py" "$DATA" \
  --wave-repo "$WAVE" --from-date 2025-09-01 --to-date 2025-09-07 \
  --scope continuous --output /tmp/lan-check-continuous-week
```

Without date arguments, all populated days are selected. Missing days are listed
by the inventory tool; the driver does not synthesize traffic for gaps.
`--scope day` is appropriate for independent daily runs, and cannot establish
cross-day ordering. `--scope continuous` keeps one watermark across the selected
days. Filenames and directories are passed chronologically, using the WAVE
tool's directory expansion. Reports contain per-run JSON, stderr and a
`summary.json`, updated after each completed run. Use a new output directory for
each selection; no automatic resume is performed. Daily host/context counts
are not a deduplicated corpus-wide host inventory.

Exit status: **0** pass, **1** refused or late records, **2** execution/input
failure. Declared context-array truncation alone is not failure. Gzip integrity,
JSON, required-field types and event-time order are checked by WAVE during a
full pass. The inventory tool only checks paths and sizes; it does not open gzip
streams or certify record validity.
The inventory exits 1 for zero-byte files, unexpected filenames, misplaced files
or an empty selection; absent calendar days are reported without making the
inventory fail. Run it as well as the WAVE preflight: an empty input file can
yield no records without a schema refusal, so a preflight pass alone does not
establish collection completeness.

The checker modification prepared in this session ignores additional fields
recursively while validating recognized fields. An unchanged WAVE checker and
`wave-offline` ingestion still use their strict schema. Do not interpret a pass
from an extension-tolerant checker as proof that strict ingestion accepts the
same data. Record the WAVE commit and checker patch with published results.

## WAVE processing

The installed daily orchestration entry point is
`/home/rysavy/lan-dataset-tools/dp_workbench.py`. Its commands are `init`,
`inspect`, `validate`, `run` and `status`. See [WORKBENCH.md](WORKBENCH.md) for
environment installation, date selection, enrichment parameters and output paths.
It uses a dedicated pristine WAVE checkout and automatically selects working
unprivileged user-namespace isolation on this host.

After preflight, run a bounded daily replay, with enrichment directories supplied
by the operator:

```bash
"$WAVE/bin/wave-offline" --connections "$DATA/2025/09/01" \
  --threatfox /path/to/threatfox --netify /path/to/netify
```

Start with one day; several months of derived engine state are substantially
larger than the compressed input. Choose daily or continuous scope deliberately.
Do not import ISCX-specific timestamp corrections or label assumptions into this
office dataset. Historical capture dates also require explicit interpretation of
the enrichment snapshot and evaluation time; a current feed match is not proof
of what was known at capture time.

## Documentation deployment

The host's `/mnt/data` CIFS share is mounted **read-only**. This README and scripts
are prepared in a writable companion directory and must be copied into the
dataset through its writable source share by an operator. The original README
referenced a collection catalogue; keep that catalogue consistent if it still
contains this dataset entry. The source mount was not remounted or altered.
