#!/bin/bash

# Fetch Latest PyPI Version

source "$(dirname "$0")/utils.sh"

log_step "[1/6] Fetching latest version from PyPI..."

PYPI_VERSION=$(curl -s https://pypi.org/pypi/autotrend/json | python3 -c "import sys, json; print(json.load(sys.stdin)['info']['version'])" 2>/dev/null || echo "not_found")

if [ "$PYPI_VERSION" = "not_found" ]; then
    log_info "  Package not found on PyPI (this might be the first release)"
    PYPI_VERSION="0.0.0"
    echo "  Using baseline: 0.0.0"
else
    echo "  Latest PyPI version: ${GREEN}${PYPI_VERSION}${NC}"
fi
echo ""

# Export for use in other scripts
echo "$PYPI_VERSION" > /tmp/autotrend_pypi_version