#!/bin/bash

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
NC='\033[0m' # No Color

# Get current version from setup.py
CURRENT_VERSION=$(grep "version=" setup.py | head -1 | sed "s/.*version='\([0-9.]*\)'.*/\1/")

if [ -z "$CURRENT_VERSION" ]; then
    echo -e "${RED}✗ Could not find current version in setup.py${NC}"
    exit 1
fi

echo -e "${YELLOW}Current version: ${CURRENT_VERSION}${NC}"

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

echo -e "${GREEN}New version: ${NEW_VERSION}${NC}"
echo ""

# Ask for confirmation
read -p "Update version from $CURRENT_VERSION to $NEW_VERSION? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cancelled.${NC}"
    exit 0
fi

# Update setup.py
sed -i '' "s/version='[0-9.]*'/version='$NEW_VERSION'/" setup.py
echo -e "${GREEN}✓ Updated setup.py${NC}"

# Update pyproject.toml
sed -i '' "s/version = \"[0-9.]*\"/version = \"$NEW_VERSION\"/" pyproject.toml
echo -e "${GREEN}✓ Updated pyproject.toml${NC}"

# Update __init__.py if it has __version__
if grep -q "__version__" autotrend/__init__.py 2>/dev/null; then
    sed -i '' "s/__version__ = '[0-9.]*'/__version__ = '$NEW_VERSION'/" autotrend/__init__.py
    echo -e "${GREEN}✓ Updated autotrend/__init__.py${NC}"
fi

echo ""
echo -e "${GREEN}✓ Version updated to $NEW_VERSION${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review changes: git diff"
echo "  2. Build package:"
echo "     rm -rf build/ dist/ *.egg-info"
echo "     python setup.py sdist bdist_wheel"
echo "  3. Check package: twine check dist/*"
echo "  4. Upload: twine upload dist/*"
echo "  5. Commit: git add . && git commit -m 'Release v$NEW_VERSION' && git tag v$NEW_VERSION"