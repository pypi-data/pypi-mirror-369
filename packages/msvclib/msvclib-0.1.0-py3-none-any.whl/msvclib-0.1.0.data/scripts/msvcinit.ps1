# PowerShell script for MSVC environment initialization
Write-Host "Initializing MSVC environment..." -ForegroundColor Yellow

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$devcmdPath = Join-Path $scriptDir "..\Lib\site-packages\msvclib\devcmd.ps1"

# Source the PowerShell script
& $devcmdPath

# Set DISTUTILS_USE_SDK
$env:DISTUTILS_USE_SDK = "1"

Write-Host "MSVC environment initialized successfully!" -ForegroundColor Green
Write-Host "You can now use Visual Studio build tools in this PowerShell session." -ForegroundColor Cyan
