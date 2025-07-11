# Automated Human Experiment Simulator

## Overview

This system simulates 50 realistic human participants performing a controlled experiment to test the effectiveness of AI agents in food ordering interfaces. The experiment compares two phases:

- **Phase A (Baseline)**: Standard food ordering interface without AI agents
- **Phase B (Agent-Enhanced)**: Food ordering interface with AI agent assistance

## Features

### 🎯 Realistic Human Simulation
- **50 unique participants** with diverse demographics
- **Realistic decision-making patterns** based on age, occupation, and tech-savviness
- **Dietary preferences and allergies** that affect menu choices
- **Variable attention spans and decision speeds**
- **Unbiased experimental design** with random phase assignment

### 🤖 AI Agent Testing
- **Context Intelligence Agent**: Analyzes user context and provides situational recommendations
- **Preference Learning Agent**: Learns from user selections and provides personalized suggestions
- **Preparation Time Agent**: Optimizes order preparation time and queue management
- **Comprehensive agent interaction tracking** and feedback analysis

### 📊 Comprehensive Data Collection
- **NASA-TLX scores** for cognitive workload assessment
- **System Usability Scale (SUS)** for interface evaluation
- **Custom satisfaction surveys** for specific aspects
- **Detailed interaction logs** with timing and error tracking
- **Agent recommendation acceptance rates** and feedback

### 🔬 Experimental Design
- **Controlled comparison** between baseline and agent-enhanced interfaces
- **Balanced participant distribution** across phases
- **Realistic task scenarios** with specific success criteria
- **Quality assurance measures** to prevent bias and ensure reliability

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements_experiment.txt
   ```

2. **Ensure the backend server is running**:
   ```bash
   python simple_server.py
   ```

3. **Verify server is accessible** at `http://localhost:8000`

## Usage

### Quick Start

Run the complete experiment simulation:

```bash
cd removed
python automated_human_experiment_simulator.py
```

### Configuration

The experiment parameters are defined in `experiment_config.json`:

- **Participant demographics** and behavioral characteristics
- **Task specifications** and success criteria
- **Agent testing scenarios** and expected behaviors
- **Measurement instruments** and data collection parameters
- **Experimental hypotheses** and quality assurance measures

### Customization

You can modify the experiment by editing the configuration file:

```json
{
  "participant_configuration": {
    "total_participants": 50,
    "phase_distribution": {
      "phase_a": 25,
      "phase_b": 25
    }
  }
}
```

## Experimental Tasks

The experiment consists of 12 specific tasks:

1. **Customer Identification** - Enter phone number and load preferences
2. **Dietary Preferences Setup** - Select restrictions and allergies
3. **Activity Context Selection** - Choose current activity for recommendations
4. **Protein Selection** - Choose proteins with portion sizes
5. **Base Selection** - Choose base type and specific option
6. **Sauce Selection** - Choose sauces with portion sizes
7. **Vegetable Selection** - Select multiple vegetables with portions
8. **Garnish Selection** - Select garnishes with portions
9. **Dish Naming** - Generate or select dish name
10. **Agent Recommendations** (Phase B only) - Review AI agent suggestions
11. **Order Review** - Review complete order with pricing
12. **Assessment Completion** - Complete measurement questionnaires

## AI Agent Testing

### Context Intelligence Agent
- **Purpose**: Analyze user context and provide situational recommendations
- **Test Scenarios**: Dietary conflicts, allergy warnings, activity-based suggestions
- **Expected Behaviors**: Detect incompatibilities, suggest alternatives, provide context-aware recommendations

### Preference Learning Agent
- **Purpose**: Learn from user selections and provide personalized recommendations
- **Test Scenarios**: Previous order analysis, pattern recognition, personalized suggestions
- **Expected Behaviors**: Remember choices, identify patterns, suggest similar items

### Preparation Time Agent
- **Purpose**: Optimize order preparation time and queue management
- **Test Scenarios**: Queue analysis, time estimation, refreshment suggestions
- **Expected Behaviors**: Calculate accurate times, suggest optimizations, recommend refreshments

## Data Collection

### Timing Metrics
- Step completion times
- Total experiment duration
- Decision-making time
- Agent interaction time

### Interaction Metrics
- Selections made
- Errors committed
- Agent recommendations accepted
- Refreshment purchases

### Quality Metrics
- Task completion rate
- Error rate
- Satisfaction scores
- Usability scores

### Agent-Specific Metrics
- Recommendation accuracy
- Acceptance rate
- User feedback
- Interaction success rate

## Output Files

The system generates comprehensive output files:

### Individual Data
- `participant_P001.json` - Complete data for each participant
- Includes demographics, interaction logs, measurement scores, and agent interactions

### Aggregate Data
- `experiment_results.json` - Comprehensive statistical summaries
- `participant_demographics.csv` - Demographic analysis
- `measurement_scores.csv` - Assessment scores for analysis

### Analysis Reports
- `detailed_analysis.md` - Detailed findings and recommendations
- Statistical analysis and hypothesis testing results

## Experimental Hypotheses

The experiment tests four main hypotheses:

1. **H1**: AI agent-enhanced interfaces will improve user satisfaction
2. **H2**: AI agents will reduce task completion time
3. **H3**: Agent recommendations will be accepted at >40% rate
4. **H4**: Users will report lower cognitive workload with agents

## Quality Assurance

### Data Validation
- Participant ID uniqueness
- Complete data collection
- Realistic timing patterns
- Consistent demographic distribution

### Bias Prevention
- Random phase assignment
- Balanced demographic distribution
- Unbiased task presentation
- Neutral measurement instruments

### Reliability Checks
- Consistent decision patterns
- Realistic interaction timing
- Valid measurement scores
- Logical task progression

## Analysis and Results

### Statistical Analysis
The system performs comprehensive statistical analysis:

- **Descriptive statistics** for all metrics
- **Phase comparison** using t-tests and effect sizes
- **Demographic analysis** to identify patterns
- **Agent effectiveness** evaluation

### Key Metrics
- **Completion time** comparison between phases
- **Satisfaction scores** and usability ratings
- **Agent acceptance rates** and feedback
- **Cognitive workload** assessment

### Visualization
- Demographic distributions
- Performance comparisons
- Agent interaction patterns
- Satisfaction trends

## Troubleshooting

### Common Issues

1. **Server Connection Error**:
   - Ensure `simple_server.py` is running on port 8000
   - Check firewall settings
   - Verify network connectivity

2. **Data Collection Errors**:
   - Check file permissions in `removed/experiment_results/`
   - Ensure sufficient disk space
   - Verify JSON configuration is valid

3. **Participant Generation Issues**:
   - Check random seed consistency
   - Verify demographic parameters
   - Ensure balanced phase distribution

### Debug Mode

Enable detailed logging by modifying the logging level:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Research Applications

This system is designed for:

- **Human-Computer Interaction research**
- **AI agent effectiveness evaluation**
- **User experience optimization**
- **Interface design validation**
- **Cognitive workload assessment**

## Publication Support

The system generates data suitable for:

- **Academic publications** in HCI journals
- **Conference presentations** with statistical rigor
- **Industry reports** on AI agent effectiveness
- **Design recommendations** for food ordering systems

## Contributing

To extend the experiment system:

1. **Add new measurement instruments** in the configuration
2. **Implement additional agent types** in the simulator
3. **Create new analysis methods** for specific research questions
4. **Enhance visualization capabilities** for better insights

## License

This experiment system is designed for research purposes and should be used in accordance with ethical research guidelines.

## Contact

For questions about the experiment system or research applications, please refer to the main project documentation.