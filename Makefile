run-back:
	python start.py

init-data:
	@python -m app.initial_data

remove-test-data:
	@python -m app.remove_test_data

remove-test-data-initial:
	@python -m app.remove_test_data

start-rabbitmq:
	docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.11-management

pre-start:
	python -m app.celeryworker_pre_start
	celery -A "app.worker" worker                                                                      
	python -m app.backend_pre_start
	python -m app.tests_pre_start

start-docker:	stop-docker
	docker-compose -f compose/compose.yml up -d	
	docker-compose -f compose/compose.yml up -d		

stop-docker:
	docker-compose -f compose/compose.yml down 

test:	init-data remove-test-data-initial clean-cache pytest	remove-test-data

pytest:
	@pytest -m "not draft" -vv 

generate-func:
	pytest --generate-missing --feature _docs/funcionalidades/util/*.feature > _docs/draft/util_feature_draft.txt
	pytest --generate-missing --feature _docs/funcionalidades/backend/*.feature > _docs/draft/backend_feature_draft.txt

lint: format
	@black app --check
	@flake8 app

mypy:
	@mypy app

format:
	@autopep8 . -r --in-place
	@isort --force-single-line-imports .
	@autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place . 
	@isort .
	@black .

coverage:
	rm -Rf htmlcov
	pytest --cov -s
	coverage report -m
	coverage html 

qa:	remove-test-data-initial clean-cache format lint coverage remove-test-data 

clean-cache:
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$\)" | xargs rm -rf
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache