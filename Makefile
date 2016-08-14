.PHONY: test

test:
	env -i nosetests -s -v viking/tests/
