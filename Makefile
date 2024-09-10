test:
	pip install pytest
	export PYTHONPATH="${PYTHONPATH}:./src:./tests"
	pytest

install_dependencies:
	pip install -r requirements.txt | findstr /V /C:"Requirement already satisfied"

install_dev :
	pip install mypy types-waitress pylint ruff | findstr /V /C:"Requirement already satisfied"

check: install_dependencies

	ruff check . --fix
	git ls-files '*.py' | xargs pylint
	mypy --install-types
	mypy .
