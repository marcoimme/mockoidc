.PHONY: help install test run demo docker-build docker-run docker-stop clean

# Variables
IMAGE_NAME = marcoimme/oidcmock
IMAGE_TAG = latest
CONTAINER_NAME = mockoidc
PORT = 8080
DEMO_PORT = 8081

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with uv
	uv sync

test: ## Run tests
	uv run pytest --tb=short -v

test-quick: ## Run tests in quiet mode
	uv run pytest --tb=no -q

run: ## Run the application locally with Python
	uv run python main.py

demo: ## Start both mock OIDC server and demo callback server
	@echo "Starting Mock OIDC Server on port $(PORT)..."
	@uv run python main.py & echo $$! > .mockoidc.pid
	@sleep 2
	@echo "Starting Demo Callback Server on port $(DEMO_PORT)..."
	@uv run python demo/callback_server.py & echo $$! > .demo.pid
	@echo ""
	@echo "✅ Servers started!"
	@echo "   Mock OIDC: http://localhost:$(PORT)"
	@echo "   Demo App:  http://localhost:$(DEMO_PORT)"
	@echo ""
	@echo "To stop: make demo-stop"

demo-stop: ## Stop demo servers
	@if [ -f .mockoidc.pid ]; then \
		kill `cat .mockoidc.pid` 2>/dev/null || true; \
		rm .mockoidc.pid; \
		echo "Mock OIDC server stopped"; \
	fi
	@if [ -f .demo.pid ]; then \
		kill `cat .demo.pid` 2>/dev/null || true; \
		rm .demo.pid; \
		echo "Demo callback server stopped"; \
	fi

docker-build: ## Build Docker image
	docker buildx build --network=host -t $(IMAGE_NAME):$(IMAGE_TAG) .

docker-run: ## Run Docker container after local build
	@echo "Starting Docker container..."
	@docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(PORT):$(PORT) \
		$(IMAGE_NAME):$(IMAGE_TAG)
	@echo "Container started: $(CONTAINER_NAME)"
	@echo "Waiting for server to be ready..."
	@sleep 3
	@docker logs $(CONTAINER_NAME)
	@echo ""
	@echo "✅ Mock OIDC Server running at http://localhost:$(PORT)"
	@echo "   Discovery: http://localhost:$(PORT)/.well-known/openid-configuration"
	@echo ""
	@echo "To view logs: docker logs -f $(CONTAINER_NAME)"
	@echo "To stop:      make docker-stop"

docker-stop: ## Stop and remove Docker container
	@docker rm -f $(CONTAINER_NAME) 2>/dev/null || true
	@echo "Container stopped and removed"

docker-logs: ## Show Docker container logs
	docker logs -f $(CONTAINER_NAME)

docker-shell: ## Open shell in running container
	docker exec -it $(CONTAINER_NAME) /bin/sh

docker-test: docker-build docker-run ## Build and run Docker container
	@echo "Testing endpoints..."
	@sleep 2
	@curl -f http://localhost:$(PORT)/health || (make docker-stop && exit 1)
	@curl -f http://localhost:$(PORT)/.well-known/openid-configuration || (make docker-stop && exit 1)
	@echo ""
	@echo "✅ All tests passed!"

clean: ## Clean up temporary files and containers
	@rm -f .mockoidc.pid .demo.pid
	@docker rm -f $(CONTAINER_NAME) 2>/dev/null || true
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup completed"

lock: ## Update dependency lock file
	uv lock

upgrade: ## Upgrade dependencies
	uv lock --upgrade

format: ## Format code with ruff
	uv run ruff format .

lint: ## Lint code with ruff
	uv run ruff check .

all: install test docker-build docker-run ## Install, test, build and run
