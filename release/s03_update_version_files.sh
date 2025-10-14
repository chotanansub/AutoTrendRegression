#!/bin/bash

# Update Version Files

source "$(dirname "$0")/utils.sh"

log_step "[3/6] Checking local version files..."

TARGET_VERSION=$(cat /tmp/autotrend_target_version)

VERSION_SETUP=$(grep "version=" setup.py | head -1 | sed "s/.*version='\([0-9.]*\)'.*/\1/")
VERSION_PYPROJECT=$(grep "version = " pyproject.toml | head -1 | sed 's/.*version = "\([0-9.]*\)".*/\1/')
VERSION_INIT=$(grep "__version__ = " autotrend/__init__.py | sed "s/.*__version__ = '\([0-9.]*\)'.*/\1/")

echo "  Current versions:"
echo "    setup.py:              ${VERSION_SETUP}"
echo "    pyproject.toml:        ${VERSION_PYPROJECT}"
echo "    autotrend/__init__.py: ${VERSION_INIT}"
echo ""
echo "  Target version:          ${GREEN}${TARGET_VERSION}${NC}"
echo ""

# Check if all versions match target version
if [ "$VERSION_SETUP" != "$TARGET_VERSION" ] || [ "$VERSION_PYPROJECT" != "$TARGET_VERSION" ] || [ "$VERSION_INIT" != "$TARGET_VERSION" ]; then
    log_warning "Version files need to be updated to ${TARGET_VERSION}"
    echo ""
    
    if ask_yes_no "Update version files automatically?"; then
        echo ""
        log_info "Updating version files..."
        
        # Detect OS for sed compatibility
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/version='[0-9.]*'/version='$TARGET_VERSION'/" setup.py
            sed -i '' "s/version = \"[0-9.]*\"/version = \"$TARGET_VERSION\"/" pyproject.toml
            sed -i '' "s/__version__ = '[0-9.]*'/__version__ = '$TARGET_VERSION'/" autotrend/__init__.py
        else
            # Linux
            sed -i "s/version='[0-9.]*'/version='$TARGET_VERSION'/" setup.py
            sed -i "s/version = \"[0-9.]*\"/version = \"$TARGET_VERSION\"/" pyproject.toml
            sed -i "s/__version__ = '[0-9.]*'/__version__ = '$TARGET_VERSION'/" autotrend/__init__.py
        fi
        
        log_success "Updated setup.py"
        log_success "Updated pyproject.toml"
        log_success "Updated autotrend/__init__.py"
        echo ""
    else
        echo ""
        echo -e "${YELLOW}Cancelled${NC}"
        echo ""
        echo "Update version files manually:"
        echo "  setup.py: version='$TARGET_VERSION'"
        echo "  pyproject.toml: version = \"$TARGET_VERSION\""
        echo "  autotrend/__init__.py: __version__ = '$TARGET_VERSION'"
        exit 1
    fi
else
    log_success "All version files already match target: ${TARGET_VERSION}"
    echo ""
fi