.PHONY: init init-from-template run hooks seed test check cfn-lint ldb init-db idb flask-init-db deploy-dev deploy-qa

PYTHON=poetry run

init: init-from-template hooks

init-from-template:
	git init
	npm install

run:
	FLASK_ENV=development $(PYTHON) flask run --reload

hooks:
	$(PYTHON) pre-commit install

seed:
	$(PYTHON) flask seed

test:
	$(PYTHON) pytest

check:
	$(PYTHON) flake8
	$(PYTHON) mypy .
	$(PYTHON) bento check
	$(PYTHON) pytest

# init DB
init-db: idb
idb: dropcreatedb flask-init-db seed

dropcreatedb:
	dropdb supbackend --if-exists
	createdb supbackend

flask-init-db:
	flask init-db