# Adaptive Artificial Participant System

A sophisticated system for simulating realistic human participants in food ordering experiments, with intelligent learning and adaptation capabilities.

## Features

- **Realistic Participant Profiles**: Generates diverse participants with varying demographics, dietary restrictions, and personality traits
- **Adaptive Learning**: Participants learn and adapt from their experiences across trials
- **Multi-API Support**: Supports both OpenAI ChatGPT and GROQ APIs for intelligent feedback
- **Comprehensive Metrics**: Tracks satisfaction, task completion time, dietary compliance, privacy concerns, and more
- **Statistical Analysis**: Performs detailed statistical analysis with effect sizes and significance testing
- **Realistic Failures**: Models real-world system failures, dietary restriction violations, and cultural mismatches

## API Integration

### OpenAI ChatGPT API (Recommended)

The system now primarily uses OpenAI's ChatGPT API for generating realistic participant feedback:

```bash
export OPENAI_API_KEY='your-openai-api-key-here'
```

**Models Supported:**
- `gpt-3.5-turbo` (default, cost-effective)
- `gpt-4` (higher quality, more expensive)
- `gpt-4-turbo` (latest, best performance)

### GROQ API (Legacy Support)

For users with GROQ API access:

```bash
export GROQ_API_KEY='your-groq-api-key-here'
```

**Models Supported:**
- `llama3-8b-8192` (default)
- `mixtral-8x7b-32768` (alternative)

### Fallback Mode

If no API key is provided, the system runs without LLM feedback using pre-defined templates.

## Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd human_experiments_data
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up API keys:**
```bash
# For OpenAI (recommended)
export OPENAI_API_KEY='your-openai-api-key-here'

# For GROQ (alternative)
export GROQ_API_KEY='your-groq-api-key-here'
```

## Configuration

Edit `experiment_config.py` to customize experiment parameters:

```python
# Experiment settings
NUM_PARTICIPANTS = 50
TRIALS_PER_PARTICIPANT = 10
BASELINE_TRIALS = 5
ADAPTIVE_TRIALS = 5

# API settings
OPENAI_MODEL = "gpt-3.5-turbo"  # or "gpt-4", "gpt-4-turbo"
GROQ_MODEL = "llama3-8b-8192"

# LLM feedback settings
ENABLE_LLM_FEEDBACK = True
LLM_FEEDBACK_FREQUENCY = 3  # Every 3rd trial
```

## Usage

### Quick Start

1. **Test API integration:**
```bash
python test_openai_api.py
```

2. **Run a small experiment (3 participants):**
```bash
python test_system.py
```

3. **Run full experiment:**
```bash
python run_experiment.py
```

### Custom Experiments

```python
from adaptive_participant_system import AdaptiveParticipantSystem
from experiment_analyzer import ExperimentAnalyzer

# Initialize system with OpenAI API
system = AdaptiveParticipantSystem(
    openai_api_key="your-api-key",
    num_participants=20,
    trials_per_participant=8
)

# Generate participants
system.generate_participants()

# Run experiment
await system.run_experiment()

# Analyze results
analyzer = ExperimentAnalyzer(system.trial_data, system.participants)
results = analyzer.analyze()
```

## Output Files

The system generates several output files:

- `experiment_results_YYYYMMDD_HHMMSS.json`: Raw trial data and statistics
- `experiment_report_YYYYMMDD_HHMMSS.md`: Detailed analysis report
- `participant_profiles.json`: Generated participant profiles
- `system_performance.json`: System performance metrics

## Key Metrics

### Primary Metrics
- **Satisfaction Score**: 1-5 scale measuring user satisfaction
- **Task Completion Time**: Time in seconds to complete ordering task
- **Recommendation Acceptance Rate**: Percentage of recommendations accepted
- **Dietary Compliance**: Whether dietary restrictions were properly followed

### Secondary Metrics
- **Privacy Concerns**: Participant privacy-related issues
- **Cultural Mismatches**: Cultural appropriateness of recommendations
- **System Failures**: Technical failures and errors
- **Learning Effects**: Improvement over trials

### Statistical Analysis
- **Effect Sizes**: Cohen's d for practical significance
- **P-values**: Statistical significance testing
- **Confidence Intervals**: 95% confidence intervals for estimates
- **Power Analysis**: Statistical power calculations

## API Troubleshooting

### OpenAI API Issues

1. **Invalid API Key:**
```bash
# Check your API key
echo $OPENAI_API_KEY

# Regenerate API key at: https://platform.openai.com/api-keys
```

2. **Rate Limiting:**
- Reduce `LLM_FEEDBACK_FREQUENCY` in config
- Use `gpt-3.5-turbo` instead of `gpt-4`
- Add delays between API calls

3. **Authentication Errors:**
```bash
# Test API connection
python test_openai_api.py
```

### GROQ API Issues

1. **401 Unauthorized:**
- Verify API key at: https://console.groq.com/
- Check account status and billing

2. **Model Not Found:**
- Use supported models: `llama3-8b-8192`, `mixtral-8x7b-32768`

## Example Results

```
EXPERIMENT SUMMARY
============================================================
Baseline Satisfaction: 3.45 ± 0.67
Adaptive Satisfaction: 4.12 ± 0.58
Improvement: +19.4%
Statistical Significance: p = 0.0023
Effect Size: 0.456

✅ Statistically significant improvement in satisfaction

Baseline Task Time: 78.3s ± 12.4s
Adaptive Task Time: 65.1s ± 10.8s
Improvement: -16.9%

✅ Statistically significant improvement in task completion time

System Failures: 8.2%
Dietary Compliance: 94.7%
Privacy Concerns: 12.3%
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the example outputs
3. Test with a small experiment first
4. Open an issue with detailed error information