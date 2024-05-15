################################################################################
# Variables
################################################################################

##==============================================================================
# Directories
IMG_D     = img
SRC_D     = src
TST_D     = test
ENV_DIR   = .venv
ifneq ($(wildcard $(ENV_DIR)/bin/.),)
NOSE_DIR  = $(ENV_DIR)/bin
else
NOSE_DIR  = $(ENV_DIR)/Scripts
endif

##==============================================================================
# File Paths
DATA    = data
P_DATA  = ./docs/milp-pap-paper-frontiers/img/data
ifneq ($(shell uname -s), "Linux")
BIN     = $(ENV_DIR)/bin
else
BIN     = $(ENV_DIR)/Scripts
endif
DEP     = dependencies
PYTHON  = python

##==============================================================================
# Makefile configuration
.PHONY: all setup install update run debug clean test help

################################################################################
# Recipes
################################################################################

##==============================================================================
#
all: setup update run ## Default action

##==============================================================================
#
test: ## Run unit tests
	echo +++++++++
	ls
	echo +++++++++

	cd $(shell pwd)        &&  \
	source $(BIN)/activate  &&  \
	$(PYTHON) -m unittest discover -s $(TST_D) -p "test_*.py"

##==============================================================================
#
setup: ## Set up the project
	@# Set up virtual environemnt
	@$(PYTHON) -m venv $(ENV_DIR)
	@$(BIN)/pip install --upgrade pip
	@# Create output directories
	@mkdir -p $(DATA)
	@mkdir -p $(IMG_D)
	@# Intall packages into virtual environemnt
	@$(BIN)/pip install -r $(DEP)

##==============================================================================
#
update: ## Update the virtual environment packages
	@$(BIN)/pip install --upgrade pip
	@$(BIN)/pip install -r $(DEP)

##==============================================================================
#
run: ## Execute the program
	cd "$(shell pwd)"        &&  \
	source $(BIN)/activate  &&  \
	cd $(SRC_D)             &&  \
	$(PYTHON) main.py

##==============================================================================
#
debug: ## Enable the debugger (requires `pudb`)
	@source $(BIN)/activate  && \
	cd $(SRC_D)              && \
	python -m pudb main.py

##==============================================================================
#
clean: ## Cleanup the project
	rm -rfv $(ENV_DIR)

##==============================================================================
# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help:  ## Auto-generated help menu
	@grep -P '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	sort                                                | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
