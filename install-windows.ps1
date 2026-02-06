# Licensed to Elasticsearch B.V under one or more agreements.
# Elasticsearch B.V licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information

# Elastic Vale Style Guide Installation Script for Windows
# This script installs Vale and configures it to use the Elastic style guide

# Requires PowerShell 5.0 or later
#Requires -Version 5.0

# Stop on any error
$ErrorActionPreference = "Stop"

# Functions for colored output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-ColorOutput "Error: $Message" "Red"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput $Message "Green"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput $Message "Yellow"
}

# 1. Detect Windows
Write-Info "Checking operating system..."
# PowerShell 5.1 compatibility: check PSEdition (Desktop = Windows PS 5.1) or OS environment variable
if ($PSVersionTable.PSEdition -eq "Desktop") {
    # PowerShell 5.1 on Windows
    Write-Success "[OK] Running on Windows"
} elseif ($PSVersionTable.PSEdition -eq "Core") {
    # PowerShell Core - check Platform
    if ($PSVersionTable.Platform -eq "Unix") {
        Write-ErrorMsg "This script is designed for Windows only."
        exit 1
    }
    Write-Success "[OK] Running on Windows"
} elseif ($env:OS -like "*Windows*") {
    # Fallback: check OS environment variable
    Write-Success "[OK] Running on Windows"
} else {
    Write-ErrorMsg "This script is designed for Windows only."
    exit 1
}

# 2. Check if Vale is already installed
Write-Info "Checking for existing Vale installation..."
$valeAlreadyInstalled = $false
try {
    $valeOutput = & vale --version 2>&1
    if ($? -and $valeOutput) {
        $valeVersion = ($valeOutput | Out-String).Trim()
        Write-Success "[OK] Vale is already installed: $valeVersion"
        $valeAlreadyInstalled = $true
    } else {
        Write-Info "Vale not found, will install it"
    }
}
catch {
    Write-Info "Vale not found, will install it"
}

# 3. If Vale is not installed, install it
if (-not $valeAlreadyInstalled) {
    Write-Info "Installing Vale..."
    
    # Try Chocolatey first
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Info "Installing Vale via Chocolatey..."
        try {
            choco install vale -y
            Write-Success "[OK] Vale installed successfully via Chocolatey"
        }
        catch {
            Write-ErrorMsg "Failed to install Vale via Chocolatey"
            Write-Host "You can install Vale manually from: https://vale.sh/docs/vale-cli/installation/"
            exit 1
        }
    }
    # Try Scoop as alternative
    elseif (Get-Command scoop -ErrorAction SilentlyContinue) {
        Write-Info "Installing Vale via Scoop..."
        try {
            scoop install vale
            Write-Success "[OK] Vale installed successfully via Scoop"
        }
        catch {
            Write-ErrorMsg "Failed to install Vale via Scoop"
            Write-Host "You can install Vale manually from: https://vale.sh/docs/vale-cli/installation/"
            exit 1
        }
    }
    # Manual installation
    else {
        Write-Info "No package manager found (Chocolatey or Scoop)"
        Write-Info "Downloading Vale binary..."
        
        $valeVersion = "3.12.0"
        $downloadUrl = "https://github.com/errata-ai/vale/releases/download/v$valeVersion/vale_${valeVersion}_Windows_64-bit.zip"
        $tempZip = "$env:TEMP\vale.zip"
        $installDir = "$env:LOCALAPPDATA\Programs\Vale"
        
        try {
            # Download Vale
            Invoke-WebRequest -Uri $downloadUrl -OutFile $tempZip
            
            # Create installation directory
            New-Item -ItemType Directory -Path $installDir -Force | Out-Null
            
            # Extract Vale
            Expand-Archive -Path $tempZip -DestinationPath $installDir -Force
            
            # Add to PATH for current session
            $env:Path = "$installDir;$env:Path"
            
            # Add to PATH permanently (user level)
            $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
            if ($userPath -notlike "*$installDir*") {
                [Environment]::SetEnvironmentVariable("Path", "$userPath;$installDir", "User")
            }
            
            # Clean up
            Remove-Item $tempZip
            
            Write-Success "[OK] Vale installed successfully to $installDir"
            Write-Info "Note: You may need to restart your terminal for PATH changes to take effect"
        }
        catch {
            Write-ErrorMsg "Failed to download and install Vale: $_"
            Write-Host "You can install Vale manually from: https://vale.sh/docs/vale-cli/installation/"
            exit 1
        }
    }

    # Verify installation
    Write-Info "Verifying Vale installation..."
    try {
        $valeVersion = & vale --version
        Write-Success "[OK] Vale is installed: $valeVersion"
    }
    catch {
        Write-ErrorMsg "Vale installation verification failed"
        exit 1
    }
}

# 4. Set up Vale directories
$valeConfigDir = "$env:LOCALAPPDATA\vale"
$valeConfigFile = "$valeConfigDir\.vale.ini"
$valeStylesDir = "$valeConfigDir\styles"

# 5. Check existing Vale installation
if (Test-Path $valeConfigDir) {
    Write-Info "Existing Vale installation detected at: $valeConfigDir"
    
    # Check if it's an Elastic installation
    $isElastic = $false
    if (Test-Path "$valeStylesDir\Elastic") {
        $isElastic = $true
    }
    if (Test-Path $valeConfigFile) {
        $configContent = Get-Content $valeConfigFile -Raw
        if ($configContent -match "elastic-vale\.zip") {
            $isElastic = $true
        }
    }
    
    if ($isElastic) {
        Write-Info "Detected existing Elastic Vale installation - will update"
    }
    else {
        Write-Info "Detected non-Elastic Vale installation"
        $response = Read-Host "This will replace your existing Vale configuration. Continue? [y/N]"
        if ($response -notmatch "^[Yy]$") {
            Write-Info "Installation cancelled by user"
            exit 0
        }
        Write-Info "Removing existing Vale installation..."
        try {
            Remove-Item -Path $valeConfigDir -Recurse -Force
        }
        catch {
            Write-ErrorMsg "Failed to remove existing Vale installation: $_"
            exit 1
        }
    }
}
else {
    Write-Info "No existing Vale installation found"
}

# 6. Create Vale configuration directory and file
Write-Info "Setting up Vale configuration..."
New-Item -ItemType Directory -Path $valeConfigDir -Force | Out-Null

# Create the .vale.ini file
Write-Info "Creating configuration at $valeConfigFile..."

# Create minimal .vale.ini - the package will provide the full config via merge
$configContent = @"
StylesPath = styles

Packages = https://github.com/elastic/vale-rules/releases/latest/download/elastic-vale.zip
"@

Set-Content -Path $valeConfigFile -Value $configContent -Encoding UTF8

Write-Success "[OK] Vale configuration created at: $valeConfigFile"

# 7. Download and install Elastic style package
# Remove existing Elastic styles to force re-download (vale sync doesn't have a --force flag)
if (Test-Path "$valeStylesDir\Elastic") {
    Write-Info "Removing existing Elastic styles to ensure latest version..."
    Remove-Item -Path "$valeStylesDir\Elastic" -Recurse -Force
    if (Test-Path "$valeStylesDir\.vale-config") {
        Remove-Item -Path "$valeStylesDir\.vale-config" -Recurse -Force
    }
}

Write-Info "Downloading and installing Elastic style package..."
try {
    & vale --config="$valeConfigFile" sync
    Write-Success "[OK] Elastic styles package downloaded and installed successfully"
}
catch {
    Write-ErrorMsg "Failed to sync Vale styles package: $_"
    exit 1
}

# 8. Verify that the installed styles are accessible
Write-Info "Verifying installed style guide..."
if ((Test-Path "$valeStylesDir\Elastic") -and (Get-ChildItem "$valeStylesDir\Elastic\*.yml" -ErrorAction SilentlyContinue)) {
    # Check if VERSION file exists and read it
    $versionFile = "$valeStylesDir\Elastic\VERSION"
    if (Test-Path $versionFile) {
        $installedVersion = Get-Content $versionFile -Raw
        $installedVersion = $installedVersion.Trim()
        Write-Success "[OK] Elastic styles installed and accessible (version: $installedVersion)"
    }
    else {
        Write-Success "[OK] Elastic styles installed and accessible"
    }
}
else {
    Write-ErrorMsg "Elastic styles verification failed"
    exit 1
}

# 9. Final verification
Write-Info "Performing final verification..."
try {
    & vale --config="$valeConfigFile" --help | Out-Null
    Write-Success "[OK] Vale configuration is valid"
}
catch {
    Write-ErrorMsg "Vale configuration verification failed: $_"
    exit 1
}

# 10. Success message
Write-Host ""
Write-Success "Installation completed successfully!"
Write-Host ""
if ($installedVersion) {
    Write-Host "Elastic Vale Style Guide version: $installedVersion"
    Write-Host ""
}
Write-Host "Vale is now configured with the Elastic style guide. You can:"
Write-Host "  - Run 'vale <file>' to check a specific file"
Write-Host "  - Run 'vale <directory>' to check all supported files in a directory"
Write-Host ""
Write-Host "Configuration file location: $valeConfigFile"
Write-Host "Styles installed to: $valeStylesDir\Elastic"
Write-Host ""
Write-Host "To update the styles in the future, re-run this script or run:"
Write-Host "  Remove-Item -Path '$valeStylesDir\Elastic','$valeStylesDir\.vale-config' -Recurse -Force"
Write-Host "  vale --config='$valeConfigFile' sync"

