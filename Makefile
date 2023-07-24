PWD		= $(shell pwd)
USER	= $(shell whoami)

.PHONY: start build 

build:
	@docker build -q -t su_blog_nikola .ci/

start: build
	@test -d src/output || mkdir $(PWD)/src/output
	@docker run --rm -v $(PWD)/src/:/data su_blog_nikola build
	@docker run --rm -v $(PWD)/src/:/data -p 8000:8000 su_blog_nikola serve --browser
