#!/bin/bash

# Elastic Vale Style Guide Installation Script for Linux
# This script installs Vale and configures it to use the Elastic style guide

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_error() {
    echo -e "${RED}Error: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_info() {
    echo -e "${YELLOW}$1${NC}"
}

# 1. Detect Linux
print_info "Checking operating system..."
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "This script is designed for Linux only. Current OS: $OSTYPE"
    exit 1
fi
print_success "✓ Running on Linux"

# 2. Check if Vale is already installed
print_info "Checking for existing Vale installation..."
if command -v vale &> /dev/null; then
    VALE_VERSION=$(vale --version)
    print_success "✓ Vale is already installed: $VALE_VERSION"
    VALE_ALREADY_INSTALLED=true
else
    print_info "Vale not found, will install it"
    VALE_ALREADY_INSTALLED=false
fi

# 3. If Vale is not installed, install it
if [ "$VALE_ALREADY_INSTALLED" = false ]; then
    print_info "Installing Vale..."
    
    # Try to detect package manager and install
    if command -v snap &> /dev/null; then
        print_info "Installing Vale via snap..."
        if sudo snap install vale; then
            print_success "✓ Vale installed successfully via snap"
        else
            print_error "Failed to install Vale via snap"
            echo "You can also install Vale manually from: https://vale.sh/docs/vale-cli/installation/"
            exit 1
        fi
    elif command -v apt-get &> /dev/null; then
        print_info "Detected Debian/Ubuntu system"
        print_info "Downloading Vale binary..."
        VALE_VERSION="3.12.0"
        wget -O vale.tar.gz "https://github.com/errata-ai/vale/releases/download/v${VALE_VERSION}/vale_${VALE_VERSION}_Linux_64-bit.tar.gz"
        sudo tar -xvzf vale.tar.gz -C /usr/local/bin vale
        rm vale.tar.gz
        print_success "✓ Vale installed successfully"
    elif command -v dnf &> /dev/null; then
        print_info "Detected Fedora/RHEL system"
        print_info "Downloading Vale binary..."
        VALE_VERSION="3.12.0"
        wget -O vale.tar.gz "https://github.com/errata-ai/vale/releases/download/v${VALE_VERSION}/vale_${VALE_VERSION}_Linux_64-bit.tar.gz"
        sudo tar -xvzf vale.tar.gz -C /usr/local/bin vale
        rm vale.tar.gz
        print_success "✓ Vale installed successfully"
    else
        print_error "Could not detect package manager"
        echo "Please install Vale manually from: https://vale.sh/docs/vale-cli/installation/"
        exit 1
    fi

    # Verify installation
    print_info "Verifying Vale installation..."
    if command -v vale &> /dev/null; then
        VALE_VERSION=$(vale --version)
        print_success "✓ Vale is installed: $VALE_VERSION"
    else
        print_error "Vale installation verification failed"
        exit 1
    fi
fi

# 4. Set up XDG directories
# XDG_DATA_HOME defaults to ~/.local/share if not set
XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"

VALE_DATA_DIR="$XDG_DATA_HOME/vale"
VALE_CONFIG_DIR="$XDG_CONFIG_HOME/vale"
VALE_CONFIG_FILE="$VALE_CONFIG_DIR/.vale.ini"

# 5. Clean existing Vale installation
print_info "Cleaning existing Vale installation..."
if [ -d "$VALE_DATA_DIR" ]; then
    print_info "Removing existing Vale data directory: $VALE_DATA_DIR"
    if rm -rf "$VALE_DATA_DIR"; then
        print_success "✓ Existing Vale data cleaned"
    else
        print_error "Failed to clean existing Vale data"
        exit 1
    fi
else
    print_info "No existing Vale data found"
fi

if [ -d "$VALE_CONFIG_DIR" ]; then
    print_info "Removing existing Vale config directory: $VALE_CONFIG_DIR"
    if rm -rf "$VALE_CONFIG_DIR"; then
        print_success "✓ Existing Vale config cleaned"
    else
        print_error "Failed to clean existing Vale config"
        exit 1
    fi
else
    print_info "No existing Vale config found"
fi

# 6. Create Vale configuration directory and file
print_info "Setting up Vale configuration..."
mkdir -p "$VALE_CONFIG_DIR"

# Create the .vale.ini file
print_info "Creating new configuration at $VALE_CONFIG_FILE..."

# Create minimal .vale.ini - the package will provide the full config via merge
cat > "$VALE_CONFIG_FILE" << 'EOF'
StylesPath = styles

Packages = https://github.com/elastic/vale-rules/releases/latest/download/elastic-vale.zip
EOF

print_success "✓ Vale configuration created at: $VALE_CONFIG_FILE"

# 7. Download and install Elastic style package
print_info "Downloading and installing Elastic style package..."
if vale --config="$VALE_CONFIG_FILE" sync; then
    print_success "✓ Elastic styles package downloaded and installed successfully"
else
    print_error "Failed to sync Vale styles package"
    exit 1
fi

# 8. Verify that the installed styles are accessible
VALE_STYLES_DIR="$XDG_DATA_HOME/vale/styles"
print_info "Verifying installed style guide..."
if [ -d "$VALE_STYLES_DIR/Elastic" ] && ls "$VALE_STYLES_DIR/Elastic"/*.yml > /dev/null 2>&1; then
    # Check if VERSION file exists and read it
    if [ -f "$VALE_STYLES_DIR/Elastic/VERSION" ]; then
        INSTALLED_VERSION=$(cat "$VALE_STYLES_DIR/Elastic/VERSION")
        print_success "✓ Elastic styles installed and accessible (version: $INSTALLED_VERSION)"
    else
        print_success "✓ Elastic styles installed and accessible"
    fi
else
    print_error "Elastic styles verification failed"
    exit 1
fi

# 9. Final verification
print_info "Performing final verification..."
if vale --config="$VALE_CONFIG_FILE" --help &> /dev/null; then
    print_success "✓ Vale configuration is valid"
else
    print_error "Vale configuration verification failed"
    exit 1
fi

# 10. Success message
echo
print_success "🎉 Installation completed successfully!"
echo
if [ -n "$INSTALLED_VERSION" ]; then
    echo "Elastic Vale Style Guide version: $INSTALLED_VERSION"
    echo
fi
echo "Vale is now configured with the Elastic style guide. You can:"
echo "  • Run 'vale <file>' to check a specific file"
echo "  • Run 'vale <directory>' to check all supported files in a directory"
echo
echo "Configuration file location: $VALE_CONFIG_FILE"
echo "Styles installed to: $VALE_STYLES_DIR/Elastic"
echo
echo "To update the styles in the future:"
echo "  • Re-run this script, or"
echo "  • Run 'vale --config=\"$VALE_CONFIG_FILE\" sync' to update to the latest package"

