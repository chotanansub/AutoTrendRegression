#!/bin/bash

# Check Prerequisites

source "$(dirname "$0")/utils.sh"

log_step "Checking prerequisites..."

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    log_error "GitHub CLI (gh) is not installed"
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
    log_warning "Not authenticated with GitHub"
    echo ""
    if ask_yes_no "Authenticate now?"; then
        gh auth login
    else
        log_error "Authentication required to create releases"
        exit 1
    fi
fi

log_success "GitHub CLI installed and authenticated"
echo ""