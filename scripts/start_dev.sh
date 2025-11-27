#!/bin/bash
# Development startup script for IMIGO LINE Bot
# This script:
# 1. Starts ngrok in the background
# 2. Waits for ngrok to be ready
# 3. Automatically updates the LINE webhook URL
# 4. Starts the FastAPI development server

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}IMIGO LINE Bot - Development Startup${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo -e "${YELLOW}Please create .env file from .env.example${NC}"
    exit 1
fi

# Load environment variables
source .env

# Check if ngrok authtoken is set
if [ -z "$NGROK_AUTHTOKEN" ] || [ "$NGROK_AUTHTOKEN" = "your_ngrok_authtoken_here" ]; then
    echo -e "${RED}❌ Error: NGROK_AUTHTOKEN not set in .env${NC}"
    echo -e "${YELLOW}Please add your ngrok authtoken to .env${NC}"
    echo -e "${YELLOW}Get it from: https://dashboard.ngrok.com/get-started/your-authtoken${NC}"
    exit 1
fi

# Check if LINE credentials are set
if [ -z "$LINE_CHANNEL_ACCESS_TOKEN" ] || [ "$LINE_CHANNEL_ACCESS_TOKEN" = "your_channel_access_token_here" ]; then
    echo -e "${RED}❌ Error: LINE credentials not set in .env${NC}"
    echo -e "${YELLOW}Please add LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN to .env${NC}"
    exit 1
fi

# Kill any existing ngrok processes
echo -e "\n${YELLOW}🧹 Cleaning up existing ngrok processes...${NC}"
pkill -f ngrok || true
sleep 2

# Start ngrok in the background
echo -e "\n${GREEN}🚀 Starting ngrok tunnel...${NC}"
ngrok http 8000 --authtoken=$NGROK_AUTHTOKEN > /dev/null &
NGROK_PID=$!

# Wait for ngrok to initialize
echo -e "${YELLOW}⏳ Waiting for ngrok to initialize...${NC}"
sleep 5

# Update LINE webhook
echo -e "\n${GREEN}📡 Updating LINE webhook URL...${NC}"
python3 scripts/update_line_webhook.py

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to update webhook${NC}"
    echo -e "${YELLOW}Stopping ngrok...${NC}"
    kill $NGROK_PID 2>/dev/null || true
    exit 1
fi

# Start the FastAPI server
echo -e "\n${GREEN}🚀 Starting FastAPI server...${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Development environment ready!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "FastAPI: http://localhost:8000"
echo -e "ngrok Inspector: http://localhost:4040"
echo -e "API Docs: http://localhost:8000/api/docs"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down...${NC}"
    kill $NGROK_PID 2>/dev/null || true
    pkill -f "uvicorn main:app" || true
    echo -e "${GREEN}✅ Shutdown complete${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM

# Start the FastAPI app
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
