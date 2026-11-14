PWD				= $(shell pwd)
USER			= $(shell whoami)
USER_ID			= $(shell id -u $(USER))

ifeq ($(BLOG_ENV), prod)
LOCAL_PORT		= 8000
REACTIONS_PORT	= 8082
CONTAINER_NAME	= su-blog
URL				= https://su-blog.ru
REACTIONS_VOLUME_SOURCE = $(PWD)/data
else
LOCAL_PORT		= 8888
REACTIONS_PORT	= 8083
CONTAINER_NAME	= dev-su-blog
URL				= https://dev.su-blog.ru
REACTIONS_VOLUME_SOURCE = /tmp/su-blog-ru-data
endif

ifneq ($(USER), blog)
LOCAL_PORT		= 8888
REACTIONS_PORT	= 8083
URL				= http://127.0.0.1:8888/
REACTIONS_VOLUME_SOURCE = /tmp/su-blog-ru-data
endif

DOCKER_RUN      = docker run --rm -v $(PWD)/src/:/data
DOCKER_IMAGE    = su_blog_nikola:$(USER)

.PHONY: start build test stop console clean

docker:
	@CONTAINER_NAME=$(CONTAINER_NAME) LOCAL_PORT=$(LOCAL_PORT) REACTIONS_PORT=$(REACTIONS_PORT) USER_ID=$(USER_ID) REACTIONS_VOLUME_SOURCE=$(REACTIONS_VOLUME_SOURCE) docker compose build

clean:
	-rm src/.doit.db
	-rm -rf src/__pycache__
	-rm -rf src/cache
	-rm -rf src/output
	-rm -rf /tmp/su-blog-ru-data

build: docker
	$(DOCKER_RUN) --entrypoint rst-lint $(DOCKER_IMAGE) --level info posts/ pages/
	$(DOCKER_RUN) -e REACTIONS_PORT=$(REACTIONS_PORT) $(DOCKER_IMAGE) build

test: stop clean build
	$(DOCKER_RUN) --entrypoint pyspelling $(DOCKER_IMAGE) -v

start: build
	@test -d $(PWD)/src/output || mkdir $(PWD)/src/output
	@mkdir -p $(REACTIONS_VOLUME_SOURCE)
	@CONTAINER_NAME=$(CONTAINER_NAME) LOCAL_PORT=$(LOCAL_PORT) REACTIONS_PORT=$(REACTIONS_PORT) USER_ID=$(USER_ID) REACTIONS_VOLUME_SOURCE=$(REACTIONS_VOLUME_SOURCE) docker compose up -d
	@/bin/echo "Site available url $(URL)"

stop:
	@CONTAINER_NAME=$(CONTAINER_NAME) LOCAL_PORT=$(LOCAL_PORT) REACTIONS_PORT=$(REACTIONS_PORT) USER_ID=$(USER_ID) REACTIONS_VOLUME_SOURCE=$(REACTIONS_VOLUME_SOURCE) docker compose down

console: docker
	$(DOCKER_RUN) -it --entrypoint /bin/bash $(DOCKER_IMAGE)
