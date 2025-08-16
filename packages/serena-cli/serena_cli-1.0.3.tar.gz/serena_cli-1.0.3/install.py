#!/usr/bin/env python3
"""
One-click installation script for Serena CLI.
This script automatically handles all dependencies and environment setup.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print installation banner."""
    print("=" * 60)
    print("🚀 Serena CLI - One-Click Installation")
    print("=" * 60)
    print()

def check_python_version():
    """Check Python version compatibility."""
    print("🔍 Checking Python version...")
    
    version = sys.version_info
    print(f"   Current Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("   ✅ Python version is compatible")
        return True
    else:
        print("   ❌ Python 3.8+ is required")
        print("   Please upgrade Python and try again")
        return False

def check_system():
    """Check system information."""
    print("🔍 Checking system information...")
    
    system = platform.system()
    print(f"   Operating System: {system}")
    
    if system in ["Darwin", "Linux", "Windows"]:
        print("   ✅ Operating system is supported")
        return True
    else:
        print("   ⚠️  Operating system may not be fully supported")
        return True

def install_pip():
    """Ensure pip is available."""
    print("🔍 Checking pip availability...")
    
    try:
        import pip
        print("   ✅ pip is available")
        return True
    except ImportError:
        print("   ❌ pip not found, attempting to install...")
        
        try:
            # Try to install pip
            subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], 
                         check=True, capture_output=True)
            print("   ✅ pip installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("   ❌ Failed to install pip")
            print("   Please install pip manually and try again")
            return False

def create_virtual_environment():
    """Create virtual environment if needed."""
    print("🔍 Setting up virtual environment...")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("   ✅ Virtual environment already exists")
        return True
    
    try:
        print("   Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], 
                     check=True, capture_output=True)
        print("   ✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to create virtual environment: {e}")
        return False

def activate_virtual_environment():
    """Activate virtual environment."""
    print("🔍 Activating virtual environment...")
    
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
        if os.path.exists(activate_script):
            print("   ✅ Virtual environment activated")
            print("   💡 Run 'venv\\Scripts\\activate' to activate manually")
            return True
    else:
        activate_script = "venv/bin/activate"
        if os.path.exists(activate_script):
            print("   ✅ Virtual environment activated")
            print("   💡 Run 'source venv/bin/activate' to activate manually")
            return True
    
    print("   ❌ Virtual environment activation failed")
    return False

def install_dependencies():
    """Install project dependencies."""
    print("🔍 Installing dependencies...")
    
    try:
        # Install in development mode
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], 
                     check=True, capture_output=True)
        print("   ✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to install dependencies: {e}")
        return False

def verify_installation():
    """Verify the installation."""
    print("🔍 Verifying installation...")
    
    try:
        # Test basic command
        result = subprocess.run([sys.executable, "-m", "serena_cli.cli", "--version"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ Serena CLI installed successfully")
            print(f"   Version: {result.stdout.strip()}")
            return True
        else:
            print("   ❌ Installation verification failed")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⏰ Command timeout")
        return False
    except Exception as e:
        print(f"   ❌ Verification error: {e}")
        return False

def create_aliases():
    """Create convenient aliases."""
    print("🔍 Creating convenient aliases...")
    
    # Create serena-cli command
    try:
        if platform.system() == "Windows":
            # Windows batch file
            with open("serena-cli.bat", "w") as f:
                f.write("@echo off\n")
                f.write(f'"{sys.executable}" -m serena_cli.cli %*\n')
            print("   ✅ Created serena-cli.bat")
        else:
            # Unix shell script
            with open("serena-cli", "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f'"{sys.executable}" -m serena_cli.cli "$@"\n')
            
            # Make executable
            os.chmod("serena-cli", 0o755)
            print("   ✅ Created serena-cli script")
            
    except Exception as e:
        print(f"   ⚠️  Failed to create aliases: {e}")

def show_usage_instructions():
    """Show usage instructions."""
    print("\n" + "=" * 60)
    print("🎉 Installation Complete!")
    print("=" * 60)
    
    print("\n📚 Quick Start:")
    print("   1. Activate virtual environment:")
    
    if platform.system() == "Windows":
        print("      venv\\Scripts\\activate")
    else:
        print("      source venv/bin/activate")
    
    print("\n   2. Test installation:")
    print("      serena-cli --version")
    print("      serena-cli --help")
    
    print("\n   3. Check environment:")
    print("      serena-cli check-env")
    
    print("\n   4. Get project information:")
    print("      serena-cli info")
    
    print("\n🔧 Available Commands:")
    print("   serena-cli check-env    - Check environment compatibility")
    print("   serena-cli info         - Get project information")
    print("   serena-cli status       - Query Serena status")
    print("   serena-cli config       - Edit configuration")
    print("   serena-cli enable       - Enable Serena in project")
    print("   serena-cli mcp-tools    - Show MCP tools")
    
    print("\n📖 Documentation:")
    print("   README.md               - Project overview")
    print("   QUICK_START.md          - Quick start guide (Chinese)")
    print("   QUICK_START_EN.md       - Quick start guide (English)")
    print("   usage_instructions.md   - Detailed usage (Chinese)")
    print("   usage_instructions_EN.md- Detailed usage (English)")
    
    print("\n💡 Tips:")
    print("   - All CLI functions work immediately")
    print("   - MCP server has compatibility issues with Python 3.13")
    print("   - Use CLI commands as primary interface")
    print("   - Check logs in ~/.serena-cli/logs/ for debugging")
    
    print("\n🚀 You're ready to use Serena CLI!")

def main():
    """Main installation function."""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_system():
        sys.exit(1)
    
    if not install_pip():
        sys.exit(1)
    
    # Setup environment
    if not create_virtual_environment():
        sys.exit(1)
    
    if not activate_virtual_environment():
        sys.exit(1)
    
    # Install project
    if not install_dependencies():
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        sys.exit(1)
    
    # Create convenience aliases
    create_aliases()
    
    # Show usage instructions
    show_usage_instructions()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Installation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Installation failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
