#!/bin/bash

# VIP Threat Monitoring System - Complete Startup Script
# This script installs dependencies and starts backend and frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${BLUE}=====================================================================${NC}"
    echo -e "${GREEN}🛡️  VIP THREAT & MISINFORMATION MONITORING SYSTEM${NC}"
    echo -e "${BLUE}=====================================================================${NC}"
    echo -e "${YELLOW}🎯 Complete Full-Stack Application${NC}"
    echo -e "${YELLOW}🚀 Backend API + React Frontend Dashboard${NC}"
    echo -e "${BLUE}=====================================================================${NC}"
    echo ""
}

print_urls() {
    echo -e "${GREEN}🌐 Application URLs:${NC}"
    echo -e "   📊 Dashboard: http://localhost:3000"
    echo -e "   🔧 Backend API: http://localhost:8000"
    echo -e "   📖 API Docs: http://localhost:8000/docs"
    echo -e "   🩺 Health Check: http://localhost:8000/health"
    echo ""
}

check_dependencies() {
    echo -e "${BLUE}🔍 Checking system dependencies...${NC}"

    # Check Python installation
    if command -v python3 &> /dev/null; then
        version=$(python3 --version | cut -d' ' -f2)
        echo -e "${GREEN}✅ Found Python version $version${NC}"
    else
        echo -e "${RED}❌ Python3 not found. Please install Python 3.8+${NC}"
        exit 1
    fi

    # Check Node.js installation
    if command -v node &> /dev/null; then
        version=$(node --version)
        echo -e "${GREEN}✅ Found Node.js version $version${NC}"
    else
        echo -e "${RED}❌ Node.js not found. Please install Node.js 16+${NC}"
        exit 1
    fi

    # Check npm installation
    if command -v npm &> /dev/null; then
        version=$(npm --version)
        echo -e "${GREEN}✅ Found npm version $version${NC}"
    else
        echo -e "${RED}❌ npm not found. Please install npm${NC}"
        exit 1
    fi
}

install_backend() {
    echo -e "${BLUE}📦 Installing Python backend dependencies...${NC}"
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    echo -e "${GREEN}✅ Backend dependencies installed${NC}"
    echo ""
}

install_frontend() {
    echo -e "${BLUE}📦 Installing React frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    echo ""
}

start_backend() {
    echo -e "${YELLOW}🚀 Starting backend server...${NC}"
    cd backend/dashboard
    python3 dashboard.py &
    BACKEND_PID=$!
    cd ../..
    sleep 5  # wait a bit for backend startup
}

start_frontend() {
    echo -e "${YELLOW}🎨 Starting React frontend...${NC}"
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
}

cleanup() {
    echo -e "${RED}\n🛑 Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

print_banner
check_dependencies
install_backend
install_frontend
print_urls
start_backend
start_frontend

echo -e "${GREEN}Application started successfully.${NC}"
echo "Press Ctrl+C to stop."

# Wait indefinitely
while true; do sleep 10; done
