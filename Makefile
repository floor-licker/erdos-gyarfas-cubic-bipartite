PYTHON ?= python3
PAPER_NAME := Tranquilli_2026_Erdos-Gyarfas_60-Vertex_Lower_Bound
export SOURCE_DATE_EPOCH ?= 1785283200
export FORCE_SOURCE_DATE ?= 1

.PHONY: all paper build-paper tables validate-paper-data
.PHONY: verify-certificate verify-certificates generate-certificates
.PHONY: reproduce-search verify-full verify-v29 verify-transcripts
.PHONY: verify-positive compare-genbg verify-genbg verify-unreduced
.PHONY: verify-all manifest verify-manifest clean-paper

all: paper

tables:
	$(PYTHON) research/scripts/generate_report_tables.py

paper: tables
	cd paper && pdflatex -jobname=$(PAPER_NAME) -interaction=nonstopmode -halt-on-error main.tex
	cd paper && pdflatex -jobname=$(PAPER_NAME) -interaction=nonstopmode -halt-on-error main.tex
	cd paper && pdflatex -jobname=$(PAPER_NAME) -interaction=nonstopmode -halt-on-error main.tex

build-paper: paper

validate-paper-data:
	$(PYTHON) research/scripts/validate_report_data.py

verify-certificate: verify-certificates

verify-certificates:
	$(PYTHON) research/scripts/reproduce_witness_certificates.py verify

generate-certificates:
	$(PYTHON) research/scripts/reproduce_witness_certificates.py generate

reproduce-search: verify-full verify-transcripts

verify-full:
	$(PYTHON) research/scripts/reproduce_all_v7_v29.py

verify-v29:
	$(PYTHON) research/scripts/reproduce_v29_all_orbits.py

verify-transcripts:
	$(PYTHON) research/scripts/reproduce_transcript_hashes.py

verify-positive:
	$(PYTHON) research/scripts/verify_positive_controls.py

compare-genbg: verify-genbg

verify-genbg:
	$(PYTHON) research/scripts/compare_c4_census_with_genbg.py

verify-unreduced:
	$(PYTHON) research/scripts/verify_unreduced_root_counts.py

verify-all: verify-manifest verify-certificates verify-full verify-v29
verify-all: verify-transcripts verify-positive verify-genbg verify-unreduced
verify-all: validate-paper-data paper

manifest:
	$(PYTHON) research/scripts/sha256_manifest.py generate

verify-manifest:
	$(PYTHON) research/scripts/sha256_manifest.py check

clean-paper:
	rm -f paper/$(PAPER_NAME).aux paper/$(PAPER_NAME).bbl
	rm -f paper/$(PAPER_NAME).blg paper/$(PAPER_NAME).log
	rm -f paper/$(PAPER_NAME).out paper/$(PAPER_NAME).toc
	rm -f paper/$(PAPER_NAME).fdb_latexmk paper/$(PAPER_NAME).fls
	rm -f paper/$(PAPER_NAME).synctex.gz
