#!/usr/bin/env python3
"""
Quick Start Script for Automated Human Experiment Simulator
===========================================================

This script provides an easy way to run the experiment with proper setup
and error handling.

Usage:
    python run_experiment.py [--test] [--participants N] [--config FILE]
"""

import sys
import os
import argparse
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['requests', 'numpy', 'pandas']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall dependencies with:")
        print("   pip install -r requirements_experiment.txt")
        return False

    print("✅ All required packages are installed")
    return True

def check_server():
    """Check if the backend server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            return True
        else:
            print(f"❌ Backend server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ Backend server is not running")
        print("   Starting backend server...")

        try:
            # Start the server in the background
            server_process = subprocess.Popen(
                ["python", "simple_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )

            # Wait a moment for the server to start
            time.sleep(3)

            # Check if server started successfully
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Backend server started successfully")
                    return True
                else:
                    print("❌ Backend server failed to start properly")
                    return False
            except requests.exceptions.RequestException:
                print("❌ Backend server failed to start")
                return False

        except Exception as e:
            print(f"❌ Failed to start backend server: {e}")
            return False

def create_results_directory():
    """Create the results directory if it doesn't exist"""
    results_dir = Path("removed/experiment_results")
    results_dir.mkdir(parents=True, exist_ok=True)
    print("✅ Results directory ready")

def run_test_mode():
    """Run the experiment in test mode with a small number of participants"""
    print("\n🧪 Running in TEST MODE")
    print("=" * 40)

    try:
        from test_experiment_system import main as test_main
        success = test_main()

        if success:
            print("\n🎉 Test mode completed successfully!")
            print("The experiment system is ready for full execution.")
        else:
            print("\n⚠️ Test mode found issues. Please resolve them before running the full experiment.")

        return success

    except ImportError:
        print("❌ Test script not found")
        return False
    except Exception as e:
        print(f"❌ Test mode failed: {e}")
        return False

def run_full_experiment(participant_count=50):
    """Run the full experiment with specified number of participants"""
    print(f"\n🚀 Running FULL EXPERIMENT with {participant_count} participants")
    print("=" * 60)

    try:
        from automated_human_experiment_simulator import ExperimentSimulator

        # Initialize simulator
        simulator = ExperimentSimulator()

        # Modify participant count if needed
        if participant_count != 50:
            print(f"⚠️ Note: Running with {participant_count} participants instead of default 50")

        # Run the experiment
        simulator.run_full_experiment()

        print("\n🎉 Full experiment completed successfully!")
        print(f"📊 Results saved to: {simulator.results_dir}")

        return True

    except ImportError:
        print("❌ Experiment simulator not found")
        return False
    except Exception as e:
        print(f"❌ Full experiment failed: {e}")
        return False

def show_results_summary():
    """Show a summary of the experiment results"""
    results_dir = Path("removed/experiment_results")

    if not results_dir.exists():
        print("❌ No results directory found")
        return

    print("\n📊 Experiment Results Summary")
    print("=" * 40)

    # Count participant files
    participant_files = list(results_dir.glob("participant_*.json"))
    print(f"📁 Participants: {len(participant_files)}")

    # Check for main results file
    if (results_dir / "experiment_results.json").exists():
        print("📈 Main results: experiment_results.json")

    # Check for CSV files
    csv_files = list(results_dir.glob("*.csv"))
    if csv_files:
        print(f"📊 CSV reports: {len(csv_files)} files")

    # Check for analysis report
    if (results_dir / "detailed_analysis.md").exists():
        print("📋 Analysis: detailed_analysis.md")

    print("\n📖 To view detailed results:")
    print("   - Open experiment_results.json for comprehensive data")
    print("   - Open detailed_analysis.md for analysis report")
    print("   - Open *.csv files for statistical analysis")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run the Automated Human Experiment Simulator")
    parser.add_argument("--test", action="store_true", help="Run in test mode with minimal participants")
    parser.add_argument("--participants", type=int, default=50, help="Number of participants (default: 50)")
    parser.add_argument("--config", type=str, help="Path to custom configuration file")

    args = parser.parse_args()

    print("🚀 Automated Human Experiment Simulator")
    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check server
    if not check_server():
        print("\n❌ Cannot proceed without backend server")
        print("Please ensure simple_server.py is running on port 8000")
        sys.exit(1)

    # Create results directory
    create_results_directory()

    # Run based on mode
    if args.test:
        success = run_test_mode()
    else:
        success = run_full_experiment(args.participants)

    if success:
        show_results_summary()
        print("\n✅ Experiment completed successfully!")
    else:
        print("\n❌ Experiment failed")
        sys.exit(1)

if __name__ == "__main__":
    main()