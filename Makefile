init:
	pyenv local "$(cat .python-version)"
	test -d venv || python -m venv .venv
	. .venv/bin/activate; pip install -r requirements.txt

freeze:
	. .venv/bin/activate; pip freeze > requirements.txt

lint:
	. .venv/bin/activate; python -m black .

.PHONY: init freeze lint
