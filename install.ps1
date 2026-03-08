# GitHub Hacker Installer for Windows
# Usage: iwr -useb https://raw.githubusercontent.com/YOUR_USERNAME/GithubHacker/main/install.ps1 | iex

param(
    [string]$Repo = "YOUR_USERNAME/GithubHacker",
    [string]$InstallDir = "$env:USERPROFILE\.github-hacker"
)

$ErrorActionPreference = "Stop"

Write-Host "Installing GitHub Hacker..." -ForegroundColor Green

# Get latest release
Write-Host "Fetching latest version..."
try {
    $Response = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest" -UseBasicParsing
    $Version = $Response.tag_name
    Write-Host "Latest version: $Version" -ForegroundColor Cyan
    $DownloadUrl = $Response.assets[0].browser_download_url
} catch {
    Write-Host "Could not fetch latest release, using main branch..." -ForegroundColor Yellow
    $Version = "main"
}

# Create installation directory
if (!(Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}
Set-Location $InstallDir

# Download source
Write-Host "Downloading..."
if ($Version -eq "main") {
    git clone --depth 1 "https://github.com/$Repo.git" . 2>$null || {
        Write-Host "Failed to clone repository" -ForegroundColor Red
        exit 1
    }
} else {
    $ZipUrl = "https://github.com/$Repo/archive/refs/tags/$Version.zip"
    Invoke-WebRequest -Uri $ZipUrl -OutFile "archive.zip" -UseBasicParsing
    Expand-Archive -Path "archive.zip" -DestinationPath "." -Force
    Move-Item -Path "$Version\*" -Destination "." -Force
    Remove-Item -Path "archive.zip" -Force
    Remove-Item -Path $Version -Recurse -Force
}

# Create virtual environment
Write-Host "Creating virtual environment..."
python -m venv venv

# Activate and install
Write-Host "Installing dependencies..."
& "$InstallDir\venv\Scripts\pip.exe" install -e . --quiet

# Create launcher
$BinDir = "$env:LOCALAPPDATA\bin"
if (!(Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
}

@"
@echo off
"%USERPROFILE%\.github-hacker\venv\Scripts\python.exe" -m githubhacker.cli %*
"@ | Out-File -FilePath "$BinDir\github-hacker.cmd" -Encoding ASCII -Force

# Add to PATH
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$BinDir", "User")
}

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Please restart your terminal and run:"
Write-Host "  github-hacker --help" -ForegroundColor Cyan
