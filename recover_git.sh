#!/bin/bash
# Git Recovery Script for LFT AI

echo "╔═══════════════════════════════════════╗"
echo "║   LFT AI Git Repository Recovery      ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# List of new files to preserve
NEW_FILES=(
    "profissa_lft/visualizer.py"
    "visualize_network.py"
    "VISUALIZER_GUIDE.md"
    "requirements_visualizer.txt"
    "VISUALIZER_SUMMARY.txt"
    "LLM_INTEGRATION_GUIDE.md"
    "QUICK_START_LLM.md"
    "practical_examples.py"
    "DOCUMENTATION_INDEX.md"
    "test_ai_generator.py"
)

echo "Step 1: Backing up new files..."
mkdir -p /tmp/lft_ai_recovery
for file in "${NEW_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp -p "$file" "/tmp/lft_ai_recovery/$file"
        echo "  ✓ Backed up: $file"
    fi
done

echo ""
echo "Step 2: Removing corrupted .git directory..."
rm -rf .git

echo ""
echo "Step 3: Re-initializing git repository..."
git init
git remote add origin https://github.com/dcasseb/lft_ai.git

echo ""
echo "Step 4: Fetching from remote..."
git fetch origin

echo ""
echo "Step 5: Checking out main branch..."
git checkout -b main origin/main

echo ""
echo "Step 6: Restoring new files..."
for file in "${NEW_FILES[@]}"; do
    if [ -f "/tmp/lft_ai_recovery/$file" ]; then
        mkdir -p "$(dirname "$file")"
        cp -p "/tmp/lft_ai_recovery/$file" "$file"
        echo "  ✓ Restored: $file"
    fi
done

echo ""
echo "Step 7: Checking status..."
git status

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║   Recovery Complete!                  ║"
echo "╚═══════════════════════════════════════╝"
echo ""
echo "To commit changes, run:"
echo "  git add ."
echo "  git commit -m 'Add network visualizer and LLM integration docs'"
echo "  git push origin main"

