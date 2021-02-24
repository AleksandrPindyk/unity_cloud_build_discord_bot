TAG ?= latest
CONTAINER_NAME ?= unity_cloud_build_discord_bot
IMAGE_NAME ?= $(CONTAINER_NAME):$(TAG)

build:
	docker build . -t $(IMAGE_NAME)

up: build
	docker run -d \
	--name $(CONTAINER_NAME) \
	--env-file .env \
	$(IMAGE_NAME)

down:
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)
