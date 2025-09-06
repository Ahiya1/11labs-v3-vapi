#!/usr/bin/env python3
"""
Setup script for the Vapi Hebrew Assistant TTS Server

This script helps set up the development environment and validates the configuration.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from urllib.parse import urlparse

def print_banner():
    """Print setup banner."""
    print("""
🌟 Vapi Hebrew Assistant Setup
===============================
Dynamic Voice Routing TTS Server

This script will help you set up your development environment
and validate your configuration.
    """)

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    try:
        # Check if requirements.txt exists
        if not Path("requirements.txt").exists():
            print("❌ requirements.txt not found!")
            return False
        
        # Install dependencies
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist."""
    print("⚙️  Setting up environment file...")
    
    if Path(".env").exists():
        print("✅ .env file already exists")
        return True
    
    if not Path(".env.example").exists():
        print("❌ .env.example not found!")
        return False
    
    # Copy .env.example to .env
    with open(".env.example", "r") as example_file:
        content = example_file.read()
    
    with open(".env", "w") as env_file:
        env_file.write(content)
    
    print("📝 Created .env file from template")
    print("⚠️  Please edit .env file with your API keys before continuing")
    return True

def validate_env_variables():
    """Validate environment variables."""
    print("🔍 Validating environment variables...")
    
    # Load .env file
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    # Parse .env file
    env_vars = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value.strip()
    
    # Required variables
    required_vars = [
        "OPENAI_API_KEY",
        "ELEVENLABS_API_KEY",
        "ELEVENLABS_VOICE_ID",
        "VAPI_PRIVATE_KEY"
    ]
    
    missing_vars = []
    placeholder_vars = []
    
    for var in required_vars:
        if var not in env_vars or not env_vars[var]:
            missing_vars.append(var)
        elif env_vars[var].startswith('your-') or env_vars[var].startswith('sk-your'):
            placeholder_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing variables: {', '.join(missing_vars)}")
        return False
    
    if placeholder_vars:
        print(f"⚠️  Placeholder values detected: {', '.join(placeholder_vars)}")
        print("   Please update these with your actual API keys")
        return False
    
    # Validate API key formats
    if not env_vars["OPENAI_API_KEY"].startswith("sk-"):
        print("❌ OPENAI_API_KEY should start with 'sk-'")
        return False
    
    if not env_vars["ELEVENLABS_API_KEY"].startswith("sk_"):
        print("❌ ELEVENLABS_API_KEY should start with 'sk_'")
        return False
    
    print("✅ Environment variables look good")
    return True

def validate_config_files():
    """Validate Vapi configuration files."""
    print("📋 Validating Vapi configuration files...")
    
    config_files = [
        "vapi_assistant_config.json",
        "vapi_assistant_config_realtime.json"
    ]
    
    for config_file in config_files:
        if not Path(config_file).exists():
            print(f"❌ {config_file} not found")
            return False
        
        try:
            with open(config_file) as f:
                config = json.load(f)
            
            # Check if URL needs to be updated
            voice_config = config.get("voice", {})
            url = voice_config.get("url", "")
            
            if "your-server-domain.com" in url:
                print(f"⚠️  {config_file} still has placeholder URL")
                print(f"   Current: {url}")
                print(f"   Update this with your actual server URL after deployment")
            
            print(f"✅ {config_file} is valid JSON")
            
        except json.JSONDecodeError as e:
            print(f"❌ {config_file} contains invalid JSON: {e}")
            return False
    
    return True

def test_imports():
    """Test if all required packages can be imported."""
    print("🔬 Testing package imports...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "httpx",
        "websockets",
        "pydub",
        "numpy",
        "dotenv",
        "aiohttp"  # For test script
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            failed_imports.append(package)
            print(f"  ❌ {package}")
    
    if failed_imports:
        print(f"❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All packages imported successfully")
    return True

def run_basic_tests():
    """Run basic functionality tests."""
    print("🧪 Running basic tests...")
    
    try:
        # Test server startup (import only)
        import tts_server
        print("✅ TTS server module loads successfully")
        
        # Test configuration loading
        from tts_server import OPENAI_API_KEY, ELEVENLABS_API_KEY
        
        if not OPENAI_API_KEY:
            print("❌ OPENAI_API_KEY not loaded")
            return False
        
        if not ELEVENLABS_API_KEY:
            print("❌ ELEVENLABS_API_KEY not loaded")
            return False
        
        print("✅ Configuration loaded successfully")
        
        # Test audio processing utilities
        from tts_server import convert_to_pcm_16khz_mono
        print("✅ Audio utilities available")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic tests failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("""
🎉 Setup Complete!

📋 Next Steps:

1. 🔧 Update your .env file with real API keys:
   - OpenAI API key (with Realtime access)
   - ElevenLabs API key (Pro tier recommended)
   - Vapi private key
   - Choose a strong VAPI_SECRET

2. 🧪 Test the server locally:
   python test_server.py

3. 🚀 Start the development server:
   python start_server.py

4. 🌐 Deploy to production:
   - Railway: railway up
   - Render: Connect GitHub repo
   - VPS: See DEPLOYMENT.md

5. ⚙️  Update Vapi configuration:
   - Replace "your-server-domain.com" with your actual URL
   - Update X-VAPI-SECRET header
   - Create assistant in Vapi Dashboard

6. 📞 Test your assistant:
   - Use "Test Call" in Vapi Dashboard
   - Speak in Hebrew
   - Verify responses are natural and clear

📚 Documentation:
   - README.md - Complete user guide
   - DEPLOYMENT.md - Deployment instructions
   - API documentation at /docs when server is running

🆘 Need help?
   - Check troubleshooting section in README.md
   - Review server logs for error messages
   - Test with provided test scripts first

Happy voice calling! 📞✨
    """)

def main():
    """Main setup function."""
    print_banner()
    
    steps = [
        ("Python Version", check_python_version),
        ("Dependencies", install_dependencies),
        ("Environment File", create_env_file),
        ("Environment Variables", validate_env_variables),
        ("Configuration Files", validate_config_files),
        ("Package Imports", test_imports),
        ("Basic Tests", run_basic_tests)
    ]
    
    passed = 0
    total = len(steps)
    
    for step_name, step_function in steps:
        print(f"\n🔄 {step_name}...")
        if step_function():
            passed += 1
        else:
            print(f"❌ {step_name} failed")
            
            # Some failures are not critical
            if step_name in ["Environment Variables", "Configuration Files"]:
                print("⚠️  You can fix this manually and continue")
                continue
            else:
                print(f"\n💥 Setup failed at step: {step_name}")
                sys.exit(1)
    
    print(f"\n📊 Setup Summary: {passed}/{total} steps completed")
    
    if passed == total:
        print("🎉 All checks passed!")
        print_next_steps()
    else:
        print("⚠️  Some steps need attention. Please review the output above.")
        print_next_steps()

if __name__ == "__main__":
    main()
