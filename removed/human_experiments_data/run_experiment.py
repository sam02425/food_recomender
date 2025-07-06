import asyncio
import time
from datetime import datetime
import json

from experiment_config import ExperimentConfig
from adaptive_participant_system import AdaptiveParticipantSystem
from experiment_runner import ExperimentRunner

async def main():
    """Main experiment runner"""

    # Load configuration
    config = ExperimentConfig()

    # Validate configuration
    if not config.validate_config():
        print("Configuration validation failed")
        return

    print("Starting Adaptive Artificial Participant Experiment")
    print("=" * 60)
    print(f"Participants: {config.NUM_PARTICIPANTS}")
    print(f"Trials per participant: {config.TRIALS_PER_PARTICIPANT}")
    print(f"Total trials: {config.NUM_PARTICIPANTS * config.TRIALS_PER_PARTICIPANT}")
    print(f"LLM Feedback: {'Enabled' if config.ENABLE_LLM_FEEDBACK else 'Disabled'}")

    # Set up experiment runner
    runner = ExperimentRunner({
        'experiment_name': 'Adaptive Artificial Participant Experiment',
        'total_participants': config.NUM_PARTICIPANTS,
        'trials_per_participant': config.TRIALS_PER_PARTICIPANT,
        'conditions': ['baseline', 'adaptive'],
        'trial_types': ['free_choice', 'free_choice', 'free_choice', 'specific_order', 'specific_order'],
        'start_time': datetime.now(),
        'end_time': None
    })

    # Run experiment
    print("\nRunning experiment...")
    start_time = time.time()
    results = await runner.run_experiment()
    end_time = time.time()
    duration = end_time - start_time

    print(f"\nExperiment completed in {duration:.1f} seconds")
    print(f"Total trials completed: {len(results)}")

    # Analyze results
    print("\nAnalyzing results...")
    analysis = runner.analyze_results(results)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"experiment_results_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump([r.__dict__ for r in results], f, indent=2, default=str)
    print(f"\nResults saved to: {results_file}")

    # Generate report
    runner.generate_report(results, analysis)
    print("Report generated.")

    print("\nExperiment completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())