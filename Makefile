.PHONY: clean-pyc clean-build docs

clean: clean-build clean-pyc


clean-build:
	rm -fr deploy/
	rm -fr build/
	rm -fr dist/
	rm -fr test/build/
	rm -fr *.egg-info


clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

docs:
	git submodule init
	git submodule update
	$(MAKE) -C docs html


install: clean-build clean-pyc
	python setup.py install

test: clean-build
	nosetests -v

format:
	unify --in-place `find liquidluck -type f -name '*.py' | grep -v __pycache__ | grep -v pb2`
	yapf -i `find liquidluck -type f -name '*.py' | grep -v __pycache__ | grep -v pb2`
	isort -rc `find liquidluck -type f -name '*.py' | grep -v __pycache__ | grep -v pb2`

check:
	flake8 --exclude=rpc --ignore E501,F403,F401 liquidluck

