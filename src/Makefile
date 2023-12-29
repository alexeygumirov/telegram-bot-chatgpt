PYTHON_VERSION=3.11
PYTHON=python$(PYTHON_VERSION)
VIRTUAL_ENV=.venv
VIRTUAL_ENV_ACTIVATE=$(VIRTUAL_ENV)/bin/activate
APP_FILE=app/telegram_bot.py
REQUIREMENTS_FILE=app/requirements.txt
DEV_REQUIREMENTS_FILE=app/requirements-dev.txt
VERSION_FILE=app/VERSION
VERSION=$(shell cat $(VERSION_FILE))
SOURCE_IMAGE=$(shell sed -n '/FROM /p' Dockerfile | sed 's/FROM //')

.DEFAULT_GOAL := build

check_python_version:
	@echo "Checking python version..."
	@which $(PYTHON) > /dev/null || (echo "Python $(PYTHON_VERSION) not found. Please install it." && exit 1)

check_docker:
	@echo "Checking docker..."
	@which docker > /dev/null || (echo "Docker not found. Please install it." && exit 1)

$(VIRTUAL_ENV_ACTIVATE): check_python_version
	@if [ ! -d $(VIRTUAL_ENV_ACTIVATE) ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VIRTUAL_ENV); \
	fi

activate-venv: $(VIRTUAL_ENV_ACTIVATE)
	@echo "Activating virtual environment..."
	@. $(VIRTUAL_ENV_ACTIVATE)

install-requirements: activate-venv $(REQUIREMENTS_FILE)
	@echo "Installing requirements..."
	@$(VIRTUAL_ENV)/bin/pip install -U pip
	@$(VIRTUAL_ENV)/bin/pip install -U -r $(REQUIREMENTS_FILE)

install-dev-requirements: install-requirements $(DEV_REQUIREMENTS_FILE)
	@echo "Installing dev requirements..."
	@$(VIRTUAL_ENV)/bin/pip install -U pip
	@$(VIRTUAL_ENV)/bin/pip install -U -r $(DEV_REQUIREMENTS_FILE)

build: check_docker $(VERSION_FILE) 
	@echo "Building..."
	@docker build --no-cache --tag telegram_bot:$(VERSION) .

build-latest: check_docker $(VERSION_FILE)
	@echo "Building..."
	@docker build --no-cache --tag telegram_bot --tag telegram_bot:$(VERSION) .

clean-environment:
	@echo "Cleaning..."
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@rm -rf $(VIRTUAL_ENV)

clean-docker:
	@echo "Cleaning docker..."
	@docker rmi -f telegram_bot:$(VERSION)
	@docker rmi -f telegram_bot:latest

clean-all: clean-environment clean-docker
	@echo "Cleaning all..."
	@docker rmi -f $(SOURCE_IMAGE)

.PHONY: check_python_version check_docker clean-environment clean-docker
