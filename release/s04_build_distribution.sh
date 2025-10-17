#!/bin/bash

# Build Distribution Files

source "$(dirname "$0")/utils.sh"

log_step "[4/6] Building distribution files..."

TARGET_VERSION=$(cat /tmp/autotrend_target_version)

DIST_DIR="dist"
WHEEL_FILE="${DIST_DIR}/autotrend-${TARGET_VERSION}-py3-none-any.whl"
TARBALL_FILE="${DIST_DIR}/autotrend-${TARGET_VERSION}.tar.gz"

build_distribution() {
    log_info "Building distribution files..."
    
    # Clean old builds
    rm -rf build/ dist/ *.egg-info
    
    # Build package
    python setup.py sdist bdist_wheel
    
    if [ $? -eq 0 ]; then
        log_success "Build completed"
        
        # Verify files were created
        if [ -f "$WHEEL_FILE" ] && [ -f "$TARBALL_FILE" ]; then
            log_success "Distribution files created"
            echo "$WHEEL_FILE" > /tmp/autotrend_wheel_file
            echo "$TARBALL_FILE" > /tmp/autotrend_tarball_file
        else
            log_error "Build succeeded but files not found"
            exit 1
        fi
    else
        log_error "Build failed"
        exit 1
    fi
}

# Check if distribution files already exist
if [ -f "$WHEEL_FILE" ] && [ -f "$TARBALL_FILE" ]; then
    log_success "Distribution files already exist"
    echo "  ✓ ${WHEEL_FILE}"
    echo "  ✓ ${TARBALL_FILE}"
    echo ""
    
    if ask_yes_no "Rebuild distribution files?"; then
        echo ""
        build_distribution
    else
        log_info "Skipping build, using existing files"
        echo "$WHEEL_FILE" > /tmp/autotrend_wheel_file
        echo "$TARBALL_FILE" > /tmp/autotrend_tarball_file
    fi
else
    build_distribution
fi

echo ""