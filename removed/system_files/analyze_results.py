#!/usr/bin/env python3
"""
Analyze Experiment Results
Confidential - Internal Research Use Only
"""

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import datetime
import os
import sys
from typing import Dict, List, Tuple, Any

class ExperimentResultsAnalyzer:
    """Comprehensive analysis of experiment results"""
    
    def __init__(self, data_dir: str = "data/human_experiments"):
        self.data_dir = data_dir
        self.results_df = None
        self.analysis_results = {}
        
    def load_data(self) -> bool:
        """Load experiment data from CSV files"""
        print("📊 Loading experiment data...")
        
        results_file = os.path.join(self.data_dir, "trial_results.csv")
        
        if not os.path.exists(results_file):
            print(f"❌ Results file not found: {results_file}")
            return False
        
        try:
            self.results_df = pd.read_csv(results_file)
            print(f"✅ Loaded {len(self.results_df)} trial records")
            print(f"   Participants: {self.results_df['participant_id'].nunique()}")
            print(f"   Conditions: {self.results_df['condition'].unique()}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return False
    
    def basic_descriptive_stats(self) -> Dict[str, Any]:
        """Calculate basic descriptive statistics"""
        print("\n📈 Calculating descriptive statistics...")
        
        stats = {}
        
        # Overall statistics
        stats['total_trials'] = len(self.results_df)
        stats['total_participants'] = self.results_df['participant_id'].nunique()
        stats['conditions'] = list(self.results_df['condition'].unique())
        
        # Condition-wise statistics
        for condition in stats['conditions']:
            condition_data = self.results_df[self.results_df['condition'] == condition]
            
            stats[f'{condition}_stats'] = {
                'count': len(condition_data),
                'completion_time': {
                    'mean': condition_data['completion_time_seconds'].mean(),
                    'std': condition_data['completion_time_seconds'].std(),
                    'median': condition_data['completion_time_seconds'].median()
                },
                'satisfaction': {
                    'mean': condition_data['satisfaction_rating'].mean(),
                    'std': condition_data['satisfaction_rating'].std(),
                    'median': condition_data['satisfaction_rating'].median()
                },
                'nasa_tlx': {
                    'mean': condition_data['nasa_tlx_score'].mean(),
                    'std': condition_data['nasa_tlx_score'].std(),
                    'median': condition_data['nasa_tlx_score'].median()
                },
                'trust': {
                    'mean': condition_data['trust_rating'].mean(),
                    'std': condition_data['trust_rating'].std(),
                    'median': condition_data['trust_rating'].median()
                },
                'errors': {
                    'mean': condition_data['error_count'].mean(),
                    'std': condition_data['error_count'].std(),
                    'median': condition_data['error_count'].median()
                },
                'navigation_steps': {
                    'mean': condition_data['navigation_steps'].mean(),
                    'std': condition_data['navigation_steps'].std(),
                    'median': condition_data['navigation_steps'].median()
                }
            }
            
            # Recommendation acceptance for adaptive condition
            if condition == 'adaptive':
                rec_acceptance = condition_data['recommendation_acceptance'].dropna()
                if len(rec_acceptance) > 0:
                    stats[f'{condition}_stats']['recommendation_acceptance'] = {
                        'mean': rec_acceptance.mean(),
                        'std': rec_acceptance.std(),
                        'median': rec_acceptance.median()
                    }
        
        self.analysis_results['descriptive_stats'] = stats
        return stats
    
    def statistical_comparisons(self) -> Dict[str, Any]:
        """Perform statistical comparisons between conditions"""
        print("\n🔬 Performing statistical comparisons...")
        
        if len(self.results_df['condition'].unique()) < 2:
            print("⚠️  Need at least 2 conditions for comparison")
            return {}
        
        baseline_data = self.results_df[self.results_df['condition'] == 'baseline']
        adaptive_data = self.results_df[self.results_df['condition'] == 'adaptive']
        
        comparisons = {}
        measures = ['completion_time_seconds', 'satisfaction_rating', 'nasa_tlx_score', 
                   'trust_rating', 'error_count', 'navigation_steps']
        
        for measure in measures:
            baseline_values = baseline_data[measure].dropna()
            adaptive_values = adaptive_data[measure].dropna()
            
            if len(baseline_values) > 0 and len(adaptive_values) > 0:
                # Paired t-test (assuming within-subjects design)
                try:
                    t_stat, p_value = stats.ttest_rel(baseline_values, adaptive_values)
                    
                    # Effect size (Cohen's d)
                    pooled_std = np.sqrt(((len(baseline_values) - 1) * baseline_values.std() ** 2 + 
                                        (len(adaptive_values) - 1) * adaptive_values.std() ** 2) / 
                                       (len(baseline_values) + len(adaptive_values) - 2))
                    cohens_d = (adaptive_values.mean() - baseline_values.mean()) / pooled_std
                    
                    comparisons[measure] = {
                        'baseline_mean': baseline_values.mean(),
                        'adaptive_mean': adaptive_values.mean(),
                        'difference': adaptive_values.mean() - baseline_values.mean(),
                        'percent_change': ((adaptive_values.mean() - baseline_values.mean()) / baseline_values.mean()) * 100,
                        't_statistic': t_stat,
                        'p_value': p_value,
                        'cohens_d': cohens_d,
                        'significance': 'significant' if p_value < 0.05 else 'not_significant'
                    }
                    
                except Exception as e:
                    print(f"⚠️  Error in statistical test for {measure}: {str(e)}")
        
        self.analysis_results['statistical_comparisons'] = comparisons
        return comparisons
    
    def participant_level_analysis(self) -> Dict[str, Any]:
        """Analyze results at the participant level"""
        print("\n👥 Performing participant-level analysis...")
        
        participant_stats = {}
        
        for participant_id in self.results_df['participant_id'].unique():
            participant_data = self.results_df[self.results_df['participant_id'] == participant_id]
            
            baseline_trials = participant_data[participant_data['condition'] == 'baseline']
            adaptive_trials = participant_data[participant_data['condition'] == 'adaptive']
            
            participant_stats[participant_id] = {
                'total_trials': len(participant_data),
                'baseline_trials': len(baseline_trials),
                'adaptive_trials': len(adaptive_trials)
            }
            
            if len(baseline_trials) > 0:
                participant_stats[participant_id]['baseline_satisfaction_avg'] = baseline_trials['satisfaction_rating'].mean()
                participant_stats[participant_id]['baseline_nasa_tlx_avg'] = baseline_trials['nasa_tlx_score'].mean()
            
            if len(adaptive_trials) > 0:
                participant_stats[participant_id]['adaptive_satisfaction_avg'] = adaptive_trials['satisfaction_rating'].mean()
                participant_stats[participant_id]['adaptive_nasa_tlx_avg'] = adaptive_trials['nasa_tlx_score'].mean()
                
                rec_acceptance = adaptive_trials['recommendation_acceptance'].dropna()
                if len(rec_acceptance) > 0:
                    participant_stats[participant_id]['avg_recommendation_acceptance'] = rec_acceptance.mean()
        
        self.analysis_results['participant_level'] = participant_stats
        return participant_stats
    
    def learning_effects_analysis(self) -> Dict[str, Any]:
        """Analyze learning effects within conditions"""
        print("\n📚 Analyzing learning effects...")
        
        learning_analysis = {}
        
        for condition in self.results_df['condition'].unique():
            condition_data = self.results_df[self.results_df['condition'] == condition]
            
            # Correlation between trial number and performance metrics
            correlations = {}
            measures = ['completion_time_seconds', 'satisfaction_rating', 'nasa_tlx_score', 'error_count']
            
            for measure in measures:
                if measure in condition_data.columns:
                    correlation, p_value = stats.pearsonr(condition_data['trial_number'], condition_data[measure])
                    correlations[measure] = {
                        'correlation': correlation,
                        'p_value': p_value,
                        'significance': 'significant' if p_value < 0.05 else 'not_significant'
                    }
            
            learning_analysis[condition] = correlations
        
        self.analysis_results['learning_effects'] = learning_analysis
        return learning_analysis
    
    def generate_visualizations(self, save_plots: bool = True) -> None:
        """Generate visualization plots"""
        print("\n📊 Generating visualizations...")
        
        if save_plots:
            os.makedirs(os.path.join(self.data_dir, "plots"), exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Condition comparison boxplots
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Condition Comparisons', fontsize=16)
        
        measures = ['satisfaction_rating', 'nasa_tlx_score', 'completion_time_seconds', 
                   'trust_rating', 'error_count', 'navigation_steps']
        titles = ['Satisfaction Rating', 'NASA-TLX Score', 'Completion Time (s)', 
                 'Trust Rating', 'Error Count', 'Navigation Steps']
        
        for i, (measure, title) in enumerate(zip(measures, titles)):
            row, col = i // 3, i % 3
            sns.boxplot(data=self.results_df, x='condition', y=measure, ax=axes[row, col])
            axes[row, col].set_title(title)
            axes[row, col].set_xlabel('Condition')
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(os.path.join(self.data_dir, "plots", "condition_comparisons.png"), dpi=300, bbox_inches='tight')
        plt.show()
        
        # 2. Learning curves
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle('Learning Effects', fontsize=16)
        
        for i, condition in enumerate(['baseline', 'adaptive']):
            condition_data = self.results_df[self.results_df['condition'] == condition]
            
            # Group by trial number and calculate means
            trial_means = condition_data.groupby('trial_number')['satisfaction_rating'].mean()
            
            axes[i].plot(trial_means.index, trial_means.values, marker='o')
            axes[i].set_title(f'{condition.title()} Condition')
            axes[i].set_xlabel('Trial Number')
            axes[i].set_ylabel('Average Satisfaction Rating')
            axes[i].grid(True, alpha=0.3)
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(os.path.join(self.data_dir, "plots", "learning_curves.png"), dpi=300, bbox_inches='tight')
        plt.show()
        
        # 3. Participant-level heatmap
        participants = sorted(self.results_df['participant_id'].unique())
        measures = ['satisfaction_rating', 'nasa_tlx_score']
        
        baseline_matrix = np.zeros((len(participants), len(measures)))
        adaptive_matrix = np.zeros((len(participants), len(measures)))
        
        for i, participant in enumerate(participants):
            participant_data = self.results_df[self.results_df['participant_id'] == participant]
            
            baseline_data = participant_data[participant_data['condition'] == 'baseline']
            adaptive_data = participant_data[participant_data['condition'] == 'adaptive']
            
            for j, measure in enumerate(measures):
                if len(baseline_data) > 0:
                    baseline_matrix[i, j] = baseline_data[measure].mean()
                if len(adaptive_data) > 0:
                    adaptive_matrix[i, j] = adaptive_data[measure].mean()
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 8))
        fig.suptitle('Participant Performance Heatmaps', fontsize=16)
        
        sns.heatmap(baseline_matrix, xticklabels=measures, yticklabels=participants, 
                   annot=True, fmt='.1f', ax=axes[0], cmap='RdYlBu_r')
        axes[0].set_title('Baseline Condition')
        
        sns.heatmap(adaptive_matrix, xticklabels=measures, yticklabels=participants, 
                   annot=True, fmt='.1f', ax=axes[1], cmap='RdYlBu_r')
        axes[1].set_title('Adaptive Condition')
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(os.path.join(self.data_dir, "plots", "participant_heatmaps.png"), dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        print("\n📝 Generating analysis report...")
        
        report = []
        report.append("EXPERIMENT RESULTS ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Descriptive statistics
        if 'descriptive_stats' in self.analysis_results:
            stats = self.analysis_results['descriptive_stats']
            report.append("DESCRIPTIVE STATISTICS")
            report.append("-" * 30)
            report.append(f"Total Trials: {stats['total_trials']}")
            report.append(f"Total Participants: {stats['total_participants']}")
            report.append(f"Conditions: {', '.join(stats['conditions'])}")
            report.append("")
            
            for condition in stats['conditions']:
                if f'{condition}_stats' in stats:
                    condition_stats = stats[f'{condition}_stats']
                    report.append(f"{condition.upper()} CONDITION:")
                    report.append(f"  Trials: {condition_stats['count']}")
                    report.append(f"  Satisfaction: {condition_stats['satisfaction']['mean']:.2f} ± {condition_stats['satisfaction']['std']:.2f}")
                    report.append(f"  NASA-TLX: {condition_stats['nasa_tlx']['mean']:.1f} ± {condition_stats['nasa_tlx']['std']:.1f}")
                    report.append(f"  Completion Time: {condition_stats['completion_time']['mean']:.2f}s ± {condition_stats['completion_time']['std']:.2f}")
                    report.append(f"  Trust: {condition_stats['trust']['mean']:.2f} ± {condition_stats['trust']['std']:.2f}")
                    if 'recommendation_acceptance' in condition_stats:
                        report.append(f"  Rec. Acceptance: {condition_stats['recommendation_acceptance']['mean']:.1%}")
                    report.append("")
        
        # Statistical comparisons
        if 'statistical_comparisons' in self.analysis_results:
            comparisons = self.analysis_results['statistical_comparisons']
            report.append("STATISTICAL COMPARISONS")
            report.append("-" * 30)
            
            for measure, comparison in comparisons.items():
                report.append(f"{measure.replace('_', ' ').title()}:")
                report.append(f"  Baseline: {comparison['baseline_mean']:.3f}")
                report.append(f"  Adaptive: {comparison['adaptive_mean']:.3f}")
                report.append(f"  Difference: {comparison['difference']:+.3f} ({comparison['percent_change']:+.1f}%)")
                report.append(f"  p-value: {comparison['p_value']:.6f} ({comparison['significance']})")
                report.append(f"  Effect size (Cohen's d): {comparison['cohens_d']:.3f}")
                report.append("")
        
        # Learning effects
        if 'learning_effects' in self.analysis_results:
            learning = self.analysis_results['learning_effects']
            report.append("LEARNING EFFECTS")
            report.append("-" * 30)
            
            for condition, correlations in learning.items():
                report.append(f"{condition.upper()} CONDITION:")
                for measure, corr_data in correlations.items():
                    report.append(f"  {measure}: r={corr_data['correlation']:.3f}, p={corr_data['p_value']:.3f} ({corr_data['significance']})")
                report.append("")
        
        report_text = "\n".join(report)
        
        # Save report
        report_file = os.path.join(self.data_dir, "analysis_report.txt")
        with open(report_file, 'w') as f:
            f.write(report_text)
        
        print(f"📄 Report saved to: {report_file}")
        return report_text
    
    def save_analysis_results(self) -> None:
        """Save analysis results to JSON"""
        results_file = os.path.join(self.data_dir, "analysis_results.json")
        
        # Convert numpy types to Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            else:
                return obj
        
        analysis_json = convert_numpy(self.analysis_results)
        
        with open(results_file, 'w') as f:
            json.dump(analysis_json, f, indent=2)
        
        print(f"💾 Analysis results saved to: {results_file}")
    
    def run_complete_analysis(self) -> bool:
        """Run complete analysis pipeline"""
        print("🔍 Starting Complete Analysis Pipeline")
        print("=" * 50)
        
        # Load data
        if not self.load_data():
            return False
        
        # Run all analyses
        self.basic_descriptive_stats()
        self.statistical_comparisons()
        self.participant_level_analysis()
        self.learning_effects_analysis()
        
        # Generate outputs
        self.generate_visualizations()
        self.generate_report()
        self.save_analysis_results()
        
        print("\n🎉 Analysis complete!")
        print(f"📁 Check {self.data_dir}/ for results")
        
        return True

def main():
    """Main analysis function"""
    
    # Check if data directory exists
    data_dir = "data/human_experiments"
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        print("   Run experiments first to generate data.")
        sys.exit(1)
    
    # Create analyzer
    analyzer = ExperimentResultsAnalyzer(data_dir)
    
    # Run analysis
    success = analyzer.run_complete_analysis()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
