"""
Quick Start Script - Easy setup and launch
"""

import subprocess
import sys
import os

def print_header():
    print("="*60)
    print("🦁 Wildlife Risk Assessment System v2.0")
    print("Quick Start Setup")
    print("="*60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        return False
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        'recordings',
        'snapshots',
        'logs',
        'database',
        'uploads'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ {directory}/")
    
    return True

def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    print("This may take a few minutes...\n")
    
    try:
        subprocess.check_call([
            sys.executable, 
            '-m', 
            'pip', 
            'install', 
            '-r', 
            'requirements.txt',
            '--upgrade'
        ])
        print("\n✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error installing dependencies: {e}")
        return False

def setup_environment():
    """Setup environment file"""
    print("\n⚙️ Setting up environment...")
    
    if os.path.exists('.env'):
        print("  ✓ .env file already exists")
        return True
    
    if os.path.exists('.env.example'):
        import shutil
        shutil.copy('.env.example', '.env')
        print("  ✓ Created .env from .env.example")
        print("  ⚠️ Please edit .env file with your credentials")
        return True
    else:
        print("  ⚠️ .env.example not found")
        return False

def download_models():
    """Download AI models"""
    print("\n🤖 Downloading AI models...")
    print("This may take a few minutes on first run...\n")
    
    try:
        from ultralytics import YOLO
        print("  Downloading YOLOv8n model...")
        model = YOLO('yolov8n.pt')
        print("  ✓ YOLOv8n model ready")
        return True
    except Exception as e:
        print(f"  ⚠️ Model download will happen on first run: {e}")
        return True

def run_system():
    """Launch the system"""
    print("\n" + "="*60)
    print("🚀 Choose how to run the system:")
    print("="*60)
    print("\n1. Standalone Application (Recommended for testing)")
    print("   - Direct camera access and monitoring")
    print("   - Keyboard controls (q=quit, r=record, s=snapshot)")
    print("\n2. Web Application (Recommended for production)")
    print("   - Full web dashboard")
    print("   - Multi-camera support")
    print("   - Remote access")
    print("\n3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        print("\n🚀 Launching standalone application...")
        print("Press 'q' to quit\n")
        try:
            subprocess.run([sys.executable, 'main_v2.py'])
        except KeyboardInterrupt:
            print("\n\n✓ Application stopped")
    
    elif choice == '2':
        print("\n🚀 Launching web application...")
        print("Backend will start on http://localhost:5000")
        print("Open browser and navigate to http://localhost:5000")
        print("\nPress Ctrl+C to stop\n")
        try:
            subprocess.run([sys.executable, 'backend/app.py'])
        except KeyboardInterrupt:
            print("\n\n✓ Web server stopped")
    
    elif choice == '3':
        print("\n👋 Goodbye!")
        return
    
    else:
        print("\n❌ Invalid choice")

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        input("\nPress Enter to exit...")
        return
    
    # Ask user what they want to do
    print("\n" + "="*60)
    print("Setup Options:")
    print("="*60)
    print("\n1. Full Setup (First time installation)")
    print("2. Quick Launch (Skip setup)")
    print("3. Install Dependencies Only")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        print("\n🔧 Starting full setup...\n")
        
        create_directories()
        
        if not install_dependencies():
            print("\n❌ Setup failed at dependency installation")
            input("\nPress Enter to exit...")
            return
        
        setup_environment()
        download_models()
        
        print("\n" + "="*60)
        print("✅ Setup Complete!")
        print("="*60)
        
        print("\n📝 Next steps:")
        print("1. Edit .env file with your Twilio and email credentials")
        print("2. Run this script again and choose 'Quick Launch'")
        print("3. Or run manually:")
        print("   - Standalone: python main_v2.py")
        print("   - Web App: python backend/app.py")
        
        input("\nPress Enter to continue...")
        run_system()
    
    elif choice == '2':
        run_system()
    
    elif choice == '3':
        create_directories()
        install_dependencies()
        print("\n✓ Dependencies installed")
        input("\nPress Enter to exit...")
    
    elif choice == '4':
        print("\n👋 Goodbye!")
        return
    
    else:
        print("\n❌ Invalid choice")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
