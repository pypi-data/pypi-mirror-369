# Makefile to help automate key steps

.DEFAULT_GOAL := help
# Will likely fail on Windows, but Makefiles are in general not Windows
# compatible so we're not too worried
TEMP_FILE := $(shell mktemp)
# Directory in which to build the Fortran when using a standalone build
BUILD_DIR := build
# Coverage directory - needed to trick code cov to look in the right place
COV_DIR := $(shell uv run --no-sync python -c 'from pathlib import  Path; import example_fgen_basic; print(Path(example_fgen_basic.__file__).parent)')

# A helper script to get short descriptions of each target in the Makefile
define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([\$$\(\)a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-30s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT


.PHONY: help
help:  ## print short description of each target
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: checks
checks:  ## run all the linting checks of the codebase
	@echo "=== pre-commit ==="; uv run --no-sync pre-commit run --all-files || echo "--- pre-commit failed ---" >&2; \
		echo "=== mypy ==="; MYPYPATH=stubs uv run --no-sync mypy src || echo "--- mypy failed ---" >&2; \
		echo "======"

.PHONY: ruff-fixes
ruff-fixes:  ## fix the code using ruff
    # format before and after checking so that the formatted stuff is checked and
    # the fixed stuff is formatted
	uv run ruff format src tests scripts docs
	uv run ruff check src tests scripts docs --fix
	uv run ruff format src tests scripts docs

.PHONY: test
test:  ## run the tests (re-installs the package every time so you might want to run by hand if you're certain that step isn't needed)
	# Note: passing `src` to pytest causes the `src` directory to be imported
	# if the package has not already been installed.
	# This is a problem, as the package is not importable from `src` by itself because the extension module is not available.
	# As a result, you have to pass `pytest tests src` rather than `pytest src tests`
	# to ensure that the package is imported from the venv and not `src`.
	# The issue with this is that code coverage then doesn't work,
	# because it is looking for lines in `src` to be run,
	# but they're not because lines in `.venv` are run instead.
	# We don't have a solution to this yet.
	uv run --no-editable --reinstall-package example-fgen-basic pytest -r a -v tests src --doctest-modules --doctest-report ndiff --cov=$(COV_DIR)

# Note on code coverage and testing:
# You must specify cov=src.
# Otherwise, funny things happen when doctests are involved.
# If you want to debug what is going on with coverage,
# we have found that adding COVERAGE_DEBUG=trace
# to the front of the below command
# can be very helpful as it shows you
# if coverage is tracking the coverage
# of all of the expected files or not.
# We are sure that the coverage maintainers would appreciate a PR
# that improves the coverage handling when there are doctests
# and a `src` layout like ours.

.PHONY: docs
docs:  ## build the docs
	uv run --no-sync mkdocs build

.PHONY: docs-strict
docs-strict:  ## build the docs strictly (e.g. raise an error on warnings, this most closely mirrors what we do in the CI)
	uv run --no-sync mkdocs build --strict

.PHONY: docs-serve
docs-serve:  ## serve the docs locally
	uv run --no-sync mkdocs serve

.PHONY: changelog-draft
changelog-draft:  ## compile a draft of the next changelog
	uv run towncrier build --draft --version draft

.PHONY: licence-check
licence-check:  ## Check that licences of the dependencies are suitable
	# Will likely fail on Windows, but Makefiles are in general not Windows
	# compatible so we're not too worried
	uv export --no-dev > $(TEMP_FILE)
	uv run liccheck -r $(TEMP_FILE) -R licence-check.txt
	rm -f $(TEMP_FILE)

.PHONY: virtual-environment
virtual-environment:  ## update virtual environment, create a new one if it doesn't already exist
	uv sync --no-editable --all-extras --group all-dev
	uv run --no-sync pre-commit install

.PHONY: format-fortran
format-fortran:  ## format the Fortran files
	uv run fprettify -r src -c .fprettify.rc

$(BUILD_DIR):  # setup the standlone Fortran build directory
	uv run meson setup $(BUILD_DIR)

.PHONY: build-fortran
build-fortran: | $(BUILD_DIR)  ## build/compile the Fortran (including the extension module)
	uv run meson compile -C build -v

.PHONY: test-fortran
test-fortran: build-fortran  ## run the Fortran tests
	uv run meson test -C build -v

.PHONY: install-fortran
install-fortran: build-fortran  ## install the Fortran (including the extension module)
	uv run meson install -C build -v
	# # Can also do this to see where things go without making a mess
	# uv run meson install -C build --destdir ../install-example

.PHONY: clean
clean:  ## clean all build artefacts
	rm -rf $(BUILD_DIR)
