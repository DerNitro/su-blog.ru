PWD		= $(shell pwd)
USER	= $(shell whoami)

.PHONY: start build test

build:
	@docker build -q -t su_blog_nikola .ci/

test: build
	docker run --rm -v $(PWD)/src/:/data --entrypoint rst-lint su_blog_nikola --level info posts/ pages/
	docker run --rm -v $(PWD)/src/:/data --entrypoint pyspelling su_blog_nikola

start: build
	@test -d src/output || mkdir $(PWD)/src/output
	@docker run --rm -v $(PWD)/src/:/data su_blog_nikola build
	@docker run --rm -v $(PWD)/src/:/data -p 8000:8000 su_blog_nikola serve --browser
