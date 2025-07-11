# Adaptive Artificial Participant System

A realistic, intelligent artificial participant system for food ordering experiments that uses GROQ LLM for participant reasoning and learns from experiment interactions.

## Overview

This system simulates 50 human participants completing 10 trials each (5 baseline, 5 adaptive) for a total of 500 experimental runs. Unlike traditional simulation systems, this approach:

- **Uses GROQ LLM** for realistic participant feedback and reasoning
- **Learns and adapts** from system interactions like real participants
- **Generates authentic data** with natural variance and imperfections
- **Models realistic failures** including dietary compliance issues, privacy concerns, and cultural mismatches
- **Produces unbiased results** without preset effect sizes or means

## Key Features

### 🧠 Intelligent Participant Modeling
- **Personality traits**: Tech savviness, food adventurousness, health consciousness, price sensitivity
- **Cultural backgrounds**: South Asian (35%), Western (25%), Middle Eastern (15%), East Asian (15%), Other (10%)
- **Dietary restrictions**: Vegan, vegetarian, halal, no-pork, no-beef with realistic compliance failures
- **Learning and adaptation**: Participants learn from system mistakes and improve over time
- **Mood and fatigue**: Realistic emotional states that affect performance

### 🤖 GROQ LLM Integration
- **Realistic feedback**: Every 3rd trial generates authentic participant feedback
- **Contextual reasoning**: LLM considers participant personality, cultural background, and experience
- **Natural language**: Produces varied, human-like responses with frustrations and insights
- **API efficiency**: Optimized to minimize API usage while maintaining quality

### 📊 Authentic Data Generation
- **Natural variance**: No preset means or effect sizes - results emerge naturally
- **Realistic failures**: 15% dietary compliance failure rate, system errors, cultural mismatches
- **Learning effects**: Participants improve with experience but at different rates
- **Cultural sensitivity**: Different performance patterns based on cultural background

### 🔬 Comprehensive Analysis
- **Statistical testing**: T-tests, effect sizes, confidence intervals
- **Subgroup analysis**: Performance by cultural background, dietary restrictions
- **Qualitative insights**: LLM feedback analysis, failure patterns, learning insights
- **System performance**: Response times, recommendation quality, failure rates

## System Architecture

```
AdaptiveParticipantSystem
├── ParticipantProfile (dataclass)
│   ├── Demographics (age, gender, cultural background)
│   ├── Dietary preferences (restrictions, allergens)
│   ├── Personality traits (tech savviness, food adventurousness, etc.)
│   ├── Dynamic states (mood, fatigue, learning rate, trust)
│   └── Previous experience (learning from trials)
├── GROQClient
│   ├── Async API communication
│   ├── Contextual prompt generation
│   ├── Fallback feedback generation
│   └── Error handling
├── TrialData (dataclass)
│   ├── Performance metrics (completion time, satisfaction)
│   ├── System interaction (recommendation acceptance, dietary compliance)
│   ├── Qualitative data (privacy concerns, cultural mismatches)
│   ├── Learning insights and system failures
│   └── LLM feedback (when available)
└── Analysis Engine
    ├── Statistical analysis (t-tests, effect sizes)
    ├── Diversity analysis (cultural, dietary subgroups)
    ├── System performance analysis
    └── Qualitative insights extraction
```

## Menu System Integration

The system accurately models the actual app's menu structure:

### Proteins
- **Chicken** ($4.50) - Halal, no-pork compliant
- **Egg** ($3.00) - Vegetarian, halal compliant
- **Paneer/Indian Cheese** ($4.00) - Vegetarian, halal compliant
- **Soya** ($3.50) - Vegan, vegetarian, halal compliant
- **Potato** ($2.50) - Vegan, vegetarian, halal compliant
- **Pepperoni** ($4.50) - No-beef compliant only

### Dietary Restrictions
- **Vegan**: Excludes all animal products, allows Soya/Potato only
- **Vegetarian**: Excludes meat/poultry, allows Egg/Paneer/Soya/Potato
- **Halal**: Excludes pork, allows Chicken/Egg/Paneer/Soya/Potato
- **No-pork**: Excludes pork products, allows all except Pepperoni
- **No-beef**: Excludes beef products, allows all proteins

### Cultural Sensitivity
- **South Asian participants**: Better performance with curry-focused menu
- **Middle Eastern participants**: Halal compliance challenges
- **Western participants**: Standard performance patterns
- **Cultural mismatches**: Spice levels, halal certification, ingredient preferences

## Installation and Setup

### 1. Install Dependencies
```bash
pip install aiohttp numpy scipy pandas
```

### 2. Set GROQ API Key
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

Or edit `experiment_config.py`:
```python
GROQ_API_KEY = "your_groq_api_key_here"
```

### 3. Validate Configuration
```python
from experiment_config import ExperimentConfig
ExperimentConfig.validate_config()
```

## Usage

### Quick Test
```bash
python test_adaptive_system.py
```

### Full Experiment
```python
from adaptive_participant_system import AdaptiveParticipantSystem
import asyncio

async def run_experiment():
    experiment = AdaptiveParticipantSystem(
        groq_api_key="your_key",
        num_participants=50,
        trials_per_participant=10
    )

    results = await experiment.run_experiment()
    experiment.save_results("experiment_results.json")
    return results

asyncio.run(run_experiment())
```

### Custom Configuration
```python
from experiment_config import ExperimentConfig

# Modify experiment parameters
ExperimentConfig.NUM_PARTICIPANTS = 25
ExperimentConfig.LLM_FEEDBACK_FREQUENCY = 5  # Less frequent feedback
ExperimentConfig.ENABLE_LLM_FEEDBACK = False  # Disable LLM for faster testing
```

## Output Format

The system generates comprehensive results in JSON format:

```json
{
  "experiment_summary": {
    "total_participants": 50,
    "total_trials": 500,
    "baseline_trials": 250,
    "adaptive_trials": 250
  },
  "performance_metrics": {
    "baseline": {
      "avg_completion_time": 145.2,
      "avg_satisfaction": 3.4,
      "avg_recommendation_acceptance": 0.62,
      "dietary_compliance_rate": 0.87
    },
    "adaptive": {
      "avg_completion_time": 132.8,
      "avg_satisfaction": 3.7,
      "avg_recommendation_acceptance": 0.71,
      "dietary_compliance_rate": 0.89
    }
  },
  "statistical_analysis": {
    "task_completion_time": {
      "baseline_mean": 145.2,
      "adaptive_mean": 132.8,
      "difference": -12.4,
      "t_statistic": -2.34,
      "p_value": 0.019,
      "significant": true,
      "effect_size": -0.21,
      "effect_magnitude": "small"
    }
  },
  "participant_diversity": {
    "cultural_backgrounds": {
      "South Asian": {"count": 18, "avg_satisfaction": 3.8},
      "Western": {"count": 12, "avg_satisfaction": 3.3}
    }
  },
  "qualitative_insights": {
    "llm_feedback_count": 167,
    "sample_feedback": ["The system was okay but confusing at first..."],
    "privacy_concerns": ["Data collection concerns", "Personalization feels invasive"],
    "cultural_mismatches": ["Halal certification unclear", "Spice levels not appropriate"],
    "system_failures": {"Recommendation system unavailable": 12}
  }
}
```

## Realistic Data Characteristics

### Natural Variance
- **No preset means**: All metrics emerge from participant behavior
- **Realistic distributions**: Beta distributions for personality traits, normal for performance
- **Individual differences**: Each participant has unique learning curves and preferences

### Authentic Failures
- **Dietary compliance**: 15% failure rate, higher with more restrictions
- **System errors**: Recommendation failures (10%), dietary filter errors (5%)
- **Cultural mismatches**: Halal certification issues, inappropriate spice levels
- **Privacy concerns**: Data collection worries, invasive personalization

### Learning Effects
- **Variable learning rates**: Some participants learn faster than others
- **Trust evolution**: Recommendation acceptance changes based on experience
- **Mood changes**: Satisfaction affects subsequent trial performance
- **Fatigue accumulation**: Performance degrades over multiple trials

## Comparison with Traditional Systems

| Feature | Traditional Simulation | Adaptive System |
|---------|----------------------|-----------------|
| **Data Generation** | Preset means/variances | Emergent from behavior |
| **Participant Modeling** | Static profiles | Dynamic learning/adaptation |
| **Feedback** | None or scripted | Realistic LLM-generated |
| **Failures** | Rare or none | Realistic failure rates |
| **Cultural Sensitivity** | Limited | Comprehensive modeling |
| **Learning Effects** | None | Individual learning curves |
| **Result Bias** | Potential for bias | Unbiased emergent results |

## API Usage Optimization

The system optimizes GROQ API usage:

- **Feedback frequency**: Every 3rd trial (configurable)
- **Prompt efficiency**: Concise, focused prompts
- **Error handling**: Fallback feedback when API unavailable
- **Rate limiting**: Built-in delays to avoid overwhelming API

Estimated API usage for full experiment:
- 50 participants × 10 trials ÷ 3 = ~167 API calls
- Cost: ~$0.50-1.00 (depending on model and prompt length)

## Troubleshooting

### Common Issues

1. **GROQ API Key Error**
   ```
   Error: GROQ API key not set
   Solution: Set GROQ_API_KEY environment variable or edit experiment_config.py
   ```

2. **Configuration Validation Failed**
   ```
   Error: Cultural distributions must sum to 1.0
   Solution: Check probability distributions in experiment_config.py
   ```

3. **Memory Issues with Large Experiments**
   ```
   Solution: Reduce NUM_PARTICIPANTS or enable garbage collection
   ```

### Performance Optimization

- **Disable LLM feedback**: Set `ENABLE_LLM_FEEDBACK = False` for faster testing
- **Reduce participants**: Use smaller numbers for development
- **Batch processing**: Process participants in smaller batches
- **Memory management**: Clear data between batches if needed

## Future Enhancements

### Planned Features
- **Multi-modal feedback**: Image-based menu selection simulation
- **Advanced learning models**: Reinforcement learning for participant adaptation
- **Real-time analysis**: Live experiment monitoring and analysis
- **Export formats**: CSV, Excel, and statistical software formats
- **Web interface**: Browser-based experiment management

### Research Applications
- **A/B testing**: Compare different recommendation algorithms
- **Cultural studies**: Analyze cross-cultural food preferences
- **Accessibility research**: Test interface accessibility features
- **Personalization studies**: Evaluate recommendation personalization strategies

## Contributing

To contribute to this system:

1. **Fork the repository**
2. **Create a feature branch**
3. **Add tests** for new functionality
4. **Update documentation** for any changes
5. **Submit a pull request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include docstrings for all classes and methods
- Write unit tests for new features
- Update configuration validation for new parameters

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this system in your research, please cite:

```bibtex
@software{adaptive_participant_system,
  title={Adaptive Artificial Participant System for Food Ordering Experiments},
  author={Your Name},
  year={2024},
  url={https://github.com/your-repo/adaptive-participant-system}
}
```

## Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Contact the development team
- Check the troubleshooting section above

---

**Note**: This system is designed for research purposes and should be used in accordance with ethical guidelines for human-subject research simulation.