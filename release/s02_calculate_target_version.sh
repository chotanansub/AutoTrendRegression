#!/bin/bash

# Calculate Target Version

source "$(dirname "$0")/utils.sh"

log_step "[2/6] Calculating target version..."

UPDATE_TYPE=$1

if [ -z "$UPDATE_TYPE" ]; then
    log_error "Usage: $0 {patch|minor|major|X.Y.Z}"
    echo ""
    echo "Examples:"
    echo "  $0 patch   # Increment patch version"
    echo "  $0 minor   # Increment minor version"
    echo "  $0 major   # Increment major version"
    echo "  $0 0.2.5   # Set specific version"
    exit 1
fi

# Read PyPI version from previous step
PYPI_VERSION=$(cat /tmp/autotrend_pypi_version)

# Parse PyPI version
IFS='.' read -r -a PYPI_PARTS <<< "$PYPI_VERSION"
MAJOR="${PYPI_PARTS[0]}"
MINOR="${PYPI_PARTS[1]}"
PATCH="${PYPI_PARTS[2]}"

# Calculate target version
case $UPDATE_TYPE in
    patch)
        TARGET_VERSION="$MAJOR.$MINOR.$((PATCH+1))"
        echo "  Update type: ${BLUE}PATCH${NC}"
        ;;
    minor)
        TARGET_VERSION="$MAJOR.$((MINOR+1)).0"
        echo "  Update type: ${BLUE}MINOR${NC}"
        ;;
    major)
        TARGET_VERSION="$((MAJOR+1)).0.0"
        echo "  Update type: ${BLUE}MAJOR${NC}"
        ;;
    [0-9]*.[0-9]*.[0-9]*)
        TARGET_VERSION="$UPDATE_TYPE"
        echo "  Update type: ${BLUE}SPECIFIC${NC}"
        ;;
    *)
        log_error "Invalid argument: $UPDATE_TYPE"
        echo "Use: patch, minor, major, or specific version (e.g., 0.2.5)"
        exit 1
        ;;
esac

echo "  PyPI version:   ${PYPI_VERSION}"
echo "  Target version: ${GREEN}${TARGET_VERSION}${NC}"
echo ""

# Validate target version is greater than PyPI version
if [ "$PYPI_VERSION" != "0.0.0" ]; then
    if ! printf '%s\n' "$PYPI_VERSION" "$TARGET_VERSION" | sort -V -C; then
        log_error "Target version ($TARGET_VERSION) must be greater than PyPI version ($PYPI_VERSION)"
        exit 1
    fi
    
    # Check if versions are equal
    if [ "$TARGET_VERSION" = "$PYPI_VERSION" ]; then
        log_error "Target version ($TARGET_VERSION) already exists on PyPI!"
        echo "  You must use a higher version number."
        exit 1
    fi
fi

log_success "Target version is valid"
echo ""

# Export for use in other scripts
echo "$TARGET_VERSION" > /tmp/autotrend_target_version
echo "v$TARGET_VERSION" > /tmp/autotrend_tag