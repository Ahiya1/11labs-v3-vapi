#!/usr/bin/env python3
"""
TTS Server Test Script

Test script to validate the TTS server functionality with both voice modes.
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

# Voice settings for different modes
VOICE_SETTINGS = {
    "realtime": {
        "voice": "alloy",
        "speed": 1.0
    },
    "v3": {
        "style": 0.6,
        "stability": 0.75,
        "similarity_boost": 0.85,
        "use_speaker_boost": True
    }
}

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

async def test_synthesis(mode: str, message: str, voice_settings: dict = None):
    """Test the synthesis endpoint with specified voice settings."""
    print(f"🎤 Testing synthesis with mode: {mode}")
    print(f"   Message: {message}")
    if voice_settings:
        print(f"   Voice settings: {voice_settings}")
    
    payload = {
        "message": message,
        "mode": mode,
        "voice_settings": voice_settings or {}
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
                        
                        # Performance feedback
                        if data['generation_time_seconds'] < 1.0:
                            print(f"   ⚡ Excellent latency!")
                        elif data['generation_time_seconds'] < 2.0:
                            print(f"   👍 Good latency")
                        else:
                            print(f"   ⚠️  High latency (>2s)")
                        
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

async def test_vapi_integration():
    """Test Vapi integration with X-VAPI-SECRET header."""
    print("🔐 Testing Vapi integration endpoint...")
    
    # Get VAPI_SECRET from environment
    vapi_secret = os.getenv("VAPI_SECRET", "your-vapi-secret-here")
    
    payload = {
        "message": "בדיקת אינטגרציה עם Vapi",
        "mode": "v3",
        "voice_settings": VOICE_SETTINGS["v3"]
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-VAPI-SECRET": vapi_secret
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{SERVER_URL}/synthesize",
                json=payload,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    audio_data = await response.read()
                    print(f"✅ Vapi integration successful")
                    print(f"   Audio size: {len(audio_data)} bytes")
                    print(f"   Content-Type: {response.headers.get('Content-Type')}")
                    return True
                elif response.status == 401:
                    print(f"❌ Authentication failed - check VAPI_SECRET")
                    return False
                else:
                    print(f"❌ HTTP error: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Vapi integration error: {e}")
            return False

async def test_voice_quality_comparison():
    """Compare voice quality between different modes."""
    print("🎵 Testing voice quality comparison...")
    print("-" * 50)
    
    test_message = "שלום, זוהי בדיקה איכות קול עבור מכירות בעברית."
    
    # Test realtime mode
    print("\n📞 REALTIME MODE (Low-latency):")
    realtime_success = await test_synthesis(
        "realtime", 
        test_message, 
        VOICE_SETTINGS["realtime"]
    )
    
    print("\n" + "="*30 + "\n")
    
    # Test v3 mode  
    print("🎭 ELEVENLABS V3 MODE (Expressive quality):")
    v3_success = await test_synthesis(
        "v3", 
        test_message, 
        VOICE_SETTINGS["v3"]
    )
    
    print("\n" + "="*50)
    print("📊 COMPARISON RESULTS:")
    print(f"Realtime: {'✅ Working' if realtime_success else '❌ Failed'}")
    print(f"ElevenLabs v3: {'✅ Working' if v3_success else '❌ Failed'}")
    
    if realtime_success and v3_success:
        print("\n💡 RECOMMENDATIONS:")
        print("• Use 'realtime' mode for quick, conversational responses")
        print("• Use 'v3' mode for expressive, high-quality Hebrew speech")
        print("• Both modes support Hebrew language natively")
    
    return realtime_success and v3_success

async def main():
    """Main test function."""
    print("🧪 Starting Enhanced TTS Server Tests")
    print("="*60)
    
    # Test health check
    if not await test_health_check():
        print("❌ Health check failed, stopping tests")
        return
    
    print()
    
    # Test voice quality comparison
    await test_voice_quality_comparison()
    print()
    
    # Test both modes with Hebrew messages
    modes = [("v3", VOICE_SETTINGS["v3"]), ("realtime", VOICE_SETTINGS["realtime"])]
    success_count = 0
    total_tests = 0
    
    for mode, voice_settings in modes:
        print(f"📋 Testing {mode.upper()} mode with optimized voice settings")
        print("-" * 40)
        
        for message in TEST_MESSAGES:
            total_tests += 1
            if await test_synthesis(mode, message, voice_settings):
                success_count += 1
            print()  # Add spacing between tests
    
    # Test Vapi integration
    print("🔗 Testing Vapi Integration")
    print("-" * 40)
    vapi_success = await test_vapi_integration()
    if vapi_success:
        success_count += 1
    total_tests += 1
    print()
    
    # Summary
    print("📊 Test Summary")
    print("=" * 60)
    print(f"✅ Successful tests: {success_count}/{total_tests}")
    success_rate = (success_count / total_tests) * 100
    print(f"📈 Success rate: {success_rate:.1f}%")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Your TTS server is working perfectly.")
        print("\n🚀 Next Steps:")
        print("1. Deploy your server to a public URL (Railway, Render, etc.)")
        print("2. Update the Vapi config files with your deployed URL")
        print("3. Replace 'your-deployed-domain.com' with actual domain")
        print("4. Create an assistant in Vapi Dashboard")
        print("5. Test the assistant with 'Test Call' feature")
    else:
        print(f"⚠️  {total_tests - success_count} tests failed. Check the logs above.")
        print("\n🔧 Troubleshooting:")
        if not vapi_success:
            print("• Check VAPI_SECRET in .env file")
        print("• Verify API keys are valid")
        print("• Check internet connectivity")
        print("• Review server logs for detailed errors")
    
    print("\n📝 Configuration Summary:")
    print(f"• OpenAI Realtime Model: {os.getenv('OPENAI_REALTIME_MODEL', 'gpt-realtime')}")
    print(f"• OpenAI Realtime Voice: {os.getenv('OPENAI_REALTIME_VOICE', 'alloy')}")
    print(f"• ElevenLabs Model: {os.getenv('ELEVENLABS_MODEL_ID', 'eleven_v3')}")
    print(f"• ElevenLabs Voice ID: {os.getenv('ELEVENLABS_VOICE_ID', 'Not set')[:10]}...")

if __name__ == "__main__":
    asyncio.run(main())
