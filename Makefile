PWD				= $(shell pwd)
USER			= $(shell whoami)
USER_ID			= $(shell id -u $(USER))
GIT_BRANCH		= $(shell git branch --show-current)

ifeq ($(GIT_BRANCH), 'main')
LOCALPORT		= 8000
CONTAINER_NAME	= su-blog
else
LOCALPORT		= 8888
CONTAINER_NAME	= dev-su-blog
endif

DOCKER_RUN		= docker run --rm -v $(PWD)/src/:/data
DOCKER_IMAGE	= su_blog_nikola:$(USER)

.PHONY: start build test

build:
	@docker build --build-arg UID=$(USER_ID) -q -t $(DOCKER_IMAGE) .ci/

test: build
	$(DOCKER_RUN) --entrypoint rst-lint $(DOCKER_IMAGE) --level info posts/ pages/
	$(DOCKER_RUN) --entrypoint pyspelling $(DOCKER_IMAGE)

start: build
	@test -d src/output || mkdir $(PWD)/src/output
	@docker stop $(CONTAINER_NAME)
	@$(DOCKER_RUN) $(DOCKER_IMAGE) build
	@$(DOCKER_RUN) -p $(LOCALPORT):8000 --name $(CONTAINER_NAME) $(DOCKER_IMAGE) serve --browser

console: build
	$(DOCKER_RUN) -it --entrypoint /bin/sh $(DOCKER_IMAGE)
