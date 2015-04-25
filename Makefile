# create virtual environment
PATH := .env/bin:$(PATH)

.env:
	virtualenv .env

# install all needed for development
develop: .env
	pip install -e .[test] tox coveralls

# clean the development envrironment
clean:
	-rm -rf .env
