"""
Script to help fix GROQ API key issues
"""

import os
import asyncio
import aiohttp

def print_troubleshooting_guide():
    """Print troubleshooting guide for GROQ API issues"""

    print("🔧 GROQ API Key Troubleshooting Guide")
    print("=" * 50)
    print()
    print("❌ Current API Key Issue: Invalid API Key (401 Error)")
    print()
    print("📋 Steps to Fix:")
    print()
    print("1. 🌐 Go to https://console.groq.com/")
    print("2. 🔐 Sign in to your GROQ account")
    print("3. 💳 Check if you have credits/usage available")
    print("4. 🔑 Go to 'API Keys' section")
    print("5. ➕ Create a new API key")
    print("6. 📋 Copy the new API key (starts with 'gsk_')")
    print("7. 🔄 Update the key in experiment_config.py")
    print()
    print("💡 Alternative: Run experiment without LLM feedback")
    print("   The system works perfectly with fallback feedback!")
    print()

async def test_new_api_key(api_key):
    """Test a new API key"""

    if not api_key.startswith('gsk_'):
        print("❌ Invalid API key format. Should start with 'gsk_'")
        return False

    base_url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": "Test"}],
        "max_tokens": 10
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(base_url, headers=headers, json=data) as response:
                if response.status == 200:
                    print("✅ New API key is working!")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ API key still not working: {error_text}")
                    return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def update_config_file(new_api_key):
    """Update the API key in experiment_config.py"""

    config_file = "experiment_config.py"

    try:
        with open(config_file, 'r') as f:
            content = f.read()

        # Replace the API key
        import re
        pattern = r"GROQ_API_KEY = os\.getenv\('GROQ_API_KEY', '[^']*'\)"
        replacement = f"GROQ_API_KEY = os.getenv('GROQ_API_KEY', '{new_api_key}')"

        new_content = re.sub(pattern, replacement, content)

        with open(config_file, 'w') as f:
            f.write(new_content)

        print(f"✅ Updated {config_file} with new API key")
        return True

    except Exception as e:
        print(f"❌ Error updating config file: {e}")
        return False

async def run_experiment_without_llm():
    """Run experiment without LLM feedback"""

    print("🚀 Running Experiment Without LLM Feedback")
    print("=" * 50)

    # Temporarily disable LLM feedback
    from experiment_config import ExperimentConfig
    original_enable = ExperimentConfig.ENABLE_LLM_FEEDBACK
    ExperimentConfig.ENABLE_LLM_FEEDBACK = False

    try:
        from adaptive_participant_system import AdaptiveParticipantSystem

        experiment = AdaptiveParticipantSystem(
            groq_api_key="dummy_key",
            num_participants=50,
            trials_per_participant=10
        )

        print("🧪 Starting full experiment (50 participants, 10 trials each)...")
        results = await experiment.run_experiment()

        filename = experiment.save_results("full_experiment_results.json")
        print(f"✅ Experiment completed! Results saved to: {filename}")

        # Print summary
        print("\n📊 EXPERIMENT SUMMARY")
        print("=" * 30)
        print(f"Total Participants: {results['experiment_summary']['total_participants']}")
        print(f"Total Trials: {results['experiment_summary']['total_trials']}")

        baseline = results['performance_metrics']['baseline']
        adaptive = results['performance_metrics']['adaptive']

        print(f"\nTask Completion Time:")
        print(f"  Baseline: {baseline['avg_completion_time']:.1f}s")
        print(f"  Adaptive: {adaptive['avg_completion_time']:.1f}s")
        print(f"  Difference: {adaptive['avg_completion_time'] - baseline['avg_completion_time']:+.1f}s")

        print(f"\nSatisfaction Score:")
        print(f"  Baseline: {baseline['avg_satisfaction']:.2f}/5")
        print(f"  Adaptive: {adaptive['avg_satisfaction']:.2f}/5")
        print(f"  Difference: {adaptive['avg_satisfaction'] - baseline['avg_satisfaction']:+.2f}")

        return results

    except Exception as e:
        print(f"❌ Experiment failed: {e}")
        return None
    finally:
        # Restore original setting
        ExperimentConfig.ENABLE_LLM_FEEDBACK = original_enable

async def main():
    """Main function"""

    print("🎯 GROQ API Key Fix & Experiment Runner")
    print("=" * 50)
    print()

    while True:
        print("Choose an option:")
        print("1. 🔧 Show troubleshooting guide")
        print("2. 🧪 Test a new API key")
        print("3. 🚀 Run full experiment without LLM feedback")
        print("4. 🔄 Update config file with new API key")
        print("5. ❌ Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            print_troubleshooting_guide()

        elif choice == "2":
            new_key = input("Enter new API key: ").strip()
            if new_key:
                await test_new_api_key(new_key)
            else:
                print("❌ No API key provided")

        elif choice == "3":
            print("\n" + "="*50)
            await run_experiment_without_llm()
            break

        elif choice == "4":
            new_key = input("Enter new API key: ").strip()
            if new_key:
                if update_config_file(new_key):
                    print("✅ Config updated! You can now run the experiment with LLM feedback.")
                else:
                    print("❌ Failed to update config file")
            else:
                print("❌ No API key provided")

        elif choice == "5":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please enter 1-5.")

        print()

if __name__ == "__main__":
    asyncio.run(main())