#!/usr/bin/env python3
"""
VIP Threat Monitoring System - Complete Application Launcher
Starts both backend API and React frontend
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

def print_banner():
    """Print system banner"""
    print("=" * 70)
    print("🛡️  VIP THREAT & MISINFORMATION MONITORING SYSTEM")
    print("=" * 70)
    print("🎯 Complete Full-Stack Application")
    print("🚀 Backend API + React Frontend")
    print("=" * 70)
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking system dependencies...")
    
    # Check Python version
    try:
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python 3.8+ required")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}")
    except Exception:
        print("❌ Python not found")
        return False
    
    # Check Node.js presence and version
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js {version}")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False
    
    return True

def start_backend():
    """Start the backend server"""
    print("🚀 Starting backend server...")
    os.chdir('backend/dashboard')
    
    try:
        subprocess.run([sys.executable, 'dashboard.py'])
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Backend server error: {e}")

def start_frontend():
    """Start the React frontend"""
    print("🎨 Starting React frontend...")
    time.sleep(3)  # Wait for backend to start
    
    os.chdir('../../frontend')
    
    try:
        subprocess.run(['npm', 'start'])
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except Exception as e:
        print(f"❌ Frontend server error: {e}")

def open_browser():
    """Open browser after delay"""
    time.sleep(10)  # Give servers time to start
    try:
        print("🌐 Opening browser...")
        webbrowser.open('http://localhost:3000')
    except Exception:
        pass

def main():
    """Main application launcher"""
    print_banner()
    
    if not check_dependencies():
        print("\n❌ System requirements not met. Please install:")
        print("   - Python 3.8+")
        print("   - Node.js 16+")
        return
    
    print("\n🎯 Starting VIP Threat Monitoring System...")
    print("   Backend API: http://localhost:8000")
    print("   React App: http://localhost:3000")
    print("   API Docs: http://localhost:8000/docs")
    print("\n⏱️  Servers will start shortly...\n")
    time.sleep(3)
    
    try:
        # Open browser in background
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        # Start backend in background thread
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        
        # Start frontend in main thread to catch Ctrl+C properly
        start_frontend()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down VIP Threat Monitoring System...")
        print("   All servers stopped")
    except Exception as e:
        print(f"\n❌ System error: {e}")

if __name__ == "__main__":
    main()
