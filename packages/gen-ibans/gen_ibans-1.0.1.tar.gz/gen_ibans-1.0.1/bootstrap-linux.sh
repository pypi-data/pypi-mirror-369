#!/bin/bash

# Bootstrap script for setting up the gen-ibans development environment on Linux (Debian-based)
#
# This script automatically installs the required tools for gen-ibans development:
# - Python 3.8+
# - mise (Python version manager)
# - uv (Python package manager)
#
# Usage: ./bootstrap-linux.sh
#
# Supported distributions: Ubuntu, Debian, Linux Mint, Pop!_OS, and other Debian derivatives
#
# Copyright (c) 2025 Sebastian Wallat
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

set -euo pipefail  # Exit on error, undefined variables, and pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${BLUE}🔧 $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if we're running on a Debian-based system
check_debian_based() {
    if [[ -f /etc/debian_version ]] || command_exists apt; then
        return 0
    else
        log_error "This script is designed for Debian-based Linux distributions (Ubuntu, Debian, etc.)"
        log_error "Detected system doesn't appear to be Debian-based."
        exit 1
    fi
}

# Update package lists
update_packages() {
    log_step "Updating package lists..."
    if sudo apt update; then
        log_success "Package lists updated successfully!"
    else
        log_error "Failed to update package lists"
        exit 1
    fi
}

# Install Python
install_python() {
    log_step "Installing Python..."
    
    # Check if Python 3.8+ is already installed
    if command_exists python3; then
        python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
        major=$(echo "$python_version" | cut -d. -f1)
        minor=$(echo "$python_version" | cut -d. -f2)
        
        if [[ "$major" -gt 3 ]] || [[ "$major" -eq 3 && "$minor" -ge 8 ]]; then
            log_success "Python $python_version is already installed and meets requirements."
            
            # Check if pip is installed
            if ! command_exists pip3; then
                log_step "Installing pip..."
                sudo apt install -y python3-pip
            fi
            
            return
        fi
    fi
    
    # Install Python and pip
    log_info "Installing Python 3, pip, and development tools..."
    if sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential; then
        
        # Verify installation
        if command_exists python3; then
            python_version=$(python3 --version)
            log_success "Python installed successfully: $python_version"
        else
            log_error "Python installation verification failed"
            exit 1
        fi
    else
        log_error "Failed to install Python"
        exit 1
    fi
}

# Install mise
install_mise() {
    log_step "Installing mise..."
    
    # Check if mise is already installed
    if command_exists mise; then
        mise_version=$(mise --version 2>/dev/null || echo "unknown")
        log_success "mise is already installed: $mise_version"
        return
    fi
    
    # Install mise using the official installation script
    log_info "Downloading and installing mise..."
    if curl -fsSL https://mise.run | bash; then
        
        # Add mise to PATH for current session
        export PATH="$HOME/.local/bin:$PATH"
        
        # Add mise to shell profile
        shell_profile=""
        if [[ -n "${BASH_VERSION:-}" ]]; then
            shell_profile="$HOME/.bashrc"
        elif [[ -n "${ZSH_VERSION:-}" ]]; then
            shell_profile="$HOME/.zshrc"
        else
            # Fallback to .profile
            shell_profile="$HOME/.profile"
        fi
        
        if [[ -n "$shell_profile" ]]; then
            if ! grep -q 'mise activate' "$shell_profile" 2>/dev/null; then
                echo '' >> "$shell_profile"
                echo '# mise activation' >> "$shell_profile"
                echo 'eval "$(mise activate bash)"' >> "$shell_profile"
                log_info "Added mise activation to $shell_profile"
            fi
        fi
        
        # Verify installation
        if command_exists mise; then
            mise_version=$(mise --version)
            log_success "mise installed successfully: $mise_version"
        else
            log_error "mise installation verification failed"
            log_warning "You may need to restart your shell or run: source $shell_profile"
            exit 1
        fi
    else
        log_error "Failed to install mise"
        exit 1
    fi
}

# Install uv
install_uv() {
    log_step "Installing uv..."
    
    # Check if uv is already installed
    if command_exists uv; then
        uv_version=$(uv --version 2>/dev/null || echo "unknown")
        log_success "uv is already installed: $uv_version"
        return
    fi
    
    # Install uv using the official installation script
    log_info "Downloading and installing uv..."
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        
        # Add uv to PATH for current session
        export PATH="$HOME/.cargo/bin:$PATH"
        
        # Verify installation
        if command_exists uv; then
            uv_version=$(uv --version)
            log_success "uv installed successfully: $uv_version"
        else
            log_error "uv installation verification failed"
            log_warning "You may need to restart your shell or run: source ~/.bashrc"
            exit 1
        fi
    else
        log_error "Failed to install uv"
        exit 1
    fi
}

# Install project dependencies
install_project_dependencies() {
    log_step "Installing project dependencies..."
    
    # Check if we're in the gen-ibans directory
    if [[ ! -f "pyproject.toml" ]]; then
        log_warning "pyproject.toml not found. Make sure you're in the gen-ibans project directory."
        log_warning "Skipping project dependency installation."
        return
    fi
    
    # Install dependencies using uv
    if uv sync --dev; then
        log_success "Project dependencies installed successfully!"
    else
        log_error "Failed to install project dependencies"
        log_warning "You can install them later by running 'uv sync --dev' in the project directory."
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    log_success "🎉 Bootstrap completed successfully!"
    echo ""
    log_info "Next steps:"
    echo -e "${YELLOW}1. Restart your terminal or run: source ~/.bashrc (or ~/.zshrc)${NC}"
    echo -e "${YELLOW}2. Navigate to your gen-ibans project directory${NC}"
    echo -e "${YELLOW}3. Run 'uv sync --dev' to install project dependencies (if not already done)${NC}"
    echo -e "${YELLOW}4. Run 'uv run pytest tests/' to verify everything works${NC}"
    echo -e "${YELLOW}5. Start developing! 🚀${NC}"
    
    echo ""
    log_info "Installed tools:"
    echo -e "${YELLOW}- Python: Programming language runtime${NC}"
    echo -e "${YELLOW}- mise: Tool version management${NC}"
    echo -e "${YELLOW}- uv: Fast Python package manager${NC}"
    
    echo ""
    log_info "Environment setup:"
    echo -e "${YELLOW}mise has been added to your shell profile for automatic activation.${NC}"
    echo -e "${YELLOW}uv has been installed to ~/.cargo/bin and should be in your PATH.${NC}"
}

# Check for required tools
check_requirements() {
    log_step "Checking system requirements..."
    
    # Check if we have curl
    if ! command_exists curl; then
        log_info "Installing curl..."
        sudo apt install -y curl
    fi
    
    # Check if we have git (useful for development)
    if ! command_exists git; then
        log_info "Installing git..."
        sudo apt install -y git
    fi
    
    # Check sudo access
    if ! sudo -n true 2>/dev/null; then
        log_info "This script requires sudo access for package installation."
        log_info "You may be prompted for your password."
    fi
}

# Main function
main() {
    log_info "🚀 Starting gen-ibans development environment setup for Linux..."
    log_info "This script will install: Python, mise, and uv"
    echo ""
    
    # System checks
    check_debian_based
    check_requirements
    
    # Update package lists
    update_packages
    
    # Install tools
    install_python
    install_mise
    install_uv
    
    # Install project dependencies
    install_project_dependencies
    
    # Show completion message
    show_next_steps
}

# Check if script is being run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Trap errors and show helpful message
    trap 'log_error "Bootstrap failed. Check the error messages above."' ERR
    
    main "$@"
fi