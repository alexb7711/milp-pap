################################################################################
# Variables
################################################################################

# Directories
IMG_D     = img
SRC_D     = src
TST_D     = test
ENV_DIR   = .env
NOSE_DIR  = $(ENV_DIR)/bin

# File Paths
DATA    = $(SRC_D)/data
P_DATA  = ~/Documents/docs/milp-pap/fig/data
BIN     = $(ENV_DIR)/bin
DEP     = dependencies
PYTHON  = python

# Makefile configuration
.PHONY: all setup install update run debug clean test

################################################################################
# Recipes
################################################################################

all: setup update run

test:
	# Check if nosetests is installed
	@nosetests --version >/dev/null 2>&1 && (echo "nosetests installed!") || (echo "ERROR: nosetests is required."; exit 1)
	@nosetests --plugins | grep coverage >/dev/null 2>&1 && (echo "coverage installed!") || (echo "ERROR: coverage is required."; exit 1)

	# Run tests
	@nosetests --exe --with-coverage --cover-erase --cover-package=test/ --cover-html

setup:
	@# Set up virtual environemnt
	$(PYTHON) -m venv $(ENV_DIR)
	$(BIN)/pip install --upgrade pip
	make install

install:
	@# Create output directories
	mkdir -p $(DATA)
	mkdir -p $(IMG_D)

	@# Intall packages into virtual environemnt
	$(BIN)/pip install -r $(DEP)

update:
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r $(DEP)

run:
	bash -c                    \
	"cd $(shell pwd)       &&  \
	source $(BIN)/activate &&  \
	cd $(SRC_D)              &&  \
	python main.py"

	bash -c "cp $(DATA)/*.csv $(P_DATA)"

debug:
	source $(BIN)/activate && \
	cd $(SRC_D)              && \
	python -m pudb main.py

clean:
	rm -rfv $(ENV_DIR)
