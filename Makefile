### docker commands - START ###
build:
	docker-compose build

build-no-cache:
	docker-compose build --no-cache

up:
	docker-compose up -d

up-attached:
	docker-compose up

down:
	docker-compose down

down-remove-volumes:
	docker-compose down -v

show-logs-all:
	docker-compose logs

# show-logs svc=db
show-logs:
	docker-compose logs	$(svc)

run-cdk-container:
	docker-compose run --rm cdk bash
# docker-compose run --rm cdk sh -c "cdk init --language python"

deploy-cdk:
	docker-compose run --rm cdk sh -c "cdk deploy"

### docker commands - END ###

FILES = ../lambda/lambda_function.py ../lambda/extras app.py cdk/cdk_stack.py tests

### linting / test coverege / formating commands - START ###
flake8:
	docker-compose run --rm cdk sh -c "flake8 $(FILES)"

black-check:
	docker-compose run --rm cdk sh -c "black --check $(FILES)"

black-diff:
	docker-compose run --rm cdk sh -c "black --diff $(FILES)"

black:
	docker-compose run --rm cdk sh -c "black $(FILES)"

isort-check:
	docker-compose run --rm cdk sh -c "isort $(FILES) --check-only"

isort-diff:
	docker-compose run --rm cdk sh -c "isort $(FILES) --diff"

isort:
	docker-compose run --rm cdk sh -c "isort $(FILES)"

# runnign combined - black - isort - flake8
format:
	docker-compose run --rm cdk sh -c "black $(FILES) && isort $(FILES) && flake8 $(FILES)"
### linting / test coverege / formating commands - END ###