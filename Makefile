.PHONY: install test

# install dependencies for development
install:
	python -m pip install -e '.[dev]'

# run tests with pytest
test:
	pytest tests --maxfail=1 --disable-warnings -q