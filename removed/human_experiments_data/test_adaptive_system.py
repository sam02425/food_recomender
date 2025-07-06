"""
Test script for the Adaptive Artificial Participant System
Runs a small-scale test to verify functionality
"""

import asyncio
import json
import logging
from adaptive_participant_system import AdaptiveParticipantSystem
from experiment_config import ExperimentConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_small_experiment():
    """Run a small test experiment with 3 participants"""

    print("=== ADAPTIVE PARTICIPANT SYSTEM TEST ===")

    # Validate configuration
    if not ExperimentConfig.validate_config():
        print("❌ Configuration validation failed")
        return

    print("✅ Configuration validated")

    # Create test experiment with small numbers
    test_config = {
        'num_participants': 3,
        'trials_per_participant': 4,  # 2 baseline + 2 adaptive
        'groq_api_key': ExperimentConfig.GROQ_API_KEY
    }

    experiment = AdaptiveParticipantSystem(
        groq_api_key=test_config['groq_api_key'],
        num_participants=test_config['num_participants'],
        trials_per_participant=test_config['trials_per_participant']
    )

    print(f"🧪 Running test with {test_config['num_participants']} participants")
    print(f"📊 {test_config['trials_per_participant']} trials per participant")

    try:
        # Generate participants first
        participants = experiment.generate_realistic_participants()
        print(f"✅ Generated {len(participants)} participant profiles")

        # Show sample participant
        sample_participant = participants[0]
        print(f"\n📋 Sample Participant Profile:")
        print(f"  ID: {sample_participant.participant_id}")
        print(f"  Age: {sample_participant.age}")
        print(f"  Cultural Background: {sample_participant.cultural_background}")
        print(f"  Dietary Restrictions: {sample_participant.dietary_restrictions}")
        print(f"  Allergens: {sample_participant.allergens}")
        print(f"  Tech Savviness: {sample_participant.tech_savviness:.2f}")
        print(f"  Food Adventurousness: {sample_participant.food_adventurousness:.2f}")

        # Test single trial simulation
        print(f"\n🧪 Testing single trial simulation...")
        trial_data, system_perf = experiment.simulate_trial(
            sample_participant, 'baseline', 1
        )

        print(f"✅ Trial simulation successful:")
        print(f"  Trial ID: {trial_data.trial_id}")
        print(f"  Completion Time: {trial_data.task_completion_time:.1f}s")
        print(f"  Satisfaction: {trial_data.satisfaction_score:.2f}/5")
        print(f"  Recommendation Acceptance: {trial_data.recommendation_acceptance_rate:.1%}")
        print(f"  Dietary Compliance: {trial_data.dietary_compliance}")
        print(f"  System Quality: {system_perf.get('overall_quality', 0):.2f}")

        # Test LLM feedback (if API key is available)
        if ExperimentConfig.GROQ_API_KEY != 'YOUR_GROQ_API_KEY_HERE':
            print(f"\n🤖 Testing LLM feedback...")
            async with experiment.GROQClient(ExperimentConfig.GROQ_API_KEY) as groq_client:
                feedback = await groq_client.get_participant_feedback(
                    sample_participant, trial_data, system_perf
                )
                print(f"✅ LLM Feedback: {feedback}")
        else:
            print(f"\n⚠️  Skipping LLM feedback test (no API key)")

        # Run full experiment
        print(f"\n🚀 Running full test experiment...")
        results = await experiment.run_experiment()

        print(f"✅ Experiment completed successfully!")
        print(f"\n📊 Results Summary:")
        print(f"  Total Trials: {results['experiment_summary']['total_trials']}")
        print(f"  Baseline Trials: {results['experiment_summary']['baseline_trials']}")
        print(f"  Adaptive Trials: {results['experiment_summary']['adaptive_trials']}")

        # Show performance comparison
        baseline = results['performance_metrics']['baseline']
        adaptive = results['performance_metrics']['adaptive']

        print(f"\n📈 Performance Comparison:")
        print(f"  Task Completion Time:")
        print(f"    Baseline: {baseline['avg_completion_time']:.1f}s")
        print(f"    Adaptive: {adaptive['avg_completion_time']:.1f}s")
        print(f"    Difference: {adaptive['avg_completion_time'] - baseline['avg_completion_time']:.1f}s")

        print(f"  Satisfaction Score:")
        print(f"    Baseline: {baseline['avg_satisfaction']:.2f}/5")
        print(f"    Adaptive: {adaptive['avg_satisfaction']:.2f}/5")
        print(f"    Difference: {adaptive['avg_satisfaction'] - baseline['avg_satisfaction']:.2f}")

        print(f"  Recommendation Acceptance:")
        print(f"    Baseline: {baseline['avg_recommendation_acceptance']:.1%}")
        print(f"    Adaptive: {adaptive['avg_recommendation_acceptance']:.1%}")
        print(f"    Difference: {adaptive['avg_recommendation_acceptance'] - baseline['avg_recommendation_acceptance']:.1%}")

        # Show statistical analysis
        if 'statistical_analysis' in results:
            print(f"\n📊 Statistical Analysis:")
            for metric, analysis in results['statistical_analysis'].items():
                if 'significant' in analysis:
                    significance = "✅" if analysis['significant'] else "❌"
                    print(f"  {metric}: {significance} p={analysis['p_value']:.3f}")

        # Save results
        filename = experiment.save_results("test_results.json")
        print(f"\n💾 Results saved to: {filename}")

        print(f"\n🎉 Test completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
        return False

async def test_participant_generation():
    """Test participant generation specifically"""

    print("\n=== PARTICIPANT GENERATION TEST ===")

    experiment = AdaptiveParticipantSystem(
        groq_api_key="test_key",
        num_participants=10,
        trials_per_participant=2
    )

    participants = experiment.generate_realistic_participants()

    print(f"✅ Generated {len(participants)} participants")

    # Analyze diversity
    cultural_backgrounds = {}
    dietary_restrictions = {}
    age_range = []

    for p in participants:
        # Cultural backgrounds
        cultural_backgrounds[p.cultural_background] = cultural_backgrounds.get(p.cultural_background, 0) + 1

        # Dietary restrictions
        if p.dietary_restrictions:
            for restriction in p.dietary_restrictions:
                dietary_restrictions[restriction] = dietary_restrictions.get(restriction, 0) + 1
        else:
            dietary_restrictions['none'] = dietary_restrictions.get('none', 0) + 1

        # Age range
        age_range.append(p.age)

    print(f"\n📊 Participant Diversity:")
    print(f"  Cultural Backgrounds:")
    for bg, count in cultural_backgrounds.items():
        print(f"    {bg}: {count} ({count/len(participants)*100:.1f}%)")

    print(f"  Dietary Restrictions:")
    for restriction, count in dietary_restrictions.items():
        print(f"    {restriction}: {count} ({count/len(participants)*100:.1f}%)")

    print(f"  Age Range: {min(age_range)} - {max(age_range)} (avg: {sum(age_range)/len(age_range):.1f})")

    return True

async def main():
    """Main test function"""

    print("🧪 Testing Adaptive Artificial Participant System")
    print("=" * 50)

    # Test 1: Participant generation
    success1 = await test_participant_generation()

    # Test 2: Small experiment
    success2 = await test_small_experiment()

    if success1 and success2:
        print("\n🎉 All tests passed!")
        print("\n✅ System is ready for full experiment")
        print("\nTo run the full experiment:")
        print("1. Set your GROQ API key in experiment_config.py")
        print("2. Run: python adaptive_participant_system.py")
    else:
        print("\n❌ Some tests failed")
        print("Please check the error messages above")

if __name__ == "__main__":
    asyncio.run(main())