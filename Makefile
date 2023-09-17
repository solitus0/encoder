install:
	pipenv install .

install_dev:
	pipenv install --editable .

shell:
	pipenv shell

which:
	pipenv --venv

remove:
	pipenv --rm

run:
	PIPENV_DONT_LOAD_ENV=1 pipenv run python3 bin/run.py

run_dev:
	pipenv run python3 bin/run.py

pip_install:
	pip install -r requirements.txt

dump_requirements:
	pipenv requirements > requirements.txt
