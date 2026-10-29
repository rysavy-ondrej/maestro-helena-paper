SHELL := /bin/bash

PANDOC  ?= pandoc
LATEXMK ?= latexmk
PYTHON  ?= python3

SECTIONS       := $(sort $(wildcard paper/sections/*.md))
GENERATED      := latex/generated
FIGURE_SCRIPTS := $(wildcard figures/src/*.py)
FIGURES        := $(patsubst figures/src/%.py,figures/%.pdf,$(FIGURE_SCRIPTS))

PANDOC_OPTS := -f markdown -t latex \
  --top-level-division=section \
  --wrap=preserve \
  --natbib \
  --metadata-file=paper/metadata.yaml
# pandoc-crossref first, then every Lua filter in latex/filters/ (templates may add their own).
LUA_FILTERS    := $(sort $(wildcard latex/filters/*.lua))
PANDOC_FILTERS := --filter pandoc-crossref $(addprefix --lua-filter=,$(LUA_FILTERS))

.PHONY: all pdf latex figures snapshot check-tools clean

all: pdf

$(GENERATED):
	mkdir -p $@

$(GENERATED)/abstract.tex: paper/abstract.md paper/metadata.yaml | $(GENERATED)
	$(PANDOC) $(PANDOC_OPTS) $< -o $@

$(GENERATED)/body.tex: $(SECTIONS) paper/metadata.yaml $(LUA_FILTERS) | $(GENERATED)
	$(PANDOC) $(PANDOC_OPTS) $(PANDOC_FILTERS) $(SECTIONS) -o $@

latex: $(GENERATED)/abstract.tex $(GENERATED)/body.tex

# Each figures/src/<name>.py writes figures/<name>.pdf (output path is argv[1]).
figures/%.pdf: figures/src/%.py
	$(PYTHON) $< $@

figures: $(FIGURES)

pdf: latex figures
	mkdir -p build
	cd latex && $(LATEXMK) -pdf \
	  -interaction=nonstopmode \
	  -halt-on-error \
	  -outdir=../build main.tex
	cp build/main.pdf build/paper.pdf

# Freeze the current sources (and PDF, if built) as drafts/NN-label.
snapshot:
	@[[ "$(NAME)" =~ ^[0-9]{2}-[a-z0-9-]+$$ && "$(NAME)" != 00-* ]] || \
	  { echo "usage: make snapshot NAME=NN-label (e.g. 02-first-draft; 00 is reserved)"; exit 1; }
	@test ! -e drafts/$(NAME) || { echo "drafts/$(NAME) already exists"; exit 1; }
	mkdir -p drafts/$(NAME)
	cp -R paper references figures drafts/$(NAME)/
	if [ -f build/paper.pdf ]; then cp build/paper.pdf drafts/$(NAME)/paper.pdf; fi

check-tools:
	@missing=; \
	for t in $(PANDOC) pandoc-crossref $(LATEXMK) pdflatex bibtex; do \
	  command -v $$t >/dev/null || { echo "missing: $$t"; missing=1; }; \
	done; \
	test -z "$$missing" && echo "all build tools found"

clean:
	rm -rf build $(GENERATED)
