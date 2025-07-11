"""
Example script for running the Adaptive Artificial Participant Experiment
Shows how to run with or without GROQ API key for testing
"""

import asyncio
import json
import logging
from adaptive_participant_system import AdaptiveParticipantSystem
from experiment_config import ExperimentConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_experiment_with_llm():
    """Run experiment with GROQ LLM feedback"""

    print("🚀 Running Adaptive Participant Experiment with LLM Feedback")
    print("=" * 60)

    # Validate configuration
    if not ExperimentConfig.validate_config():
        print("❌ Configuration validation failed")
        print("Please set your GROQ API key in experiment_config.py")
        return None

    # Create experiment
    experiment = AdaptiveParticipantSystem(
        groq_api_key=ExperimentConfig.GROQ_API_KEY,
        num_participants=50,
        trials_per_participant=10
    )

    print(f"📊 Experiment Configuration:")
    print(f"  Participants: {ExperimentConfig.NUM_PARTICIPANTS}")
    print(f"  Trials per participant: {ExperimentConfig.TRIALS_PER_PARTICIPANT}")
    print(f"  Total trials: {ExperimentConfig.NUM_PARTICIPANTS * ExperimentConfig.TRIALS_PER_PARTICIPANT}")
    print(f"  LLM feedback frequency: Every {ExperimentConfig.LLM_FEEDBACK_FREQUENCY} trials")
    print(f"  Estimated API calls: ~{ExperimentConfig.NUM_PARTICIPANTS * ExperimentConfig.TRIALS_PER_PARTICIPANT // ExperimentConfig.LLM_FEEDBACK_FREQUENCY}")

    try:
        # Run experiment
        print(f"\n🧪 Starting experiment...")
        results = await experiment.run_experiment()

        # Save results
        filename = experiment.save_results("adaptive_experiment_results.json")

        # Print summary
        print(f"\n✅ Experiment completed successfully!")
        print(f"📁 Results saved to: {filename}")

        return results

    except Exception as e:
        logger.error(f"Experiment failed: {e}")
        print(f"❌ Experiment failed: {e}")
        return None

async def run_experiment_without_llm():
    """Run experiment without GROQ LLM feedback (for testing)"""

    print("🧪 Running Adaptive Participant Experiment (LLM Disabled)")
    print("=" * 60)

    # Temporarily disable LLM feedback
    original_enable = ExperimentConfig.ENABLE_LLM_FEEDBACK
    ExperimentConfig.ENABLE_LLM_FEEDBACK = False

    # Create experiment with dummy API key
    experiment = AdaptiveParticipantSystem(
        groq_api_key="dummy_key",
        num_participants=10,  # Smaller number for testing
        trials_per_participant=4  # 2 baseline + 2 adaptive
    )

    print(f"📊 Test Configuration:")
    print(f"  Participants: 10")
    print(f"  Trials per participant: 4")
    print(f"  Total trials: 40")
    print(f"  LLM feedback: Disabled")

    try:
        # Run experiment
        print(f"\n🧪 Starting test experiment...")
        results = await experiment.run_experiment()

        # Save results
        filename = experiment.save_results("test_experiment_results.json")

        # Print summary
        print(f"\n✅ Test experiment completed successfully!")
        print(f"📁 Results saved to: {filename}")

        # Restore original setting
        ExperimentConfig.ENABLE_LLM_FEEDBACK = original_enable

        return results

    except Exception as e:
        logger.error(f"Test experiment failed: {e}")
        print(f"❌ Test experiment failed: {e}")
        # Restore original setting
        ExperimentConfig.ENABLE_LLM_FEEDBACK = original_enable
        return None

def print_results_summary(results):
    """Print a summary of experiment results"""

    if not results:
        return

    print(f"\n📊 EXPERIMENT RESULTS SUMMARY")
    print(f"=" * 50)

    # Basic stats
    summary = results['experiment_summary']
    print(f"Total Participants: {summary['total_participants']}")
    print(f"Total Trials: {summary['total_trials']}")
    print(f"Baseline Trials: {summary['baseline_trials']}")
    print(f"Adaptive Trials: {summary['adaptive_trials']}")

    # Performance comparison
    baseline = results['performance_metrics']['baseline']
    adaptive = results['performance_metrics']['adaptive']

    print(f"\n📈 PERFORMANCE COMPARISON")
    print(f"-" * 30)

    # Task completion time
    baseline_time = baseline['avg_completion_time']
    adaptive_time = adaptive['avg_completion_time']
    time_diff = adaptive_time - baseline_time
    time_improvement = (time_diff / baseline_time) * 100

    print(f"Task Completion Time:")
    print(f"  Baseline: {baseline_time:.1f}s")
    print(f"  Adaptive: {adaptive_time:.1f}s")
    print(f"  Difference: {time_diff:+.1f}s ({time_improvement:+.1f}%)")

    # Satisfaction
    baseline_sat = baseline['avg_satisfaction']
    adaptive_sat = adaptive['avg_satisfaction']
    sat_diff = adaptive_sat - baseline_sat

    print(f"\nSatisfaction Score:")
    print(f"  Baseline: {baseline_sat:.2f}/5")
    print(f"  Adaptive: {adaptive_sat:.2f}/5")
    print(f"  Difference: {sat_diff:+.2f}")

    # Recommendation acceptance
    baseline_rec = baseline['avg_recommendation_acceptance']
    adaptive_rec = adaptive['avg_recommendation_acceptance']
    rec_diff = adaptive_rec - baseline_rec
    rec_improvement = (rec_diff / baseline_rec) * 100

    print(f"\nRecommendation Acceptance:")
    print(f"  Baseline: {baseline_rec:.1%}")
    print(f"  Adaptive: {adaptive_rec:.1%}")
    print(f"  Difference: {rec_diff:+.1%} ({rec_improvement:+.1f}%)")

    # Dietary compliance
    baseline_comp = baseline['dietary_compliance_rate']
    adaptive_comp = adaptive['dietary_compliance_rate']
    comp_diff = adaptive_comp - baseline_comp

    print(f"\nDietary Compliance:")
    print(f"  Baseline: {baseline_comp:.1%}")
    print(f"  Adaptive: {adaptive_comp:.1%}")
    print(f"  Difference: {comp_diff:+.1%}")

    # Statistical significance
    if 'statistical_analysis' in results:
        print(f"\n📊 STATISTICAL ANALYSIS")
        print(f"-" * 25)

        for metric, analysis in results['statistical_analysis'].items():
            if 'significant' in analysis:
                significance = "✅ SIGNIFICANT" if analysis['significant'] else "❌ NOT SIGNIFICANT"
                print(f"{metric.replace('_', ' ').title()}:")
                print(f"  p-value: {analysis['p_value']:.3f}")
                print(f"  Effect size: {analysis['effect_size']:.2f} ({analysis['effect_magnitude']})")
                print(f"  Result: {significance}")
                print()

    # Participant diversity
    if 'participant_diversity' in results:
        print(f"🌍 PARTICIPANT DIVERSITY")
        print(f"-" * 25)

        cultural = results['participant_diversity']['cultural_backgrounds']
        for bg, data in cultural.items():
            print(f"{bg}: {data['count']} participants (avg satisfaction: {data['avg_satisfaction']:.2f})")

    # Qualitative insights
    if 'qualitative_insights' in results:
        insights = results['qualitative_insights']
        print(f"\n💭 QUALITATIVE INSIGHTS")
        print(f"-" * 25)
        print(f"LLM Feedback Count: {insights['llm_feedback_count']}")

        if insights['privacy_concerns']:
            print(f"Privacy Concerns: {', '.join(insights['privacy_concerns'])}")

        if insights['cultural_mismatches']:
            print(f"Cultural Mismatches: {', '.join(insights['cultural_mismatches'])}")

        if insights['system_failures']:
            print(f"System Failures: {insights['system_failures']}")

async def main():
    """Main function with options for running with or without LLM"""

    print("🎯 Adaptive Artificial Participant System")
    print("=" * 50)
    print()
    print("Choose an option:")
    print("1. Run full experiment with LLM feedback (requires GROQ API key)")
    print("2. Run test experiment without LLM feedback")
    print("3. Show configuration")
    print("4. Exit")

    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == "1":
                print("\n" + "="*60)
                results = await run_experiment_with_llm()
                if results:
                    print_results_summary(results)
                break

            elif choice == "2":
                print("\n" + "="*60)
                results = await run_experiment_without_llm()
                if results:
                    print_results_summary(results)
                break

            elif choice == "3":
                print("\n" + "="*60)
                config = ExperimentConfig.get_config()
                print("📋 Current Configuration:")
                print(f"  Participants: {config['experiment_params']['num_participants']}")
                print(f"  Trials per participant: {config['experiment_params']['trials_per_participant']}")
                print(f"  LLM feedback enabled: {config['groq_settings']['enable_feedback']}")
                print(f"  LLM feedback frequency: Every {config['groq_settings']['feedback_frequency']} trials")
                print(f"  GROQ model: {config['groq_settings']['model']}")

                # Validate configuration
                if ExperimentConfig.validate_config():
                    print("  ✅ Configuration is valid")
                else:
                    print("  ❌ Configuration has errors")
                print()

            elif choice == "4":
                print("👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

        except KeyboardInterrupt:
            print("\n\n👋 Experiment cancelled by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())