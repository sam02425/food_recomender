#!/usr/bin/env python3
"""
Test Script for Automated Human Experiment Simulator
====================================================

This script tests the experiment system with a small number of participants
to verify functionality before running the full 50-participant experiment.

Usage:
    python test_experiment_system.py
"""

import sys
import os
import requests
import json
from pathlib import Path

# Add the parent directory to the path to import the simulator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automated_human_experiment_simulator import ExperimentSimulator

def test_server_connection(base_url: str = "http://localhost:8000") -> bool:
    """Test if the backend server is accessible"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is accessible")
            return True
        else:
            print(f"❌ Backend server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend server: {e}")
        print("   Please ensure simple_server.py is running on port 8000")
        return False

def test_api_endpoints(base_url: str = "http://localhost:8000") -> bool:
    """Test if all required API endpoints are working"""
    endpoints = [
        ("/api/menu-data", "GET"),
        ("/api/dietary/restrictions/available", "GET"),
        ("/api/dietary/allergens/available", "GET"),
        ("/api/agent-status", "GET"),
        ("/api/agent-recommendations", "POST")
    ]

    all_working = True
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            elif method == "POST":
                response = requests.post(f"{base_url}{endpoint}",
                                       json={"user_id": "test", "context": {}},
                                       timeout=5)

            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Status {response.status_code}")
                all_working = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Error: {e}")
            all_working = False

    return all_working

def test_participant_generation() -> bool:
    """Test participant generation functionality"""
    try:
        simulator = ExperimentSimulator()
        participants = simulator.generate_participants(5)  # Test with 5 participants

        if len(participants) == 5:
            print("✅ Participant generation - OK")

            # Check participant diversity
            phases = [p.experiment_phase for p in participants]
            if "A" in phases and "B" in phases:
                print("✅ Phase distribution - OK")
            else:
                print("⚠️ Phase distribution may be skewed")

            # Check demographic diversity
            ages = [p.age for p in participants]
            if min(ages) >= 18 and max(ages) <= 65:
                print("✅ Age distribution - OK")
            else:
                print("❌ Age distribution out of range")
                return False

            return True
        else:
            print(f"❌ Expected 5 participants, got {len(participants)}")
            return False

    except Exception as e:
        print(f"❌ Participant generation failed: {e}")
        return False

def test_single_participant_experiment() -> bool:
    """Test running a single participant experiment"""
    try:
        simulator = ExperimentSimulator()
        participants = simulator.generate_participants(1)
        participant = participants[0]

        print(f"🧪 Testing experiment with participant {participant.id} (Phase {participant.experiment_phase})")

        # Run a simplified experiment (just a few steps)
        experiment_data = simulator.run_participant_experiment(participant)

        # Save the participant data to CSV and DB for test validation
        simulator.save_participant_data(participant, experiment_data)

        if experiment_data and "steps" in experiment_data:
            print(f"✅ Single participant experiment completed with {len(experiment_data['steps'])} steps")
            print(f"   Total time: {experiment_data.get('total_time', 0):.2f} seconds")
            return True
        else:
            print("❌ Single participant experiment failed")
            return False

    except Exception as e:
        print(f"❌ Single participant experiment failed: {e}")
        return False

def test_data_output() -> bool:
    """Test data output functionality"""
    try:
        results_dir = Path("experiment_results")
        if results_dir.exists():
            # Check for participant files
            participant_files = list(results_dir.glob("participant_*.json"))
            if participant_files:
                print(f"✅ Data output - {len(participant_files)} participant files created")

                # Check file content
                with open(participant_files[0], 'r') as f:
                    data = json.load(f)
                    if "participant" in data and "experiment" in data:
                        print("✅ Data file structure - OK")
                        return True
                    else:
                        print("❌ Data file structure incorrect")
                        return False
            else:
                print("❌ No participant data files found")
                return False
        else:
            print("❌ Results directory not found")
            return False

    except Exception as e:
        print(f"❌ Data output test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Automated Human Experiment Simulator")
    print("=" * 60)

    tests = [
        ("Server Connection", test_server_connection),
        ("API Endpoints", test_api_endpoints),
        ("Participant Generation", test_participant_generation),
        ("Single Participant Experiment", test_single_participant_experiment),
        ("Data Output", test_data_output)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 40)

        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The experiment system is ready to use.")
        print("\nTo run the full experiment:")
        print("  python automated_human_experiment_simulator.py")
    else:
        print("⚠️ Some tests failed. Please check the issues above before running the full experiment.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)