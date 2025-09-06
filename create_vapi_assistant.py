#!/usr/bin/env python3
"""
Create VAPI Assistant with ElevenLabs V3 Custom Voice Provider

This script creates a VAPI assistant that uses our custom TTS server
for ElevenLabs V3 voice synthesis (no realtime mode).

Author: Keen AI Agent
Date: 2025-09-06
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
VAPI_BASE_URL = "https://api.vapi.ai"
CONFIG_FILE = "vapi_assistant_final_v3.json"

def load_assistant_config():
    """Load the assistant configuration from JSON file"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ Loaded assistant configuration from {CONFIG_FILE}")
        return config
    except FileNotFoundError:
        print(f"❌ Configuration file {CONFIG_FILE} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        return None

def create_vapi_assistant(config):
    """Create the assistant using VAPI API"""
    if not VAPI_PRIVATE_KEY:
        print("❌ VAPI_PRIVATE_KEY not found in environment variables")
        return None

    headers = {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }

    url = f"{VAPI_BASE_URL}/assistant"
    
    print(f"🚀 Creating VAPI assistant: {config['name']}")
    print(f"📡 Endpoint: {url}")
    print(f"🎙️ Voice Provider: {config['voice']['provider']}")
    print(f"🌐 TTS Server: {config['voice']['server']['url']}")
    
    try:
        response = requests.post(url, headers=headers, json=config, timeout=30)
        
        if response.status_code == 201:
            assistant_data = response.json()
            print(f"\n✅ Assistant created successfully!")
            print(f"📋 Assistant ID: {assistant_data['id']}")
            print(f"👤 Assistant Name: {assistant_data['name']}")
            print(f"🕐 Created At: {assistant_data['createdAt']}")
            
            # Save assistant info to file
            save_assistant_info(assistant_data)
            
            return assistant_data
        else:
            print(f"\n❌ Failed to create assistant")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def save_assistant_info(assistant_data):
    """Save assistant information to a file"""
    filename = f"assistant_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    assistant_info = {
        "id": assistant_data["id"],
        "name": assistant_data["name"],
        "created_at": assistant_data["createdAt"],
        "org_id": assistant_data["orgId"],
        "voice_provider": "custom-voice",
        "voice_mode": "elevenlabs_v3_only",
        "tts_server_url": assistant_data["voice"]["server"]["url"],
        "dashboard_url": f"https://dashboard.vapi.ai/assistant/{assistant_data['id']}",
        "test_call_info": {
            "description": "To test this assistant, go to the VAPI dashboard and click 'Test Call'",
            "expected_behavior": "Assistant should speak Hebrew using ElevenLabs V3 voice only",
            "fallback_voice": "ElevenLabs direct API (if custom server fails)"
        },
        "integration_notes": {
            "server_endpoint": "/synthesize",
            "required_headers": ["X-VAPI-SECRET"],
            "voice_mode_forced": "v3",
            "no_realtime": True
        }
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(assistant_info, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Assistant info saved to: {filename}")
    except Exception as e:
        print(f"⚠️ Failed to save assistant info: {e}")

def test_tts_server():
    """Test if the TTS server is accessible"""
    server_url = "https://11labs-v3-vapi-production.up.railway.app/health"
    
    print(f"\n🔍 Testing TTS server health...")
    try:
        response = requests.get(server_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ TTS Server is healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Supported Modes: {data.get('supported_modes')}")
            return True
        else:
            print(f"⚠️ TTS Server returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ TTS Server is not accessible: {e}")
        return False

def main():
    """Main function to create the VAPI assistant"""
    print("🎯 VAPI Assistant Creation Script")
    print("===================================")
    print(f"Target: ElevenLabs V3 Only Assistant")
    print(f"Mode: Custom Voice Provider")
    print(f"Language: Hebrew")
    print(f"Server: https://11labs-v3-vapi-production.up.railway.app/")
    print()
    
    # Test TTS server first
    if not test_tts_server():
        print("\n⚠️ TTS server is not accessible. Assistant creation may fail.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborting...")
            return False
    
    # Load configuration
    config = load_assistant_config()
    if not config:
        return False
    
    # Add dynamic timestamp to name
    config["name"] += f" - {datetime.now().strftime('%Y%m%d_%H%M')}"
    
    # Create assistant
    assistant = create_vapi_assistant(config)
    if not assistant:
        return False
    
    print("\n🎉 SUCCESS! Your ElevenLabs V3 Assistant is ready!")
    print("\n📖 Next Steps:")
    print(f"   1. Visit: https://dashboard.vapi.ai/assistant/{assistant['id']}")
    print("   2. Click 'Test Call' to test your assistant")
    print("   3. The assistant will only use ElevenLabs V3 voice (no realtime)")
    print("   4. All conversations will be in Hebrew")
    print("\n💡 Tips:")
    print("   - The assistant uses your custom TTS server for voice synthesis")
    print("   - Fallback to direct ElevenLabs API if server fails")
    print("   - Check server logs if voice issues occur")
    print("   - Update voice settings in the assistant config if needed")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
