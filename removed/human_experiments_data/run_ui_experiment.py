#!/usr/bin/env python3
"""
Run UI-Based Experiment with Realistic Timing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_ui_experiment import SimpleUIExperimentConfig, SimpleUIExperimentRunner
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ui_experiment.log'),
        logging.StreamHandler()
    ]
)

def main():
    """Run the UI-based experiment"""
    print("Starting UI-Based Experiment with Realistic Timing")
    print("=" * 60)

    # Configuration
    config = SimpleUIExperimentConfig(
        frontend_url="http://localhost:3000",
        backend_url="http://localhost:8000",
        total_participants=10,  # Adjust as needed
        trials_per_participant=10,
        baseline_trials=5,
        adaptive_trials=5,
        realistic_timing=True,
        output_dir="ui_experiment_results"
    )

    print(f"Configuration:")
    print(f"  Participants: {config.total_participants}")
    print(f"  Trials per participant: {config.trials_per_participant}")
    print(f"  Baseline trials: {config.baseline_trials}")
    print(f"  Adaptive trials: {config.adaptive_trials}")
    print(f"  Realistic timing: {config.realistic_timing}")
    print(f"  Output directory: {config.output_dir}")
    print()

    # Create and run experiment
    runner = SimpleUIExperimentRunner(config)

    print("Starting experiment...")
    print("Note: This will take time due to realistic human interaction timing")
    print()

    try:
        results = runner.run_full_experiment()
        runner.save_results(results)

        print("=" * 60)
        print("Experiment completed successfully!")
        print(f"Total trials completed: {len(results)}")
        print(f"Results saved to: {config.output_dir}/")

        # Print summary
        baseline_trials = [r for r in results if r.condition == "baseline"]
        adaptive_trials = [r for r in results if r.condition == "adaptive"]

        print("\nSummary:")
        print(f"  Baseline trials: {len(baseline_trials)}")
        print(f"  Adaptive trials: {len(adaptive_trials)}")

        if baseline_trials and adaptive_trials:
            baseline_avg_time = sum(r.completion_time_seconds for r in baseline_trials) / len(baseline_trials)
            adaptive_avg_time = sum(r.completion_time_seconds for r in adaptive_trials) / len(adaptive_trials)

            baseline_avg_satisfaction = sum(r.satisfaction_rating for r in baseline_trials) / len(baseline_trials)
            adaptive_avg_satisfaction = sum(r.satisfaction_rating for r in adaptive_trials) / len(adaptive_trials)

            print(f"  Average completion time:")
            print(f"    Baseline: {baseline_avg_time:.2f} seconds")
            print(f"    Adaptive: {adaptive_avg_time:.2f} seconds")
            print(f"    Difference: {adaptive_avg_time - baseline_avg_time:.2f} seconds")

            print(f"  Average satisfaction:")
            print(f"    Baseline: {baseline_avg_satisfaction:.2f}/7.0")
            print(f"    Adaptive: {adaptive_avg_satisfaction:.2f}/7.0")
            print(f"    Difference: {adaptive_avg_satisfaction - baseline_avg_satisfaction:.2f}")

    except Exception as e:
        print(f"Error running experiment: {e}")
        logging.error(f"Experiment failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())