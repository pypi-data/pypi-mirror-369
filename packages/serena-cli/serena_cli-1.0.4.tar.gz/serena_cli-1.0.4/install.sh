#!/bin/bash

# Serena CLI - One-Click Installation Script
# For Unix/Linux/macOS systems

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}🔍 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_banner() {
    echo "============================================================"
    echo "🚀 Serena CLI - One-Click Installation"
    echo "============================================================"
    echo
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python() {
    print_info "Checking Python version..."
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python not found. Please install Python 3.8+ first."
        exit 1
    fi
    
    # Check version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    echo "   Current Python version: $PYTHON_VERSION"
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        print_success "Python version is compatible"
    else
        print_error "Python 3.8+ is required. Current: $PYTHON_VERSION"
        exit 1
    fi
}

# Check system
check_system() {
    print_info "Checking system information..."
    
    OS=$(uname -s)
    echo "   Operating System: $OS"
    
    if [ "$OS" = "Darwin" ] || [ "$OS" = "Linux" ]; then
        print_success "Operating system is supported"
    else
        print_warning "Operating system may not be fully supported"
    fi
}

# Check pip
check_pip() {
    print_info "Checking pip availability..."
    
    if command_exists pip3; then
        PIP_CMD="pip3"
        print_success "pip3 is available"
    elif command_exists pip; then
        PIP_CMD="pip"
        print_success "pip is available"
    else
        print_info "pip not found, attempting to install..."
        
        if $PYTHON_CMD -m ensurepip --upgrade; then
            PIP_CMD="$PYTHON_CMD -m pip"
            print_success "pip installed successfully"
        else
            print_error "Failed to install pip. Please install manually."
            exit 1
        fi
    fi
}

# Create virtual environment
create_venv() {
    print_info "Setting up virtual environment..."
    
    if [ -d "venv" ]; then
        print_success "Virtual environment already exists"
    else
        echo "   Creating virtual environment..."
        if $PYTHON_CMD -m venv venv; then
            print_success "Virtual environment created successfully"
        else
            print_error "Failed to create virtual environment"
            exit 1
        fi
    fi
}

# Activate virtual environment
activate_venv() {
    print_info "Activating virtual environment..."
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Virtual environment activated"
        echo "   💡 Run 'source venv/bin/activate' to activate manually"
    else
        print_error "Virtual environment activation failed"
        exit 1
    fi
}

# Install dependencies
install_deps() {
    print_info "Installing dependencies..."
    
    if $PIP_CMD install -e .; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
}

# Verify installation
verify_install() {
    print_info "Verifying installation..."
    
    if python -m serena_cli.cli --version >/dev/null 2>&1; then
        VERSION=$(python -m serena_cli.cli --version)
        print_success "Serena CLI installed successfully"
        echo "   Version: $VERSION"
    else
        print_error "Installation verification failed"
        exit 1
    fi
}

# Create convenient script
create_script() {
    print_info "Creating convenient script..."
    
    cat > serena-cli << 'EOF'
#!/bin/bash
# Serena CLI wrapper script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment if it exists
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Run Serena CLI
python -m serena_cli.cli "$@"
EOF
    
    chmod +x serena-cli
    print_success "Created serena-cli script"
}

# Show usage instructions
show_instructions() {
    echo
    echo "============================================================"
    echo "🎉 Installation Complete!"
    echo "============================================================"
    
    echo
    echo "📚 Quick Start:"
    echo "   1. Activate virtual environment:"
    echo "      source venv/bin/activate"
    echo
    echo "   2. Test installation:"
    echo "      ./serena-cli --version"
    echo "      ./serena-cli --help"
    echo
    echo "   3. Check environment:"
    echo "      ./serena-cli check-env"
    echo
    echo "   4. Get project information:"
    echo "      ./serena-cli info"
    
    echo
    echo "🔧 Available Commands:"
    echo "   ./serena-cli check-env    - Check environment compatibility"
    echo "   ./serena-cli info         - Get project information"
    echo "   ./serena-cli status       - Query Serena status"
    echo "   ./serena-cli config       - Edit configuration"
    echo "   ./serena-cli enable       - Enable Serena in project"
    echo "   ./serena-cli mcp-tools    - Show MCP tools"
    
    echo
    echo "📖 Documentation:"
    echo "   README.md               - Project overview"
    echo "   QUICK_START.md          - Quick start guide (Chinese)"
    echo "   QUICK_START_EN.md       - Quick start guide (English)"
    echo "   usage_instructions.md   - Detailed usage (Chinese)"
    echo "   usage_instructions_EN.md- Detailed usage (English)"
    
    echo
    echo "💡 Tips:"
    echo "   - All CLI functions work immediately"
    echo "   - MCP server has compatibility issues with Python 3.13"
    echo "   - Use CLI commands as primary interface"
    echo "   - Check logs in ~/.serena-cli/logs/ for debugging"
    
    echo
    echo "🚀 You're ready to use Serena CLI!"
    echo
    echo "💡 To use from anywhere, add to PATH:"
    echo "   export PATH=\"\$PATH:$(pwd)\""
    echo "   echo 'export PATH=\"\$PATH:$(pwd)\"' >> ~/.bashrc"
}

# Main installation function
main() {
    print_banner
    
    # Check prerequisites
    check_python
    check_system
    check_pip
    
    # Setup environment
    create_venv
    activate_venv
    
    # Install project
    install_deps
    
    # Verify installation
    verify_install
    
    # Create convenience script
    create_script
    
    # Show usage instructions
    show_instructions
}

# Run main function
main "$@"
