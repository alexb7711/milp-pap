IMG     = img
SRC     = src
DATA    = $(SRC)/data
ENV_DIR = $(SRC)/environment
BIN     = $(ENV_DIR)/bin
DEP     = dependencies.txt

setup:
	@# Set up virtual environemnt
	python3.9 -m venv ./$(ENV_DIR)
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
	source $(BIN)/activate && \
	cd $(SRC)              && \
	python main.py

debug:
	$(BIN)/python -m pudb main.py

clean:
	rm -rfv $(ENV_DIR)
	rm -f $(DATA)/*
