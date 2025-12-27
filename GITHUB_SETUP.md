# GitHub Setup Guide

Follow these steps to push PHAI to GitHub and share it with others.

## Step 1: Create a GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top right → "New repository"
3. Name it: `PHAI` or `phai-media-organizer`
4. Description: "Personal Media AI Organizer - Organize and search your photos/videos with AI"
5. Choose **Public** (so others can use it) or **Private** (if you want to keep it private)
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

## Step 2: Push Your Code

Run these commands in your terminal (in the PHAI project folder):

```bash
# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: PHAI Media Organizer with GUI"

# Add your GitHub repository as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/PHAI.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Add Repository Information

After pushing, go to your GitHub repository and:

1. Click "Settings" → "General"
2. Add topics: `python`, `ai`, `media-organizer`, `clip`, `semantic-search`, `gui`
3. Add a description if you haven't already
4. Enable "Issues" and "Discussions" if you want community feedback

## Step 4: Create a Release (Optional)

1. Go to "Releases" → "Create a new release"
2. Tag: `v1.0.0`
3. Title: `PHAI v1.0.0 - Initial Release`
4. Description: Copy from README features
5. Click "Publish release"

## Step 5: Share Your Project

Share your repository URL:
```
https://github.com/YOUR_USERNAME/PHAI
```

## Troubleshooting

### If you get authentication errors:
```bash
# Use GitHub CLI (recommended)
gh auth login

# Or use a personal access token
# Go to GitHub Settings → Developer settings → Personal access tokens
# Create token with "repo" permissions
# Use token as password when pushing
```

### If you need to update later:
```bash
git add .
git commit -m "Your commit message"
git push
```

## Making It Easy for Others to Use

Your README.md already has:
- ✅ Clear installation instructions
- ✅ Usage examples
- ✅ Feature list
- ✅ Requirements

Consider adding:
- Screenshots of the GUI
- Demo video/GIF
- More examples in README

