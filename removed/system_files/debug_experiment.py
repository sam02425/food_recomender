#!/usr/bin/env python3
"""
Debug Experiment System
Confidential - Internal Research Use Only
"""

import asyncio
import json
import logging
import os
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, List

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from human_experiment_system import HumanExperimentSystem, TrialResult

# Configure detailed logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler(f'debug_experiment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("debug_experiment")

class ExperimentDebugger:
    """Debug utilities for experiment system"""
    
    def __init__(self):
        self.system = None
        self.debug_data = {}
        
    async def debug_participant_registration(self):
        """Debug participant registration process"""
        logger.info("=== DEBUGGING PARTICIPANT REGISTRATION ===")
        
        self.system = HumanExperimentSystem()
        
        test_participants = [
            {'age': 25, 'gender': 'male', 'tech_proficiency': 'high', 'consent_facial': True},
            {'age': 35, 'gender': 'female', 'tech_proficiency': 'low', 'consent_facial': False},
            {'age': 45, 'gender': 'other', 'tech_proficiency': 'moderate', 'consent_facial': True}
        ]
        
        registered_ids = []
        
        for i, participant_data in enumerate(test_participants):
            logger.debug(f"Registering participant {i+1}: {participant_data}")
            
            try:
                participant_id = await self.system.register_participant(participant_data)
                registered_ids.append(participant_id)
                logger.info(f"✓ Successfully registered: {participant_id}")
                
                # Verify participant data
                stored_participant = self.system.participants[participant_id]
                logger.debug(f"Stored participant data: {stored_participant}")
                
            except Exception as e:
                logger.error(f"✗ Failed to register participant {i+1}: {str(e)}")
                traceback.print_exc()
        
        logger.info(f"Registered {len(registered_ids)} participants: {registered_ids}")
        return registered_ids
    
    async def debug_trial_execution(self, participant_id: str):
        """Debug individual trial execution"""
        logger.info(f"=== DEBUGGING TRIAL EXECUTION FOR {participant_id} ===")
        
        trial_results = []
        
        # Test baseline trial
        logger.info("Testing baseline trial...")
        try:
            baseline_result = await self.system.run_baseline_trial(participant_id, 1, 'free_choice')
            trial_results.append(baseline_result)
            logger.info(f"✓ Baseline trial completed: {baseline_result.completion_time_seconds:.2f}s")
            logger.debug(f"Baseline trial data: {baseline_result}")
            
        except Exception as e:
            logger.error(f"✗ Baseline trial failed: {str(e)}")
            traceback.print_exc()
        
        # Test adaptive trial
        logger.info("Testing adaptive trial...")
        try:
            adaptive_result = await self.system.run_adaptive_trial(participant_id, 2, 'specific_requirement')
            trial_results.append(adaptive_result)
            logger.info(f"✓ Adaptive trial completed: {adaptive_result.completion_time_seconds:.2f}s")
            logger.debug(f"Adaptive trial data: {adaptive_result}")
            
        except Exception as e:
            logger.error(f"✗ Adaptive trial failed: {str(e)}")
            traceback.print_exc()
        
        return trial_results
    
    async def debug_agent_systems(self):
        """Debug individual agent systems"""
        logger.info("=== DEBUGGING AGENT SYSTEMS ===")
        
        if not self.system:
            self.system = HumanExperimentSystem()
        
        # Test emotion recognition agent
        logger.info("Testing Emotion Recognition Agent...")
        try:
            emotion_result = await self.system.emotion_agent.detect_emotion("DEBUG_PARTICIPANT")
            logger.info(f"✓ Emotion detection: {emotion_result}")
        except Exception as e:
            logger.error(f"✗ Emotion detection failed: {str(e)}")
        
        # Test health recommender agent (if available)
        if hasattr(self.system, 'health_agent'):
            logger.info("Testing Health Recommender Agent...")
            try:
                health_recs = await self.system.health_agent.get_health_recommendations('workout', 'high-protein')
                logger.info(f"✓ Health recommendations: {health_recs}")
            except Exception as e:
                logger.error(f"✗ Health recommendations failed: {str(e)}")
        
        # Test weather recommender agent (if available)
        if hasattr(self.system, 'weather_agent'):
            logger.info("Testing Weather Recommender Agent...")
            try:
                weather_recs = await self.system.weather_agent.get_weather_recommendations('cold')
                logger.info(f"✓ Weather recommendations: {weather_recs}")
            except Exception as e:
                logger.error(f"✗ Weather recommendations failed: {str(e)}")
    
    async def debug_data_collection(self, trial_results: List[TrialResult]):
        """Debug data collection and saving"""
        logger.info("=== DEBUGGING DATA COLLECTION ===")
        
        if not trial_results:
            logger.warning("No trial results to debug")
            return
        
        # Test saving results
        logger.info("Testing result saving...")
        try:
            await self.system.save_experiment_results(trial_results)
            logger.info("✓ Results saved successfully")
            
            # Verify file exists
            results_file = "data/human_experiments/trial_results.csv"
            if os.path.exists(results_file):
                file_size = os.path.getsize(results_file)
                logger.info(f"✓ Results file created: {results_file} ({file_size} bytes)")
                
                # Read back first few lines
                with open(results_file, 'r') as f:
                    lines = f.readlines()[:3]
                    logger.debug(f"First 3 lines of results file: {lines}")
            else:
                logger.error("✗ Results file not created")
                
        except Exception as e:
            logger.error(f"✗ Result saving failed: {str(e)}")
            traceback.print_exc()
        
        # Test analysis
        logger.info("Testing result analysis...")
        try:
            analysis = await self.system.analyze_results(trial_results)
            logger.info(f"✓ Analysis completed")
            logger.debug(f"Analysis results: {json.dumps(analysis, indent=2)}")
            
        except Exception as e:
            logger.error(f"✗ Analysis failed: {str(e)}")
            traceback.print_exc()
    
    async def debug_full_mini_experiment(self):
        """Debug a complete mini experiment"""
        logger.info("=== DEBUGGING FULL MINI EXPERIMENT ===")
        
        try:
            self.system = HumanExperimentSystem()
            
            # Run mini experiment with 1 participant
            logger.info("Starting mini experiment with 1 participant...")
            results = await self.system.run_full_experiment(num_participants=1)
            
            logger.info(f"✓ Mini experiment completed")
            logger.info(f"  Participants: {results['total_participants']}")
            logger.info(f"  Trials: {results['total_trials']}")
            logger.info(f"  Analysis keys: {list(results['analysis'].keys())}")
            
            return results
            
        except Exception as e:
            logger.error(f"✗ Mini experiment failed: {str(e)}")
            traceback.print_exc()
            return None
    
    def debug_system_state(self):
        """Debug current system state"""
        logger.info("=== DEBUGGING SYSTEM STATE ===")
        
        if not self.system:
            logger.warning("No system instance available")
            return
        
        logger.info(f"Registered participants: {len(self.system.participants)}")
        for pid, participant in self.system.participants.items():
            logger.debug(f"  {pid}: {participant}")
        
        logger.info(f"Trials per condition: {self.system.trials_per_condition}")
        logger.info(f"Available conditions: {self.system.conditions}")
        
        # Check data directory
        data_dir = "data/human_experiments"
        if os.path.exists(data_dir):
            files = os.listdir(data_dir)
            logger.info(f"Data directory files: {files}")
        else:
            logger.warning("Data directory does not exist")
    
    async def run_comprehensive_debug(self):
        """Run comprehensive debugging session"""
        logger.info("🔍 STARTING COMPREHENSIVE DEBUG SESSION")
        logger.info("=" * 60)
        
        try:
            # 1. Debug participant registration
            participant_ids = await self.debug_participant_registration()
            
            # 2. Debug agent systems
            await self.debug_agent_systems()
            
            # 3. Debug trial execution
            if participant_ids:
                trial_results = await self.debug_trial_execution(participant_ids[0])
                
                # 4. Debug data collection
                await self.debug_data_collection(trial_results)
            
            # 5. Debug system state
            self.debug_system_state()
            
            # 6. Debug full mini experiment
            mini_results = await self.debug_full_mini_experiment()
            
            logger.info("🎉 COMPREHENSIVE DEBUG SESSION COMPLETED")
            
            return True
            
        except Exception as e:
            logger.error(f"💥 DEBUG SESSION FAILED: {str(e)}")
            traceback.print_exc()
            return False

async def debug_specific_issue(issue_type: str):
    """Debug specific issues"""
    debugger = ExperimentDebugger()
    
    if issue_type == "registration":
        await debugger.debug_participant_registration()
    elif issue_type == "agents":
        await debugger.debug_agent_systems()
    elif issue_type == "trials":
        # Need to register a participant first
        participant_ids = await debugger.debug_participant_registration()
        if participant_ids:
            await debugger.debug_trial_execution(participant_ids[0])
    elif issue_type == "data":
        # Create some sample trial results
        debugger.system = HumanExperimentSystem()
        participant_id = await debugger.system.register_participant({'age': 25, 'consent_facial': True})
        trial_results = await debugger.debug_trial_execution(participant_id)
        await debugger.debug_data_collection(trial_results)
    elif issue_type == "mini":
        await debugger.debug_full_mini_experiment()
    else:
        logger.error(f"Unknown issue type: {issue_type}")

def main():
    """Main debug function"""
    
    if len(sys.argv) > 1:
        issue_type = sys.argv[1]
        logger.info(f"Debugging specific issue: {issue_type}")
        asyncio.run(debug_specific_issue(issue_type))
    else:
        # Run comprehensive debug
        debugger = ExperimentDebugger()
        success = asyncio.run(debugger.run_comprehensive_debug())
        
        if success:
            print("\n✅ Debug session completed successfully!")
            print("Check the debug log file for detailed information.")
        else:
            print("\n❌ Debug session encountered errors!")
            print("Check the debug log file for error details.")
        
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    print("🐛 Experiment Debug System")
    print("Usage:")
    print("  python debug_experiment.py                    # Run comprehensive debug")
    print("  python debug_experiment.py registration       # Debug participant registration")
    print("  python debug_experiment.py agents             # Debug agent systems")
    print("  python debug_experiment.py trials             # Debug trial execution")
    print("  python debug_experiment.py data               # Debug data collection")
    print("  python debug_experiment.py mini               # Debug mini experiment")
    print()
    
    main()
