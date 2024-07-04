install:
	pip install -r requirements.txt

lint:
	#ruff check . --fix
	ruff check .
	black .
	pylint .
	isort .
#	ruff . --fix

test:
	pytest

coverage:
	coverage run -m pytest
	coverage report -m

format:
	black .
	docformatter -r .

type-check:
	mypy .
