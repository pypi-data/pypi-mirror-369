#!/bin/bash

# Package Installation Test Script
# This script tests installing and using packages from PyPI or TestPyPI

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate environment
validate_environment() {
    print_info "Validating environment..."

    # Check if uv is installed
    if ! command_exists uv; then
        print_error "uv is not installed. Please install it first."
        exit 1
    fi

    print_success "Environment validation passed"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [PACKAGE_NAME] [VERSION]"
    echo ""
    echo "Target Options (choose one):"
    echo "  --testpypi          Test installation from TestPyPI"
    echo "  --pypi              Test installation from production PyPI"
    echo ""
    echo "Additional Options:"
    echo "  --clean             Clean up test environment after testing"
    echo "  --keep              Keep test environment for inspection (default)"
    echo "  --verbose           Show detailed output"
    echo "  --help              Show this help message"
    echo ""
    echo "Arguments:"
    echo "  PACKAGE_NAME        Package name to test (default: zenodotos)"
    echo "  VERSION             Specific version to test (default: latest)"
    echo ""
    echo "Examples:"
    echo "  $0 --testpypi zenodotos 0.2.1     # Test specific version from TestPyPI"
    echo "  $0 --pypi zenodotos               # Test latest version from PyPI"
    echo "  $0 --testpypi --clean 0.2.1       # Test and clean up"
    echo ""
    echo "Note: Only one target option (--testpypi or --pypi) can be used at a time."
    echo "      If no target is specified, TestPyPI will be used by default."
}

# Parse command line arguments
TEST_TESTPYPI=false
TEST_PYPI=false
CLEAN_AFTER=false
VERBOSE=false
PACKAGE_NAME="zenodotos"
VERSION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --testpypi)
            if [ "$TEST_PYPI" = true ]; then
                print_error "Cannot use --testpypi and --pypi together. Use only one target."
                show_usage
                exit 1
            fi
            TEST_TESTPYPI=true
            shift
            ;;
        --pypi)
            if [ "$TEST_TESTPYPI" = true ]; then
                print_error "Cannot use --testpypi and --pypi together. Use only one target."
                show_usage
                exit 1
            fi
            TEST_PYPI=true
            shift
            ;;
        --clean)
            CLEAN_AFTER=true
            shift
            ;;
        --keep)
            CLEAN_AFTER=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        -*)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            # If this looks like a version number and we don't have a version yet, treat it as version
            if [ -z "$VERSION" ] && [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+ ]]; then
                VERSION="$1"
            elif [ -z "$PACKAGE_NAME" ] || [ "$PACKAGE_NAME" = "zenodotos" ]; then
                PACKAGE_NAME="$1"
            elif [ -z "$VERSION" ]; then
                VERSION="$1"
            else
                print_error "Too many arguments: $1"
                show_usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Set default behavior if no target specified
if [ "$TEST_TESTPYPI" = false ] && [ "$TEST_PYPI" = false ]; then
    TEST_TESTPYPI=true
fi

# Main execution
print_info "Starting package installation test..."
print_info "Package: $PACKAGE_NAME"
if [ -n "$VERSION" ]; then
    print_info "Version: $VERSION"
else
    print_info "Version: latest"
fi

# Determine target index
if [ "$TEST_TESTPYPI" = true ]; then
    INDEX_URL="https://test.pypi.org/simple/"
    INDEX_NAME="TestPyPI"
    print_info "Target: TestPyPI"
elif [ "$TEST_PYPI" = true ]; then
    INDEX_URL="https://pypi.org/simple/"
    INDEX_NAME="PyPI"
    print_info "Target: PyPI"
fi

# Validate environment
validate_environment

# Create temporary directory for testing
TEST_DIR=$(mktemp -d)
print_info "Created test directory: $TEST_DIR"

# Function to clean up
cleanup() {
    if [ "$CLEAN_AFTER" = true ]; then
        print_info "Cleaning up test directory..."
        rm -rf "$TEST_DIR"
        print_success "Test directory cleaned up"
    else
        print_info "Test directory preserved at: $TEST_DIR"
        print_info "You can inspect it manually or run with --clean to remove it"
    fi
}

# Set up trap to clean up on exit
trap cleanup EXIT

# Change to test directory
cd "$TEST_DIR"
print_info "Changed to test directory: $(pwd)"

# Create virtual environment
print_info "Creating virtual environment..."
uv venv
print_success "Virtual environment created"

# Initialize uv project
print_info "Initializing uv project..."
uv init .
print_success "Project initialized"

# Install package with retry logic
print_info "Installing $PACKAGE_NAME from $INDEX_NAME..."
MAX_RETRIES=5
RETRY_DELAY=60

for attempt in $(seq 1 $MAX_RETRIES); do
    print_info "Installation attempt $attempt of $MAX_RETRIES..."

    if [ -n "$VERSION" ]; then
        print_info "Installing specific version: $VERSION"
        if uv add --index "$INDEX_URL" --index-strategy unsafe-best-match "$PACKAGE_NAME==$VERSION" 2>&1; then
            print_success "Package installed successfully on attempt $attempt"
            break
        else
            print_warning "Installation failed on attempt $attempt"
        fi
    else
        print_info "Installing latest version"
        if uv add --index "$INDEX_URL" --index-strategy unsafe-best-match "$PACKAGE_NAME" 2>&1; then
            print_success "Package installed successfully on attempt $attempt"
            break
        else
            print_warning "Installation failed on attempt $attempt"
        fi
    fi

    if [ $attempt -lt $MAX_RETRIES ]; then
        print_info "Waiting $RETRY_DELAY seconds before retry..."
        sleep $RETRY_DELAY
    else
        print_error "Failed to install $PACKAGE_NAME after $MAX_RETRIES attempts"
        exit 1
    fi
done

# Test basic functionality
print_info "Testing basic functionality..."

# Test help command (if it's a CLI package)
print_info "Testing '$PACKAGE_NAME --help'..."
if uv run "$PACKAGE_NAME" --help > /dev/null 2>&1; then
    print_success "$PACKAGE_NAME --help works correctly"
else
    print_warning "$PACKAGE_NAME --help failed (may not be a CLI package)"
fi

# Test specific commands for zenodotos
if [ "$PACKAGE_NAME" = "zenodotos" ]; then
    print_info "Testing zenodotos-specific commands..."

    # Test list-files help
    print_info "Testing 'zenodotos list-files --help'..."
    if uv run zenodotos list-files --help > /dev/null 2>&1; then
        print_success "zenodotos list-files --help works correctly"
    else
        print_error "zenodotos list-files --help failed"
        exit 1
    fi

    # Test get-file help
    print_info "Testing 'zenodotos get-file --help'..."
    if uv run zenodotos get-file --help > /dev/null 2>&1; then
        print_success "zenodotos get-file --help works correctly"
    else
        print_error "zenodotos get-file --help failed"
        exit 1
    fi

    # Test export help
    print_info "Testing 'zenodotos export --help'..."
    if uv run zenodotos export --help > /dev/null 2>&1; then
        print_success "zenodotos export --help works correctly"
    else
        print_error "zenodotos export --help failed"
        exit 1
    fi
fi

# Show installed package info
print_info "Installed package information:"
uv pip show "$PACKAGE_NAME"

# Test Python import
print_info "Testing Python import..."
if uv run python -c "import $PACKAGE_NAME; print('✅ $PACKAGE_NAME imported successfully')" 2>/dev/null; then
    print_success "Python import test passed"
else
    print_error "Python import test failed"
    exit 1
fi

# Test library usage (zenodotos-specific)
if [ "$PACKAGE_NAME" = "zenodotos" ]; then
    print_info "Testing library usage..."
    if uv run python -c "
from zenodotos import Zenodotos
print('✅ Zenodotos class imported successfully')
try:
    client = Zenodotos()
    print('✅ Zenodotos client created successfully')
except Exception as e:
    print(f'⚠️  Zenodotos client creation failed (expected without auth): {e}')
" 2>/dev/null; then
        print_success "Library usage test passed"
    else
        print_error "Library usage test failed"
        exit 1
    fi
fi

print_success "All $INDEX_NAME installation tests passed!"
print_info "Version tested: $(uv run pip show $PACKAGE_NAME | grep Version | cut -d' ' -f2)"

# Show what was tested
echo ""
print_info "Test Summary:"
echo "  ✅ Package installation from $INDEX_NAME"
echo "  ✅ CLI help commands"
echo "  ✅ Python import"
if [ "$PACKAGE_NAME" = "zenodotos" ]; then
    echo "  ✅ Library usage"
fi
echo "  ✅ All basic functionality"

if [ "$CLEAN_AFTER" = false ]; then
    echo ""
    print_info "Test environment preserved at: $TEST_DIR"
    print_info "You can inspect it or run additional tests manually"
fi
