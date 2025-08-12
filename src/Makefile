# Makefile for Emmett KiCad Plugin
# This creates a ZIP package that can be installed via KiCad Plugin and Content Manager

# Plugin information
PLUGIN_NAME = emmett
PLUGIN_VERSION = 1.0.0
PLUGIN_AUTHOR = Your Name
PLUGIN_DESCRIPTION = Route PCB elements with Emmett Element Router

# Build directory (separate from source)
BUILD_DIR = ../build
PLUGIN_BUILD_DIR = $(BUILD_DIR)/$(PLUGIN_NAME)

# Source files to include in the package
PLUGIN_CONTENTS = metadata.json plugins resources
PLUGIN_FILES = $(wildcard plugins/*.py) $(wildcard plugins/*.png) $(wildcard resources/*)

# Output ZIP file (in build directory)
ZIP_FILE = $(BUILD_DIR)/$(PLUGIN_NAME)-$(PLUGIN_VERSION).zip

# Default target
all: package

# Create build directory structure for development
build-dir:
	@echo "Creating build directory structure..."
	@mkdir -p $(BUILD_DIR)
	@echo "Build directory created: $(BUILD_DIR)"

# Create the distributable ZIP package
package: $(ZIP_FILE)

$(ZIP_FILE): $(PLUGIN_FILES)
	@echo "Creating Emmett plugin package: $(ZIP_FILE)"
	@mkdir -p $(BUILD_DIR)
	@rm -f $(ZIP_FILE)
	@zip -r -x@exclude.lst $(ZIP_FILE) $(PLUGIN_CONTENTS)
	@echo "Package created: $(ZIP_FILE)"
	@echo "You can now install Emmett via KiCad Plugin and Content Manager"

# Clean up generated files
clean:
	@echo "Cleaning up build directory..."
	@rm -rf $(BUILD_DIR)
	@echo "Clean complete"

# Run tests
test:
	@echo "Running tests..."
	@cd .. && python3 tests/run_tests.py

# Run tests with pytest (if available)
test-pytest:
	@echo "Running tests with pytest..."
	@cd .. && python3 -m pytest tests/ -v

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	@pip install -r ../requirements-dev.txt

# Code quality checks
lint:
	@echo "Running code quality checks..."
	@cd .. && python3 -m flake8 src/ tests/
	@cd .. && python3 -m black --check src/ tests/
	@cd .. && python3 -m isort --check-only src/ tests/

# Format code
format:
	@echo "Formatting code..."
	@cd .. && python3 -m black src/ tests/
	@cd .. && python3 -m isort src/ tests/

# Show build directory contents
show-build:
	@echo "Build directory contents:"
	@if [ -d "$(BUILD_DIR)" ]; then \
		ls -la $(BUILD_DIR); \
	else \
		echo "Build directory does not exist yet. Run 'make package' first."; \
	fi

# Show help
help:
	@echo "Available targets:"
	@echo "  all        - Create the plugin package (default)"
	@echo "  build-dir  - Create build directory structure"
	@echo "  package    - Create the distributable ZIP file"
	@echo "  install    - Install plugin directly to KiCad (requires KICAD_PLUGIN_DIR)"
	@echo "  uninstall  - Remove plugin from KiCad"
	@echo "  clean      - Remove build directory and all generated files"
	@echo "  test       - Run tests with custom test runner"
	@echo "  test-pytest- Run tests with pytest (if available)"
	@echo "  install-dev- Install development dependencies"
	@echo "  lint       - Run code quality checks"
	@echo "  format     - Format code with black and isort"
	@echo "  show-build - Show contents of build directory"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "Environment variables:"
	@echo "  KICAD_PLUGIN_DIR - Path to KiCad plugin directory"
	@echo ""
	@echo "Example usage:"
	@echo "  make build-dir                  # Create build directory structure"
	@echo "  make package                    # Create ZIP file in ../build/"
	@echo "  make show-build                 # Show build directory contents"
	@echo "  make test                       # Run tests"
	@echo "  make install-dev                # Install development tools"
	@echo "  make format                     # Format code"
	@echo "  export KICAD_PLUGIN_DIR=~/.local/share/kicad/9.0/scripting/plugins"
	@echo "  make install                    # Install for testing"
	@echo "  make uninstall                  # Remove after testing"
	@echo "  make clean                      # Clean build directory"

.PHONY: all build-dir package install uninstall clean test test-pytest install-dev lint format show-build help
