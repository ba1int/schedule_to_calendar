#!/bin/bash
# Quick deployment script for VPS
# Usage: ./deploy_vps.sh user@your-vps-ip

set -e

if [ -z "$1" ]; then
    echo "Usage: ./deploy_vps.sh user@your-vps-ip"
    exit 1
fi

VPS_HOST=$1
PROJECT_DIR="schedule_automation"

echo "📦 Creating deployment package..."
tar -czf schedule_automation.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    .

echo "📤 Uploading to VPS..."
scp schedule_automation.tar.gz $VPS_HOST:~/

echo "🚀 Deploying on VPS..."
ssh $VPS_HOST << 'ENDSSH'
    mkdir -p ~/schedule_automation
    cd ~/schedule_automation
    tar -xzf ../schedule_automation.tar.gz
    echo "📦 Installing dependencies..."
    python3 -m pip install --user -r requirements.txt
    echo "✅ Deployment complete!"
    echo ""
    echo "📝 Next steps:"
    echo "1. Test with: cd ~/schedule_automation && python3 main.py"
    echo "2. Set up cron: crontab -e"
ENDSSH

echo "🧹 Cleaning up local package..."
rm schedule_automation.tar.gz

echo ""
echo "✨ All done! SSH into your VPS and set up the cron job."
