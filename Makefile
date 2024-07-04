install:
	pip install -r requirements.txt

lint:
	ruff .
	black .
	pylint aaa.py
	isort .

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
