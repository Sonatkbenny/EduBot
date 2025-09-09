#!/usr/bin/env python3
"""
EduBot Setup Script
Initializes the EduBot project with database setup and model downloads
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = [
        "models_cache",
        "data",
        "logs",
        "uploads"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/")

def setup_database():
    """Setup database tables"""
    print("🗄️ Setting up database...")
    try:
        from config.database import create_tables
        create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️ Database setup failed: {e}")
        print("You can run this manually later with: python config/database.py")

def download_models():
    """Download required AI models"""
    print("🤖 Downloading AI models...")
    try:
        # This will trigger model downloads when first used
        from models.summarizer import get_summarizer
        print("✅ T5 model will be downloaded on first use")
    except Exception as e:
        print(f"⚠️ Model setup failed: {e}")

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if not env_file.exists():
        print("🔧 Creating .env file...")
        with open("env_example.txt", "r") as example:
            content = example.read()
        
        with open(".env", "w") as env:
            env.write(content)
        
        print("✅ Created .env file")
        print("⚠️ Please update .env file with your actual API keys and database credentials")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function"""
    print("🚀 EduBot Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Setup database
    setup_database()
    
    # Download models
    download_models()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Update .env file with your API keys and database credentials")
    print("2. Start the application with: streamlit run app.py")
    print("3. Open your browser and navigate to the provided URL")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()



