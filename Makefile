.PHONY: init
init:
	pyenv local "$(cat .python-version)"
	python -m venv .venv
	source .venv/bin/activate
	pip install -r requirements.txt

.PHONY: activate
activate:
	source .venv/bin/activate

.PHONY: freeze
freeze:
	pip freeze > requirements.txt

.PHONY: lint
lint:
	python -m black .
