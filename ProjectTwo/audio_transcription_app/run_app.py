#!/usr/bin/env python3
"""
Simple script to run the Audio Transcription Application

This script demonstrates:
- How to properly start a FastAPI application
- Environment setup checking
- Basic error handling for startup

Educational note: This shows students how to create user-friendly
startup scripts for their applications.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Ensure we're using Python 3.7+"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def check_virtual_environment():
    """Check if we're in a virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
        return True
    else:
        print("⚠️  Virtual environment not detected")
        print("It's recommended to run this in a virtual environment")
        response = input("Continue anyway? (y/N): ").lower().strip()
        return response == 'y'

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'librosa',
        'pydub'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    dirs = ['audio_files', 'audio_files/chunks', 'audio_files/temp']
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory: {dir_path}")

def print_startup_info():
    """Print helpful information about the application"""
    print("\n" + "="*60)
    print("🎵 AI Audio Transcription & Editing App")
    print("="*60)
    print("Educational Features:")
    print("  🔧 Virtual Environment Isolation")
    print("  🏗️  Modular Architecture Design")
    print("  🤖 AI API Integration (ElevenLabs)")
    print("  📝 Interactive Transcription Editing")
    print("  🎯 Error Handling & Validation")
    print("\nAccess the application at:")
    print("  🌐 Web Interface: http://localhost:8000")
    print("  📚 API Documentation: http://localhost:8000/docs")
    print("  🔍 Health Check: http://localhost:8000/api/health")
    print("  🏛️  Architecture Info: http://localhost:8000/api/architecture")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)

def main():
    """Main startup function"""
    print("🚀 Starting Audio Transcription Application...")
    print("-" * 50)
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_virtual_environment():
        sys.exit(1)
    
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    print("\n📁 Setting up directories...")
    create_directories()
    
    # Print educational information
    print_startup_info()
    
    # Start the application
    try:
        # Change to app directory
        os.chdir(Path(__file__).parent)
        
        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ])
        
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the correct directory")
        print("2. Check that all dependencies are installed")
        print("3. Verify your Python environment")

if __name__ == "__main__":
    main() 