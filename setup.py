"""
VIP Threat Monitoring System - Setup Script
Installs Python dependencies, initializes DB and AI model
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required Python packages from requirements.txt"""
    print("📦 Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def setup_directories():
    """Create necessary directories for data and models"""
    print("📁 Creating directories...")
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

def setup_database():
    """Initialize the DuckDB database"""
    print("🗄️  Initializing database...")
    try:
        from backend.ingestion.ingestion import DataIngestion
        ingestion = DataIngestion()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

def setup_model():
    """Initialize or train the AI threat detection model"""
    print("🤖 Setting up AI model...")
    try:
        from backend.ai.ai_scoring import VIPThreatScorer
        scorer = VIPThreatScorer()
        if not os.path.exists(scorer.model_path):
            print("Training new model (this may take a few minutes)...")
            scorer.train_model()
        print("✅ AI model ready")
    except Exception as e:
        print(f"❌ AI model setup failed: {e}")
        sys.exit(1)

def main():
    """Run all setup steps"""
    print("🛡️  VIP Threat Monitoring System - Setup")
    print("=" * 50)

    try:
        install_requirements()
        setup_directories()
        setup_database()
        setup_model()

        print("\n✅ Setup completed successfully!")
        print("\n🚀 To start the system, run:")
        print("   python run_complete.py\n")
        print("📖 API docs available at:")
        print("   http://localhost:8000/docs\n")

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
