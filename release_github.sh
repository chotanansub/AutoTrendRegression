#!/bin/bash

# GitHub Release Automation (Orchestrator)
# Executes modular release steps
#
# Usage: 
#   ./release_github.sh patch   (0.2.3 -> 0.2.4)
#   ./release_github.sh minor   (0.2.3 -> 0.3.0)
#   ./release_github.sh major   (0.2.3 -> 1.0.0)
#   ./release_github.sh 0.2.5   (set specific version)

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RELEASE_DIR="$SCRIPT_DIR/release"

# Source utilities
source "$RELEASE_DIR/utils.sh"

# Check if release directory exists
if [ ! -d "$RELEASE_DIR" ]; then
    log_error "Release directory not found: $RELEASE_DIR"
    exit 1
fi

# Display header
echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}GitHub Release Automation${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Validate arguments
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

# Execute release steps in order
"$RELEASE_DIR/pre_check_prerequisites.sh" || exit 1
"$RELEASE_DIR/s01_fetch_pypi_version.sh" || exit 1
"$RELEASE_DIR/s02_calculate_target_version.sh" "$UPDATE_TYPE" || exit 1
"$RELEASE_DIR/s03_update_version_files.sh" || exit 1
"$RELEASE_DIR/s04_build_distribution.sh" || exit 1
"$RELEASE_DIR/s05_commit_tag_push.sh" || exit 1
"$RELEASE_DIR/s06_create_github_release.sh" || exit 1

# Cleanup temporary files
rm -f /tmp/autotrend_*

echo -e "${GREEN}Release process completed!${NC}"