#!/usr/bin/env bash
# Build tool for this paper. Run `./build.sh help` for commands.
#
# Tools are taken from the project-local environment first:
#   .tools/bin      pandoc and pandoc-crossref (pinned, matching versions)
#   .tools/TinyTeX  LaTeX, only if no suitable system TeX is found
#   .venv           Python for figure scripts and checks
# Set PAPER_FORGE_TOOLS=/some/dir (and PAPER_FORGE_VENV) to share them between projects.
# Platforms: macOS (arm64, x86_64) and Linux (x86_64, arm64; also WSL). Needs bash,
# curl, make, perl, tar with xz, unzip (macOS), and python3.
set -euo pipefail

PANDOC_VERSION=3.12.1
CROSSREF_VERSION=0.3.26   # must be built for PANDOC_VERSION

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS="${PAPER_FORGE_TOOLS:-$ROOT/.tools}"
VENV="${PAPER_FORGE_VENV:-$ROOT/.venv}"
BUILD_LOG="$ROOT/build/build.log"
cd "$ROOT"

say() { printf '%s\n' "$*"; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }

tinytex_bin() { ls -d "$TOOLS"/TinyTeX/bin/* 2>/dev/null | head -1 || true; }

activate() {
  local tex
  tex="$(tinytex_bin)"
  export PATH="$TOOLS/bin${tex:+:$tex}${VENV:+:$VENV/bin}:$PATH"
  export MPLCONFIGDIR="${MPLCONFIGDIR:-$ROOT/build/.matplotlib}"
}

# A Python 3 interpreter that actually runs (some systems ship broken shims).
find_python() {
  local candidate
  for candidate in "${PYTHON:-}" python3 /usr/bin/python3 python; do
    [ -n "$candidate" ] && "$candidate" -c 'import venv' >/dev/null 2>&1 && { echo "$candidate"; return; }
  done
  return 1
}

python_bin() {
  if [ -x "$VENV/bin/python" ]; then echo "$VENV/bin/python"; else find_python; fi
}

document_class() {
  sed -n 's/^[^%]*\\documentclass\(\[[^]]*\]\)\{0,1\}{\([^}]*\)}.*/\2/p' latex/main.tex | head -1
}

class_found() {
  local cls
  cls="$(document_class)"
  [ -z "$cls" ] || [ -f "latex/$cls.cls" ] || kpsewhich "$cls.cls" >/dev/null 2>&1
}

tex_ready() {
  command -v latexmk >/dev/null && command -v pdflatex >/dev/null && command -v bibtex >/dev/null && class_found
}

platform() {
  case "$(uname -s)-$(uname -m)" in
    Darwin-arm64)                echo "pandoc-$PANDOC_VERSION-arm64-macOS.zip macOS-ARM64 darwin" ;;
    Darwin-x86_64)               echo "pandoc-$PANDOC_VERSION-x86_64-macOS.zip macOS-X64 darwin" ;;
    Linux-x86_64)                echo "pandoc-$PANDOC_VERSION-linux-amd64.tar.gz Linux-X64 linux-x86_64" ;;
    Linux-aarch64 | Linux-arm64) echo "pandoc-$PANDOC_VERSION-linux-arm64.tar.gz Linux-ARM64 linux-arm64" ;;
    *) die "unsupported platform $(uname -s)-$(uname -m); install pandoc, pandoc-crossref, and TeX manually" ;;
  esac
}

# ---------------------------------------------------------------- setup

setup_pandoc() {
  if [ -x "$TOOLS/bin/pandoc" ] && "$TOOLS/bin/pandoc" --version | head -1 | grep -q " $PANDOC_VERSION\$" \
     && [ -x "$TOOLS/bin/pandoc-crossref" ]; then
    say "pandoc $PANDOC_VERSION and pandoc-crossref $CROSSREF_VERSION: already installed"
    return
  fi
  local asset crossref _ tmp
  read -r asset crossref _ <<<"$(platform)"
  tmp="$(mktemp -d "${TMPDIR:-/tmp}/paper-forge.XXXXXX")"
  mkdir -p "$TOOLS/bin" "$tmp/pandoc" "$tmp/crossref"
  say "downloading pandoc $PANDOC_VERSION ..."
  curl -fsSL -o "$tmp/$asset" "https://github.com/jgm/pandoc/releases/download/$PANDOC_VERSION/$asset"
  case "$asset" in
    *.zip) unzip -q "$tmp/$asset" -d "$tmp/pandoc" ;;
    *) tar xzf "$tmp/$asset" -C "$tmp/pandoc" ;;
  esac
  cp "$(find "$tmp/pandoc" -type f -name pandoc | head -1)" "$TOOLS/bin/pandoc"
  say "downloading pandoc-crossref $CROSSREF_VERSION ..."
  curl -fsSL -o "$tmp/crossref.tar.xz" \
    "https://github.com/lierdakil/pandoc-crossref/releases/download/v$CROSSREF_VERSION/pandoc-crossref-$crossref.tar.xz"
  tar xJf "$tmp/crossref.tar.xz" -C "$tmp/crossref"
  cp "$(find "$tmp/crossref" -type f -name pandoc-crossref | head -1)" "$TOOLS/bin/pandoc-crossref"
  chmod +x "$TOOLS/bin/pandoc" "$TOOLS/bin/pandoc-crossref"
  rm -rf "$tmp"
}

tex_packages() {
  [ -f latex/tex-packages.txt ] && sed 's/#.*//' latex/tex-packages.txt | tr -s ' \n' '\n' | grep . || true
}

setup_tex() {
  if [ "${1:-}" != "--tinytex" ] && tex_ready; then
    say "TeX: using $(command -v pdflatex) (class $(document_class) found)"
    return
  fi
  local os tlmgr
  read -r _ _ os <<<"$(platform)"
  if [ -z "$(tinytex_bin)" ]; then
    local python url tmp
    python="$(find_python)" || die "python3 is required to locate the TinyTeX release"
    url="$(curl -fsSL https://api.github.com/repos/rstudio/tinytex-releases/releases/latest | "$python" -c "
import json, sys
assets = json.load(sys.stdin)['assets']
print(next(a['browser_download_url'] for a in assets if a['name'].startswith('TinyTeX-1-$os-')))")"
    tmp="$(mktemp -d "${TMPDIR:-/tmp}/paper-forge.XXXXXX")"
    say "downloading TinyTeX (${url##*/}) ..."
    curl -fsSL -o "$tmp/tinytex.tar.xz" "$url"
    mkdir -p "$TOOLS"
    tar xJf "$tmp/tinytex.tar.xz" -C "$TOOLS"
    # The Linux archive unpacks to .TinyTeX, the macOS one to TinyTeX.
    [ -d "$TOOLS/.TinyTeX" ] && mv "$TOOLS/.TinyTeX" "$TOOLS/TinyTeX"
    rm -rf "$tmp"
  fi
  activate
  tlmgr="$(tinytex_bin)/tlmgr"
  "$tlmgr" option repository "${CTAN_MIRROR:-https://mirror.ctan.org/systems/texlive/tlnet}" >/dev/null
  "$tlmgr" update --self >/dev/null 2>&1 || true
  install_tex_packages
}

# Install latex/tex-packages.txt into the project-local TinyTeX.
install_tex_packages() {
  local tlmgr packages
  tlmgr="$(tinytex_bin)/tlmgr"
  packages="$(tex_packages | tr '\n' ' ')"
  if [ -n "$packages" ]; then
    say "installing TeX packages: $packages"
    # shellcheck disable=SC2086
    "$tlmgr" install $packages >/dev/null ||
      die "tlmgr could not install packages; retry, or pick a mirror: CTAN_MIRROR=https://<mirror>/systems/texlive/tlnet ./build.sh setup"
  fi
}

setup_python() {
  if [ ! -x "$VENV/bin/python" ]; then
    local python
    python="$(find_python)" || die "python3 not found"
    say "creating .venv with $python ..."
    if "$python" -c 'import ensurepip' >/dev/null 2>&1; then
      "$python" -m venv "$VENV"
    else
      # Debian/Ubuntu without python3-venv: bootstrap pip without root.
      "$python" -m venv --without-pip "$VENV"
      curl -fsSL https://bootstrap.pypa.io/get-pip.py | "$VENV/bin/python" - -q --disable-pip-version-check
    fi
  fi
  "$VENV/bin/python" -m pip install -q --disable-pip-version-check -r requirements.txt
  say "Python: .venv ready ($(sed 's/#.*//' requirements.txt | tr -s ' \n' ' '))"
}

require_commands() {
  local tool missing=""
  for tool in "$@"; do command -v "$tool" >/dev/null || missing="$missing $tool"; done
  [ -z "$missing" ] && return
  case "$(uname -s)" in
    Linux) die "missing:$missing (Debian/Ubuntu: sudo apt install curl make perl xz-utils python3; Fedora: sudo dnf install curl make perl xz python3)" ;;
    *) die "missing:$missing (macOS: xcode-select --install)" ;;
  esac
}

cmd_setup() {
  require_commands curl make perl tar xz
  [ "$(uname -s)" = Darwin ] && require_commands unzip
  find_python >/dev/null || die "python3 not found (Debian/Ubuntu: sudo apt install python3)"
  setup_pandoc
  activate
  setup_tex "${1:-}"
  setup_python
  cmd_doctor
}

# ---------------------------------------------------------------- doctor

cmd_doctor() {
  activate
  local ok=1 tool path
  for tool in pandoc pandoc-crossref latexmk pdflatex bibtex make perl; do
    if path="$(command -v "$tool")"; then
      printf '  %-16s %s\n' "$tool" "$path"
    else
      printf '  %-16s MISSING\n' "$tool"
      ok=0
    fi
  done
  if command -v pandoc >/dev/null && command -v pandoc-crossref >/dev/null; then
    local pv cv
    pv="$(pandoc --version | head -1 | awk '{print $2}')"
    cv="$(pandoc-crossref --version 2>/dev/null | sed -n 's/.*built with Pandoc v\([0-9.]*\).*/\1/p')"
    if [ -n "$cv" ] && [ "$pv" != "$cv" ]; then
      printf '  %-16s pandoc %s but pandoc-crossref built for %s\n' "MISMATCH" "$pv" "$cv"
      ok=0
    fi
  fi
  local cls
  cls="$(document_class)"
  if [ -n "$cls" ] && ! { [ -f "latex/$cls.cls" ] || kpsewhich "$cls.cls" >/dev/null 2>&1; }; then
    printf '  %-16s %s.cls not found\n' "class" "$cls"
    ok=0
  fi
  if ls figures/src/*.py >/dev/null 2>&1 && ! "$(python_bin)" -c 'import matplotlib' >/dev/null 2>&1; then
    printf '  %-16s matplotlib not available for figures/src/*.py\n' "python"
    ok=0
  fi
  if [ "$ok" = 1 ]; then
    say "READY"
  else
    say "NOT READY: run ./build.sh setup"
    return 1
  fi
}

# ---------------------------------------------------------------- build

# With a project-local TinyTeX, install a missing package named in the log.
install_missing_tex_package() {
  local tlmgr file package
  [ -n "$(tinytex_bin)" ] || return 1
  tlmgr="$(tinytex_bin)/tlmgr"
  file="$(grep -ohE "File \`[^']+' not found|can't find file \`[^']+'" "$BUILD_LOG" build/main.log 2>/dev/null \
          | head -1 | sed -E "s/.*\`([^']+)'.*/\1/" || true)"
  case "$file" in "" | figures/* | */figures/*) return 1 ;; esac
  package="$("$tlmgr" search --global --file "/$file" 2>/dev/null | grep -E '^[A-Za-z0-9._-]+:$' | head -1 | tr -d : || true)"
  [ -n "$package" ] || return 1
  say "installing missing TeX package '$package' (for $file) ..."
  "$tlmgr" install "$package" >/dev/null 2>&1
}

cmd_pdf() {
  activate
  # A local TinyTeX shared with other projects may lack this template's class.
  if [ -n "$(tinytex_bin)" ] && ! class_found; then install_tex_packages; fi
  cmd_doctor >/dev/null || { cmd_doctor; exit 2; }
  mkdir -p build
  # Always regenerate the LaTeX from Markdown (fast); timestamps can mislead make
  # after checkouts or copies.
  rm -rf latex/generated
  local attempt python
  python="$(python_bin)"
  for attempt in 1 2 3 4 5 6 7 8 9 10; do
    if make pdf PYTHON="$python" >"$BUILD_LOG.tmp" 2>&1; then
      mv "$BUILD_LOG.tmp" "$BUILD_LOG"
      local pages summary
      pages="$(sed -n 's/^Output written on .*(\([0-9]*\) page.*/\1/p' build/main.log | tail -1)"
      summary="$("$python" scripts/validate.py . | tail -1 || true)"
      say "BUILD OK: build/paper.pdf, ${pages:-?} page(s); check: $summary"
      return 0
    fi
    mv "$BUILD_LOG.tmp" "$BUILD_LOG"
    install_missing_tex_package || break
    rm -f build/main.*   # latexmk does not retry a failed run without changes
  done
  "$python" scripts/validate.py . --diagnose "$BUILD_LOG"
  say "BUILD FAILED (full output: build/build.log, LaTeX log: build/main.log)"
  return 1
}

cmd_check() {
  activate
  "$(python_bin)" scripts/validate.py . "$@"
}

cmd_figures() {
  activate
  make figures PYTHON="$(python_bin)"
}

cmd_preview() {
  activate
  local python target="${1:-build/paper.pdf}"
  python="$(python_bin)"
  [ -f "$target" ] || die "$target not found (run ./build.sh first)"
  "$python" -c 'import fitz' 2>/dev/null || die "PyMuPDF missing; run ./build.sh setup"
  mkdir -p build/preview
  "$python" - "$target" <<'EOF'
import sys
from pathlib import Path
import fitz

pdf = Path(sys.argv[1])
doc = fitz.open(pdf)
for page in doc:
    out = Path("build/preview") / f"{pdf.stem}-{page.number + 1}.png"
    page.get_pixmap(dpi=110).save(out)
    print(out)
EOF
}

cmd_snapshot() {
  [ -n "${1:-}" ] || die "usage: ./build.sh snapshot NN-label"
  make -s snapshot NAME="$1" && say "SNAPSHOT OK: drafts/$1"
}

cmd_help() {
  cat <<EOF
Usage: ./build.sh [command]

  (none) | pdf      build build/paper.pdf; prints BUILD OK or BUILD FAILED with the cause
  setup [--tinytex] install pandoc $PANDOC_VERSION + pandoc-crossref $CROSSREF_VERSION into .tools/,
                    TinyTeX if no system TeX has the class (or always with --tinytex),
                    and a Python .venv from requirements.txt
  doctor            show which tools are used; prints READY or NOT READY
  check [options]   full source/log/PDF checks (--max-pages N, --anonymous)
  figures           rebuild figures/<name>.pdf from figures/src/<name>.py
  preview [pdf]     render pages of build/paper.pdf (or another PDF) to build/preview/*.png
  snapshot NN-label freeze the current paper into drafts/NN-label
  clean             remove build/ and latex/generated/
EOF
}

command="${1:-pdf}"
[ $# -gt 0 ] && shift
case "$command" in
  pdf) cmd_pdf ;;
  setup) cmd_setup "$@" ;;
  doctor) cmd_doctor ;;
  check) cmd_check "$@" ;;
  figures) cmd_figures ;;
  preview) cmd_preview "$@" ;;
  snapshot) cmd_snapshot "$@" ;;
  clean) make clean ;;
  help | -h | --help) cmd_help ;;
  *) cmd_help; exit 2 ;;
esac
