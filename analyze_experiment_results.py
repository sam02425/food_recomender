#!/usr/bin/env python3
"""
Comprehensive Analysis of AI-Powered Food Recommender Experiment Results
Analyzes partial experiment data to identify improvements for the full run.
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter, defaultdict
import os

def load_experiment_data():
    """Load all experiment data files"""
    data = {}

    # Load experiment log
    if os.path.exists('data/experiment_log.csv'):
        data['experiment_log'] = pd.read_csv('data/experiment_log.csv')
        print(f"✅ Loaded experiment log: {len(data['experiment_log'])} records")

    # Load agent interactions
    if os.path.exists('data/agent_interactions.csv'):
        data['agent_interactions'] = pd.read_csv('data/agent_interactions.csv')
        print(f"✅ Loaded agent interactions: {len(data['agent_interactions'])} records")

    # Load orders
    if os.path.exists('data/orders.csv'):
        data['orders'] = pd.read_csv('data/orders.csv')
        print(f"✅ Loaded orders: {len(data['orders'])} records")

    # Load learning data
    if os.path.exists('data/learning_data.json'):
        with open('data/learning_data.json', 'r') as f:
            data['learning_data'] = json.load(f)
        print(f"✅ Loaded learning data: {len(data['learning_data'])} records")

    return data

def analyze_participant_progress(data):
    """Analyze participant progress and completion rates"""
    print("\n" + "="*60)
    print("📊 PARTICIPANT PROGRESS ANALYSIS")
    print("="*60)

    if 'experiment_log' not in data:
        print("❌ No experiment log data available")
        return

    df = data['experiment_log']

    # Extract participant IDs and conditions
    df['participant_id'] = df['experiment_number'].str.extract(r'(P\d+)')
    df['condition'] = df['experiment_number'].str.extract(r'_(emotion_responsive|traditional)_')
    df['trial_number'] = df['experiment_number'].str.extract(r'_(\d+)$').astype(int)

    # Participant statistics
    unique_participants = df['participant_id'].nunique()
    total_trials = len(df)
    avg_trials_per_participant = total_trials / unique_participants

    print(f"👥 Total Participants: {unique_participants}")
    print(f"🔄 Total Trials: {total_trials}")
    print(f"📈 Average Trials per Participant: {avg_trials_per_participant:.1f}")

    # Condition breakdown
    condition_stats = df.groupby('condition').agg({
        'participant_id': 'nunique',
        'experiment_number': 'count'
    }).rename(columns={'participant_id': 'participants', 'experiment_number': 'trials'})

    print(f"\n📋 Condition Breakdown:")
    for condition, stats in condition_stats.iterrows():
        print(f"   {condition}: {stats['participants']} participants, {stats['trials']} trials")

    # Trial completion analysis
    trial_completion = df.groupby('participant_id')['trial_number'].max()
    print(f"\n🎯 Trial Completion Analysis:")
    print(f"   Average max trial: {trial_completion.mean():.1f}")
    print(f"   Participants with 5+ trials: {(trial_completion >= 5).sum()}")
    print(f"   Participants with 10+ trials: {(trial_completion >= 10).sum()}")

    return df

def analyze_agent_performance(data):
    """Analyze AI agent performance and recommendations"""
    print("\n" + "="*60)
    print("🤖 AI AGENT PERFORMANCE ANALYSIS")
    print("="*60)

    if 'experiment_log' not in data:
        print("❌ No experiment log data available")
        return

    df = data['experiment_log']

    # Analyze agent recommendations
    emotion_responsive_trials = df[df['condition'] == 'emotion_responsive']
    traditional_trials = df[df['condition'] == 'traditional']

    print(f"🎭 Emotion Responsive Trials: {len(emotion_responsive_trials)}")
    print(f"📋 Traditional Trials: {len(traditional_trials)}")

    # Agent recommendation analysis
    def analyze_agent_recommendations(trials_df, condition_name):
        print(f"\n📊 {condition_name.upper()} CONDITION:")

        # Count trials with agent recommendations
        trials_with_agents = trials_df[trials_df['agent_recommendations'].notna()]
        trials_without_agents = trials_df[trials_df['agent_recommendations'].isna()]

        print(f"   Trials with agent recommendations: {len(trials_with_agents)}")
        print(f"   Trials without agent recommendations: {len(trials_without_agents)}")

        if len(trials_with_agents) > 0:
            # Parse agent recommendations
            agent_data = []
            for _, row in trials_with_agents.iterrows():
                try:
                    if pd.notna(row['agent_recommendations']):
                        rec_data = json.loads(row['agent_recommendations'])
                        if 'recommendations' in rec_data:
                            for agent_type, recommendations in rec_data['recommendations'].items():
                                agent_data.append({
                                    'agent_type': agent_type,
                                    'recommendation_count': len(recommendations),
                                    'participant_id': row['participant_id'],
                                    'trial_number': row.get('trial_number', 0)
                                })
                except:
                    continue

            if agent_data:
                agent_df = pd.DataFrame(agent_data)
                agent_summary = agent_df.groupby('agent_type').agg({
                    'recommendation_count': ['mean', 'sum', 'count']
                }).round(2)

                print(f"   Agent Recommendation Summary:")
                for agent_type in agent_summary.index:
                    mean_recs = agent_summary.loc[agent_type, ('recommendation_count', 'mean')]
                    total_recs = agent_summary.loc[agent_type, ('recommendation_count', 'sum')]
                    trials = agent_summary.loc[agent_type, ('recommendation_count', 'count')]
                    print(f"     {agent_type}: {mean_recs} avg, {total_recs} total, {trials} trials")

    analyze_agent_recommendations(emotion_responsive_trials, "Emotion Responsive")
    analyze_agent_recommendations(traditional_trials, "Traditional")

def analyze_agent_interactions(data):
    """Analyze detailed agent interaction patterns"""
    print("\n" + "="*60)
    print("🔄 AGENT INTERACTION PATTERNS")
    print("="*60)

    if 'agent_interactions' not in data:
        print("❌ No agent interactions data available")
        return

    df = data['agent_interactions']

    # Basic statistics
    print(f"📈 Total Agent Interactions: {len(df)}")
    print(f"👥 Unique Participants: {df['participant_id'].nunique()}")

    # Agent type analysis
    agent_types = df['agent_type'].value_counts()
    print(f"\n🤖 Agent Type Distribution:")
    for agent_type, count in agent_types.items():
        print(f"   {agent_type}: {count} interactions")

    # Action analysis
    actions = df['action'].value_counts()
    print(f"\n✅ Action Distribution:")
    for action, count in actions.items():
        print(f"   {action}: {count} times")

    # Agent acceptance rates
    print(f"\n📊 Agent Acceptance Rates:")
    for agent_type in df['agent_type'].unique():
        agent_data = df[df['agent_type'] == agent_type]
        total_shown = len(agent_data[agent_data['action'] == 'shown'])
        total_accepted = len(agent_data[agent_data['action'] == 'accept'])
        total_rejected = len(agent_data[agent_data['action'] == 'reject'])
        total_ignored = len(agent_data[agent_data['action'] == 'ignore'])

        if total_shown > 0:
            acceptance_rate = (total_accepted / total_shown) * 100
            rejection_rate = (total_rejected / total_shown) * 100
            ignore_rate = (total_ignored / total_shown) * 100

            print(f"   {agent_type}:")
            print(f"     Shown: {total_shown}, Accepted: {total_accepted} ({acceptance_rate:.1f}%)")
            print(f"     Rejected: {total_rejected} ({rejection_rate:.1f}%), Ignored: {total_ignored} ({ignore_rate:.1f}%)")

def analyze_timing_data(data):
    """Analyze timing and performance data"""
    print("\n" + "="*60)
    print("⏱️ TIMING AND PERFORMANCE ANALYSIS")
    print("="*60)

    if 'experiment_log' not in data:
        print("❌ No experiment log data available")
        return

    df = data['experiment_log']

    # Extract timing columns
    timing_columns = [col for col in df.columns if 'duration' in col]

    if timing_columns:
        print(f"📊 Timing Analysis:")
        for col in timing_columns:
            if col in df.columns and df[col].notna().any():
                valid_times = df[col].dropna()
                if len(valid_times) > 0:
                    print(f"   {col}:")
                    print(f"     Mean: {valid_times.mean():.2f}s")
                    print(f"     Median: {valid_times.median():.2f}s")
                    print(f"     Min: {valid_times.min():.2f}s")
                    print(f"     Max: {valid_times.max():.2f}s")
                    print(f"     Valid records: {len(valid_times)}")

    # Emotional state analysis
    if 'emotional_state' in df.columns:
        emotions = df['emotional_state'].value_counts()
        print(f"\n😊 Emotional State Distribution:")
        for emotion, count in emotions.items():
            percentage = (count / len(df)) * 100
            print(f"   {emotion}: {count} ({percentage:.1f}%)")

def analyze_preference_learning(data):
    """Analyze preference learning system performance"""
    print("\n" + "="*60)
    print("🧠 PREFERENCE LEARNING ANALYSIS")
    print("="*60)

    if 'learning_data' not in data:
        print("❌ No learning data available")
        return

    learning_data = data['learning_data']

    print(f"📚 Learning Data Records: {len(learning_data)}")

    # Analyze user preferences
    user_preferences = defaultdict(int)
    recommendation_types = defaultdict(int)

    for record in learning_data:
        if isinstance(record, dict):
            # Count user interactions
            user_id = record.get('user_id', 'unknown')
            user_preferences[user_id] += 1

            # Count recommendation types
            recommendations = record.get('recommendations', [])
            for rec in recommendations:
                if isinstance(rec, dict):
                    rec_type = rec.get('type', 'unknown')
                    recommendation_types[rec_type] += 1

    print(f"👥 Unique Users: {len(user_preferences)}")
    print(f"📊 Recommendation Types:")
    for rec_type, count in recommendation_types.items():
        print(f"   {rec_type}: {count}")

def identify_improvements(data):
    """Identify areas for improvement based on analysis"""
    print("\n" + "="*60)
    print("🔧 IMPROVEMENT RECOMMENDATIONS")
    print("="*60)

    improvements = []

    if 'experiment_log' in data:
        df = data['experiment_log']

        # Check for missing subjective scores
        missing_scores = df[df['nasa_tlx_overall'] == 0]
        if len(missing_scores) > 0:
            improvements.append(f"❌ Missing NASA-TLX scores: {len(missing_scores)} trials")

        # Check for incomplete trials
        if 'trial_number' in df.columns:
            incomplete_participants = df.groupby('participant_id')['trial_number'].max()
            incomplete = incomplete_participants[incomplete_participants < 10]
            if len(incomplete) > 0:
                improvements.append(f"⚠️ Incomplete participants: {len(incomplete)} participants with <10 trials")

    if 'agent_interactions' in data:
        df = data['agent_interactions']

        # Check for agent errors
        error_interactions = df[df['action'] == 'error']
        if len(error_interactions) > 0:
            improvements.append(f"❌ Agent errors: {len(error_interactions)} error interactions")

        # Check for low acceptance rates
        for agent_type in df['agent_type'].unique():
            agent_data = df[df['agent_type'] == agent_type]
            total_shown = len(agent_data[agent_data['action'] == 'shown'])
            total_accepted = len(agent_data[agent_data['action'] == 'accept'])

            if total_shown > 0:
                acceptance_rate = (total_accepted / total_shown) * 100
                if acceptance_rate < 50:
                    improvements.append(f"⚠️ Low acceptance rate for {agent_type}: {acceptance_rate:.1f}%")

    # General recommendations
    improvements.extend([
        "✅ Ensure all participants complete full 10 trials (5 baseline + 5 agent-assisted)",
        "✅ Implement proper error handling for agent interactions",
        "✅ Add more diverse emotional states and personality types",
        "✅ Improve agent recommendation quality and relevance",
        "✅ Add real-time performance monitoring during experiments",
        "✅ Implement automatic experiment recovery mechanisms"
    ])

    for improvement in improvements:
        print(f"   {improvement}")

def generate_summary_report(data):
    """Generate a comprehensive summary report"""
    print("\n" + "="*60)
    print("📋 EXPERIMENT SUMMARY REPORT")
    print("="*60)

    summary = {
        'timestamp': datetime.now().isoformat(),
        'data_files_loaded': list(data.keys()),
        'total_records': sum(len(v) if hasattr(v, '__len__') else 1 for v in data.values())
    }

    if 'experiment_log' in data:
        df = data['experiment_log']
        summary.update({
            'total_participants': df['participant_id'].nunique() if 'participant_id' in df.columns else 0,
            'total_trials': len(df),
            'emotion_responsive_trials': len(df[df['condition'] == 'emotion_responsive']),
            'traditional_trials': len(df[df['condition'] == 'traditional']),
            'trials_with_agents': len(df[df['agent_recommendations'].notna()]),
            'trials_without_agents': len(df[df['agent_recommendations'].isna()])
        })

    if 'agent_interactions' in data:
        df = data['agent_interactions']
        summary.update({
            'total_agent_interactions': len(df),
            'unique_agent_types': df['agent_type'].nunique(),
            'agent_acceptance_rate': (len(df[df['action'] == 'accept']) / len(df)) * 100 if len(df) > 0 else 0
        })

    print(f"📅 Analysis Timestamp: {summary['timestamp']}")
    print(f"📁 Data Files: {', '.join(summary['data_files_loaded'])}")
    print(f"📊 Total Records: {summary['total_records']}")

    if 'total_participants' in summary:
        print(f"👥 Participants: {summary['total_participants']}")
        print(f"🔄 Total Trials: {summary['total_trials']}")
        print(f"🎭 Emotion Responsive: {summary['emotion_responsive_trials']}")
        print(f"📋 Traditional: {summary['traditional_trials']}")
        print(f"🤖 With Agents: {summary['trials_with_agents']}")
        print(f"📝 Without Agents: {summary['trials_without_agents']}")

    if 'total_agent_interactions' in summary:
        print(f"🔄 Agent Interactions: {summary['total_agent_interactions']}")
        print(f"🤖 Agent Types: {summary['unique_agent_types']}")
        print(f"✅ Acceptance Rate: {summary['agent_acceptance_rate']:.1f}%")

    return summary

def main():
    """Main analysis function"""
    print("🔍 AI-POWERED FOOD RECOMMENDER EXPERIMENT ANALYSIS")
    print("="*60)
    print("Analyzing partial experiment results to identify improvements...")

    # Load data
    data = load_experiment_data()

    if not data:
        print("❌ No experiment data found. Please ensure experiment has been run.")
        return

    # Run analyses
    df = analyze_participant_progress(data)
    analyze_agent_performance(data)
    analyze_agent_interactions(data)
    analyze_timing_data(data)
    analyze_preference_learning(data)
    identify_improvements(data)
    summary = generate_summary_report(data)

    print("\n" + "="*60)
    print("✅ ANALYSIS COMPLETE")
    print("="*60)
    print("The analysis reveals key insights for improving the full experiment run.")
    print("Focus on completing all 50 participants with full 10 trials each.")

if __name__ == "__main__":
    main()