ENV_DIR = environment
BIN     = $(ENV_DIR)/bin
DEP     = ../dependencies.txt

setup:
	python3.9 -m venv ./$(ENV_DIR)
	$(BIN)/pip install --upgrade pip
	make install

install:
	$(BIN)/pip install -r $(DEP)

run:
	$(BIN)/python main.py

