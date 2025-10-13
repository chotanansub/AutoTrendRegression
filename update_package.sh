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
# STEP 1: Check PyPI for Latest Published Version
# ============================================================
echo -e "${YELLOW}[1/5] Fetching latest version from PyPI...${NC}"

PYPI_VERSION=$(curl -s https://pypi.org/pypi/autotrend/json | python3 -c "import sys, json; print(json.load(sys.stdin)['info']['version'])" 2>/dev/null || echo "not_found")

if [ "$PYPI_VERSION" = "not_found" ]; then
    echo -e "${BLUE}  Package not found on PyPI (this might be the first release)${NC}"
    PYPI_VERSION="0.0.0"  # Use 0.0.0 as baseline for first release
    echo "  Using baseline: 0.0.0"
else
    echo "  Latest PyPI version: ${GREEN}${PYPI_VERSION}${NC}"
fi
echo ""

# ============================================================
# STEP 2: Determine Target Version Based on Update Type
# ============================================================
echo -e "${YELLOW}[2/5] Calculating target version...${NC}"

UPDATE_TYPE=$1

if [ -z "$UPDATE_TYPE" ]; then
    echo -e "${RED}Usage: $0 {patch|minor|major|X.Y.Z}${NC}"
    echo ""
    echo "Examples:"
    echo "  $0 patch   # Increment patch version"
    echo "  $0 minor   # Increment minor version"
    echo "  $0 major   # Increment major version"
    echo "  $0 0.2.5   # Set specific version"
    exit 1
fi

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
        echo -e "${RED}✗ Invalid argument: $UPDATE_TYPE${NC}"
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
        echo -e "${RED}✗ Target version ($TARGET_VERSION) must be greater than PyPI version ($PYPI_VERSION)${NC}"
        exit 1
    fi
    
    # Check if versions are equal
    if [ "$TARGET_VERSION" = "$PYPI_VERSION" ]; then
        echo -e "${RED}✗ Target version ($TARGET_VERSION) already exists on PyPI!${NC}"
        echo -e "${RED}  You must use a higher version number.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Target version is valid${NC}"
echo ""

# ============================================================
# STEP 3: Check Current Version Consistency in Source Files
# ============================================================
echo -e "${YELLOW}[3/5] Checking version consistency in source files...${NC}"

VERSION_SETUP=$(grep "version=" setup.py | head -1 | sed "s/.*version='\([0-9.]*\)'.*/\1/")
VERSION_PYPROJECT=$(grep "version = " pyproject.toml | head -1 | sed 's/.*version = "\([0-9.]*\)".*/\1/')
VERSION_INIT=$(grep "__version__ = " autotrend/__init__.py | sed "s/.*__version__ = '\([0-9.]*\)'.*/\1/")

echo "  setup.py:              ${VERSION_SETUP}"
echo "  pyproject.toml:        ${VERSION_PYPROJECT}"
echo "  autotrend/__init__.py: ${VERSION_INIT}"
echo ""

# Check if all versions match
if [ "$VERSION_SETUP" != "$VERSION_PYPROJECT" ] || [ "$VERSION_SETUP" != "$VERSION_INIT" ]; then
    echo -e "${YELLOW}⚠ Version mismatch detected in source files${NC}"
    echo ""
    
    # Show each file's status relative to target
    if [ "$VERSION_SETUP" != "$TARGET_VERSION" ]; then
        echo -e "  setup.py:              ${YELLOW}$VERSION_SETUP${NC} → ${GREEN}$TARGET_VERSION${NC}"
    else
        echo -e "  setup.py:              ${GREEN}$VERSION_SETUP ✓${NC}"
    fi
    
    if [ "$VERSION_PYPROJECT" != "$TARGET_VERSION" ]; then
        echo -e "  pyproject.toml:        ${YELLOW}$VERSION_PYPROJECT${NC} → ${GREEN}$TARGET_VERSION${NC}"
    else
        echo -e "  pyproject.toml:        ${GREEN}$VERSION_PYPROJECT ✓${NC}"
    fi
    
    if [ "$VERSION_INIT" != "$TARGET_VERSION" ]; then
        echo -e "  autotrend/__init__.py: ${YELLOW}$VERSION_INIT${NC} → ${GREEN}$TARGET_VERSION${NC}"
    else
        echo -e "  autotrend/__init__.py: ${GREEN}$VERSION_INIT ✓${NC}"
    fi
else
    CURRENT_VERSION="$VERSION_SETUP"
    
    if [ "$CURRENT_VERSION" = "$TARGET_VERSION" ]; then
        echo -e "${GREEN}✓ All source files already at target version: ${TARGET_VERSION}${NC}"
    else
        echo -e "${YELLOW}⚠ All source files at version: ${CURRENT_VERSION}${NC}"
        echo -e "  Will update to: ${GREEN}${TARGET_VERSION}${NC}"
    fi
fi
echo ""

# ============================================================
# STEP 4: Confirm Update
# ============================================================
echo -e "${YELLOW}[4/5] Confirmation required${NC}"
echo -e "  Current versions in source: ${YELLOW}setup.py=${VERSION_SETUP}, pyproject.toml=${VERSION_PYPROJECT}, __init__.py=${VERSION_INIT}${NC}"
echo -e "  Target version: ${GREEN}${TARGET_VERSION}${NC}"
echo ""
read -p "Update all files to version $TARGET_VERSION? (y/n) " -n 1 -r
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

echo -e "${GREEN}✓ Updated setup.py${NC}"
echo -e "${GREEN}✓ Updated pyproject.toml${NC}"
echo -e "${GREEN}✓ Updated autotrend/__init__.py${NC}"

echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}✓ Version updated to $TARGET_VERSION${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""

# ============================================================
# INTERACTIVE BUILD AND PUBLISH WORKFLOW
# ============================================================

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}Build and Publish Workflow${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Step 1: Build
echo -e "${YELLOW}Step 1: Build Package${NC}"
echo -e "  This will clean old builds and create new distribution files"
echo ""
read -p "Proceed with build? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Build skipped. You can build manually later with:${NC}"
    echo -e "  ${BLUE}rm -rf build/ dist/ *.egg-info${NC}"
    echo -e "  ${BLUE}python setup.py sdist bdist_wheel${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Running: rm -rf build/ dist/ *.egg-info${NC}"
rm -rf build/ dist/ *.egg-info

echo -e "${BLUE}Running: python setup.py sdist bdist_wheel${NC}"
python setup.py sdist bdist_wheel

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Build completed successfully${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

# Step 2: Verify
echo -e "${YELLOW}Step 2: Verify Package${NC}"
echo -e "  This will check if the distribution files are valid"
echo ""
read -p "Proceed with verification? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Verification skipped. You can verify manually later with:${NC}"
    echo -e "  ${BLUE}twine check dist/*${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Running: twine check dist/*${NC}"
twine check dist/*

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Package verification passed${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}✗ Package verification failed${NC}"
    exit 1
fi

# Step 3: Publish
echo -e "${YELLOW}Step 3: Publish to PyPI${NC}"
echo -e "  ${RED}WARNING: This will publish version ${TARGET_VERSION} to PyPI (CANNOT BE UNDONE)${NC}"
echo ""
echo -e "  You can also test on TestPyPI first with:"
echo -e "  ${BLUE}twine upload --repository testpypi dist/*${NC}"
echo ""
read -p "Proceed with publishing to PyPI? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Publishing skipped.${NC}"
    echo ""
    echo -e "${YELLOW}To publish later:${NC}"
    echo -e "  Test on TestPyPI: ${BLUE}twine upload --repository testpypi dist/*${NC}"
    echo -e "  Publish to PyPI:  ${BLUE}twine upload dist/*${NC}"
    echo ""
    echo -e "${YELLOW}To commit and tag:${NC}"
    echo -e "  ${BLUE}git add .${NC}"
    echo -e "  ${BLUE}git commit -m 'Release v$TARGET_VERSION'${NC}"
    echo -e "  ${BLUE}git tag v$TARGET_VERSION${NC}"
    echo -e "  ${BLUE}git push && git push --tags${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Running: twine upload dist/*${NC}"
twine upload dist/*

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Package published successfully to PyPI${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}✗ Publishing failed${NC}"
    exit 1
fi

# Step 4: Git commit and tag
echo -e "${YELLOW}Step 4: Commit and Tag${NC}"
echo -e "  This will commit version changes and create a git tag"
echo ""
read -p "Proceed with git commit and tag? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Git operations skipped.${NC}"
    echo ""
    echo -e "${YELLOW}To commit and tag manually:${NC}"
    echo -e "  ${BLUE}git add .${NC}"
    echo -e "  ${BLUE}git commit -m 'Release v$TARGET_VERSION'${NC}"
    echo -e "  ${BLUE}git tag v$TARGET_VERSION${NC}"
    echo -e "  ${BLUE}git push && git push --tags${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Running: git add .${NC}"
git add .

echo -e "${BLUE}Running: git commit -m 'Release v$TARGET_VERSION'${NC}"
git commit -m "Release v$TARGET_VERSION"

echo -e "${BLUE}Running: git tag v$TARGET_VERSION${NC}"
git tag v$TARGET_VERSION

echo -e "${BLUE}Running: git push && git push --tags${NC}"
git push && git push --tags

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Git commit and tag completed${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}✗ Git operations failed${NC}"
    exit 1
fi

# Final summary
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}✓ Release v$TARGET_VERSION Complete!${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo -e "${YELLOW}Summary:${NC}"
echo -e "  • Version updated to: ${GREEN}$TARGET_VERSION${NC}"
echo -e "  • Package built and verified"
echo -e "  • Published to PyPI"
echo -e "  • Git committed and tagged"
echo ""
echo -e "  View on PyPI: ${BLUE}https://pypi.org/project/autotrend/$TARGET_VERSION/${NC}"
echo ""