#!/usr/bin/env python3
"""
Bias Analysis for Experiment Results
Checks for systematic bias in the adaptive vs baseline conditions
"""

import json
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from datetime import datetime

def load_results(filename):
    """Load experiment results"""
    with open(filename, 'r') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def analyze_bias(df):
    """Comprehensive bias analysis"""

    print("=" * 60)
    print("BIAS ANALYSIS REPORT")
    print("=" * 60)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Trials: {len(df)}")
    print()

    # Separate baseline and adaptive trials
    baseline = df[df['condition'] == 'baseline']
    adaptive = df[df['condition'] == 'adaptive']

    print(f"Baseline Trials: {len(baseline)}")
    print(f"Adaptive Trials: {len(adaptive)}")
    print()

    # Check for balance
    print("1. TRIAL BALANCE CHECK")
    print("-" * 30)
    print(f"Baseline/Adaptive Ratio: {len(baseline)/len(adaptive):.3f}")
    if abs(len(baseline) - len(adaptive)) <= 1:
        print("✅ Trial balance is good")
    else:
        print("❌ Trial balance issue detected")
    print()

    # Check for systematic differences in key metrics
    metrics = ['satisfaction_rating', 'completion_time_seconds', 'nasa_tlx_score',
               'error_count', 'navigation_steps', 'trust_rating']

    print("2. SYSTEMATIC DIFFERENCES ANALYSIS")
    print("-" * 40)

    bias_detected = False

    for metric in metrics:
        baseline_mean = baseline[metric].mean()
        adaptive_mean = adaptive[metric].mean()
        baseline_std = baseline[metric].std()
        adaptive_std = adaptive[metric].std()

        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(((len(baseline) - 1) * baseline_std**2 + (len(adaptive) - 1) * adaptive_std**2) / (len(baseline) + len(adaptive) - 2))
        effect_size = abs(baseline_mean - adaptive_mean) / pooled_std

        # Perform t-test
        t_stat, p_value = stats.ttest_ind(baseline[metric], adaptive[metric])

        print(f"\n{metric.upper()}:")
        print(f"  Baseline: {baseline_mean:.3f} ± {baseline_std:.3f}")
        print(f"  Adaptive:  {adaptive_mean:.3f} ± {adaptive_std:.3f}")
        print(f"  Difference: {adaptive_mean - baseline_mean:.3f}")
        print(f"  Effect Size: {effect_size:.3f}")
        print(f"  P-value: {p_value:.4f}")

        # Check for suspicious patterns
        if effect_size > 0.8:  # Large effect size
            print(f"  ⚠️  Large effect size detected ({effect_size:.3f})")
            bias_detected = True

        if p_value < 0.001:  # Very significant
            print(f"  ⚠️  Very high significance (p={p_value:.4f})")
            bias_detected = True

    print()

    # Check for unrealistic patterns
    print("3. REALISM CHECKS")
    print("-" * 20)

    # Check satisfaction distribution
    print(f"Satisfaction Range: {df['satisfaction_rating'].min():.2f} - {df['satisfaction_rating'].max():.2f}")
    if df['satisfaction_rating'].min() < 1.0 or df['satisfaction_rating'].max() > 7.0:
        print("❌ Satisfaction scores outside expected range (1-7)")
        bias_detected = True
    else:
        print("✅ Satisfaction scores in expected range")

    # Check completion time distribution
    print(f"Completion Time Range: {df['completion_time_seconds'].min():.2f} - {df['completion_time_seconds'].max():.2f} seconds")
    if df['completion_time_seconds'].min() < 3.0 or df['completion_time_seconds'].max() > 30.0:
        print("❌ Completion times outside realistic range")
        bias_detected = True
    else:
        print("✅ Completion times in realistic range")

    # Check NASA-TLX distribution
    print(f"NASA-TLX Range: {df['nasa_tlx_score'].min():.2f} - {df['nasa_tlx_score'].max():.2f}")
    if df['nasa_tlx_score'].min() < 0.0 or df['nasa_tlx_score'].max() > 100.0:
        print("❌ NASA-TLX scores outside expected range (0-100)")
        bias_detected = True
    else:
        print("✅ NASA-TLX scores in expected range")

    print()

    # Check for learning effects
    print("4. LEARNING EFFECTS ANALYSIS")
    print("-" * 30)

    # Check if adaptive trials show improvement over time
    adaptive_by_trial = adaptive.groupby('trial_number')['satisfaction_rating'].mean()
    baseline_by_trial = baseline.groupby('trial_number')['satisfaction_rating'].mean()

    print("Satisfaction by Trial Number:")
    for trial in range(1, 6):
        if trial in adaptive_by_trial.index and trial in baseline_by_trial.index:
            print(f"  Trial {trial}: Baseline={baseline_by_trial[trial]:.3f}, Adaptive={adaptive_by_trial[trial]:.3f}")

    # Check for suspicious learning patterns
    adaptive_trend = np.polyfit(adaptive_by_trial.index, adaptive_by_trial.values, 1)[0]
    baseline_trend = np.polyfit(baseline_by_trial.index, baseline_by_trial.values, 1)[0]

    print(f"Learning Trend (slope): Baseline={baseline_trend:.4f}, Adaptive={adaptive_trend:.4f}")

    if adaptive_trend > 0.1:  # Suspiciously steep learning curve
        print("⚠️  Suspiciously steep learning curve in adaptive condition")
        bias_detected = True

    print()

    # Check for demographic bias
    print("5. DEMOGRAPHIC BIAS CHECK")
    print("-" * 30)

    # Extract participant IDs and check distribution
    participants = df['participant_id'].unique()
    print(f"Total Participants: {len(participants)}")

    # Check if all participants have equal trials
    trials_per_participant = df.groupby('participant_id').size()
    print(f"Trials per participant: {trials_per_participant.min()} - {trials_per_participant.max()}")

    if trials_per_participant.min() != trials_per_participant.max():
        print("❌ Unequal trials per participant detected")
        bias_detected = True
    else:
        print("✅ Equal trials per participant")

    print()

    # Check for recommendation acceptance bias
    print("6. RECOMMENDATION ACCEPTANCE ANALYSIS")
    print("-" * 40)

    adaptive_with_recs = adaptive[adaptive['recommendation_acceptance'].notna()]
    if len(adaptive_with_recs) > 0:
        acceptance_rate = adaptive_with_recs['recommendation_acceptance'].mean()
        print(f"Recommendation Acceptance Rate: {acceptance_rate:.3f}")

        if acceptance_rate > 0.9:
            print("⚠️  Suspiciously high recommendation acceptance rate")
            bias_detected = True
        elif acceptance_rate < 0.1:
            print("⚠️  Suspiciously low recommendation acceptance rate")
            bias_detected = True
        else:
            print("✅ Realistic recommendation acceptance rate")
    else:
        print("No recommendation acceptance data found")

    print()

    # Overall bias assessment
    print("7. OVERALL BIAS ASSESSMENT")
    print("-" * 30)

    if bias_detected:
        print("❌ POTENTIAL BIAS DETECTED")
        print("The experiment shows signs of systematic bias that should be investigated.")
        print("Recommendations:")
        print("- Review randomization procedures")
        print("- Check for hardcoded values in simulation")
        print("- Verify participant generation logic")
        print("- Consider re-running with different parameters")
    else:
        print("✅ NO SIGNIFICANT BIAS DETECTED")
        print("The experiment appears to be producing realistic, unbiased results.")
        print("The differences between conditions are within expected ranges.")

    print()
    print("=" * 60)

    return bias_detected

def main():
    """Main analysis function"""
    import glob
    import os

    # Find the most recent experiment results file
    result_files = glob.glob("experiment_results_*.json")
    if not result_files:
        print("No experiment results files found!")
        return True

    # Sort by modification time and get the most recent
    latest_file = max(result_files, key=os.path.getmtime)
    print(f"Analyzing results from: {latest_file}")
    print()

    try:
        df = load_results(latest_file)
        bias_detected = analyze_bias(df)

        if bias_detected:
            print("\nRECOMMENDATION: Review and potentially re-run the experiment")
            return True
        else:
            print("\nRECOMMENDATION: Results appear unbiased, proceed with analysis")
            return False

    except Exception as e:
        print(f"Error analyzing results: {e}")
        return True

if __name__ == "__main__":
    main()