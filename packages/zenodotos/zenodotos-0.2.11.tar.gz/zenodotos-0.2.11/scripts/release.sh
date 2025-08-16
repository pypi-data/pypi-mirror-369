#!/bin/bash

# Manual Release Script for Zenodotos
# This script handles building and publishing to PyPI (TestPyPI or production)
# For verification and testing, use the separate availability and installation scripts

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

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo -e "${BLUE}ℹ️  Loading environment variables from .env file...${NC}"
    export $(grep -v '^#' .env | xargs)
fi

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

    # Check if we're in the right directory
    if [ ! -f "pyproject.toml" ]; then
        print_error "pyproject.toml not found. Please run this script from the project root."
        exit 1
    fi

    # Check for appropriate token based on target
    if [ "$PUBLISH_TARGET" = "test" ]; then
        if [ -z "$TEST_PYPI_TOKEN" ]; then
            print_error "TEST_PYPI_TOKEN environment variable is not set."
            print_info "Please set it with: export TEST_PYPI_TOKEN=your_test_pypi_token"
            exit 1
        fi
    elif [ "$PUBLISH_TARGET" = "production" ]; then
        if [ -z "$PYPI_TOKEN" ]; then
            print_error "PYPI_TOKEN environment variable is not set."
            print_info "Please set it with: export PYPI_TOKEN=your_production_pypi_token"
            exit 1
        fi
    fi

    print_success "Environment validation passed"
}

# Function to get current version
get_current_version() {
    # For dynamic versioning, get version from Git tag
    # Remove 'v' prefix from the current Git tag
    git describe --tags --abbrev=0 | sed 's/^v//'
}

# Function to build package
build_package() {
    print_info "Building package..."

    # Clean previous builds
    rm -rf dist/ build/ *.egg-info/

    # Build package
    uv build

    # For dynamic versioning, check if any package was built successfully
    # The exact filename depends on the version from Git tag
    if ls dist/zenodotos-*.tar.gz 1> /dev/null 2>&1; then
        print_success "Package built successfully"
        # Show the actual built package name
        BUILT_PACKAGE=$(ls dist/zenodotos-*.tar.gz | head -1)
        print_info "Built package: $(basename "$BUILT_PACKAGE")"
    else
        print_error "Package build failed"
        exit 1
    fi
}

# Function to publish to TestPyPI
publish_to_test_pypi() {
    print_info "Publishing to TestPyPI..."

    # Publish to TestPyPI
    uv publish --publish-url https://test.pypi.org/legacy/ --check-url https://test.pypi.org/simple/ --token "$TEST_PYPI_TOKEN"

    print_success "Package published to TestPyPI"

    # Wait a moment for upload to complete
    print_info "Waiting for upload to complete..."
    sleep 5

    print_success "Package published to TestPyPI successfully!"
    print_info "Package upload completed. Availability may take a few minutes to propagate."
}

# Function to publish to production PyPI
publish_to_production_pypi() {
    if [ -z "$PYPI_TOKEN" ]; then
        print_warning "Skipping production PyPI publishing (PYPI_TOKEN not set)"
        return
    fi

    print_info "Publishing to production PyPI..."

    # Publish to production PyPI
    uv publish --publish-url https://upload.pypi.org/legacy/ --check-url https://pypi.org/simple/ --token "$PYPI_TOKEN"

    print_success "Package published to production PyPI"

    # Wait a moment for upload to complete
    print_info "Waiting for upload to complete..."
    sleep 5

    print_success "Package published to PyPI successfully!"
    print_info "Package upload completed. Availability may take a few minutes to propagate."
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Target Options (choose one):"
    echo "  --testpypi      Publish to TestPyPI only"
    echo "  --pypi          Publish to production PyPI only"
    echo ""
    echo "Additional Options:"
    echo "  --help          Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  TEST_PYPI_TOKEN    Your TestPyPI API token (required for --testpypi)"
    echo "  PYPI_TOKEN         Your production PyPI API token (required for --pypi)"
    echo ""
    echo "Examples:"
echo "  export TEST_PYPI_TOKEN=your_test_token"
echo "  ./scripts/release.sh --testpypi"
echo ""
echo "  export PYPI_TOKEN=your_production_token"
echo "  ./scripts/release.sh --pypi"
echo ""
echo "Note: To publish to both indexes, run the script twice:"
echo "  ./scripts/release.sh --testpypi && ./scripts/release.sh --pypi"
echo ""
echo "Decoupled Workflow:"
echo "  1. Publish: ./scripts/release.sh --testpypi"
echo "  2. Verify: ./scripts/check-package-availability.sh --testpypi --wait <version>"
echo "  3. Test: ./scripts/test-package-install.sh --testpypi <version>"
}

# Parse command line arguments
PUBLISH_TESTPYPI=false
PUBLISH_PYPI=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --testpypi)
            if [ "$PUBLISH_PYPI" = true ]; then
                print_error "Cannot use --testpypi and --pypi together. Use only one target."
                show_usage
                exit 1
            fi
            PUBLISH_TESTPYPI=true
            shift
            ;;
        --pypi)
            if [ "$PUBLISH_TESTPYPI" = true ]; then
                print_error "Cannot use --testpypi and --pypi together. Use only one target."
                show_usage
                exit 1
            fi
            PUBLISH_PYPI=true
            shift
            ;;

        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate that a target was specified
if [ "$PUBLISH_TESTPYPI" = false ] && [ "$PUBLISH_PYPI" = false ]; then
    print_error "No publish target specified. Use --testpypi or --pypi"
    show_usage
    exit 1
fi

# Main execution
print_info "Starting Zenodotos release process..."

# Get version from Git tag for dynamic versioning
VERSION=$(get_current_version)
if [ -z "$VERSION" ]; then
    print_error "No Git tag found. Please ensure you're on a tagged commit for releases."
    print_info "For development builds, use: git tag v0.2.8 && git push origin v0.2.8"
    exit 1
fi

print_info "Current version: $VERSION"
print_info "Note: Package version will be $VERSION from Git tag v$VERSION"

# Validate environment
validate_environment

# Build package
build_package

# Publish to specified target
if [ "$PUBLISH_TESTPYPI" = true ]; then
    print_info "Publishing to TestPyPI..."
    publish_to_test_pypi
    print_success "TestPyPI release completed successfully!"
    print_info "Version $VERSION is now available on TestPyPI"
    echo ""
    print_info "📋 Next Steps:"
    print_info "  • Check availability: ./scripts/check-package-availability.sh --testpypi --wait $VERSION"
    print_info "  • Test installation: ./scripts/test-package-install.sh --testpypi $VERSION"
    print_info "  • View deployment times: ./scripts/check-package-availability.sh --deployment-times"
fi

if [ "$PUBLISH_PYPI" = true ]; then
    print_info "Publishing to production PyPI..."
    publish_to_production_pypi
    print_success "Production PyPI release completed successfully!"
    print_info "Version $VERSION is now available on production PyPI"
    echo ""
    print_info "📋 Next Steps:"
    print_info "  • Check availability: ./scripts/check-package-availability.sh --pypi --wait $VERSION"
    print_info "  • Test installation: pip install zenodotos==$VERSION"
    print_info "  • View deployment times: ./scripts/check-package-availability.sh --deployment-times"
fi
