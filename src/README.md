# Emmett KiCad Plugin

Welcome to the Emmett Element Router - a comprehensive helper for routing heating element traces.

## Features

- Adds a button on the PCB Editor Toolbar.
- Opens a dialog for entering heating element design parameters
- Saves dialog state between sessions
- Comprehensive calculations based on high-level design goals like dimensions, input power, peak temperature, etc.
- Allowances for manufacturing variances - as much as is possible when asking a PCB manufacturer to make you a resistor!
- Automated fitting of the trace to meet the required resistance value - at least within the constraints of the physics of copper resistive elements.

## Requirements

- KiCad 9.0 or later
- Python 3.6+ (included with KiCad)

## Building the Plugin

### Option 1: Create ZIP Package (Recommended for Distribution)

```bash
cd src
make package
```

This creates `emmett-<version>.zip` which can be installed via KiCad's Plugin and Content Manager.

## Installation

1. Open KiCad
2. Go to Tools → Plugin and Content Manager
3. Click "Install Plugin"
4. Select the `emmett-<version>.zip` file
5. Restart KiCad

## Usage

1. Open a PCB file in KiCad
2. Look for the "Emmett" button in the toolbar
3. Click the button to open the parameter dialog
4. Enter your design parameters.
5. Click the go button.

## Development

### File Structure

- `__init__.py` - Plugin entry point
- `emmett_action.py` - Main plugin action class
- `emmett_dialog.py` - User interface dialog
- `emmett_icon.png` - Toolbar icon (24x24 or 32x32 recommended)
- `Makefile` - Build and installation automation

### Customizing the Dialog

TBA...

### Adding Element Routing Logic

TBA...

## Troubleshooting

TBA...

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
