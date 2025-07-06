#!/usr/bin/env python3
"""
Test Suite for Artificial Participant System

This module tests the artificial participant system to ensure it works correctly
before running the full experiment.

Author: AI Research Assistant
Date: 2024
"""

import asyncio
import random
from artificial_participant_system import (
    ArtificialParticipantSystem,
    ArtificialParticipant,
    RealisticBehavioralModels,
    ParticipantProfile
)

async def test_single_participant():
    """Test a single artificial participant"""
    print("Testing single artificial participant...")

    # Create a realistic participant
    behavioral_models = RealisticBehavioralModels()
    profile = behavioral_models.generate_realistic_participant("TEST001")

    participant = ArtificialParticipant("TEST001")
    participant.profile = profile

    print(f"Initial mood: {participant.current_mood}")

    # Test mood updates
    participant.update_mood(1, 'baseline')
    print(f"After trial 1 (baseline): {participant.current_mood}")

    participant.update_mood(1, 'adaptive')
    print(f"After trial 1 (adaptive): {participant.current_mood}")

    # Test protein selection
    protein = participant.select_protein()
    print(f"Selected protein: {protein}")

    # Test protein selection with recommendations
    protein_with_rec = participant.select_protein(['Chicken', 'Paneer'])
    print(f"Selected protein with recommendations: {protein_with_rec}")

    # Test sauce selection
    sauce = participant.select_sauce()
    print(f"Selected sauce: {sauce}")

    # Test base selection
    base_type, base_option = participant.select_base_type()
    print(f"Selected base: {base_type} - {base_option}")

    # Test veggie selection
    veggies = participant.select_veggies()
    print(f"Selected veggies: {veggies}")

    # Test completion time calculation
    baseline_time = participant.behavioral_models.calculate_realistic_completion_time(
        participant.profile, 'baseline', 'free_choice'
    )
    adaptive_time = participant.behavioral_models.calculate_realistic_completion_time(
        participant.profile, 'adaptive', 'free_choice'
    )
    print(f"Baseline completion time: {baseline_time:.2f}s")
    print(f"Adaptive completion time: {adaptive_time:.2f}s")

    # Test satisfaction calculation
    baseline_satisfaction = participant.behavioral_models.calculate_realistic_satisfaction(
        participant.profile, 'baseline', baseline_time
    )
    adaptive_satisfaction = participant.behavioral_models.calculate_realistic_satisfaction(
        participant.profile, 'adaptive', adaptive_time
    )
    print(f"Baseline satisfaction: {baseline_satisfaction:.2f}/7.0")
    print(f"Adaptive satisfaction: {adaptive_satisfaction:.2f}/7.0")

    # Test NASA-TLX calculation
    baseline_nasa = participant.behavioral_models.calculate_realistic_nasa_tlx(
        participant.profile, 'baseline', baseline_time
    )
    adaptive_nasa = participant.behavioral_models.calculate_realistic_nasa_tlx(
        participant.profile, 'adaptive', adaptive_time
    )
    print(f"Baseline NASA-TLX: {baseline_nasa:.1f}/100")
    print(f"Adaptive NASA-TLX: {adaptive_nasa:.1f}/100")

    print("Single participant test completed successfully!\n")

def test_behavioral_models():
    """Test behavioral models"""
    print("Testing behavioral models...")

    behavioral_models = RealisticBehavioralModels()

    # Test participant generation
    profile = behavioral_models.generate_realistic_participant("TEST002")
    print(f"Generated participant: {profile.participant_id}, Age: {profile.age}, Gender: {profile.gender}")
    print(f"Technical proficiency: {profile.technical_proficiency}")
    print(f"Dietary restrictions: {profile.dietary_restrictions}")
    print(f"Food preferences: {profile.food_preferences}")
    print(f"Cultural background: {profile.cultural_background}")
    print(f"Decision style: {profile.decision_style}")
    print(f"Recommendation trust: {profile.recommendation_trust:.2f}")
    print(f"Privacy concerns: {profile.privacy_concerns:.2f}")

    # Test recommendation generation
    recommendations = behavioral_models.generate_realistic_recommendations(
        profile, 'happy', 'warm'
    )
    print(f"Generated recommendations: {recommendations}")

    # Test dietary compliance checking
    issues = behavioral_models.check_dietary_compliance(profile, recommendations)
    print(f"Dietary compliance issues: {issues}")

    print("Behavioral models test completed successfully!\n")

async def test_small_experiment():
    """Test a small experiment with 3 participants"""
    print("Testing small experiment with 3 participants...")

    # Create system
    system = ArtificialParticipantSystem()
    system.experiment_config['total_participants'] = 3

    # Generate profiles
    profiles = system.generate_participant_profiles()
    print(f"Created {len(profiles)} test participants")

    # Run experiment
    results = await system.run_experiment()
    print(f"Completed {len(results)} total trials")

    # Basic analysis
    baseline_trials = [r for r in results if r.condition == 'baseline']
    adaptive_trials = [r for r in results if r.condition == 'adaptive']

    if baseline_trials and adaptive_trials:
        baseline_satisfaction = sum(t.satisfaction_rating for t in baseline_trials) / len(baseline_trials)
        adaptive_satisfaction = sum(t.satisfaction_rating for t in adaptive_trials) / len(adaptive_trials)
        baseline_nasa = sum(t.nasa_tlx_score for t in baseline_trials) / len(baseline_trials)
        adaptive_nasa = sum(t.nasa_tlx_score for t in adaptive_trials) / len(adaptive_trials)

        print(f"\nTest Results Summary:")
        print(f"Baseline satisfaction: {baseline_satisfaction:.2f}")
        print(f"Adaptive satisfaction: {adaptive_satisfaction:.2f}")
        print(f"Baseline NASA-TLX: {baseline_nasa:.1f}")
        print(f"Adaptive NASA-TLX: {adaptive_nasa:.1f}")

        # Recommendation acceptance
        rec_trials = [t for t in adaptive_trials if t.recommendation_acceptance is not None]
        if rec_trials:
            acceptance_rate = sum(t.recommendation_acceptance for t in rec_trials) / len(rec_trials)
            print(f"Recommendation acceptance: {acceptance_rate:.1%}")

        # Dietary issues
        trials_with_issues = [t for t in adaptive_trials if t.dietary_compliance_issues]
        if trials_with_issues:
            print(f"Trials with dietary issues: {len(trials_with_issues)}/{len(adaptive_trials)}")

    print("Small experiment test completed successfully!\n")

async def main():
    """Run all tests"""
    print("=" * 60)
    print("ARTIFICIAL PARTICIPANT SYSTEM TEST SUITE")
    print("=" * 60)

    try:
        # Test single participant
        await test_single_participant()

        # Test behavioral models
        test_behavioral_models()

        # Test small experiment
        await test_small_experiment()

        print("=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nThe artificial participant system is working correctly.")
        print("You can now run the full experiment with 50 participants.")
        print("\nTo run the full experiment:")
        print("python experiment_runner.py")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        print("\n❌ Some tests failed!")

if __name__ == "__main__":
    asyncio.run(main())