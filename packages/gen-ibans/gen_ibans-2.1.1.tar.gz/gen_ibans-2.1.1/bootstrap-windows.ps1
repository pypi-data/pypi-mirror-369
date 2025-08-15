#!/usr/bin/env powershell
<#
.SYNOPSIS
    Bootstrap script for setting up the gen-ibans development environment on Windows.

.DESCRIPTION
    This script automatically installs the required tools for gen-ibans development:
    - Scoop (if not already installed)
    - Python 3.8+
    - mise (Python version manager)
    - uv (Python package manager)

.EXAMPLE
    ./bootstrap-windows.ps1
    
.NOTES
    This script requires PowerShell execution policy to allow script execution.
    You may need to run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Copyright (c) 2025 Sebastian Wallat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
#>

# Enable strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Colors for output
$Red = [System.ConsoleColor]::Red
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Blue = [System.ConsoleColor]::Blue

function Write-ColorOutput {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,
        [System.ConsoleColor]$Color = [System.ConsoleColor]::White
    )
    Write-Host $Message -ForegroundColor $Color
}

function Test-Command {
    param([string]$Command)
    try {
        if (Get-Command $Command -ErrorAction SilentlyContinue) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

function Install-Scoop {
    Write-ColorOutput "🔧 Installing Scoop package manager..." $Blue
    try {
        # Check if Scoop is already installed
        if (Test-Command "scoop") {
            Write-ColorOutput "✅ Scoop is already installed." $Green
            return
        }

        # Install Scoop
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
        
        # Verify installation
        if (Test-Command "scoop") {
            Write-ColorOutput "✅ Scoop installed successfully!" $Green
        } else {
            throw "Scoop installation verification failed"
        }
    } catch {
        Write-ColorOutput "❌ Failed to install Scoop: $($_.Exception.Message)" $Red
        exit 1
    }
}

function Install-Python {
    Write-ColorOutput "🐍 Installing Python..." $Blue
    try {
        # Check if Python is already installed and meets version requirement
        if (Test-Command "python") {
            $pythonVersion = python --version 2>&1
            if ($pythonVersion -match "Python (\d+)\.(\d+)") {
                $major = [int]$matches[1]
                $minor = [int]$matches[2]
                if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 8)) {
                    Write-ColorOutput "✅ Python $($matches[0]) is already installed and meets requirements." $Green
                    return
                }
            }
        }

        # Install Python using Scoop
        scoop install python
        
        # Refresh environment variables
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "User") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "Machine")
        
        # Verify installation
        if (Test-Command "python") {
            $pythonVersion = python --version
            Write-ColorOutput "✅ Python installed successfully: $pythonVersion" $Green
        } else {
            throw "Python installation verification failed"
        }
    } catch {
        Write-ColorOutput "❌ Failed to install Python: $($_.Exception.Message)" $Red
        exit 1
    }
}

function Install-Mise {
    Write-ColorOutput "⚙️ Installing mise..." $Blue
    try {
        # Check if mise is already installed
        if (Test-Command "mise") {
            Write-ColorOutput "✅ mise is already installed." $Green
            return
        }

        # Install mise using Scoop
        scoop install mise
        
        # Refresh environment variables
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "User") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "Machine")
        
        # Verify installation
        if (Test-Command "mise") {
            $miseVersion = mise --version
            Write-ColorOutput "✅ mise installed successfully: $miseVersion" $Green
        } else {
            throw "mise installation verification failed"
        }
    } catch {
        Write-ColorOutput "❌ Failed to install mise: $($_.Exception.Message)" $Red
        exit 1
    }
}

function Install-UV {
    Write-ColorOutput "📦 Installing uv..." $Blue
    try {
        # Check if uv is already installed
        if (Test-Command "uv") {
            Write-ColorOutput "✅ uv is already installed." $Green
            return
        }

        # Install uv using PowerShell method (recommended by uv docs)
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
        
        # Refresh environment variables
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "User") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "Machine")
        
        # Verify installation
        if (Test-Command "uv") {
            $uvVersion = uv --version
            Write-ColorOutput "✅ uv installed successfully: $uvVersion" $Green
        } else {
            throw "uv installation verification failed"
        }
    } catch {
        Write-ColorOutput "❌ Failed to install uv: $($_.Exception.Message)" $Red
        exit 1
    }
}

function Install-ProjectDependencies {
    Write-ColorOutput "📚 Installing project dependencies..." $Blue
    try {
        # Check if we're in the gen-ibans directory
        if (-not (Test-Path "pyproject.toml")) {
            Write-ColorOutput "⚠️ pyproject.toml not found. Make sure you're in the gen-ibans project directory." $Yellow
            Write-ColorOutput "Skipping project dependency installation." $Yellow
            return
        }

        # Install dependencies using uv
        uv sync --dev
        
        Write-ColorOutput "✅ Project dependencies installed successfully!" $Green
    } catch {
        Write-ColorOutput "❌ Failed to install project dependencies: $($_.Exception.Message)" $Red
        Write-ColorOutput "You can install them later by running 'uv sync --dev' in the project directory." $Yellow
    }
}

function Show-NextSteps {
    Write-ColorOutput "`n🎉 Bootstrap completed successfully!" $Green
    Write-ColorOutput "`nNext steps:" $Blue
    Write-ColorOutput "1. Restart your PowerShell session to ensure all PATH changes take effect" $Yellow
    Write-ColorOutput "2. Navigate to your gen-ibans project directory" $Yellow
    Write-ColorOutput "3. Run 'uv sync --dev' to install project dependencies (if not already done)" $Yellow
    Write-ColorOutput "4. Run 'uv run pytest tests/' to verify everything works" $Yellow
    Write-ColorOutput "5. Start developing! 🚀" $Yellow
    
    Write-ColorOutput "`nInstalled tools:" $Blue
    Write-ColorOutput "- Scoop: Package manager for Windows" $Yellow
    Write-ColorOutput "- Python: Programming language runtime" $Yellow
    Write-ColorOutput "- mise: Tool version management" $Yellow
    Write-ColorOutput "- uv: Fast Python package manager" $Yellow
}

# Main execution
function Main {
    Write-ColorOutput "🚀 Starting gen-ibans development environment setup for Windows..." $Blue
    Write-ColorOutput "This script will install: Scoop, Python, mise, and uv`n" $Yellow
    
    # Check PowerShell execution policy
    $executionPolicy = Get-ExecutionPolicy -Scope CurrentUser
    if ($executionPolicy -eq "Restricted") {
        Write-ColorOutput "⚠️ PowerShell execution policy is Restricted. Setting to RemoteSigned for current user..." $Yellow
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    }
    
    Install-Scoop
    Install-Python  
    Install-Mise
    Install-UV
    Install-ProjectDependencies
    Show-NextSteps
}

# Run main function
try {
    Main
} catch {
    Write-ColorOutput "❌ Bootstrap failed: $($_.Exception.Message)" $Red
    exit 1
}