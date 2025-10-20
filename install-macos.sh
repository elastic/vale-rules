# Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
# or more contributor license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch B.V. licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

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

# 4. Clean existing Vale installation
VALE_CONFIG_DIR="$HOME/Library/Application Support/vale"
print_info "Cleaning existing Vale installation..."
if [ -d "$VALE_CONFIG_DIR" ]; then
    print_info "Removing existing Vale directory: $VALE_CONFIG_DIR"
    if rm -rf "$VALE_CONFIG_DIR"; then
        print_success "✓ Existing Vale installation cleaned"
    else
        print_error "Failed to clean existing Vale installation"
        exit 1
    fi
else
    print_info "No existing Vale installation found"
fi

# 5. Create or update Vale configuration directory and file
VALE_CONFIG_DIR="$HOME/Library/Application Support/vale"
VALE_CONFIG_FILE="$VALE_CONFIG_DIR/.vale.ini"

print_info "Setting up Vale configuration..."
mkdir -p "$VALE_CONFIG_DIR"

# Create the .vale.ini file
print_info "Creating new configuration at $VALE_CONFIG_FILE..."

# Create or overwrite the .vale.ini file with Packages configuration
cat > "$VALE_CONFIG_FILE" << 'EOF'
StylesPath = styles
MinAlertLevel = suggestion

Packages = https://github.com/elastic/vale-rules/releases/latest/download/Elastic.zip

[*.md]
BasedOnStyles = Elastic

[*.adoc]
BasedOnStyles = Elastic
EOF

print_success "✓ Vale configuration created at: $VALE_CONFIG_FILE"

# 6. Download and install Elastic style package
print_info "Downloading and installing Elastic style package..."
if vale --config="$VALE_CONFIG_FILE" sync; then
    print_success "✓ Elastic styles package downloaded and installed successfully"
else
    print_error "Failed to sync Vale styles package"
    exit 1
fi

# 7. Verify that the installed styles are accessible
VALE_STYLES_DIR="$VALE_CONFIG_DIR/styles"
print_info "Verifying installed style guide..."
if [ -d "$VALE_STYLES_DIR/Elastic" ] && ls "$VALE_STYLES_DIR/Elastic"/*.yml > /dev/null 2>&1; then
    print_success "✓ Elastic styles installed and accessible"
else
    print_error "Elastic styles verification failed"
    exit 1
fi

# 8. Final verification
print_info "Performing final verification..."
if vale --config="$VALE_CONFIG_FILE" --help &> /dev/null; then
    print_success "✓ Vale configuration is valid"
else
    print_error "Vale configuration verification failed"
    exit 1
fi

# 9. Success message
echo
print_success "🎉 Installation completed successfully!"
echo
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
