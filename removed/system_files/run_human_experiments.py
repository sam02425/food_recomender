#!/usr/bin/env python3
"""
Human Experiments Runner
Confidential - Internal Research Use Only
"""

import asyncio
import argparse
import json
import logging
import os
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from human_experiment_system import HumanExperimentSystem

# Configure logging
def setup_logging(log_level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'human_experiments_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

class ExperimentRunner:
    def __init__(self):
        self.experiment_system = None
        self.running = False
        self.results = None
        
    def signal_handler(self, signum, frame):
        logger.info("Received interrupt signal. Gracefully shutting down...")
        self.running = False
        
    async def run_experiment_batch(self, 
                                 num_participants: int,
                                 condition_order: str = "balanced",
                                 save_interval: int = 10) -> Dict[str, Any]:
        """Run experiment with specified parameters"""
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Initialize experiment system
        self.experiment_system = HumanExperimentSystem()
        self.running = True
        
        # Ensure data directory exists
        os.makedirs("data/human_experiments", exist_ok=True)
        
        logger.info(f"Starting experiment batch with {num_participants} participants")
        logger.info(f"Condition order: {condition_order}")
        logger.info(f"Save interval: every {save_interval} participants")
        
        all_results = []
        completed_participants = 0
        
        try:
            for i in range(num_participants):
                if not self.running:
                    logger.info("Experiment interrupted by user")
                    break
                
                # Generate participant data
                participant_data = {
                    'age': 25 + (i % 40),  # Age 25-65
                    'gender': ['male', 'female', 'other'][i % 3],
                    'tech_proficiency': ['low', 'moderate', 'high'][i % 3],
                    'food_experience': 'regular',
                    'consent_facial': True
                }
                
                # Register participant
                participant_id = await self.experiment_system.register_participant(participant_data)
                
                # Determine condition order
                if condition_order == "balanced":
                    conditions = ['baseline', 'adaptive'] if i % 2 == 0 else ['adaptive', 'baseline']
                elif condition_order == "baseline_first":
                    conditions = ['baseline', 'adaptive']
                else:  # adaptive_first
                    conditions = ['adaptive', 'baseline']
                
                # Run participant session
                participant_results = await self.experiment_system.run_participant_session(
                    participant_id, conditions
                )
                
                all_results.extend(participant_results)
                completed_participants += 1
                
                # Progress update
                progress = (completed_participants / num_participants) * 100
                logger.info(f"Progress: {completed_participants}/{num_participants} participants ({progress:.1f}%)")
                
                # Periodic save
                if completed_participants % save_interval == 0:
                    await self.save_intermediate_results(all_results, completed_participants)
                    logger.info(f"Intermediate results saved after {completed_participants} participants")
            
            # Final save and analysis
            if all_results:
                await self.experiment_system.save_experiment_results(all_results)
                analysis = await self.experiment_system.analyze_results(all_results)
                
                # Save summary
                summary = {
                    'experiment_date': datetime.now().isoformat(),
                    'total_participants': completed_participants,
                    'total_trials': len(all_results),
                    'condition_order': condition_order,
                    'analysis': analysis,
                    'completed': completed_participants == num_participants
                }
                
                with open("data/human_experiments/experiment_summary.json", 'w') as f:
                    json.dump(summary, f, indent=2)
                
                logger.info(f"Results saved to: data/human_experiments/")
                
                self.results = {
                    'summary': summary,
                    'results': all_results
                }
                
                return self.results
        
        except Exception as e:
            logger.error(f"Experiment failed: {str(e)}")
            if all_results:
                await self.save_intermediate_results(all_results, completed_participants)
                logger.info("Partial results saved due to error")
            raise
        
        finally:
            self.running = False
    
    async def save_intermediate_results(self, results, participant_count):
        """Save intermediate results during experiment"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        intermediate_file = f"data/human_experiments/intermediate_results_{timestamp}.json"
        
        intermediate_data = {
            'timestamp': datetime.now().isoformat(),
            'participants_completed': participant_count,
            'total_trials': len(results),
            'results': [
                {
                    'participant_id': r.participant_id,
                    'trial_number': r.trial_number,
                    'condition': r.condition,
                    'satisfaction_rating': r.satisfaction_rating,
                    'nasa_tlx_score': r.nasa_tlx_score,
                    'completion_time_seconds': r.completion_time_seconds
                }
                for r in results
            ]
        }
        
        with open(intermediate_file, 'w') as f:
            json.dump(intermediate_data, f, indent=2)
    
    def print_results_summary(self):
        """Print experiment results summary"""
        if not self.results:
            print("No results available")
            return
        
        summary = self.results['summary']
        analysis = summary['analysis']
        
        print("\n" + "="*60)
        print("EXPERIMENT RESULTS SUMMARY")
        print("="*60)
        print(f"Date: {summary['experiment_date']}")
        print(f"Participants: {summary['total_participants']}")
        print(f"Total Trials: {summary['total_trials']}")
        print(f"Condition Order: {summary['condition_order']}")
        print(f"Status: {'COMPLETED' if summary['completed'] else 'INTERRUPTED'}")
        
        if 'baseline_stats' in analysis and 'adaptive_stats' in analysis:
            baseline = analysis['baseline_stats']
            adaptive = analysis['adaptive_stats']
            
            print("\nCONDITION COMPARISON:")
            print("-" * 40)
            print(f"Satisfaction (1-7):")
            print(f"  Baseline: {baseline['satisfaction']:.2f}")
            print(f"  Adaptive: {adaptive['satisfaction']:.2f}")
            print(f"  Improvement: {((adaptive['satisfaction']-baseline['satisfaction'])/baseline['satisfaction']*100):.1f}%")
            
            print(f"\nNASA-TLX (0-100, lower better):")
            print(f"  Baseline: {baseline['nasa_tlx']:.1f}")
            print(f"  Adaptive: {adaptive['nasa_tlx']:.1f}")
            print(f"  Improvement: {((baseline['nasa_tlx']-adaptive['nasa_tlx'])/baseline['nasa_tlx']*100):.1f}%")
            
            print(f"\nCompletion Time (seconds):")
            print(f"  Baseline: {baseline['completion_time']:.2f}")
            print(f"  Adaptive: {adaptive['completion_time']:.2f}")
            
            if 'rec_acceptance' in adaptive:
                print(f"\nRecommendation Acceptance: {adaptive['rec_acceptance']:.1%}")
        
        print(f"\n📁 Check data/human_experiments/ for results")
        print("="*60)

async def main():
    parser = argparse.ArgumentParser(description="Run Human Experiments")
    parser.add_argument("--participants", "-p", type=int, default=50,
                       help="Number of participants (default: 50)")
    parser.add_argument("--condition-order", "-c", choices=["balanced", "baseline_first", "adaptive_first"],
                       default="balanced", help="Condition order (default: balanced)")
    parser.add_argument("--save-interval", "-s", type=int, default=10,
                       help="Save intermediate results every N participants (default: 10)")
    parser.add_argument("--log-level", "-l", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level (default: INFO)")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Create experiment runner
    runner = ExperimentRunner()
    
    try:
        # Run experiment
        results = await runner.run_experiment_batch(
            num_participants=args.participants,
            condition_order=args.condition_order,
            save_interval=args.save_interval
        )
        
        # Print results
        runner.print_results_summary()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Experiment interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Experiment failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
