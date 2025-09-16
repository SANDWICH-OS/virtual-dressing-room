#!/bin/bash
# Railway setup script

echo "🚀 Setting up Railway deployment..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Create new project
echo "📦 Creating Railway project..."
railway new

# Add environment variables
echo "🔧 Setting up environment variables..."
railway variables set BOT_TOKEN="your_telegram_bot_token_here"
railway variables set OPENAI_API_KEY="your_openai_key"
railway variables set REPLICATE_API_TOKEN="your_replicate_token"

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Railway setup complete!"
echo "📊 Check your deployment at: https://railway.app/dashboard"
