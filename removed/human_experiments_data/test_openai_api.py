#!/usr/bin/env python3
"""
Test script for OpenAI API integration
"""

import asyncio
import os
import sys
import aiohttp
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from adaptive_participant_system import OpenAIClient, ParticipantProfile, TrialData

async def test_openai_connection():
    """Test basic OpenAI API connectivity"""

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'YOUR_OPENAI_API_KEY_HERE':
        print("❌ OPENAI_API_KEY not set or invalid")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False

    print("🔍 Testing OpenAI API connection...")

    try:
        async with OpenAIClient(api_key, "gpt-3.5-turbo") as client:
            # Test with a simple prompt
            test_prompt = "Say 'Hello, OpenAI API is working!' in one sentence."

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": test_prompt}],
                "temperature": 0.7,
                "max_tokens": 50
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result['choices'][0]['message']['content']
                        print(f"✅ OpenAI API connection successful!")
                        print(f"Response: {response_text}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ OpenAI API error: {response.status}")
                        print(f"Error details: {error_text}")
                        return False

    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

async def test_participant_feedback():
    """Test participant feedback generation"""

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'YOUR_OPENAI_API_KEY_HERE':
        print("❌ OPENAI_API_KEY not set")
        return False

    print("\n🧪 Testing participant feedback generation...")

    # Create a test participant
    participant = ParticipantProfile(
        participant_id="test_001",
        age=25,
        gender="female",
        cultural_background="Indian",
        dietary_restrictions=["vegetarian"],
        allergens=["nuts"],
        tech_savviness=0.8,
        food_adventurousness=0.6,
        health_consciousness=0.7,
        price_sensitivity=0.5,
        time_pressure=0.3,
        learning_rate=0.6,
        trust_in_recommendations=0.7,
        previous_experience=0.4,
        mood=0.8,
        fatigue=0.2
    )

    # Create test trial data
    trial_data = TrialData(
        trial_id="trial_test_001",
        participant_id="test_001",
        trial_type="adaptive",
        start_time=datetime.now(),
        end_time=datetime.now(),
        task_completion_time=45.2,
        satisfaction_score=4.2,
        nasa_tlx_scores={"mental_demand": 3.5, "physical_demand": 2.0, "temporal_demand": 2.5, "performance": 4.0, "effort": 3.0, "frustration": 1.0},
        sus_scores={"ease_of_use": 4.0, "complexity": 2.0, "confidence": 4.5, "learnability": 4.0},
        recommendation_acceptance_rate=0.8,
        dietary_compliance=True,
        privacy_concerns=[],
        cultural_mismatches=[],
        learning_insights=["System adapted to my preferences."],
        system_failures=[],
        final_order={"main": "Paneer Biryani", "sides": ["Raita"]},
        llm_feedback=None
    )

    # Test system performance data
    system_performance = {
        'recommendations_count': 5,
        'dietary_accuracy': 0.95,
        'response_time': 1.2
    }

    try:
        async with OpenAIClient(api_key, "gpt-3.5-turbo") as client:
            feedback = await client.get_participant_feedback(
                participant, trial_data, system_performance
            )

            print(f"✅ Feedback generation successful!")
            print(f"Generated feedback: {feedback}")
            return True

    except Exception as e:
        print(f"❌ Feedback generation failed: {e}")
        return False

async def test_fallback_feedback():
    """Test fallback feedback when API is unavailable"""

    print("\n🔄 Testing fallback feedback...")

    # Create test data
    participant = ParticipantProfile(
        participant_id="test_002",
        age=30,
        gender="male",
        cultural_background="American",
        dietary_restrictions=["vegan"],
        allergens=[],
        tech_savviness=0.5,
        food_adventurousness=0.3,
        health_consciousness=0.9,
        price_sensitivity=0.7,
        time_pressure=0.6,
        learning_rate=0.4,
        trust_in_recommendations=0.3,
        previous_experience=0.8,
        mood=0.6,
        fatigue=0.4
    )

    trial_data = TrialData(
        trial_id="trial_test_002",
        participant_id="test_002",
        trial_type="baseline",
        start_time=datetime.now(),
        end_time=datetime.now(),
        task_completion_time=67.8,
        satisfaction_score=3.1,
        nasa_tlx_scores={"mental_demand": 4.0, "physical_demand": 2.5, "temporal_demand": 3.0, "performance": 3.0, "effort": 3.5, "frustration": 2.0},
        sus_scores={"ease_of_use": 3.0, "complexity": 3.0, "confidence": 3.5, "learnability": 3.0},
        recommendation_acceptance_rate=0.4,
        dietary_compliance=False,
        privacy_concerns=["System asked for unnecessary personal info."],
        cultural_mismatches=["Recommended beef to a vegan participant."],
        learning_insights=["System did not adapt to my feedback."],
        system_failures=["Timeout error during order submission."],
        final_order={"main": "Vegan Wrap", "sides": ["Salad"]},
        llm_feedback=None
    )

    # Test with invalid API key to trigger fallback
    async with OpenAIClient("invalid_key", "gpt-3.5-turbo") as client:
        feedback = await client.get_participant_feedback(
            participant, trial_data, {}
        )

        print(f"✅ Fallback feedback working!")
        print(f"Fallback feedback: {feedback}")
        return True

def main():
    """Run all tests"""

    print("OpenAI API Integration Tests")
    print("=" * 40)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Run tests
    tests = [
        ("API Connection", test_openai_connection),
        ("Participant Feedback", test_participant_feedback),
        ("Fallback Feedback", test_fallback_feedback)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = asyncio.run(test_func())
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nTests passed: {passed}/{len(results)}")

    if passed == len(results):
        print("🎉 All tests passed! OpenAI integration is ready.")
    else:
        print("⚠️  Some tests failed. Check configuration and API key.")

    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)