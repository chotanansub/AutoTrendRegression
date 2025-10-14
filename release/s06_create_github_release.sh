#!/bin/bash

# Create GitHub Release

source "$(dirname "$0")/utils.sh"

log_step "[6/6] Creating GitHub release..."

TARGET_VERSION=$(cat /tmp/autotrend_target_version)
PYPI_VERSION=$(cat /tmp/autotrend_pypi_version)
TAG=$(cat /tmp/autotrend_tag)
WHEEL_FILE=$(cat /tmp/autotrend_wheel_file)
TARBALL_FILE=$(cat /tmp/autotrend_tarball_file)

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
echo -e "  New version:   ${GREEN}${TARGET_VERSION}${NC}"
echo -e "  Tag:           ${GREEN}${TAG}${NC}"
echo -e "  Artifacts:     ${GREEN}2 files${NC}"

WHEEL_SIZE=$(du -h "$WHEEL_FILE" | cut -f1)
TARBALL_SIZE=$(du -h "$TARBALL_FILE" | cut -f1)
echo -e "    - $(basename "$WHEEL_FILE") (${WHEEL_SIZE})"
echo -e "    - $(basename "$TARBALL_FILE") (${TARBALL_SIZE})"
echo ""

if ask_yes_no "Create GitHub release?"; then
    echo ""
    log_info "Creating release..."
    
    # Create release with gh CLI
    gh release create "$TAG" \
        "$WHEEL_FILE" \
        "$TARBALL_FILE" \
        --title "AutoTrend v${TARGET_VERSION}" \
        --notes "$RELEASE_NOTES" \
        --latest
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}=================================${NC}"
        log_success "Release Created Successfully!"
        echo -e "${GREEN}=================================${NC}"
        echo ""
        echo -e "${YELLOW}Release Details:${NC}"
        echo -e "  PyPI (old):   ${PYPI_VERSION}"
        echo -e "  PyPI (new):   ${GREEN}${TARGET_VERSION}${NC} (publishing via GitHub Actions...)"
        echo -e "  Release URL:  ${BLUE}https://github.com/chotanansub/autotrend/releases/tag/${TAG}${NC}"
        echo ""
        echo -e "${YELLOW}GitHub Actions Status:${NC}"
        echo -e "  • Monitor: ${BLUE}https://github.com/chotanansub/autotrend/actions${NC}"
        echo -e "  • Publishing usually takes 2-5 minutes"
        echo ""
        echo -e "${YELLOW}After Publication:${NC}"
        echo -e "  • PyPI: ${BLUE}https://pypi.org/project/autotrend/${TARGET_VERSION}/${NC}"
        echo -e "  • Install: ${GREEN}pip install autotrend==${TARGET_VERSION}${NC}"
        echo ""
    else
        echo ""
        log_error "Failed to create release"
        echo ""
        echo "Troubleshooting:"
        echo "  • Check existing releases: gh release list"
        echo "  • View release: gh release view ${TAG}"
        echo "  • Delete if needed: gh release delete ${TAG}"
        exit 1
    fi
else
    echo ""
    echo -e "${YELLOW}Cancelled${NC}"
    exit 0
fi
```

---

## Final Directory Structure
```
project/
├── release_github.sh              # Main orchestrator
├── release/
│   ├── utils.sh                  # Shared utilities
│   ├── pre_check_prerequisites.sh
│   ├── s01_fetch_pypi_version.sh
│   ├── s02_calculate_target_version.sh
│   ├── s03_update_version_files.sh
│   ├── s04_build_distribution.sh
│   ├── s05_commit_tag_push.sh
│   └── s06_create_github_release.sh
└── ...