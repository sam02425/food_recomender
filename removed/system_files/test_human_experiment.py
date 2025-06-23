#!/usr/bin/env python3
"""
Test Human Experiment System
Confidential - Internal Research Use Only
"""

import asyncio
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from human_experiment_system import (
    HumanExperimentSystem, 
    EmotionRecognitionAgent,
    ParticipantProfile,
    TrialResult
)

class TestEmotionRecognitionAgent(unittest.TestCase):
    def setUp(self):
        self.agent = EmotionRecognitionAgent()
    
    async def test_emotion_detection(self):
        """Test emotion detection functionality"""
        result = await self.agent.detect_emotion("P001")
        
        self.assertIn('emotion', result)
        self.assertIn('confidence', result)
        self.assertIn('timestamp', result)
        self.assertIn('participant_id', result)
        self.assertEqual(result['participant_id'], "P001")
        self.assertIn(result['emotion'], self.agent.emotions)
        self.assertTrue(0.0 <= result['confidence'] <= 1.0)
    
    def test_emotion_detection_sync(self):
        """Synchronous wrapper for emotion detection test"""
        asyncio.run(self.test_emotion_detection())

class TestHumanExperimentSystem(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        self.system = HumanExperimentSystem()
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    async def test_participant_registration(self):
        """Test participant registration"""
        participant_data = {
            'age': 25,
            'gender': 'female',
            'tech_proficiency': 'high',
            'food_experience': 'regular',
            'consent_facial': True
        }
        
        participant_id = await self.system.register_participant(participant_data)
        
        self.assertTrue(participant_id.startswith('P'))
        self.assertEqual(len(participant_id), 4)  # P001, P002, etc.
        self.assertIn(participant_id, self.system.participants)
        
        participant = self.system.participants[participant_id]
        self.assertEqual(participant.age, 25)
        self.assertEqual(participant.gender, 'female')
        self.assertEqual(participant.technical_proficiency, 'high')
    
    def test_participant_registration_sync(self):
        """Synchronous wrapper for participant registration test"""
        asyncio.run(self.test_participant_registration())
    
    async def test_baseline_trial(self):
        """Test baseline trial execution"""
        participant_id = await self.system.register_participant({
            'age': 30,
            'gender': 'male',
            'consent_facial': True
        })
        
        result = await self.system.run_baseline_trial(participant_id, 1, 'free_choice')
        
        self.assertIsInstance(result, TrialResult)
        self.assertEqual(result.participant_id, participant_id)
        self.assertEqual(result.trial_number, 1)
        self.assertEqual(result.condition, 'baseline')
        self.assertEqual(result.trial_type, 'free_choice')
        self.assertIsNone(result.recommendation_acceptance)
        self.assertIsNone(result.facial_emotion_data)
        self.assertTrue(result.completion_time_seconds > 0)
        self.assertTrue(4.0 <= result.satisfaction_rating <= 6.0)
        self.assertTrue(60 <= result.nasa_tlx_score <= 80)
    
    def test_baseline_trial_sync(self):
        """Synchronous wrapper for baseline trial test"""
        asyncio.run(self.test_baseline_trial())
    
    async def test_adaptive_trial(self):
        """Test adaptive trial execution"""
        participant_id = await self.system.register_participant({
            'age': 28,
            'gender': 'other',
            'consent_facial': True
        })
        
        result = await self.system.run_adaptive_trial(participant_id, 1, 'specific_requirement')
        
        self.assertIsInstance(result, TrialResult)
        self.assertEqual(result.participant_id, participant_id)
        self.assertEqual(result.trial_number, 1)
        self.assertEqual(result.condition, 'adaptive')
        self.assertEqual(result.trial_type, 'specific_requirement')
        self.assertIsNotNone(result.recommendation_acceptance)
        self.assertIsNotNone(result.facial_emotion_data)
        self.assertTrue(result.completion_time_seconds > 0)
        self.assertTrue(6.0 <= result.satisfaction_rating <= 7.5)
        self.assertTrue(35 <= result.nasa_tlx_score <= 55)
        self.assertTrue(0.7 <= result.recommendation_acceptance <= 0.95)
    
    def test_adaptive_trial_sync(self):
        """Synchronous wrapper for adaptive trial test"""
        asyncio.run(self.test_adaptive_trial())
    
    async def test_multiple_participants(self):
        """Test registration of multiple participants"""
        participant_ids = []
        
        for i in range(3):
            participant_data = {
                'age': 20 + i * 10,
                'gender': ['male', 'female', 'other'][i],
                'consent_facial': True
            }
            participant_id = await self.system.register_participant(participant_data)
            participant_ids.append(participant_id)
        
        self.assertEqual(len(participant_ids), 3)
        self.assertEqual(len(set(participant_ids)), 3)  # All unique
        self.assertEqual(participant_ids, ['P001', 'P002', 'P003'])
    
    def test_multiple_participants_sync(self):
        """Synchronous wrapper for multiple participants test"""
        asyncio.run(self.test_multiple_participants())
    
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    async def test_save_results(self, mock_open):
        """Test saving experiment results"""
        participant_id = await self.system.register_participant({'age': 25, 'consent_facial': True})
        
        # Create sample results
        results = [
            await self.system.run_baseline_trial(participant_id, 1, 'free_choice'),
            await self.system.run_adaptive_trial(participant_id, 2, 'specific_requirement')
        ]
        
        await self.system.save_experiment_results(results)
        
        # Verify file was opened for writing
        mock_open.assert_called_once()
        self.assertTrue(mock_open.call_args[0][0].endswith('trial_results.csv'))
    
    def test_save_results_sync(self):
        """Synchronous wrapper for save results test"""
        asyncio.run(self.test_save_results())

class TestExperimentIntegration(unittest.TestCase):
    """Integration tests for complete experiment workflow"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        self.system = HumanExperimentSystem()
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    async def test_small_experiment(self):
        """Test running a small complete experiment"""
        # Run experiment with 2 participants
        results = await self.system.run_full_experiment(num_participants=2)
        
        self.assertEqual(results['total_participants'], 2)
        self.assertEqual(results['total_trials'], 20)  # 2 participants × 10 trials each
        self.assertIn('analysis', results)
        self.assertIn('baseline_stats', results['analysis'])
        self.assertIn('adaptive_stats', results['analysis'])
        
        # Check that we have both conditions
        conditions = [r.condition for r in results['results']]
        self.assertIn('baseline', conditions)
        self.assertIn('adaptive', conditions)
        
        # Check participant IDs
        participant_ids = list(set(r.participant_id for r in results['results']))
        self.assertEqual(len(participant_ids), 2)
        self.assertEqual(sorted(participant_ids), ['P001', 'P002'])
    
    def test_small_experiment_sync(self):
        """Synchronous wrapper for small experiment test"""
        asyncio.run(self.test_small_experiment())
    
    async def test_condition_counterbalancing(self):
        """Test that condition order is properly counterbalanced"""
        results = await self.system.run_full_experiment(num_participants=4)
        
        # Group results by participant
        by_participant = {}
        for result in results['results']:
            pid = result.participant_id
            if pid not in by_participant:
                by_participant[pid] = []
            by_participant[pid].append(result)
        
        # Check condition orders
        condition_orders = []
        for pid in sorted(by_participant.keys()):
            participant_results = sorted(by_participant[pid], key=lambda x: x.trial_number)
            first_half = [r.condition for r in participant_results[:5]]
            second_half = [r.condition for r in participant_results[5:]]
            
            # Should be all baseline then all adaptive, or vice versa
            if first_half[0] == 'baseline':
                self.assertTrue(all(c == 'baseline' for c in first_half))
                self.assertTrue(all(c == 'adaptive' for c in second_half))
                condition_orders.append('baseline_first')
            else:
                self.assertTrue(all(c == 'adaptive' for c in first_half))
                self.assertTrue(all(c == 'baseline' for c in second_half))
                condition_orders.append('adaptive_first')
        
        # Should have both orders represented
        self.assertIn('baseline_first', condition_orders)
        self.assertIn('adaptive_first', condition_orders)
    
    def test_condition_counterbalancing_sync(self):
        """Synchronous wrapper for condition counterbalancing test"""
        asyncio.run(self.test_condition_counterbalancing())

def run_test_suite():
    """Run all tests"""
    print("Running Human Experiment System Tests...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEmotionRecognitionAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestHumanExperimentSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestExperimentIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall: {'SUCCESS' if success else 'FAILED'}")
    
    return success

async def run_quick_integration_test():
    """Run a quick integration test"""
    print("\nRunning Quick Integration Test...")
    print("-" * 30)
    
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    
    try:
        os.chdir(temp_dir)
        
        system = HumanExperimentSystem()
        
        print("Testing participant registration...")
        participant_id = await system.register_participant({
            'age': 25,
            'gender': 'test',
            'consent_facial': True
        })
        print(f"✓ Registered participant: {participant_id}")
        
        print("Testing baseline trial...")
        baseline_result = await system.run_baseline_trial(participant_id, 1, 'free_choice')
        print(f"✓ Baseline trial completed in {baseline_result.completion_time_seconds:.2f}s")
        
        print("Testing adaptive trial...")
        adaptive_result = await system.run_adaptive_trial(participant_id, 2, 'specific_requirement')
        print(f"✓ Adaptive trial completed in {adaptive_result.completion_time_seconds:.2f}s")
        
        print("Testing small experiment...")
        results = await system.run_full_experiment(num_participants=1)
        print(f"✓ Small experiment completed: {results['total_trials']} trials")
        
        print("\n✓ All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {str(e)}")
        return False
        
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        # Run quick integration test only
        success = asyncio.run(run_quick_integration_test())
        sys.exit(0 if success else 1)
    else:
        # Run full test suite
        success = run_test_suite()
        
        # Also run integration test
        print("\n" + "=" * 50)
        integration_success = asyncio.run(run_quick_integration_test())
        
        overall_success = success and integration_success
        sys.exit(0 if overall_success else 1)
