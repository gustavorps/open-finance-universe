SHELL := /bin/bash

PYTHON_PREFIX := python
PYTHON_PACKAGES_DIR := python/packages

.PHONY: /git/hard-clear

/git/hard-clear:
	@git -C .. clean -Xdf

