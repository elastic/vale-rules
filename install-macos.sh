#!/bin/bash

# Licensed to Elasticsearch B.V under one or more agreements.
# Elasticsearch B.V licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information

# Elastic Vale Style Guide Installation Script for macOS
# This script installs Vale and configures it to use the Elastic style guide

set -e  # Exit on any error

# Parse flags
ENABLE_SPELLING=false
for arg in "$@"; do
    case "$arg" in
        --enable-spelling) ENABLE_SPELLING=true ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --enable-spelling  Enable the experimental Elastic.Spelling rule"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg (use --help for usage)"
            exit 1
            ;;
    esac
done

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

# 4. Check existing Vale installation
VALE_CONFIG_DIR="$HOME/Library/Application Support/vale"
VALE_CONFIG_FILE="$VALE_CONFIG_DIR/.vale.ini"
VALE_STYLES_DIR="$VALE_CONFIG_DIR/styles"

if [ -d "$VALE_CONFIG_DIR" ]; then
    print_info "Existing Vale installation detected at: $VALE_CONFIG_DIR"
    
    # Check if it's an Elastic installation
    if [ -d "$VALE_STYLES_DIR/Elastic" ] || grep -q "elastic-vale.zip" "$VALE_CONFIG_FILE" 2>/dev/null; then
        print_info "Detected existing Elastic Vale installation - will update"
    else
        print_info "Detected non-Elastic Vale installation"
        echo -n "This will replace your existing Vale configuration. Continue? [y/N] "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_info "Installation cancelled by user"
            exit 0
        fi
        print_info "Removing existing Vale installation..."
        rm -rf "$VALE_CONFIG_DIR"
    fi
else
    print_info "No existing Vale installation found"
fi

# 5. Create or update Vale configuration directory and file
print_info "Setting up Vale configuration..."
mkdir -p "$VALE_CONFIG_DIR"

# Create the .vale.ini file
print_info "Creating configuration at $VALE_CONFIG_FILE..."

# Create minimal .vale.ini - the package will provide the full config via merge
cat > "$VALE_CONFIG_FILE" << 'EOF'
StylesPath = styles

Packages = https://github.com/elastic/vale-rules/releases/latest/download/elastic-vale.zip
EOF

print_success "✓ Vale configuration created at: $VALE_CONFIG_FILE"

# 6. Download and install Elastic style package
# Remove existing Elastic styles to force re-download (vale sync doesn't have a --force flag)
if [ -d "$VALE_STYLES_DIR/Elastic" ]; then
    print_info "Removing existing Elastic styles to ensure latest version..."
    rm -rf "$VALE_STYLES_DIR/Elastic"
    rm -rf "$VALE_STYLES_DIR/.vale-config"
fi

print_info "Downloading and installing Elastic style package..."
if vale --config="$VALE_CONFIG_FILE" sync; then
    print_success "✓ Elastic styles package downloaded and installed successfully"
else
    print_error "Failed to sync Vale styles package"
    exit 1
fi

# 7. Apply optional rule overrides
if [ "$ENABLE_SPELLING" = true ]; then
    print_info "Enabling experimental spelling rule..."
    # Append override after the package line so it takes effect after merge
    if ! grep -q "Elastic.Spelling" "$VALE_CONFIG_FILE"; then
        echo "" >> "$VALE_CONFIG_FILE"
        echo "[*.md]" >> "$VALE_CONFIG_FILE"
        echo "Elastic.Spelling = YES" >> "$VALE_CONFIG_FILE"
    else
        sed -i '' 's/Elastic\.Spelling = NO/Elastic.Spelling = YES/' "$VALE_CONFIG_FILE"
    fi
    print_success "✓ Spelling rule enabled"
fi

# 8. Verify that the installed styles are accessible
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
if [ "$ENABLE_SPELLING" = true ]; then
    echo "Spelling rule: ENABLED (experimental)"
else
    echo "Spelling rule: disabled (run with --enable-spelling to enable)"
fi
echo
echo "Configuration file location: $VALE_CONFIG_FILE"
echo "Styles installed to: $VALE_STYLES_DIR/Elastic"
echo
echo "To update the styles in the future, re-run this script or run:"
echo "  rm -rf \"$VALE_STYLES_DIR/Elastic\" \"$VALE_STYLES_DIR/.vale-config\""
echo "  vale --config=\"$VALE_CONFIG_FILE\" sync"
