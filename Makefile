install:
	pipenv install

shell:
	pipenv shell

which:
	pipenv --venv

remove:
	pipenv --rm

run:
	pipenv run python3 main.py