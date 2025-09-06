#!/usr/bin/env python3
"""
TTS Server Test Script

Test script to validate the TTS server functionality.
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test configuration
SERVER_URL = "http://localhost:8000"
TEST_MESSAGES = [
    "שלום, איך אתה?",  # Hello, how are you?
    "אני דן כהן, סוכן מכירות מקצועי.",  # I'm Dan Cohen, professional sales agent
    "יש לי פתרון מעולה בשבילכם!",  # I have an excellent solution for you!
]

async def test_health_check():
    """Test the health check endpoint."""
    print("🏥 Testing health check endpoint...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{SERVER_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data['status']}")
                    print(f"   Supported modes: {data['supported_modes']}")
                    print(f"   API versions: {data['api_versions']}")
                    return True
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

async def test_synthesis(mode: str, message: str):
    """Test the synthesis endpoint."""
    print(f"🎤 Testing synthesis with mode: {mode}")
    print(f"   Message: {message}")
    
    payload = {
        "message": message,
        "mode": mode,
        "voice_settings": {}
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{SERVER_URL}/test",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        print(f"✅ Synthesis successful")
                        print(f"   Audio size: {data['audio_size_bytes']} bytes")
                        print(f"   Generation time: {data['generation_time_seconds']}s")
                        print(f"   Format: {data['format']}")
                        return True
                    else:
                        print(f"❌ Synthesis failed: {data.get('error')}")
                        return False
                else:
                    print(f"❌ HTTP error: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Synthesis error: {e}")
            return False

async def main():
    """Main test function."""
    print("🧪 Starting TTS Server Tests")
    print("="*50)
    
    # Test health check
    if not await test_health_check():
        print("❌ Health check failed, stopping tests")
        return
    
    print()
    
    # Test both modes with Hebrew messages
    modes = ["v3", "realtime"]
    success_count = 0
    total_tests = 0
    
    for mode in modes:
        print(f"📋 Testing {mode.upper()} mode")
        print("-" * 30)
        
        for message in TEST_MESSAGES:
            total_tests += 1
            if await test_synthesis(mode, message):
                success_count += 1
            print()  # Add spacing between tests
    
    # Summary
    print("📊 Test Summary")
    print("=" * 50)
    print(f"✅ Successful tests: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Your TTS server is working correctly.")
    else:
        print(f"⚠️  {total_tests - success_count} tests failed. Check the logs above.")
    
    print("\n📝 Next Steps:")
    print("1. Deploy your server to a public URL")
    print("2. Update the Vapi config with your server URL")
    print("3. Create an assistant in Vapi Dashboard")
    print("4. Test the assistant with 'Test Call' feature")

if __name__ == "__main__":
    asyncio.run(main())
