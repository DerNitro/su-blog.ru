PWD				= $(shell pwd)
USER			= $(shell whoami)
USER_ID			= $(shell id -u $(USER))
GIT_BRANCH		= $(shell git branch --show-current)

ifeq ($(GIT_BRANCH), main)
LOCAL_PORT		= 8000
CONTAINER_NAME	= su-blog
URL				= https://su-blog.ru
else
LOCAL_PORT		= 8888
CONTAINER_NAME	= dev-su-blog
URL				= https://dev.su-blog.ru
endif

ifneq ($(USER), blog)
URL				= http://127.0.0.1:8888/
endif

DOCKER_RUN      = docker run --rm -v $(PWD)/src/:/data
DOCKER_IMAGE    = su_blog_nikola:$(USER)

.PHONY: start build test stop console

build:
	docker build --build-arg UID=$(USER_ID) -t $(DOCKER_IMAGE) .ci/
	$(DOCKER_RUN) --entrypoint rst-lint $(DOCKER_IMAGE) --level info posts/ pages/
	$(DOCKER_RUN) $(DOCKER_IMAGE) build -a

test: build
	$(DOCKER_RUN) --entrypoint pyspelling $(DOCKER_IMAGE) -v

start: build stop
	@test -d $(PWD)/src/output || mkdir $(PWD)/src/output
	@CONTAINER_NAME=$(CONTAINER_NAME) LOCAL_PORT=$(LOCAL_PORT) docker compose up -d
	@/bin/echo "Site available url $(URL)"

stop:
	@CONTAINER_NAME=$(CONTAINER_NAME) LOCAL_PORT=$(LOCAL_PORT) docker compose down

console: build
	$(DOCKER_RUN) -it --entrypoint /bin/bash $(DOCKER_IMAGE)
