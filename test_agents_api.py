import requests
import datetime
import json

API_URL = "http://localhost:8000/api/v1/agents"
DUMMY_TOKEN = "testtoken"  # Replace with a real token if your API requires auth

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {DUMMY_TOKEN}"
}

def print_json(title, data):
    print(f"\n=== {title} ===")
    print(json.dumps(data, indent=2))

def check_health():
    resp = requests.get(f"{API_URL}/health", headers=HEADERS)
    print_json("Agent Health", resp.json())

def test_recommendation(request_type):
    payload = {
        "user_context": {
            "user_id": "test_user",
            "session_id": "test_session",
            "current_time": datetime.datetime.utcnow().isoformat() + "Z",
            "location": {"latitude": 37.7749, "longitude": -122.4194, "address": "San Francisco"},
            "device_info": {"user_agent": "test", "screen_size": "1920x1080", "platform": "web"}
        },
        "request_type": request_type
    }
    resp = requests.post(f"{API_URL}/recommendations", headers=HEADERS, json=payload)
    print_json(f"Recommendation ({request_type})", resp.json())

def main():
    print("Testing agent health endpoint...")
    check_health()
    for req_type in ["full_recommendation", "quick_recommendation", "risk_assessment", "context_only"]:
        print(f"\nTesting {req_type}...")
        test_recommendation(req_type)

if __name__ == "__main__":
    main()