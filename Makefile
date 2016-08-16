.PHONY: test

test:
	`which python` `which nosetests` -s -v --with-coverage --cover-package=viking viking/tests --cover-branches
