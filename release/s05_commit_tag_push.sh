#!/bin/bash

# Commit, Tag, and Push

source "$(dirname "$0")/utils.sh"

log_step "[5/6] Committing, tagging, and pushing to GitHub..."

TARGET_VERSION=$(cat /tmp/autotrend_target_version)
TAG=$(cat /tmp/autotrend_tag)

# Check if tag already exists
if git tag | grep -q "^${TAG}$"; then
    log_success "Git tag ${TAG} already exists"
    echo ""
    exit 0
fi

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    log_warning "You have uncommitted changes"
    echo ""
    
    # Show what files have changed
    echo "Changed files:"
    git status --short
    echo ""
    
    if ask_yes_no "Commit these changes?"; then
        echo ""
        log_info "Committing changes..."
        
        # Stage all changes
        git add .
        
        # Commit with standard message
        git commit -m "Release v${TARGET_VERSION}"
        
        if [ $? -eq 0 ]; then
            log_success "Changes committed"
        else
            log_error "Failed to commit changes"
            exit 1
        fi
    else
        echo ""
        echo -e "${YELLOW}Cancelled${NC}"
        echo ""
        echo "Commit changes manually:"
        echo "  git add ."
        echo "  git commit -m 'Release v${TARGET_VERSION}'"
        exit 1
    fi
else
    log_success "No uncommitted changes"
fi

# Push commits if needed
if git status -sb | grep -q "ahead"; then
    log_info "Pushing commits to GitHub..."
    git push origin main
    
    if [ $? -eq 0 ]; then
        log_success "Commits pushed"
    else
        log_error "Failed to push commits"
        exit 1
    fi
fi

# Create and push tag
log_info "Creating tag ${TAG}..."
git tag -a "${TAG}" -m "Release v${TARGET_VERSION}"

if [ $? -eq 0 ]; then
    log_success "Tag ${TAG} created"
    
    log_info "Pushing tag to GitHub..."
    git push origin "${TAG}"
    
    if [ $? -eq 0 ]; then
        log_success "Tag pushed"
    else
        log_error "Failed to push tag"
        exit 1
    fi
else
    log_error "Failed to create tag"
    exit 1
fi

echo ""