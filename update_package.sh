#!/bin/bash

# Make executable: chmod +x update_package.sh
#
# Usage: 
#   ./update_package.sh patch   (0.1.0 -> 0.1.1)
#   ./update_package.sh minor   (0.1.1 -> 0.2.0)
#   ./update_package.sh major   (0.2.0 -> 1.0.0)
#   ./update_package.sh 0.1.5   (set specific version)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}AutoTrend Package Update Script${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# ============================================================
# STEP 1: Check Version Consistency in Source Files
# ============================================================
echo -e "${YELLOW}[1/5] Checking version consistency...${NC}"

VERSION_SETUP=$(grep "version=" setup.py | head -1 | sed "s/.*version='\([0-9.]*\)'.*/\1/")
VERSION_PYPROJECT=$(grep "version = " pyproject.toml | head -1 | sed 's/.*version = "\([0-9.]*\)".*/\1/')
VERSION_INIT=$(grep "__version__ = " autotrend/__init__.py | sed "s/.*__version__ = '\([0-9.]*\)'.*/\1/")

echo "  setup.py:              ${VERSION_SETUP}"
echo "  pyproject.toml:        ${VERSION_PYPROJECT}"
echo "  autotrend/__init__.py: ${VERSION_INIT}"
echo ""

# Check if all versions match
if [ "$VERSION_SETUP" != "$VERSION_PYPROJECT" ] || [ "$VERSION_SETUP" != "$VERSION_INIT" ]; then
    echo -e "${RED}✗ Version mismatch detected!${NC}"
    echo ""
    
    # Find the highest version to suggest
    HIGHEST_VERSION=$(printf '%s\n' "$VERSION_SETUP" "$VERSION_PYPROJECT" "$VERSION_INIT" | sort -V | tail -n1)
    
    # Show each file with suggestion
    if [ "$VERSION_SETUP" != "$HIGHEST_VERSION" ]; then
        echo -e "  setup.py:              ${RED}$VERSION_SETUP${NC} ${YELLOW}(suggest: $HIGHEST_VERSION)${NC}"
    else
        echo -e "  setup.py:              ${GREEN}$VERSION_SETUP${NC}"
    fi
    
    if [ "$VERSION_PYPROJECT" != "$HIGHEST_VERSION" ]; then
        echo -e "  pyproject.toml:        ${RED}$VERSION_PYPROJECT${NC} ${YELLOW}(suggest: $HIGHEST_VERSION)${NC}"
    else
        echo -e "  pyproject.toml:        ${GREEN}$VERSION_PYPROJECT${NC}"
    fi
    
    if [ "$VERSION_INIT" != "$HIGHEST_VERSION" ]; then
        echo -e "  autotrend/__init__.py: ${RED}$VERSION_INIT${NC} ${YELLOW}(suggest: $HIGHEST_VERSION)${NC}"
    else
        echo -e "  autotrend/__init__.py: ${GREEN}$VERSION_INIT${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}Recommended action: Update all versions to ${GREEN}$HIGHEST_VERSION${NC}"
    echo ""
    read -p "Would you like to auto-fix all versions to $HIGHEST_VERSION? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Detect OS for sed compatibility
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/version='[0-9.]*'/version='$HIGHEST_VERSION'/" setup.py
            sed -i '' "s/version = \"[0-9.]*\"/version = \"$HIGHEST_VERSION\"/" pyproject.toml
            sed -i '' "s/__version__ = '[0-9.]*'/__version__ = '$HIGHEST_VERSION'/" autotrend/__init__.py
        else
            sed -i "s/version='[0-9.]*'/version='$HIGHEST_VERSION'/" setup.py
            sed -i "s/version = \"[0-9.]*\"/version = \"$HIGHEST_VERSION\"/" pyproject.toml
            sed -i "s/__version__ = '[0-9.]*'/__version__ = '$HIGHEST_VERSION'/" autotrend/__init__.py
        fi
        
        echo -e "${GREEN}✓ All versions updated to $HIGHEST_VERSION${NC}"
        echo ""
        echo -e "${YELLOW}Please run the script again to proceed with version update.${NC}"
        exit 0
    else
        echo -e "${YELLOW}Please fix versions manually and run the script again.${NC}"
        exit 1
    fi
fi

CURRENT_VERSION="$VERSION_SETUP"
echo -e "${GREEN}✓ All versions are consistent: ${CURRENT_VERSION}${NC}"
echo ""

# ============================================================
# STEP 2: Check PyPI for Latest Published Version
# ============================================================
echo -e "${YELLOW}[2/5] Checking PyPI for conflicts...${NC}"

# Try to fetch the latest version from PyPI
PYPI_VERSION=$(curl -s https://pypi.org/pypi/autotrend/json | python3 -c "import sys, json; print(json.load(sys.stdin)['info']['version'])" 2>/dev/null || echo "not_found")

if [ "$PYPI_VERSION" = "not_found" ]; then
    echo -e "${BLUE}  Package not found on PyPI (this might be the first release)${NC}"
else
    echo "  Latest PyPI version: ${PYPI_VERSION}"
    
    # Compare versions
    if [ "$CURRENT_VERSION" = "$PYPI_VERSION" ]; then
        echo -e "${RED}✗ Current version ($CURRENT_VERSION) already exists on PyPI!${NC}"
        echo -e "${RED}  You must increment the version number.${NC}"
        exit 1
    fi
    
    # Check if current version is older than or equal to PyPI version
    # sort -V sorts in version order, so if CURRENT comes before or equals PYPI, it's older/same
    SORTED_FIRST=$(printf '%s\n' "$PYPI_VERSION" "$CURRENT_VERSION" | sort -V | head -n1)
    
    if [ "$SORTED_FIRST" = "$CURRENT_VERSION" ] && [ "$CURRENT_VERSION" != "$PYPI_VERSION" ]; then
        echo -e "${RED}✗ Current version ($CURRENT_VERSION) is older than PyPI version ($PYPI_VERSION)!${NC}"
        echo -e "${RED}  New version must be greater than the published version.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ No conflicts with PyPI${NC}"
fi
echo ""

# ============================================================
# STEP 3: Determine New Version
# ============================================================
echo -e "${YELLOW}[3/5] Calculating new version...${NC}"

# Parse version parts
IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"

# Determine new version based on argument
UPDATE_TYPE=$1

if [ -z "$UPDATE_TYPE" ]; then
    echo -e "${RED}Usage: $0 {patch|minor|major|X.Y.Z}${NC}"
    echo ""
    echo "Examples:"
    echo "  $0 patch   # $CURRENT_VERSION -> $MAJOR.$MINOR.$((PATCH+1))"
    echo "  $0 minor   # $CURRENT_VERSION -> $MAJOR.$((MINOR+1)).0"
    echo "  $0 major   # $CURRENT_VERSION -> $((MAJOR+1)).0.0"
    echo "  $0 0.2.5   # $CURRENT_VERSION -> 0.2.5"
    exit 1
fi

case $UPDATE_TYPE in
    patch)
        NEW_VERSION="$MAJOR.$MINOR.$((PATCH+1))"
        ;;
    minor)
        NEW_VERSION="$MAJOR.$((MINOR+1)).0"
        ;;
    major)
        NEW_VERSION="$((MAJOR+1)).0.0"
        ;;
    [0-9]*.[0-9]*.[0-9]*)
        NEW_VERSION="$UPDATE_TYPE"
        ;;
    *)
        echo -e "${RED}✗ Invalid argument: $UPDATE_TYPE${NC}"
        echo "Use: patch, minor, major, or specific version (e.g., 0.2.5)"
        exit 1
        ;;
esac

echo "  Current version: ${CURRENT_VERSION}"
echo "  New version:     ${NEW_VERSION}"
echo ""

# Verify new version is greater than current
if ! printf '%s\n' "$CURRENT_VERSION" "$NEW_VERSION" | sort -V -C; then
    echo -e "${RED}✗ New version ($NEW_VERSION) must be greater than current ($CURRENT_VERSION)${NC}"
    exit 1
fi

# If PyPI version exists, verify new version is greater
if [ "$PYPI_VERSION" != "not_found" ]; then
    if ! printf '%s\n' "$PYPI_VERSION" "$NEW_VERSION" | sort -V -C; then
        echo -e "${RED}✗ New version ($NEW_VERSION) must be greater than PyPI version ($PYPI_VERSION)${NC}"
        exit 1
    fi
fi

# ============================================================
# STEP 4: Confirm Update
# ============================================================
echo -e "${YELLOW}[4/5] Confirmation required${NC}"
read -p "Update version from $CURRENT_VERSION to $NEW_VERSION? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cancelled.${NC}"
    exit 0
fi
echo ""

# ============================================================
# STEP 5: Update All Version Files
# ============================================================
echo -e "${YELLOW}[5/5] Updating version in all files...${NC}"

# Detect OS for sed compatibility
if [[ "$OSTYPE" == "darwin"* ]]; then
    SED_INPLACE="sed -i ''"
else
    SED_INPLACE="sed -i"
fi

# Update setup.py
$SED_INPLACE "s/version='[0-9.]*'/version='$NEW_VERSION'/" setup.py
echo -e "${GREEN}✓ Updated setup.py${NC}"

# Update pyproject.toml
$SED_INPLACE "s/version = \"[0-9.]*\"/version = \"$NEW_VERSION\"/" pyproject.toml
echo -e "${GREEN}✓ Updated pyproject.toml${NC}"

# Update __init__.py
$SED_INPLACE "s/__version__ = '[0-9.]*'/__version__ = '$NEW_VERSION'/" autotrend/__init__.py
echo -e "${GREEN}✓ Updated autotrend/__init__.py${NC}"

echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}✓ Version updated to $NEW_VERSION${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Review changes: ${BLUE}git diff${NC}"
echo -e "  2. Build package:"
echo -e "     ${BLUE}rm -rf build/ dist/ *.egg-info${NC}"
echo -e "     ${BLUE}python setup.py sdist bdist_wheel${NC}"
echo -e "  3. Check package: ${BLUE}twine check dist/*${NC}"
echo -e "  4. Upload to TestPyPI (optional):"
echo -e "     ${BLUE}twine upload --repository testpypi dist/*${NC}"
echo -e "  5. Upload to PyPI:"
echo -e "     ${BLUE}twine upload dist/*${NC}"
echo -e "  6. Commit and tag:"
echo -e "     ${BLUE}git add .${NC}"
echo -e "     ${BLUE}git commit -m 'Release v$NEW_VERSION'${NC}"
echo -e "     ${BLUE}git tag v$NEW_VERSION${NC}"
echo -e "     ${BLUE}git push && git push --tags${NC}"
echo ""