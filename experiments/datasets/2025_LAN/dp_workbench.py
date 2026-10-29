#!/usr/bin/env python3
"""Local LAN data workbench: init, inspect, validate, run, status.

Python 3.10+, Linux for init/run. No daemon or broker. Run --help or COMMAND
--help for options. WAVE owns the engine lifecycle; this wrapper never kills
unrelated processes or changes system settings.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import date, datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import uuid

BASE = Path(__file__).resolve().parent
SOURCE = "https://github.com/rysavy-ondrej/maestro-helena-wave.git"
DEFAULT_DATA = Path("/mnt/data/2026_MAESTRO/Datasets/2025_LAN")


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def capture(argv, **kwargs):
    return subprocess.check_output(list(map(str, argv)), text=True, **kwargs).strip()


def execute(argv, cwd=None, stdout=None, stderr=None):
    print("+ " + shlex.join(list(map(str, argv))), file=sys.stderr, flush=True)
    child = subprocess.Popen(list(map(str, argv)), cwd=cwd, stdout=stdout, stderr=stderr)
    try:
        return child.wait()
    except KeyboardInterrupt:
        # SIGINT reaches the foreground child too. Give wave-offline its teardown.
        print("Interrupted; waiting for child cleanup. See the run logs.", file=sys.stderr)
        child.wait()
        raise


def must(argv, **kwargs):
    code = execute(argv, **kwargs)
    if code:
        raise RuntimeError(f"command exited {code}: {shlex.join(list(map(str, argv)))}")


@contextmanager
def locked(state):
    state.mkdir(parents=True, exist_ok=True)
    with (state / "workbench.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("another workbench operation holds the workspace lock")
        yield


def runtime_prefix(mode):
    probe = ["unshare", "--net", "--uts", "--pid", "--fork", "--mount-proc", "true"]
    choices = {"direct": [], "userns": ["unshare", "--user", "--map-root-user"],
               "sudo": ["sudo", "-n"]}
    for name in ("direct", "userns") if mode == "auto" else (mode,):
        result = subprocess.run(choices[name] + probe, capture_output=True, text=True)
        if result.returncode == 0:
            return choices[name]
    raise RuntimeError("namespace isolation unavailable; try --runtime-mode userns, or "
                       "authorize sudo separately and use --runtime-mode sudo")


def wave_python(repo):
    python = repo / ".venv/bin/python"
    if not python.is_file():
        raise RuntimeError("WAVE environment missing; run init first")
    return python


def selected_days(args):
    if args.command == "run" and not (args.day or args.from_date or args.to_date or args.all_days):
        raise RuntimeError("run requires --day, a date range, or explicit --all-days")
    if args.day and (args.from_date or args.to_date):
        raise RuntimeError("use --day OR --from-date/--to-date")
    start, end = (args.day, args.day) if args.day else (args.from_date, args.to_date)
    if start and end and start > end:
        raise RuntimeError("--from-date exceeds --to-date")
    days = []
    for folder in sorted(args.dataset.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]")):
        try:
            day = date(*map(int, folder.relative_to(args.dataset).parts))
        except ValueError:
            continue
        if (not start or day >= start) and (not end or day <= end):
            files = sorted(folder.glob("*.ndjson.gz"))
            if files:
                days.append((day.isoformat(), folder, files))
    if not days:
        raise RuntimeError("no populated days match the selection")
    if args.day and days[0][0] != args.day.isoformat():
        raise RuntimeError("selected day not present")
    return days


def install_engine(args):
    repo = args.repo
    manifest = json.loads((repo / "scripts/v11/artifacts.json").read_text())
    spec = next(s for s in manifest["artifacts"] if s["name"] == "risingwave")
    target = repo / spec["destination"]
    if not target.is_file() or digest(target) != spec["sha256"]:
        if args.risingwave_binary:
            source = args.risingwave_binary
        else:
            if platform.machine() not in ("x86_64", "amd64"):
                raise RuntimeError("this manifest pins x86_64; supply a matching supported checkout")
            version = spec["version"].split()[1]
            url = ("https://github.com/risingwavelabs/risingwave/releases/download/"
                   f"v{version}/risingwave-v{version}-x86_64-unknown-linux.tar.gz")
            archive = args.state_dir / f"risingwave-{version}.tar.gz"
            if not archive.exists():
                print(f"Downloading {url}", file=sys.stderr, flush=True)
                partial = archive.with_suffix(".part")
                with urllib.request.urlopen(url, timeout=60) as response, partial.open("wb") as out:
                    shutil.copyfileobj(response, out)
                partial.replace(archive)
            source = args.state_dir / "risingwave.download"
            with tarfile.open(archive, "r:gz") as bundle:
                members = [m for m in bundle.getmembers()
                           if m.isfile() and Path(m.name).name == "risingwave"]
                if len(members) != 1:
                    raise RuntimeError("release archive must contain exactly one risingwave binary")
                with bundle.extractfile(members[0]) as inp, source.open("wb") as out:
                    shutil.copyfileobj(inp, out)
        if digest(source) != spec["sha256"]:
            raise RuntimeError("RisingWave binary does not match the checkout's pinned SHA-256")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        target.chmod(0o755)
    python = wave_python(repo)
    library = args.libpython or Path(capture([python, "-c", "import sysconfig; "
        "from pathlib import Path; print(Path(sysconfig.get_config_var('LIBDIR')) / 'libpython3.12.so.1.0')"]))
    if not library.is_file():
        raise RuntimeError("Python 3.12 shared library missing; supply --libpython PATH")
    libtarget = repo / "bin/lib/libpython3.12.so.1.0"
    libtarget.parent.mkdir(parents=True, exist_ok=True)
    if library.resolve() != libtarget.resolve():
        shutil.copy2(library, libtarget)
    env = {**os.environ, "LD_LIBRARY_PATH": str(libtarget.parent)}
    version = capture([target, "--version"], env=env, stderr=subprocess.STDOUT)
    if version != spec["version"]:
        raise RuntimeError(f"unexpected engine version: {version}")
    libspec = next(s for s in manifest["artifacts"] if s["name"] == "risingwave-libpython")
    # Offline-only provenance: do not pretend Kafka/JRE or the /root copy installer ran.
    provenance = dict(schema="helena-v1_1-runtime-provenance.v1", generated_at=now(),
        manifest="scripts/v11/artifacts.json", provisioner="dp_workbench.py offline-only",
        artifacts=[dict(name="risingwave", path=str(target), sha256=digest(target), version=version),
                   dict(name="risingwave-libpython", path=str(libtarget), sha256=digest(libtarget),
                        source=str(library), manifest_sha256=libspec["sha256"],
                        matches_manifest=digest(libtarget) == libspec["sha256"])])
    atomic_json(repo / ".run/v11/provenance.json", provenance)
    return provenance


def init(args, record):
    if sys.platform != "linux":
        raise RuntimeError("WAVE local runtime requires Linux")
    missing = [name for name in ("git", "unshare", "ip", "hostname") if not shutil.which(name)]
    if missing:
        raise RuntimeError(f"missing system prerequisites: {', '.join(missing)}; "
                           "install git, util-linux, iproute2 and hostname via the host administrator")
    if not args.repo.exists():
        args.repo.parent.mkdir(parents=True, exist_ok=True)
        must(["git", "clone", "--depth", "1", "--branch", args.ref, SOURCE, args.repo])
    elif not (args.repo / ".git").is_dir():
        raise RuntimeError("--repo exists but is not a Git checkout")
    elif args.update:
        if capture(["git", "-C", args.repo, "status", "--porcelain", "--untracked-files=no"]):
            raise RuntimeError("refusing to update a checkout with tracked modifications")
        must(["git", "-C", args.repo, "fetch", "origin", args.ref])
        must(["git", "-C", args.repo, "checkout", "--detach", "FETCH_HEAD"])
    if not (args.repo / "bin/wave-offline").is_file():
        raise RuntimeError("checkout does not contain bin/wave-offline")
    uv = shutil.which("uv")
    if not uv:
        bootstrap = args.state_dir / "bootstrap"
        if not (bootstrap / "bin/python").exists():
            must([sys.executable, "-m", "venv", bootstrap])
        must([bootstrap / "bin/python", "-m", "pip", "install", "uv"])
        uv = str(bootstrap / "bin/uv")
    must([uv, "sync", "--frozen", "--python", "3.12"], cwd=args.repo)
    record["runtime"] = install_engine(args)
    record["namespace_prefix"] = runtime_prefix(args.runtime_mode)
    record["commit"] = capture(["git", "-C", args.repo, "rev-parse", "HEAD"])
    if args.smoke_test:
        must(record["namespace_prefix"] + [wave_python(args.repo), args.repo / "bin/wave-offline",
             "--profile", "demo", "--out", args.operation / "demo-contexts",
             "--quarantine", args.operation / "demo-quarantine.log"], cwd=args.repo)
    return 0


def inspect(args, record):
    tool = BASE / "scripts/inventory_connections.py"
    with (args.operation / "inventory.json").open("w") as out:
        code = execute([sys.executable, tool, args.dataset], stdout=out)
    record["inventory"] = json.loads((args.operation / "inventory.json").read_text())
    if args.day or args.from_date or args.to_date:
        record["selected_days"] = [d for d, _, _ in selected_days(args)]
    print(json.dumps(record["inventory"], indent=2))
    return code


def check_day(args, label, folder, files, directory):
    empty = [str(p) for p in files if p.stat().st_size == 0]
    if len(empty) == len(files):
        atomic_json(directory / "input-error.json", {"error": "all selected files are empty", "zero_byte_files": empty})
        return 1
    if empty and not args.allow_empty_files:
        atomic_json(directory / "input-error.json", {"zero_byte_files": empty})
        print(f"{label}: {len(empty)} zero-byte files; use --allow-empty-files only "
              "to acknowledge the collection gaps", file=sys.stderr)
        return 1
    tool = args.repo / "scripts/check_flows.py"
    with (directory / "validation.json").open("w") as out, (directory / "validation.stderr").open("w") as err:
        return execute([wave_python(args.repo), tool, folder, "--json", "--order", "name"],
                       cwd=args.repo, stdout=out, stderr=err)


def process_days(args, record):
    python = wave_python(args.repo)
    record["commit"] = capture(["git", "-C", args.repo, "rev-parse", "HEAD"])
    record["checker_sha256"] = digest(args.repo / "scripts/check_flows.py")
    days = selected_days(args)
    record["days"] = []
    code = 0
    prefix = runtime_prefix(args.runtime_mode) if args.command == "run" else []
    for label, folder, files in days:
        directory = args.operation / label
        directory.mkdir()
        row = dict(day=label, files=len(files), started_at=now(), status="validating",
                   zero_byte_files=[str(p) for p in files if p.stat().st_size == 0])
        record["days"].append(row)
        atomic_json(args.operation / "status.json", record)
        result = check_day(args, label, folder, files, directory)
        row["validation_exit"] = result
        if result == 0 and args.command == "run":
            row["preflight_only"] = args.check_only
            finding = json.loads((directory / "validation.json").read_text())
            expected = args.expect if args.expect is not None else finding["contexts"]
            row["expected_contexts"] = expected
            row["status"] = "processing"
            atomic_json(args.operation / "status.json", record)
            command = prefix + [python, args.repo / "bin/wave-offline", "--connections", folder,
                "--order", "name", "--out", directory / "contexts", "--quarantine",
                directory / "quarantine.jsonl", "--tenant", args.tenant, "--sensor", args.sensor,
                "--timeout", str(args.timeout), "--expect", str(expected)]
            for name in ("threatfox", "netify", "public_suffix_list", "evaluated_at"):
                value = getattr(args, name)
                if value is not None:
                    command += ["--" + name.replace("_", "-"), str(value)]
            if args.check_only:
                command += ["--check"]
            row["argv"] = list(map(str, command))
            with (directory / "wave-summary.json").open("w") as out, (directory / "wave.stderr").open("w") as err:
                result = execute(command, cwd=args.repo, stdout=out, stderr=err)
            row["processor_exit"] = result
        row.update(status="passed" if result == 0 else "failed", finished_at=now())
        code = max(code, result if result in (0, 1) else 2)
        atomic_json(args.operation / "status.json", record)
        if result and not args.keep_going:
            break
    return code


def parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dataset", type=Path, default=DEFAULT_DATA)
    common.add_argument("--repo", type=Path, default=BASE / "maestro-helena-wave")
    common.add_argument("--state-dir", type=Path, default=BASE / ".workbench")
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("init", parents=[common], help="install a local WAVE environment and engine")
    setup.add_argument("--ref", default="main", help="branch/tag to clone; existing checkout stays unchanged unless --update")
    setup.add_argument("--update", action="store_true", help="explicitly fetch/check out --ref, refusing tracked changes")
    setup.add_argument("--risingwave-binary", type=Path, help="use a local binary; pinned checksum is enforced")
    setup.add_argument("--libpython", type=Path, help="Python 3.12 library; defaults to uv-managed Python's shared library")
    setup.add_argument("--smoke-test", action="store_true", help="run WAVE's six-context demo after installation")
    setup.add_argument("--runtime-mode", choices=("auto", "direct", "userns", "sudo"), default="auto")
    for name in ("inspect", "validate", "run"):
        sub = commands.add_parser(name, parents=[common], help={"inspect":"inventory files and collection gaps",
            "validate":"check selected days with WAVE's own validator", "run":"validate then process each selected day independently"}[name])
        sub.add_argument("--day", type=date.fromisoformat)
        sub.add_argument("--from-date", type=date.fromisoformat)
        sub.add_argument("--to-date", type=date.fromisoformat)
        if name != "inspect":
            sub.add_argument("--allow-empty-files", action="store_true", help="acknowledge and record zero-byte collection gaps")
            sub.add_argument("--keep-going", action="store_true", help="continue to later days after a failed day")
        if name == "run":
            sub.add_argument("--all-days", action="store_true", help="explicitly process every populated day if no dates supplied")
            sub.add_argument("--runtime-mode", choices=("auto", "direct", "userns", "sudo"), default="auto")
            for flag in ("threatfox", "netify", "public-suffix-list"):
                sub.add_argument("--" + flag, type=Path)
            sub.add_argument("--tenant", default="lan")
            sub.add_argument("--sensor", default="office-lan")
            sub.add_argument("--evaluated-at", help="RFC3339 enrichment evaluation time")
            sub.add_argument("--timeout", type=int, default=180, help="WAVE export timeout in seconds")
            sub.add_argument("--expect", type=int, help="override expected contexts PER DAY; default is the preflight prediction")
            sub.add_argument("--check-only", action="store_true", help="run wave-offline preflight without starting an engine")
    status = commands.add_parser("status", parents=[common], help="show installation and recorded operation status")
    status.add_argument("--limit", type=int, default=10)
    return p


def main():
    args = parser().parse_args()
    for key in ("dataset", "repo", "state_dir", "risingwave_binary", "libpython",
                "threatfox", "netify", "public_suffix_list"):
        value = getattr(args, key, None)
        if value is not None:
            setattr(args, key, value.expanduser().resolve())
    if args.state_dir == args.dataset or args.dataset in args.state_dir.parents:
        print("--state-dir must be outside the raw dataset", file=sys.stderr)
        return 2
    if args.repo == args.dataset or args.dataset in args.repo.parents:
        print("--repo must be outside the raw dataset", file=sys.stderr)
        return 2
    if getattr(args, "timeout", 1) <= 0 or getattr(args, "limit", 1) <= 0 or (getattr(args, "expect", None) is not None and args.expect < 0):
        print("timeout and limit must be positive; expect must be nonnegative", file=sys.stderr)
        return 2
    if args.command == "status":
        operations = []
        for path in sorted((args.state_dir / "operations").glob("*/status.json"), reverse=True)[:args.limit]:
            try:
                operations.append(json.loads(path.read_text()))
            except (OSError, ValueError):
                operations.append({"file": str(path), "error": "unreadable status"})
        provenance = args.repo / ".run/v11/provenance.json"
        print(json.dumps(dict(repo=str(args.repo), venv=(args.repo / '.venv/bin/python').is_file(),
            engine=(args.repo / 'bin/risingwave').is_file(), provenance=str(provenance) if provenance.exists() else None,
            operations=operations), indent=2))
        return 0
    with locked(args.state_dir):
        label = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + args.command + "-" + uuid.uuid4().hex[:8]
        args.operation = args.state_dir / "operations" / label
        args.operation.mkdir(parents=True)
        print(f"Reports: {args.operation}", file=sys.stderr, flush=True)
        record = dict(command=args.command, started_at=now(), status="running",
                      pid=os.getpid(), dataset=str(args.dataset), repo=str(args.repo), reports=str(args.operation))
        atomic_json(args.operation / "status.json", record)
        try:
            code = (init(args, record) if args.command == "init" else
                    inspect(args, record) if args.command == "inspect" else process_days(args, record))
            record.update(status="passed" if code == 0 else "failed", exit_code=code)
        except KeyboardInterrupt:
            code = 130
            record.update(status="interrupted", exit_code=code)
        except Exception as error:
            code = 2
            record.update(status="failed", exit_code=code, error=str(error))
            print(f"dp_workbench: {error}", file=sys.stderr)
        record["finished_at"] = now()
        atomic_json(args.operation / "status.json", record)
        print(json.dumps(record, indent=2))
        return code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError) as error:
        print(f"dp_workbench: {error}", file=sys.stderr)
        raise SystemExit(2)
