IMG     = img
SRC     = src
DATA    = $(SRC)/data
ENV_DIR = $(SRC)/environment
BIN     = $(ENV_DIR)/bin
DEP     = dependencies.txt
PYTHON  = python

setup:
	@# Set up virtual environemnt
	$(PYTHON) -m venv $(ENV_DIR)
	$(BIN)/pip install --upgrade pip
	make install

install:
	@# Create output directories
	mkdir -p $(DATA)
	mkdir -p $(IMG)

	@# Intall packages into virtual environemnt
	$(BIN)/pip install -r $(DEP)

update:
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r $(DEP)

run:
	bash -c                    \
	"cd $(shell pwd)       &&  \
	source $(BIN)/activate &&  \
	cd $(SRC)              &&  \
	python main.py"

debug:
	source $(BIN)/activate && \
	cd $(SRC)              && \
	python -m pudb main.py

clean:
	rm -rfv $(ENV_DIR)
