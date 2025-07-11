"""
Test script to verify GROQ API key functionality
"""

import asyncio
import aiohttp
import json

async def test_groq_api():
    """Test GROQ API with the provided key"""

    api_key = "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"
    base_url = "https://api.groq.com/openai/v1/chat/completions"

    print("🧪 Testing GROQ API Key...")
    print(f"API Key: {api_key[:20]}...{api_key[-4:]}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": "Hello, this is a test message."}],
        "temperature": 0.7,
        "max_tokens": 50
    }

    try:
        async with aiohttp.ClientSession() as session:
            print("📡 Sending test request to GROQ API...")

            async with session.post(base_url, headers=headers, json=data) as response:
                print(f"📊 Response Status: {response.status}")
                print(f"📊 Response Headers: {dict(response.headers)}")

                if response.status == 200:
                    result = await response.json()
                    print("✅ API Key is working!")
                    print(f"📝 Response: {result['choices'][0]['message']['content']}")
                    return True
                elif response.status == 401:
                    print("❌ 401 Unauthorized - API Key issue")
                    error_text = await response.text()
                    print(f"🔍 Error details: {error_text}")
                    return False
                elif response.status == 429:
                    print("⚠️ 429 Rate Limited - Too many requests")
                    return False
                else:
                    print(f"❌ Unexpected status: {response.status}")
                    error_text = await response.text()
                    print(f"🔍 Error details: {error_text}")
                    return False

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

async def test_models():
    """Test available models"""

    api_key = "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"
    models_url = "https://api.groq.com/openai/v1/models"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            print("\n📋 Testing available models...")

            async with session.get(models_url, headers=headers) as response:
                print(f"📊 Models Response Status: {response.status}")

                if response.status == 200:
                    result = await response.json()
                    print("✅ Available models:")
                    for model in result['data']:
                        print(f"  - {model['id']}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Error getting models: {error_text}")
                    return False

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

async def main():
    """Main test function"""

    print("🔍 GROQ API Diagnostic Test")
    print("=" * 40)

    # Test basic API functionality
    api_works = await test_groq_api()

    # Test available models
    models_work = await test_models()

    print("\n📊 SUMMARY")
    print("=" * 40)

    if api_works and models_work:
        print("✅ GROQ API is working correctly!")
        print("🚀 You can now run the experiment with LLM feedback.")
    else:
        print("❌ GROQ API has issues.")
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check if the API key is correct and active")
        print("2. Verify your GROQ account has credits/usage")
        print("3. Check if there are any rate limits")
        print("4. Try regenerating the API key")
        print("5. Run the experiment without LLM feedback for now")

if __name__ == "__main__":
    asyncio.run(main())