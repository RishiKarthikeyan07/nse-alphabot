#!/bin/bash

# Railway Deployment Script for NSE AlphaBot
# This script helps you deploy to Railway.app

echo "🚂 NSE AlphaBot - Railway Deployment Helper"
echo "=========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Create .gitkeep for models directory
mkdir -p models
touch models/.gitkeep

# Add all files
echo ""
echo "📝 Adding files to git..."
git add .

# Commit
echo ""
echo "💾 Creating commit..."
git commit -m "Initial commit: NSE AlphaBot with optimized weights" || echo "No changes to commit"

echo ""
echo "=========================================="
echo "✅ Local setup complete!"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Create a GitHub repository:"
echo "   - Go to https://github.com/new"
echo "   - Name: nse-alphabot"
echo "   - Make it Private (recommended)"
echo "   - Don't initialize with README"
echo ""
echo "2. Push to GitHub:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/nse-alphabot.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Deploy to Railway:"
echo "   - Go to https://railway.app"
echo "   - Click 'New Project'"
echo "   - Select 'Deploy from GitHub repo'"
echo "   - Choose your nse-alphabot repository"
echo "   - Railway will auto-detect Python and deploy!"
echo ""
echo "4. Set up Cron Job:"
echo "   - In Railway dashboard, go to your project"
echo "   - Click 'Settings' → 'Cron'"
echo "   - Add schedule: '45 3 * * 1-5'"
echo "   - (Runs at 9:15 AM IST, Mon-Fri)"
echo ""
echo "=========================================="
echo ""
echo "📖 For detailed instructions, see RAILWAY_DEPLOYMENT_GUIDE.md"
echo ""
