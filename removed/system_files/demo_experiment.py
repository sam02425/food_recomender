#!/usr/bin/env python3
"""
Demo Experiment Runner
Confidential - Internal Research Use Only
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from human_experiment_system import HumanExperimentSystem

async def run_demo():
    """Run a demonstration of the experiment system"""
    
    print("🧪 Human Experiment System - Demo Mode")
    print("=" * 50)
    print("This demo will run a small-scale experiment to demonstrate")
    print("the system capabilities and data collection process.")
    print()
    
    # Initialize the experiment system
    print("🔧 Initializing experiment system...")
    system = HumanExperimentSystem()
    
    # Demo parameters
    demo_participants = 3
    print(f"📊 Demo parameters:")
    print(f"   - Participants: {demo_participants}")
    print(f"   - Trials per participant: 10 (5 baseline + 5 adaptive)")
    print(f"   - Conditions: Counterbalanced")
    print()
    
    # Create demo data directory
    os.makedirs("data/human_experiments", exist_ok=True)
    
    print("🚀 Starting demo experiment...")
    print("-" * 30)
    
    try:
        # Run the demo experiment
        start_time = datetime.now()
        
        results = await system.run_full_experiment(num_participants=demo_participants)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n✅ Demo experiment completed in {duration:.1f} seconds!")
        print()
        
        # Display results summary
        print("📈 DEMO RESULTS SUMMARY")
        print("=" * 40)
        
        summary = results
        analysis = summary['analysis']
        
        print(f"Total Participants: {summary['total_participants']}")
        print(f"Total Trials: {summary['total_trials']}")
        print()
        
        # Condition comparison
        baseline_stats = analysis['baseline_stats']
        adaptive_stats = analysis['adaptive_stats']
        
        print("CONDITION COMPARISON:")
        print("-" * 25)
        
        print(f"User Satisfaction (1-7 scale):")
        print(f"  Baseline:  {baseline_stats['satisfaction']:.2f}")
        print(f"  Adaptive:  {adaptive_stats['satisfaction']:.2f}")
        satisfaction_improvement = ((adaptive_stats['satisfaction'] - baseline_stats['satisfaction']) / baseline_stats['satisfaction']) * 100
        print(f"  Improvement: {satisfaction_improvement:+.1f}%")
        print()
        
        print(f"NASA-TLX Cognitive Load (0-100, lower is better):")
        print(f"  Baseline:  {baseline_stats['nasa_tlx']:.1f}")
        print(f"  Adaptive:  {adaptive_stats['nasa_tlx']:.1f}")
        nasa_improvement = ((baseline_stats['nasa_tlx'] - adaptive_stats['nasa_tlx']) / baseline_stats['nasa_tlx']) * 100
        print(f"  Improvement: {nasa_improvement:+.1f}%")
        print()
        
        print(f"Task Completion Time (seconds):")
        print(f"  Baseline:  {baseline_stats['completion_time']:.2f}")
        print(f"  Adaptive:  {adaptive_stats['completion_time']:.2f}")
        time_change = ((adaptive_stats['completion_time'] - baseline_stats['completion_time']) / baseline_stats['completion_time']) * 100
        print(f"  Change: {time_change:+.1f}%")
        print()
        
        if 'rec_acceptance' in adaptive_stats:
            print(f"Recommendation Acceptance Rate:")
            print(f"  Adaptive:  {adaptive_stats['rec_acceptance']:.1%}")
            print()
        
        print("📁 Results saved to: data/human_experiments/")
        print()
        
        # Sample data preview
        print("📋 SAMPLE TRIAL DATA:")
        print("-" * 25)
        sample_results = results['results'][:3]  # Show first 3 trials
        
        for i, result in enumerate(sample_results, 1):
            print(f"Trial {i}:")
            print(f"  Participant: {result.participant_id}")
            print(f"  Condition: {result.condition}")
            print(f"  Type: {result.trial_type}")
            print(f"  Completion Time: {result.completion_time_seconds:.2f}s")
            print(f"  Satisfaction: {result.satisfaction_rating:.1f}/7.0")
            print(f"  NASA-TLX: {result.nasa_tlx_score:.1f}/100")
            if result.recommendation_acceptance:
                print(f"  Rec. Acceptance: {result.recommendation_acceptance:.1%}")
            print()
        
        print("💡 Run full experiment with: python3 run_human_experiments.py")
        print()
        
        # Check if results file exists
        results_file = "data/human_experiments/trial_results.csv"
        if os.path.exists(results_file):
            file_size = os.path.getsize(results_file)
            print(f"📄 Results file: {results_file} ({file_size} bytes)")
        
        print("\n🎉 Demo completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def run_interactive_demo():
    """Run an interactive demo with user input"""
    
    print("🎮 Interactive Demo Mode")
    print("=" * 30)
    
    try:
        participants = int(input("Number of participants for demo (1-5): ") or "2")
        participants = max(1, min(5, participants))
    except ValueError:
        participants = 2
        print(f"Using default: {participants} participants")
    
    print(f"\nRunning interactive demo with {participants} participants...")
    
    system = HumanExperimentSystem()
    
    # Run experiment
    results = await system.run_full_experiment(num_participants=participants)
    
    # Interactive results exploration
    print(f"\n📊 Results for {participants} participants:")
    print(f"Total trials: {results['total_trials']}")
    
    while True:
        print("\nOptions:")
        print("1. View participant summary")
        print("2. View condition comparison")
        print("3. View individual trial data")
        print("4. Exit")
        
        choice = input("Select option (1-4): ").strip()
        
        if choice == "1":
            # Participant summary
            participants_data = {}
            for result in results['results']:
                pid = result.participant_id
                if pid not in participants_data:
                    participants_data[pid] = {'baseline': [], 'adaptive': []}
                participants_data[pid][result.condition].append(result)
            
            print(f"\nParticipant Summary:")
            for pid in sorted(participants_data.keys()):
                baseline_trials = participants_data[pid]['baseline']
                adaptive_trials = participants_data[pid]['adaptive']
                
                baseline_avg_sat = sum(t.satisfaction_rating for t in baseline_trials) / len(baseline_trials)
                adaptive_avg_sat = sum(t.satisfaction_rating for t in adaptive_trials) / len(adaptive_trials)
                
                print(f"{pid}: Baseline={baseline_avg_sat:.1f}, Adaptive={adaptive_avg_sat:.1f}")
        
        elif choice == "2":
            # Condition comparison
            analysis = results['analysis']
            baseline = analysis['baseline_stats']
            adaptive = analysis['adaptive_stats']
            
            print(f"\nCondition Comparison:")
            print(f"Satisfaction: {baseline['satisfaction']:.2f} vs {adaptive['satisfaction']:.2f}")
            print(f"NASA-TLX: {baseline['nasa_tlx']:.1f} vs {adaptive['nasa_tlx']:.1f}")
            print(f"Completion Time: {baseline['completion_time']:.2f}s vs {adaptive['completion_time']:.2f}s")
        
        elif choice == "3":
            # Individual trial data
            try:
                trial_num = int(input(f"Enter trial number (1-{results['total_trials']}): "))
                if 1 <= trial_num <= results['total_trials']:
                    trial = results['results'][trial_num - 1]
                    print(f"\nTrial {trial_num}:")
                    print(f"  Participant: {trial.participant_id}")
                    print(f"  Condition: {trial.condition}")
                    print(f"  Type: {trial.trial_type}")
                    print(f"  Satisfaction: {trial.satisfaction_rating:.1f}")
                    print(f"  NASA-TLX: {trial.nasa_tlx_score:.1f}")
                    print(f"  Completion Time: {trial.completion_time_seconds:.2f}s")
                    if trial.recommendation_acceptance:
                        print(f"  Recommendation Acceptance: {trial.recommendation_acceptance:.1%}")
                else:
                    print("Invalid trial number")
            except ValueError:
                print("Please enter a valid number")
        
        elif choice == "4" or choice.lower() == 'exit':
            break
        
        else:
            print("Invalid option")
    
    print("Interactive demo finished!")

def main():
    """Main function to run demo"""
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        asyncio.run(run_interactive_demo())
    else:
        success = asyncio.run(run_demo())
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
