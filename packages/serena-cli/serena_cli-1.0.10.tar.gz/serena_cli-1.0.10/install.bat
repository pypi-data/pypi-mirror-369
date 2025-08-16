@echo off
REM Serena CLI - One-Click Installation Script
REM For Windows systems

setlocal enabledelayedexpansion

REM Set title
title Serena CLI - One-Click Installation

REM Colors for output (Windows 10+)
set "BLUE=[94m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

REM Print colored output
:print_info
echo %BLUE%🔍 %~1%NC%
goto :eof

:print_success
echo %GREEN%✅ %~1%NC%
goto :eof

:print_warning
echo %YELLOW%⚠️  %~1%NC%
goto :eof

:print_error
echo %RED%❌ %~1%NC%
goto :eof

:print_banner
echo ============================================================
echo 🚀 Serena CLI - One-Click Installation
echo ============================================================
echo.
goto :eof

REM Check if command exists
:command_exists
where %1 >nul 2>&1
if %errorlevel% equ 0 (
    set "exists=true"
) else (
    set "exists=false"
)
goto :eof

REM Check Python version
:check_python
call :print_info "Checking Python version..."

if exist "python.exe" (
    set "PYTHON_CMD=python"
) else if exist "python3.exe" (
    set "PYTHON_CMD=python3"
) else (
    call :print_error "Python not found. Please install Python 3.8+ first."
    pause
    exit /b 1
)

REM Check version
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo    Current Python version: %PYTHON_VERSION%

for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set "PYTHON_MAJOR=%%a"
    set "PYTHON_MINOR=%%b"
)

REM Remove "Python " prefix if present
set "PYTHON_MAJOR=%PYTHON_MAJOR:Python =%"
set "PYTHON_MINOR=%PYTHON_MINOR:~0,1%"

if %PYTHON_MAJOR% equ 3 (
    if %PYTHON_MINOR% geq 8 (
        call :print_success "Python version is compatible"
    ) else (
        call :print_error "Python 3.8+ is required. Current: %PYTHON_VERSION%"
        pause
        exit /b 1
    )
) else (
    call :print_error "Python 3.8+ is required. Current: %PYTHON_VERSION%"
    pause
    exit /b 1
)
goto :eof

REM Check system
:check_system
call :print_info "Checking system information..."

echo    Operating System: Windows
call :print_success "Operating system is supported"
goto :eof

REM Check pip
:check_pip
call :print_info "Checking pip availability..."

if exist "pip.exe" (
    set "PIP_CMD=pip"
    call :print_success "pip is available"
) else if exist "pip3.exe" (
    set "PIP_CMD=pip3"
    call :print_success "pip3 is available"
) else (
    call :print_info "pip not found, attempting to install..."
    
    %PYTHON_CMD% -m ensurepip --upgrade >nul 2>&1
    if %errorlevel% equ 0 (
        set "PIP_CMD=%PYTHON_CMD% -m pip"
        call :print_success "pip installed successfully"
    ) else (
        call :print_error "Failed to install pip. Please install manually."
        pause
        exit /b 1
    )
)
goto :eof

REM Create virtual environment
:create_venv
call :print_info "Setting up virtual environment..."

if exist "venv" (
    call :print_success "Virtual environment already exists"
) else (
    echo    Creating virtual environment...
    %PYTHON_CMD% -m venv venv >nul 2>&1
    if %errorlevel% equ 0 (
        call :print_success "Virtual environment created successfully"
    ) else (
        call :print_error "Failed to create virtual environment"
        pause
        exit /b 1
    )
)
goto :eof

REM Activate virtual environment
:activate_venv
call :print_info "Activating virtual environment..."

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    call :print_success "Virtual environment activated"
    echo    💡 Run 'venv\Scripts\activate.bat' to activate manually
) else (
    call :print_error "Virtual environment activation failed"
    pause
    exit /b 1
)
goto :eof

REM Install dependencies
:install_deps
call :print_info "Installing dependencies..."

%PIP_CMD% install -e . >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Dependencies installed successfully"
) else (
    call :print_error "Failed to install dependencies"
    pause
    exit /b 1
)
goto :eof

REM Verify installation
:verify_install
call :print_info "Verifying installation..."

python -m serena_cli.cli --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python -m serena_cli.cli --version') do set "VERSION=%%i"
    call :print_success "Serena CLI installed successfully"
    echo    Version: %VERSION%
) else (
    call :print_error "Installation verification failed"
    pause
    exit /b 1
)
goto :eof

REM Create convenient batch file
:create_batch
call :print_info "Creating convenient batch file..."

(
echo @echo off
echo REM Serena CLI wrapper batch file
echo.
echo REM Get the directory where this batch file is located
echo set "SCRIPT_DIR=%%~dp0"
echo.
echo REM Activate virtual environment if it exists
echo if exist "%%SCRIPT_DIR%%venv\Scripts\activate.bat" ^(
echo     call "%%SCRIPT_DIR%%venv\Scripts\activate.bat"
echo ^)
echo.
echo REM Run Serena CLI
echo python -m serena_cli.cli %%*
) > serena-cli.bat

call :print_success "Created serena-cli.bat"
goto :eof

REM Show usage instructions
:show_instructions
echo.
echo ============================================================
echo 🎉 Installation Complete!
echo ============================================================

echo.
echo 📚 Quick Start:
echo    1. Activate virtual environment:
echo       venv\Scripts\activate.bat
echo.
echo    2. Test installation:
echo       serena-cli.bat --version
echo       serena-cli.bat --help
echo.
echo    3. Check environment:
echo       serena-cli.bat check-env
echo.
echo    4. Get project information:
echo       serena-cli.bat info

echo.
echo 🔧 Available Commands:
echo    serena-cli.bat check-env    - Check environment compatibility
echo    serena-cli.bat info         - Get project information
echo    serena-cli.bat status       - Query Serena status
echo    serena-cli.bat config       - Edit configuration
echo    serena-cli.bat enable       - Enable Serena in project
echo    serena-cli.bat mcp-tools    - Show MCP tools

echo.
echo 📖 Documentation:
echo    README.md               - Project overview
echo    QUICK_START.md          - Quick start guide ^(Chinese^)
echo    QUICK_START_EN.md       - Quick start guide ^(English^)
echo    usage_instructions.md   - Detailed usage ^(Chinese^)
echo    usage_instructions_EN.md- Detailed usage ^(English^)

echo.
echo 💡 Tips:
echo    - All CLI functions work immediately
echo    - MCP server has compatibility issues with Python 3.13
echo    - Use CLI commands as primary interface
echo    - Check logs in %%USERPROFILE%%\.serena-cli\logs\ for debugging

echo.
echo 🚀 You're ready to use Serena CLI!
echo.
echo 💡 To use from anywhere, add to PATH:
echo    setx PATH "%%PATH%%;%CD%"
goto :eof

REM Main installation function
:main
call :print_banner

REM Check prerequisites
call :check_python
call :check_system
call :check_pip

REM Setup environment
call :create_venv
call :activate_venv

REM Install project
call :install_deps

REM Verify installation
call :verify_install

REM Create convenience batch file
call :create_batch

REM Show usage instructions
call :show_instructions

echo.
echo Press any key to exit...
pause >nul
goto :eof

REM Run main function
call :main
