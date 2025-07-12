#!/usr/bin/env python3
import asyncio
import httpx

async def test_backend_connectivity():
    """Test if the async HTTP client can connect to the backend"""
    try:
        async with httpx.AsyncClient() as client:
            print("Testing backend connectivity...")
            response = await client.get("http://localhost:8000/health", timeout=5)
            print(f"✅ Backend is accessible: Status {response.status_code}")
            print(f"Response: {response.text}")
            return True
    except Exception as e:
        print(f"❌ Backend connectivity failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_backend_connectivity())