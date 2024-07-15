install:
	sh init.sh
#	pip install -r requirements.txt

lint:
	ruff .
	black .
	pylint .
	isort .
	ruff .

test:
	pytest

coverage:
	coverage run -m pytest
	coverage report -m

format:
	black .
	docformatter -r .

type-check:
	mypy aaa.py

run:
	python main.py
