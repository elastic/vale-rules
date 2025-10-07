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

# 4. Get the script directory to locate local styles
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STYLES_SOURCE_DIR="$SCRIPT_DIR/styles"

print_info "Checking for local styles directory..."
if [ ! -d "$STYLES_SOURCE_DIR" ]; then
    print_error "Local styles directory not found at: $STYLES_SOURCE_DIR"
    print_error "Make sure you're running this script from the elastic-style-guide repository root"
    exit 1
fi
print_success "✓ Local styles found at: $STYLES_SOURCE_DIR"

# 5. Update repository to latest changes
print_info "Updating repository to latest changes..."
if git fetch && git pull; then
    print_success "✓ Repository updated successfully"
else
    print_error "Failed to update repository"
    print_info "Continuing with current local version..."
fi

# 6. Clean existing Vale installation
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

# 7. Create or update Vale configuration directory and file
VALE_CONFIG_DIR="$HOME/Library/Application Support/vale"
VALE_CONFIG_FILE="$VALE_CONFIG_DIR/.vale.ini"

print_info "Setting up Vale configuration..."
mkdir -p "$VALE_CONFIG_DIR"

# Create the .vale.ini file
print_info "Creating new configuration at $VALE_CONFIG_FILE..."

# Create or overwrite the .vale.ini file
cat > "$VALE_CONFIG_FILE" << 'EOF'
MinAlertLevel = suggestion

[*.md]
BasedOnStyles = Elastic

[*.adoc]
BasedOnStyles = Elastic
EOF

print_success "✓ Vale configuration updated at: $VALE_CONFIG_FILE"

# 8. Copy local styles to Vale's styles directory
VALE_STYLES_DIR="$VALE_CONFIG_DIR/styles"
print_info "Setting up Vale styles directory..."
mkdir -p "$VALE_STYLES_DIR"

print_info "Copying Elastic styles from local repository..."
if [ -d "$STYLES_SOURCE_DIR/Elastic" ]; then
    # Copy the Elastic styles (directory is already clean)
    if cp -r "$STYLES_SOURCE_DIR/Elastic" "$VALE_STYLES_DIR/"; then
        print_success "✓ Elastic styles copied successfully to: $VALE_STYLES_DIR/Elastic"
    else
        print_error "Failed to copy Elastic styles"
        exit 1
    fi
else
    print_error "Elastic styles directory not found at: $STYLES_SOURCE_DIR/Elastic"
    exit 1
fi

# 9. Verify that the copied styles are accessible
print_info "Verifying copied style guide..."
if [ -d "$VALE_STYLES_DIR/Elastic" ] && ls "$VALE_STYLES_DIR/Elastic"/*.yml > /dev/null 2>&1; then
    print_success "✓ Elastic styles installed and accessible"
else
    print_error "Copied Elastic styles verification failed"
    exit 1
fi

# 10. Final verification
print_info "Performing final verification..."
if vale --config="$VALE_CONFIG_FILE" --help &> /dev/null; then
    print_success "✓ Vale configuration is valid"
else
    print_error "Vale configuration verification failed"
    exit 1
fi

# 11. Success message
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
echo "To update the styles in the future, simply re-run this script."
