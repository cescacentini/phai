#!/bin/bash
# Script to prepare and push PHAI to GitHub

echo "🚀 Setting up PHAI for GitHub..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git branch -M main
fi

# Add all files
echo "📦 Adding files to git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "✅ No changes to commit"
else
    echo "💾 Creating initial commit..."
    git commit -m "Initial commit: PHAI Media Organizer v1.0.0

Features:
- Date-based media organization (YYYYMMDD folders)
- AI-powered semantic search using CLIP
- Modern GUI with CustomTkinter
- Automatic indexing after organizing
- Stop operations anytime
- High accuracy search with query expansion"
fi

echo ""
echo "✅ Repository is ready!"
echo ""
echo "📝 Next steps:"
echo "1. Go to https://github.com and create a new repository"
echo "2. Name it 'PHAI' or 'phai-media-organizer'"
echo "3. DO NOT initialize with README, .gitignore, or license"
echo "4. Then run these commands:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/PHAI.git"
echo "   git push -u origin main"
echo ""
echo "Or use the GitHub CLI:"
echo "   gh repo create PHAI --public --source=. --remote=origin --push"
echo ""

