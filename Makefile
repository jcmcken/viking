.PHONY: test

test:
	env -i nosetests -s -v --with-coverage --cover-package=viking viking/tests
