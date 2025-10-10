#!/bin/bash
# Git Push Script for LFT AI Changes
# This script will configure git and push all changes to GitHub

echo "╔══════════════════════════════════════════════════════════╗"
echo "║    LFT AI - Git Configuration and Push Script           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if git username is configured
GIT_USERNAME=$(git config --global user.name)
GIT_EMAIL=$(git config --global user.email)

if [ -z "$GIT_USERNAME" ] || [ -z "$GIT_EMAIL" ]; then
    echo -e "${YELLOW}Git configuration needed!${NC}"
    echo ""
    echo "Enter your GitHub username (dcasseb):"
    read -r username
    username=${username:-dcasseb}
    
    echo "Enter your GitHub email:"
    read -r email
    
    git config --global user.name "$username"
    git config --global user.email "$email"
    
    echo -e "${GREEN}✓ Git configured${NC}"
    echo "  Username: $username"
    echo "  Email: $email"
    echo ""
else
    echo -e "${GREEN}✓ Git already configured${NC}"
    echo "  Username: $GIT_USERNAME"
    echo "  Email: $GIT_EMAIL"
    echo ""
fi

# Show what will be committed
echo "═══════════════════════════════════════════════════════════"
echo "Changes to be committed:"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "NEW FEATURES:"
echo "  ✓ profissa_lft/visualizer.py - Real-time network visualizer"
echo "  ✓ visualize_network.py - CLI wrapper for visualization"
echo "  ✓ VISUALIZER_GUIDE.md - Complete visualization documentation"
echo "  ✓ VISUALIZER_SUMMARY.txt - Feature summary"
echo ""
echo "DOCUMENTATION:"
echo "  ✓ LLM_INTEGRATION_GUIDE.md - Comprehensive LLM guide (600+ lines)"
echo "  ✓ QUICK_START_LLM.md - Quick start guide"
echo "  ✓ practical_examples.py - 10 practical examples"
echo "  ✓ DOCUMENTATION_INDEX.md - Master documentation index"
echo ""
echo "DEPENDENCIES:"
echo "  ✓ requirements_visualizer.txt - Visualization dependencies"
echo ""
echo "FIXES:"
echo "  ✓ MANIFEST.in - Fixed syntax error"
echo "  ✓ profissa_lft/__init__.py - Added exports"
echo "  ✓ profissa_lft/ai_generator.py - Changed to DeepSeek-R1"
echo "  ✓ results/analyzeResults.py - Fixed filename typo"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Proceed with commit and push? (y/n)"
read -r confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "${YELLOW}Aborted by user${NC}"
    exit 0
fi

echo ""
echo "Step 1: Fetching from remote..."
git fetch origin

echo ""
echo "Step 2: Resetting to origin/main (soft)..."
git reset --soft origin/main

echo ""
echo "Step 3: Re-adding all files..."
git add .

echo ""
echo "Step 4: Committing changes..."
git commit -m "Add network visualizer and LLM integration documentation

New Features:
- Real-time network topology visualization with matplotlib/networkx
- Auto-discovery of Docker containers and network components
- Resource monitoring (CPU, memory, network traffic)
- Interactive graphs with live updates

Documentation:
- Comprehensive LLM integration guide (600+ lines)
- Quick start guide for LLM usage
- 10 practical examples with auto-generation
- Complete visualizer documentation
- Master documentation index

Fixes:
- Fixed MANIFEST.in syntax error
- Fixed filename typo (analyzeResults)
- Added ModernAITopologyGenerator to exports
- Changed default model to DeepSeek-R1

Dependencies:
- Added requirements_visualizer.txt
- All dependencies verified in lft_env

Files Added:
- profissa_lft/visualizer.py (18KB)
- visualize_network.py (2.5KB)
- VISUALIZER_GUIDE.md (15KB)
- VISUALIZER_SUMMARY.txt
- LLM_INTEGRATION_GUIDE.md (36KB)
- QUICK_START_LLM.md (6.6KB)
- practical_examples.py (16KB)
- DOCUMENTATION_INDEX.md
- requirements_visualizer.txt"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Commit successful${NC}"
    echo ""
    echo "Step 5: Pushing to origin/main..."
    git push origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "╔══════════════════════════════════════════════════════════╗"
        echo "║          SUCCESS! Changes pushed to GitHub              ║"
        echo "╚══════════════════════════════════════════════════════════╝"
        echo ""
        echo "Repository: https://github.com/dcasseb/lft_ai"
        echo ""
        echo "You can now:"
        echo "  1. View your changes on GitHub"
        echo "  2. Test the visualizer: python visualize_network.py"
        echo "  3. Read the docs: VISUALIZER_GUIDE.md"
        echo "  4. Try LLM examples: python practical_examples.py"
        echo ""
    else
        echo ""
        echo -e "${RED}✗ Push failed${NC}"
        echo ""
        echo "Possible reasons:"
        echo "  1. Authentication required - use personal access token"
        echo "  2. No write access to repository"
        echo "  3. Network issues"
        echo ""
        echo "To use personal access token:"
        echo "  git remote set-url origin https://TOKEN@github.com/dcasseb/lft_ai.git"
        echo ""
        echo "Your commit is saved locally. Try:"
        echo "  git push origin main"
        echo ""
        exit 1
    fi
else
    echo -e "${RED}✗ Commit failed${NC}"
    exit 1
fi
