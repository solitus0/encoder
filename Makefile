install:
	pipenv install --editable .

shell:
	pipenv shell

which:
	pipenv --venv

remove:
	pipenv --rm

run:
	pipenv run python3 bin/run.py
