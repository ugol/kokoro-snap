SHELL := /bin/bash
.PHONY: dev test build

dev:
	python3 -m kokoro_server

test:
	python3 -m pytest -q

build:
	snapcraft pack
