#!/bin/bash

# Bootstrap script for setting up the gen-ibans development environment on macOS
#
# This script automatically installs the required tools for gen-ibans development:
# - Homebrew (if not already installed)
# - Python 3.8+
# - mise (Python version manager)
# - uv (Python package manager)
#
# Usage: ./bootstrap-macos.sh
#
# Supported versions: macOS 10.15+ (Catalina and later)
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

# Check if we're running on macOS
check_macos() {
    if [[ "$(uname)" != "Darwin" ]]; then
        log_error "This script is designed for macOS only."
        log_error "Detected system: $(uname)"
        exit 1
    fi
    
    # Check macOS version
    macos_version=$(sw_vers -productVersion)
    log_info "Running on macOS $macos_version"
    
    # Extract major and minor version numbers
    major=$(echo "$macos_version" | cut -d. -f1)
    minor=$(echo "$macos_version" | cut -d. -f2)
    
    # Check if version is 10.15+ (Catalina or later)
    if [[ "$major" -lt 10 ]] || [[ "$major" -eq 10 && "$minor" -lt 15 ]]; then
        log_warning "This script is tested on macOS 10.15+ (Catalina and later)"
        log_warning "Your version might work, but compatibility is not guaranteed."
        read -p "Do you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Install Homebrew
install_homebrew() {
    log_step "Installing Homebrew..."
    
    # Check if Homebrew is already installed
    if command_exists brew; then
        log_success "Homebrew is already installed."
        
        # Update Homebrew
        log_step "Updating Homebrew..."
        brew update
        log_success "Homebrew updated successfully!"
        return
    fi
    
    # Install Homebrew
    log_info "Downloading and installing Homebrew..."
    if /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; then
        
        # Add Homebrew to PATH based on architecture
        arch=$(uname -m)
        if [[ "$arch" == "arm64" ]]; then
            # Apple Silicon (M1/M2)
            homebrew_prefix="/opt/homebrew"
        else
            # Intel
            homebrew_prefix="/usr/local"
        fi
        
        # Add to current session PATH
        export PATH="$homebrew_prefix/bin:$PATH"
        
        # Add to shell profile
        shell_profile=""
        if [[ -n "${BASH_VERSION:-}" ]]; then
            shell_profile="$HOME/.bash_profile"
        elif [[ -n "${ZSH_VERSION:-}" ]] || [[ "$SHELL" == */zsh ]]; then
            shell_profile="$HOME/.zshrc"
        else
            # Fallback to .profile
            shell_profile="$HOME/.profile"
        fi
        
        if [[ -n "$shell_profile" ]]; then
            if ! grep -q "$homebrew_prefix/bin" "$shell_profile" 2>/dev/null; then
                echo '' >> "$shell_profile"
                echo '# Homebrew' >> "$shell_profile"
                echo "export PATH=\"$homebrew_prefix/bin:\$PATH\"" >> "$shell_profile"
                log_info "Added Homebrew to PATH in $shell_profile"
            fi
        fi
        
        # Verify installation
        if command_exists brew; then
            brew_version=$(brew --version | head -1)
            log_success "Homebrew installed successfully: $brew_version"
        else
            log_error "Homebrew installation verification failed"
            log_warning "You may need to restart your terminal or run: source $shell_profile"
            exit 1
        fi
    else
        log_error "Failed to install Homebrew"
        exit 1
    fi
}

# Install Python
install_python() {
    log_step "Installing Python..."
    
    # Check if Python 3.8+ is already installed
    if command_exists python3; then
        python_version=$(python3 --version 2>&1 | grep -oE '\d+\.\d+' | head -1)
        major=$(echo "$python_version" | cut -d. -f1)
        minor=$(echo "$python_version" | cut -d. -f2)
        
        if [[ "$major" -gt 3 ]] || [[ "$major" -eq 3 && "$minor" -ge 8 ]]; then
            log_success "Python $python_version is already installed and meets requirements."
            return
        fi
    fi
    
    # Install Python using Homebrew
    log_info "Installing Python via Homebrew..."
    if brew install python; then
        
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
    
    # Try installing with Homebrew first
    log_info "Installing mise via Homebrew..."
    if brew install mise; then
        
        # Add mise to shell profile for activation
        shell_profile=""
        if [[ -n "${BASH_VERSION:-}" ]]; then
            shell_profile="$HOME/.bash_profile"
        elif [[ -n "${ZSH_VERSION:-}" ]] || [[ "$SHELL" == */zsh ]]; then
            shell_profile="$HOME/.zshrc"
        else
            # Fallback to .profile
            shell_profile="$HOME/.profile"
        fi
        
        if [[ -n "$shell_profile" ]]; then
            if ! grep -q 'mise activate' "$shell_profile" 2>/dev/null; then
                echo '' >> "$shell_profile"
                echo '# mise activation' >> "$shell_profile"
                if [[ "$SHELL" == */zsh ]] || [[ -n "${ZSH_VERSION:-}" ]]; then
                    echo 'eval "$(mise activate zsh)"' >> "$shell_profile"
                else
                    echo 'eval "$(mise activate bash)"' >> "$shell_profile"
                fi
                log_info "Added mise activation to $shell_profile"
            fi
        fi
        
        # Verify installation
        if command_exists mise; then
            mise_version=$(mise --version)
            log_success "mise installed successfully: $mise_version"
        else
            log_error "mise installation verification failed"
            exit 1
        fi
    else
        # Fallback to curl installation
        log_warning "Homebrew installation failed, trying curl method..."
        if curl -fsSL https://mise.run | bash; then
            # Add mise to PATH for current session
            export PATH="$HOME/.local/bin:$PATH"
            
            # Verify installation
            if command_exists mise; then
                mise_version=$(mise --version)
                log_success "mise installed successfully via curl: $mise_version"
            else
                log_error "mise installation verification failed"
                exit 1
            fi
        else
            log_error "Failed to install mise"
            exit 1
        fi
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
    
    # Try installing with Homebrew first
    log_info "Installing uv via Homebrew..."
    if brew install uv; then
        
        # Verify installation
        if command_exists uv; then
            uv_version=$(uv --version)
            log_success "uv installed successfully: $uv_version"
        else
            log_error "uv installation verification failed"
            exit 1
        fi
    else
        # Fallback to curl installation
        log_warning "Homebrew installation failed, trying curl method..."
        if curl -LsSf https://astral.sh/uv/install.sh | sh; then
            
            # Add uv to PATH for current session
            export PATH="$HOME/.cargo/bin:$PATH"
            
            # Verify installation
            if command_exists uv; then
                uv_version=$(uv --version)
                log_success "uv installed successfully via curl: $uv_version"
            else
                log_error "uv installation verification failed"
                log_warning "You may need to restart your terminal"
                exit 1
            fi
        else
            log_error "Failed to install uv"
            exit 1
        fi
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
    
    # Determine shell
    if [[ "$SHELL" == */zsh ]] || [[ -n "${ZSH_VERSION:-}" ]]; then
        shell_config="~/.zshrc"
    else
        shell_config="~/.bash_profile"
    fi
    
    echo -e "${YELLOW}1. Restart your terminal or run: source $shell_config${NC}"
    echo -e "${YELLOW}2. Navigate to your gen-ibans project directory${NC}"
    echo -e "${YELLOW}3. Run 'uv sync --dev' to install project dependencies (if not already done)${NC}"
    echo -e "${YELLOW}4. Run 'uv run pytest tests/' to verify everything works${NC}"
    echo -e "${YELLOW}5. Start developing! 🚀${NC}"
    
    echo ""
    log_info "Installed tools:"
    echo -e "${YELLOW}- Homebrew: Package manager for macOS${NC}"
    echo -e "${YELLOW}- Python: Programming language runtime${NC}"
    echo -e "${YELLOW}- mise: Tool version management${NC}"
    echo -e "${YELLOW}- uv: Fast Python package manager${NC}"
    
    echo ""
    log_info "Environment setup:"
    echo -e "${YELLOW}All tools have been added to your shell profile for automatic activation.${NC}"
    echo -e "${YELLOW}Homebrew, mise, and uv should be available in new terminal sessions.${NC}"
}

# Check for required tools
check_requirements() {
    log_step "Checking system requirements..."
    
    # Check if we have curl (should be available by default on macOS)
    if ! command_exists curl; then
        log_error "curl is required but not found. Please install curl first."
        exit 1
    fi
    
    # Check if we have git (should be available via Xcode Command Line Tools)
    if ! command_exists git; then
        log_info "Git not found. Installing Xcode Command Line Tools..."
        xcode-select --install 2>/dev/null || true
        log_info "Please complete the Xcode Command Line Tools installation and re-run this script."
        exit 1
    fi
    
    # Check if we have sufficient macOS version for development
    log_success "System requirements check passed!"
}

# Main function
main() {
    log_info "🚀 Starting gen-ibans development environment setup for macOS..."
    log_info "This script will install: Homebrew, Python, mise, and uv"
    echo ""
    
    # System checks
    check_macos
    check_requirements
    
    # Install tools
    install_homebrew
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