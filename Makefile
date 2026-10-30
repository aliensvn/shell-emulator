PYTHON ?= python3

.PHONY: run test demo clean

run:
	PYTHONPATH=src $(PYTHON) src/main.py

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

demo:
	bash tests/os_scripts/run_stage1.sh

clean:
	rm -rf tests/data
