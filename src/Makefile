# Makefile for Emmett KiCad Plugin
# This creates a ZIP package that can be installed via KiCad Plugin and Content Manager

# Plugin information
PLUGIN_NAME = emmett
PLUGIN_VERSION = 1.0.0
PLUGIN_AUTHOR = Your Name
PLUGIN_DESCRIPTION = Route PCB elements with Emmett Element Router

# Files to include in the package
#PLUGIN_FILES = __init__.py emmett_action.py emmett_dialog.py emmett_icon.png metadata.json
PLUGIN_FILES=metadata.json plugins resources

# Output ZIP file
ZIP_FILE = $(PLUGIN_NAME)-$(PLUGIN_VERSION).zip

# Default target
all: package

# Create the distributable ZIP package
package: $(ZIP_FILE)

$(ZIP_FILE): $(PLUGIN_FILES)
	@echo "Creating Emmett plugin package: $(ZIP_FILE)"
	@rm -f $(ZIP_FILE)
	@zip -r $(ZIP_FILE) $(PLUGIN_FILES)
	@echo "Package created: $(ZIP_FILE)"
	@echo "You can now install Emmett via KiCad Plugin and Content Manager"

# Clean up generated files
clean:
	@echo "Cleaning up..."
	@rm -f $(ZIP_FILE)
	@echo "Clean complete"

# Install plugin directly to KiCad (for development/testing)
# Note: This requires setting KICAD_PLUGIN_DIR environment variable
install: $(ZIP_FILE)
	@if [ -z "$(KICAD_PLUGIN_DIR)" ]; then \
		echo "Error: KICAD_PLUGIN_DIR environment variable not set"; \
		echo "Set it to your KiCad plugin directory (e.g., ~/.local/share/kicad/9.0/scripting/plugins)"; \
		exit 1; \
	fi
	@echo "Installing plugin to $(KICAD_PLUGIN_DIR)"
	@mkdir -p "$(KICAD_PLUGIN_DIR)/$(PLUGIN_NAME)"
	@cp $(PLUGIN_FILES) "$(KICAD_PLUGIN_DIR)/$(PLUGIN_NAME)/"
	@echo "Plugin installed successfully"

# Uninstall plugin
uninstall:
	@if [ -z "$(KICAD_PLUGIN_DIR)" ]; then \
		echo "Error: KICAD_PLUGIN_DIR environment variable not set"; \
		exit 1; \
	fi
	@echo "Uninstalling plugin from $(KICAD_PLUGIN_DIR)"
	@rm -rf "$(KICAD_PLUGIN_DIR)/$(PLUGIN_NAME)"
	@echo "Plugin uninstalled successfully"

# Show help
help:
	@echo "Available targets:"
	@echo "  all        - Create the plugin package (default)"
	@echo "  package    - Create the distributable ZIP file"
	@echo "  install    - Install plugin directly to KiCad (requires KICAD_PLUGIN_DIR)"
	@echo "  uninstall  - Remove plugin from KiCad"
	@echo "  clean      - Remove generated files"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "Environment variables:"
	@echo "  KICAD_PLUGIN_DIR - Path to KiCad plugin directory"
	@echo ""
	@echo "Example usage:"
	@echo "  make package                    # Create ZIP file"
	@echo "  export KICAD_PLUGIN_DIR=~/.local/share/kicad/9.0/scripting/plugins"
	@echo "  make install                    # Install for testing"
	@echo "  make uninstall                  # Remove after testing"

.PHONY: all package install uninstall clean help
