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
