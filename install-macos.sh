#!/bin/bash

# Elastic Vale Style Guide Installation Script for macOS
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

# 1. Detect macOS
print_info "Checking operating system..."
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only. Current OS: $OSTYPE"
    exit 1
fi
print_success "✓ Running on macOS"

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

# 3. If Vale is not installed, check for Homebrew and install Vale
if [ "$VALE_ALREADY_INSTALLED" = false ]; then
    print_info "Checking for Homebrew installation..."
    if ! command -v brew &> /dev/null; then
        print_error "Homebrew is not installed. Please install Homebrew first by running:"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    print_success "✓ Homebrew is installed"

    # Install Vale using Homebrew
    print_info "Installing Vale..."
    if brew install vale; then
        print_success "✓ Vale installed successfully"
    else
        print_error "Failed to install Vale"
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

# 4. Create or update Vale configuration directory and file
VALE_CONFIG_DIR="$HOME/Library/Application Support/vale"
VALE_CONFIG_FILE="$VALE_CONFIG_DIR/.vale.ini"

print_info "Setting up Vale configuration..."
mkdir -p "$VALE_CONFIG_DIR"

# Check if config file already exists
if [ -f "$VALE_CONFIG_FILE" ]; then
    print_info "Existing configuration found at $VALE_CONFIG_FILE - overwriting..."
else
    print_info "Creating new configuration at $VALE_CONFIG_FILE..."
fi

# Create or overwrite the .vale.ini file
cat > "$VALE_CONFIG_FILE" << 'EOF'
# Elastic Vale Style Guide Configuration
# This configuration uses the Elastic style guide package

# Download the Elastic style guide package
Packages = https://github.com/elastic/vale-style-guide/releases/download/latest/elastic-vale.zip

# Set minimum alert level
MinAlertLevel = suggestion

# Apply Elastic style guide to Markdown files
[*.md]
BasedOnStyles = Elastic

# Apply Elastic style guide to AsciiDoc files
[*.adoc]
BasedOnStyles = Elastic
EOF

print_success "✓ Vale configuration updated at: $VALE_CONFIG_FILE"

# 5. Run vale sync to download the style guide
print_info "Downloading Elastic style guide..."
if vale sync; then
    print_success "✓ Elastic style guide downloaded successfully"
else
    print_error "Failed to download Elastic style guide"
    exit 1
fi

# 6. Final verification
print_info "Performing final verification..."
if vale --config="$VALE_CONFIG_FILE" --help &> /dev/null; then
    print_success "✓ Vale configuration is valid"
else
    print_error "Vale configuration verification failed"
    exit 1
fi

# 7. Success message
echo
print_success "🎉 Installation completed successfully!"
echo
echo "Vale is now configured with the Elastic style guide. You can:"
echo "  • Run 'vale <file>' to check a specific file"
echo "  • Run 'vale <directory>' to check all supported files in a directory"
echo
echo "Configuration file location: $VALE_CONFIG_FILE"
echo "To update the style guide in the future, run: vale sync"
