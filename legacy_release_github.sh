#!/bin/bash

# GitHub Release Automation Script
# Creates a GitHub release with distribution artifacts
#
# Usage: 
#   ./release_github.sh patch   (0.2.3 -> 0.2.4)
#   ./release_github.sh minor   (0.2.3 -> 0.3.0)
#   ./release_github.sh major   (0.2.3 -> 1.0.0)
#   ./release_github.sh 0.2.5   (set specific version)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}GitHub Release Automation${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# ============================================================
# Check Prerequisites
# ============================================================

echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}✗ GitHub CLI (gh) is not installed${NC}"
    echo ""
    echo "Install it with:"
    echo "  macOS:   brew install gh"
    echo "  Linux:   https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    echo "  Windows: https://github.com/cli/cli/releases"
    echo ""
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠ Not authenticated with GitHub${NC}"
    echo ""
    read -p "Authenticate now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gh auth login
    else
        echo -e "${RED}Authentication required to create releases${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ GitHub CLI installed and authenticated${NC}"
echo ""

# ============================================================
# STEP 1: Check PyPI for Latest Published Version
# ============================================================
echo -e "${YELLOW}[1/5] Fetching latest version from PyPI...${NC}"

PYPI_VERSION=$(curl -s https://pypi.org/pypi/autotrend/json | python3 -c "import sys, json; print(json.load(sys.stdin)['info']['version'])" 2>/dev/null || echo "not_found")

if [ "$PYPI_VERSION" = "not_found" ]; then
    echo -e "${BLUE}  Package not found on PyPI (this might be the first release)${NC}"
    PYPI_VERSION="0.0.0"
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

TAG="v$TARGET_VERSION"

# ============================================================
# STEP 3: Check Local Version Files
# ============================================================
echo -e "${YELLOW}[3/5] Checking local version files...${NC}"

VERSION_SETUP=$(grep "version=" setup.py | head -1 | sed "s/.*version='\([0-9.]*\)'.*/\1/")
VERSION_PYPROJECT=$(grep "version = " pyproject.toml | head -1 | sed 's/.*version = "\([0-9.]*\)".*/\1/')
VERSION_INIT=$(grep "__version__ = " autotrend/__init__.py | sed "s/.*__version__ = '\([0-9.]*\)'.*/\1/")

echo "  setup.py:              ${VERSION_SETUP}"
echo "  pyproject.toml:        ${VERSION_PYPROJECT}"
echo "  autotrend/__init__.py: ${VERSION_INIT}"
echo ""

# Check if all versions match target version
if [ "$VERSION_SETUP" != "$TARGET_VERSION" ] || [ "$VERSION_PYPROJECT" != "$TARGET_VERSION" ] || [ "$VERSION_INIT" != "$TARGET_VERSION" ]; then
    echo -e "${RED}✗ Local version files do not match target version ${TARGET_VERSION}${NC}"
    echo ""
    echo "Run update_package.sh first:"
    echo -e "  ${BLUE}./update_package.sh $UPDATE_TYPE${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All local versions match target: ${TARGET_VERSION}${NC}"
echo ""

# ============================================================
# STEP 4: Verify Git Tag and Distribution Files
# ============================================================
echo -e "${YELLOW}[4/5] Verifying git tag and distribution files...${NC}"

# Check if tag exists
TAG_EXISTS=false
if git tag | grep -q "^${TAG}$"; then
    TAG_EXISTS=true
    echo -e "${GREEN}✓ Git tag ${TAG} exists${NC}"
else
    echo -e "${YELLOW}⚠ Git tag ${TAG} does not exist${NC}"
    echo ""
    read -p "Create tag ${TAG} and push to GitHub? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        
        # Check if there are uncommitted changes
        if ! git diff-index --quiet HEAD --; then
            echo -e "${YELLOW}⚠ You have uncommitted changes${NC}"
            echo ""
            
            # Show what files have changed
            echo "Changed files:"
            git status --short
            echo ""
            
            read -p "Commit these changes automatically? (y/n) " -n 1 -r
            echo ""
            
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo ""
                echo -e "${BLUE}Committing changes...${NC}"
                
                # Stage all changes
                git add .
                
                # Commit with standard message
                git commit -m "Prepare release v${TARGET_VERSION}"
                
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}✓ Changes committed${NC}"
                    
                    # Push commits to remote
                    echo -e "${BLUE}Pushing commits to GitHub...${NC}"
                    git push origin main
                    
                    if [ $? -eq 0 ]; then
                        echo -e "${GREEN}✓ Commits pushed to GitHub${NC}"
                    else
                        echo -e "${RED}✗ Failed to push commits${NC}"
                        echo ""
                        echo "Push manually with:"
                        echo "  git push origin main"
                        exit 1
                    fi
                else
                    echo -e "${RED}✗ Failed to commit changes${NC}"
                    exit 1
                fi
                echo ""
            else
                echo ""
                echo -e "${YELLOW}Cancelled${NC}"
                echo ""
                echo "Commit changes manually:"
                echo "  git add ."
                echo "  git commit -m 'Prepare release v${TARGET_VERSION}'"
                echo "  git push origin main"
                exit 1
            fi
        fi
        
        # Now create the tag
        echo -e "${BLUE}Creating tag ${TAG}...${NC}"
        git tag -a "${TAG}" -m "Release v${TARGET_VERSION}"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Tag ${TAG} created${NC}"
            
            # Push tag to remote
            echo -e "${BLUE}Pushing tag to GitHub...${NC}"
            git push origin "${TAG}"
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ Tag pushed to GitHub${NC}"
                TAG_EXISTS=true
            else
                echo -e "${RED}✗ Failed to push tag${NC}"
                exit 1
            fi
        else
            echo -e "${RED}✗ Failed to create tag${NC}"
            exit 1
        fi
        echo ""
    else
        echo ""
        echo -e "${YELLOW}Cancelled${NC}"
        echo ""
        echo "Create tag manually with:"
        echo "  git tag -a ${TAG} -m 'Release v${TARGET_VERSION}'"
        echo "  git push origin ${TAG}"
        exit 1
    fi
fi

# Check for distribution files
DIST_DIR="dist"
WHEEL_FILE="${DIST_DIR}/autotrend-${TARGET_VERSION}-py3-none-any.whl"
TARBALL_FILE="${DIST_DIR}/autotrend-${TARGET_VERSION}.tar.gz"

if [ ! -d "$DIST_DIR" ]; then
    echo -e "${RED}✗ Distribution directory not found: ${DIST_DIR}/${NC}"
    echo ""
    echo "Build package first:"
    echo "  rm -rf build/ dist/ *.egg-info"
    echo "  python setup.py sdist bdist_wheel"
    echo ""
    echo "Or run ./update_package.sh"
    exit 1
fi

FOUND_FILES=()
MISSING_FILES=()

if [ -f "$WHEEL_FILE" ]; then
    FOUND_FILES+=("$WHEEL_FILE")
    echo -e "  ${GREEN}✓${NC} Found: $WHEEL_FILE"
else
    MISSING_FILES+=("$WHEEL_FILE")
    echo -e "  ${RED}✗${NC} Missing: $WHEEL_FILE"
fi

if [ -f "$TARBALL_FILE" ]; then
    FOUND_FILES+=("$TARBALL_FILE")
    echo -e "  ${GREEN}✓${NC} Found: $TARBALL_FILE"
else
    MISSING_FILES+=("$TARBALL_FILE")
    echo -e "  ${RED}✗${NC} Missing: $TARBALL_FILE"
fi

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}✗ Missing distribution files${NC}"
    echo ""
    read -p "Build distribution files now? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}Building distribution files...${NC}"
        
        # Clean old builds
        rm -rf build/ dist/ *.egg-info
        
        # Build package
        python setup.py sdist bdist_wheel
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Build completed${NC}"
            
            # Verify files were created
            if [ -f "$WHEEL_FILE" ] && [ -f "$TARBALL_FILE" ]; then
                FOUND_FILES=("$WHEEL_FILE" "$TARBALL_FILE")
                echo -e "${GREEN}✓ Distribution files created${NC}"
            else
                echo -e "${RED}✗ Build succeeded but files not found${NC}"
                exit 1
            fi
        else
            echo -e "${RED}✗ Build failed${NC}"
            exit 1
        fi
        echo ""
    else
        echo ""
        echo -e "${YELLOW}Cancelled${NC}"
        echo ""
        echo "Build manually with:"
        echo "  rm -rf build/ dist/ *.egg-info"
        echo "  python setup.py sdist bdist_wheel"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}✓ All distribution files found${NC}"
echo ""

# ============================================================
# STEP 5: Generate Release Notes and Create Release
# ============================================================
echo -e "${YELLOW}[5/5] Creating GitHub release...${NC}"

# Get previous tag for changelog
PREV_TAG=$(git describe --tags --abbrev=0 ${TAG}^ 2>/dev/null || echo "")

# Generate release notes
if [ -z "$PREV_TAG" ]; then
    CHANGELOG_LINK=""
else
    CHANGELOG_LINK="**Full Changelog**: https://github.com/chotanansub/autotrend/compare/${PREV_TAG}...${TAG}"
fi

RELEASE_NOTES=$(cat <<EOF
## AutoTrend v${TARGET_VERSION}

### Installation
\`\`\`bash
pip install autotrend==${TARGET_VERSION}
\`\`\`

### Quick Start
\`\`\`python
from autotrend import decompose_llt

# Run LLT decomposition
result = decompose_llt(sequence, window_size=10)

# Visualize results
result.plot_full_decomposition()
\`\`\`

### What's Included
- 📦 Source distribution (tar.gz)
- 📦 Python wheel (.whl)

### Resources
- 📚 [Documentation](https://github.com/chotanansub/autotrend#readme)
- 🚀 [Google Colab Demo](https://colab.research.google.com/drive/1jifMsj8nI_ZV-FL3ZScFP4wJJLQp97jH?usp=sharing)
- 🐛 [Report Issues](https://github.com/chotanansub/autotrend/issues)

${CHANGELOG_LINK}
EOF
)

echo "Release notes preview:"
echo "─────────────────────────────────────"
echo "$RELEASE_NOTES"
echo "─────────────────────────────────────"
echo ""

# Summary
echo -e "${YELLOW}Summary:${NC}"
echo -e "  PyPI version:  ${PYPI_VERSION}"
echo -e "  Tag:           ${GREEN}${TAG}${NC}"
echo -e "  New version:   ${GREEN}${TARGET_VERSION}${NC}"
echo -e "  Artifacts:     ${GREEN}${#FOUND_FILES[@]} files${NC}"
for file in "${FOUND_FILES[@]}"; do
    FILE_SIZE=$(du -h "$file" | cut -f1)
    echo -e "    - $(basename "$file") (${FILE_SIZE})"
done
echo ""

read -p "Create GitHub release? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Creating release...${NC}"

# Create release with gh CLI
gh release create "$TAG" \
    "${FOUND_FILES[@]}" \
    --title "AutoTrend v${TARGET_VERSION}" \
    --notes "$RELEASE_NOTES" \
    --latest

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=================================${NC}"
    echo -e "${GREEN}✓ Release Created Successfully!${NC}"
    echo -e "${GREEN}=================================${NC}"
    echo ""
    echo -e "${YELLOW}Release Details:${NC}"
    echo -e "  PyPI (old):   ${PYPI_VERSION}"
    echo -e "  PyPI (new):   ${GREEN}${TARGET_VERSION}${NC} (will be published by GitHub Actions)"
    echo -e "  Release URL:  ${BLUE}https://github.com/chotanansub/autotrend/releases/tag/${TAG}${NC}"
    echo -e "  Tag:          ${GREEN}${TAG}${NC}"
    echo ""
    echo -e "${YELLOW}GitHub Actions Status:${NC}"
    echo -e "  • Monitor workflow: ${BLUE}https://github.com/chotanansub/autotrend/actions${NC}"
    echo -e "  • The workflow will automatically build and publish to PyPI"
    echo -e "  • This usually takes 2-5 minutes"
    echo ""
    echo -e "${YELLOW}Verify Publication:${NC}"
    echo -e "  • PyPI package: ${BLUE}https://pypi.org/project/autotrend/${TARGET_VERSION}/${NC}"
    echo -e "  • Install new version: ${GREEN}pip install autotrend==${TARGET_VERSION}${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}✗ Failed to create release${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  • Check if release already exists: gh release list"
    echo "  • View release details: gh release view ${TAG}"
    echo "  • Delete existing release: gh release delete ${TAG}"
    exit 1
fi