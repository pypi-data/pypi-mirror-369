.DEFAULT_GOAL := help

###### Development

build-pythonpackage: ## Build the python package for upload to pypi
	find . -type d -name "dist" -exec rm -rf {} +
	hatch build

push-pythonpackage: ## Push python package to pypi
	hatch publish

lint: ## Fix linting issues
	@ruff check --fix .

format: ## Format code
	@ruff format .

###### Other

clean: ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +


ESCAPE = 
help: ## Print this help
	@grep -E '^([a-zA-Z_-]+:.*?## .*|######* .+)$$' Makefile \
		| sed 's/######* \(.*\)/@               $(ESCAPE)[1;31m\1$(ESCAPE)[0m/g' | tr '@' '\n' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'
