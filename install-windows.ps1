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
if ($PSVersionTable.Platform -eq "Unix") {
    Write-ErrorMsg "This script is designed for Windows only."
    exit 1
}
Write-Success "✓ Running on Windows"

# 2. Check if Vale is already installed
Write-Info "Checking for existing Vale installation..."
try {
    $valeVersion = & vale --version 2>$null
    Write-Success "✓ Vale is already installed: $valeVersion"
    $valeAlreadyInstalled = $true
}
catch {
    Write-Info "Vale not found, will install it"
    $valeAlreadyInstalled = $false
}

# 3. If Vale is not installed, install it
if (-not $valeAlreadyInstalled) {
    Write-Info "Installing Vale..."
    
    # Try Chocolatey first
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Info "Installing Vale via Chocolatey..."
        try {
            choco install vale -y
            Write-Success "✓ Vale installed successfully via Chocolatey"
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
            Write-Success "✓ Vale installed successfully via Scoop"
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
            
            Write-Success "✓ Vale installed successfully to $installDir"
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
        Write-Success "✓ Vale is installed: $valeVersion"
    }
    catch {
        Write-ErrorMsg "Vale installation verification failed"
        exit 1
    }
}

# 4. Set up Vale directories
$valeConfigDir = "$env:LOCALAPPDATA\vale"
$valeConfigFile = "$valeConfigDir\.vale.ini"

# 5. Clean existing Vale installation
Write-Info "Cleaning existing Vale installation..."
if (Test-Path $valeConfigDir) {
    Write-Info "Removing existing Vale directory: $valeConfigDir"
    try {
        Remove-Item -Path $valeConfigDir -Recurse -Force
        Write-Success "✓ Existing Vale installation cleaned"
    }
    catch {
        Write-ErrorMsg "Failed to clean existing Vale installation: $_"
        exit 1
    }
}
else {
    Write-Info "No existing Vale installation found"
}

# 6. Create Vale configuration directory and file
Write-Info "Setting up Vale configuration..."
New-Item -ItemType Directory -Path $valeConfigDir -Force | Out-Null

# Create the .vale.ini file
Write-Info "Creating new configuration at $valeConfigFile..."

# Create or overwrite the .vale.ini file with Packages configuration
$configContent = @"
StylesPath = styles
MinAlertLevel = suggestion

Packages = https://github.com/elastic/vale-rules/releases/latest/download/Elastic.zip

[*.md]
BasedOnStyles = Elastic

[*.adoc]
BasedOnStyles = Elastic
"@

Set-Content -Path $valeConfigFile -Value $configContent -Encoding UTF8

Write-Success "✓ Vale configuration created at: $valeConfigFile"

# 7. Download and install Elastic style package
Write-Info "Downloading and installing Elastic style package..."
try {
    & vale --config="$valeConfigFile" sync
    Write-Success "✓ Elastic styles package downloaded and installed successfully"
}
catch {
    Write-ErrorMsg "Failed to sync Vale styles package: $_"
    exit 1
}

# 8. Verify that the installed styles are accessible
$valeStylesDir = "$valeConfigDir\styles"
Write-Info "Verifying installed style guide..."
if ((Test-Path "$valeStylesDir\Elastic") -and (Get-ChildItem "$valeStylesDir\Elastic\*.yml" -ErrorAction SilentlyContinue)) {
    # Check if VERSION file exists and read it
    $versionFile = "$valeStylesDir\Elastic\VERSION"
    if (Test-Path $versionFile) {
        $installedVersion = Get-Content $versionFile -Raw
        $installedVersion = $installedVersion.Trim()
        Write-Success "✓ Elastic styles installed and accessible (version: $installedVersion)"
    }
    else {
        Write-Success "✓ Elastic styles installed and accessible"
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
    Write-Success "✓ Vale configuration is valid"
}
catch {
    Write-ErrorMsg "Vale configuration verification failed: $_"
    exit 1
}

# 10. Success message
Write-Host ""
Write-Success "🎉 Installation completed successfully!"
Write-Host ""
if ($installedVersion) {
    Write-Host "Elastic Vale Style Guide version: $installedVersion"
    Write-Host ""
}
Write-Host "Vale is now configured with the Elastic style guide. You can:"
Write-Host "  • Run 'vale <file>' to check a specific file"
Write-Host "  • Run 'vale <directory>' to check all supported files in a directory"
Write-Host ""
Write-Host "Configuration file location: $valeConfigFile"
Write-Host "Styles installed to: $valeStylesDir\Elastic"
Write-Host ""
Write-Host "To update the styles in the future:"
Write-Host "  • Re-run this script, or"
Write-Host "  • Run 'vale --config=`"$valeConfigFile`" sync' to update to the latest package"

