# Blite Tracing Makefile
# Simple build, test, and publish automation

.PHONY: help clean build test format check install install-dev publish pkgtest version-patch version-minor version-major release

# Default target
.DEFAULT_GOAL := help

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install package dependencies
	uv sync --no-dev

install-dev: ## Install with development dependencies
	uv sync

test: ## Run tests
	@if [ -d "tests/" ]; then \
		uv run pytest tests/ -v; \
	else \
		echo "No tests found. Create tests/ directory and add test files."; \
	fi

format: ## Format code with ruff
	uv run ruff format src/

check: format test ## Run formatting and tests
	uv run ruff check src/

clean: ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info/ .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean ## Build the package
	uv build
	@ls -la dist/

publish: ## Publish to PyPI
	@if [ ! -d "dist/" ] || [ -z "$$(ls -A dist/ 2>/dev/null)" ]; then \
		echo "❌ No build artifacts found. Run 'make build' first."; \
		exit 1; \
	fi
	@echo "Publishing version: $$(grep '^version = ' pyproject.toml | cut -d'"' -f2)"; \
	echo "Type 'publish' to confirm publishing to PyPI, or anything else to cancel:"; \
	read -p "> " confirm; \
	if [ "$$confirm" = "publish" ]; then \
		uv publish; \
	else \
		echo "❌ Publish cancelled. You typed: '$$confirm'"; \
		exit 1; \
	fi

pkgtest: ## Test package installation from PyPI
	@echo "Testing package installation from PyPI..."
	@python3 -m venv /tmp/blite-tracing-test || true
	@/tmp/blite-tracing-test/bin/pip install --upgrade pip
	@/tmp/blite-tracing-test/bin/pip install blite-tracing
	@/tmp/blite-tracing-test/bin/python -c "import blite_tracing; print('✓ Import successful'); print('✓ Available functions:', ', '.join([f for f in dir(blite_tracing) if not f.startswith('_')])); print('✓ Version:', blite_tracing.__version__)"
	@rm -rf /tmp/blite-tracing-test
	@echo "✓ Package test completed successfully!"

version-patch: ## Bump patch version (0.1.0 -> 0.1.1)
	@CURRENT_VERSION=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
	NEW_VERSION=$$(python3 -c "import sys; v=sys.argv[1].split('.'); v[2]=str(int(v[2])+1); print('.'.join(v))" $$CURRENT_VERSION); \
	sed -i "s/version = \".*\"/version = \"$$NEW_VERSION\"/" pyproject.toml; \
	sed -i "s/__version__ = \".*\"/__version__ = \"$$NEW_VERSION\"/" src/blite_tracing/__init__.py; \
	echo "Version updated to: $$NEW_VERSION"

version-minor: ## Bump minor version (0.1.0 -> 0.2.0)
	@CURRENT_VERSION=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
	NEW_VERSION=$$(python3 -c "import sys; v=sys.argv[1].split('.'); v[1]=str(int(v[1])+1); v[2]='0'; print('.'.join(v))" $$CURRENT_VERSION); \
	sed -i "s/version = \".*\"/version = \"$$NEW_VERSION\"/" pyproject.toml; \
	sed -i "s/__version__ = \".*\"/__version__ = \"$$NEW_VERSION\"/" src/blite_tracing/__init__.py; \
	echo "Version updated to: $$NEW_VERSION"

version-major: ## Bump major version (0.1.0 -> 1.0.0)
	@CURRENT_VERSION=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
	NEW_VERSION=$$(python3 -c "import sys; v=sys.argv[1].split('.'); v[0]=str(int(v[0])+1); v[1]='0'; v[2]='0'; print('.'.join(v))" $$CURRENT_VERSION); \
	sed -i "s/version = \".*\"/version = \"$$NEW_VERSION\"/" pyproject.toml; \
	sed -i "s/__version__ = \".*\"/__version__ = \"$$NEW_VERSION\"/" src/blite_tracing/__init__.py; \
	echo "Version updated to: $$NEW_VERSION"

release: ## Complete release workflow: version → format → build → publish → test
	@echo "🚀 Starting complete release workflow..."
	@echo ""
	@echo "🔐 Checking PyPI authentication..."
	@if [ -z "$$UV_PUBLISH_TOKEN" ] && [ -z "$$TWINE_PASSWORD" ] && [ -z "$$PYPI_TOKEN" ]; then \
		echo "❌ PyPI token not found."; \
		echo "   Set one of these environment variables:"; \
		echo "   export UV_PUBLISH_TOKEN=your-token-here"; \
		echo "   export PYPI_TOKEN=your-token-here"; \
		echo "   export TWINE_PASSWORD=your-token-here"; \
		echo "   Get your token at: https://pypi.org/manage/account/token/"; \
		exit 1; \
	fi
	@echo "✅ PyPI authentication configured"
	@echo ""
	@echo "Current version: $$(grep '^version = ' pyproject.toml | cut -d'"' -f2)"
	@echo "Choose version bump:"
	@echo "  1) Patch (bug fixes)"
	@echo "  2) Minor (new features)"
	@echo "  3) Major (breaking changes)"
	@echo "  4) Skip version bump"
	@read -p "Enter choice (1-4): " choice; \
	case $$choice in \
		1) make version-patch ;; \
		2) make version-minor ;; \
		3) make version-major ;; \
		4) echo "Skipping version bump..." ;; \
		*) echo "Invalid choice, exiting..." && exit 1 ;; \
	esac
	@echo ""
	@echo "📦 New version: $$(grep '^version = ' pyproject.toml | cut -d'"' -f2)"
	@echo ""
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf dist/ build/ *.egg-info/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo ""
	@echo "🎨 Formatting code..."
	@make format
	@echo ""
	@echo "📚 Installing dependencies..."
	@make install-dev
	@echo ""
	@echo "🔨 Building package..."
	@uv build
	@ls -la dist/
	@echo ""
	@echo "📤 Publishing to PyPI..."
	@make publish
	@echo ""
	@echo "🧪 Testing published package..."
	@make pkgtest
	@echo ""
	@echo "✅ Release complete! Version $$(grep '^version = ' pyproject.toml | cut -d'"' -f2) is now live on PyPI."
	@echo ""
	@echo "📋 Checking git status..."
	@git status --porcelain
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "⚠️  Ruff may have made changes to files. Review and push changes to master:"; \
		echo "   git add ."; \
		echo "   git commit -m 'Auto-format code with ruff'"; \
		echo "   git push origin master"; \
	else \
		echo "✅ No file changes detected."; \
	fi
