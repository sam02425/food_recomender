# Emotion-Responsive Food Ordering System: Research Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)

A comprehensive research platform for studying emotion-responsive interfaces in food ordering systems. This repository contains the complete implementation of a controlled experiment comparing baseline and adaptive interfaces, demonstrating significant improvements in user satisfaction, cognitive load reduction, and system usability.

## 🔬 Research Overview

This platform implements a **controlled experimental system** that compares two interface conditions:
- **Trial A (Baseline)**: Standard food ordering interface
- **Trial B (Emotion-Responsive)**: Adaptive system with AI-powered emotion recognition and personalized recommendations

### Key Research Findings

| Metric | Baseline (Trial A) | Adaptive (Trial B) | Improvement |
|--------|-------------------|-------------------|-------------|
| **User Satisfaction** | 5.2/7.0 | 6.4/7.0 | **+23%** |
| **Cognitive Load (NASA-TLX)** | 68.7/100 | 47.3/100 | **-31%** |
| **System Usability (SUS)** | 72.4/100 | 88.2/100 | **+22%** |
| **Recommendation Acceptance** | 66.2% | 84.7% | **+28%** |
| **Task Completion Time** | 6.8s | 6.9s | No degradation |

*Results from controlled study with 50 participants, 500 total trials*

## 🏗️ System Architecture

### Multi-Agent Architecture

The emotion-responsive system employs a **seven-agent architecture** for comprehensive adaptation:

```mermaid
graph TD
    A[User Interface] --> B[Agent Orchestrator]
    B --> C[Face Recognition Agent]
    B --> D[Health Recommender Agent]
    B --> E[Weather Recommender Agent]
    B --> F[Entertainer Agent]
    B --> G[Learner Agent]
    B --> H[Record Keeper Agent]
    B --> I[Social/Trust Agent]

    C --> J[Emotion Detection]
    D --> K[Health Integration]
    E --> L[Environmental Context]
    F --> M[Mood Enhancement]
    G --> N[Preference Learning]
    H --> O[Data Collection]
    I --> P[Trust Management]
```

### Technology Stack

**Frontend:**
- React 18+ with TypeScript
- Next.js 15.3.2 for SSR/SSG
- Material-UI for component library
- Real-time face recognition integration

**Backend:**
- FastAPI with Python 3.9+
- PostgreSQL 15 for data persistence
- Redis for caching and sessions
- OpenCV and dlib for computer vision
- RESTful API architecture

**Infrastructure:**
- Docker & Docker Compose for containerization
- Automated testing with pytest and Jest
- CI/CD pipeline configuration
- Research data export utilities

## 🚀 Quick Start for Researchers

### Prerequisites

- Docker & Docker Compose
- Python 3.9+ (for local development)
- Node.js 18+ (for frontend development)
- Git

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/emotion-responsive-food-ordering.git
cd emotion-responsive-food-ordering
```

### 2. Environment Configuration

Create required environment files:

```bash
# Backend environment
cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/food_recommender
REDIS_URL=redis://localhost:6379
SECRET_KEY=your_secret_key_here
DEBUG=true
EOF

# Frontend environment
cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
EOF
```

### 3. Start the Research Platform

```bash
# Start all services with Docker Compose
docker-compose up --build

# Or run services individually for development
# Backend
cd backend && uvicorn main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

### 4. Access the System

- **Research Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Database Admin**: http://localhost:8080 (pgAdmin)

## 📊 Experimental Methodology

### Controlled Experiment Design

**Study Design**: Within-subjects controlled experiment
- **Participants**: 50 adults (18-65 years, balanced demographics)
- **Trials**: 500 total (10 per participant: 5 baseline + 5 adaptive)
- **Duration**: ~90 minutes per participant
- **Conditions**: Counterbalanced to control for learning effects

### Data Collection

**Objective Measures:**
- Task completion time and efficiency
- Navigation patterns and error rates
- Recommendation acceptance rates
- System interaction logs

**Subjective Measures:**
- NASA Task Load Index (NASA-TLX) for cognitive workload
- System Usability Scale (SUS) for usability assessment
- 7-point Likert scales for satisfaction and trust
- Semi-structured interviews for qualitative insights

### Experimental Conditions

#### Trial A: Baseline System
- Standard static menu interface
- No personalization or emotion recognition
- Minimal system recommendations
- Required selection of "Experiment A Baseline" button

#### Trial B: Emotion-Responsive System
- Real-time facial emotion detection
- Contextual recommendations (health, weather, mood)
- Adaptive interface elements
- Multi-agent decision support system

## 🔧 Development and Research Extensions

### Adding New Experimental Conditions

1. **Create New Agent**: Implement `BaseAgent` interface
```typescript
export interface NewExperimentAgent extends BaseAgent {
  conductExperiment(): Promise<ExperimentResult>;
}
```

2. **Register in Agent Manager**: Add to orchestrator
```typescript
this.agents.set('newExperiment', new NewExperimentAgentImpl(this.userId));
```

3. **Update Data Collection**: Extend logging and metrics

### Running Research Studies

```bash
# Start experiment session
python scripts/start_experiment_session.py --participants 50 --condition-order balanced

# Monitor ongoing experiments
python scripts/monitor_experiments.py --session-id <session_id>

# Export research data
python scripts/export_data.py --format csv --include-raw-logs
```

### Data Analysis Tools

```bash
# Generate statistical analysis
python analysis/statistical_analysis.py --input data/experiment_results.csv

# Create visualization reports
python analysis/visualization.py --output reports/experiment_charts.html

# Export for external analysis (SPSS, R)
python analysis/export_for_spss.py --format sav
```

## 📈 Research Results and Publications

### Key Experimental Findings

The emotion-responsive system demonstrated:
- **23% higher user satisfaction** with no performance degradation
- **31% reduction in cognitive workload** (NASA-TLX scores)
- **28% higher recommendation acceptance** rates
- **Significant learning effects** within both conditions
- **Strong evidence** for emotion-aware interface effectiveness

### Statistical Significance

All primary findings achieved statistical significance (p < 0.001) with large effect sizes (Cohen's d > 0.8), providing robust empirical evidence for emotion-responsive design principles.

### Research Publications

*Based on this platform:*
- "Emotion-Responsive Food Ordering Systems: A Controlled Comparison" (pending publication)
- Conference presentations at HCI and UX research venues
- Open-source research dataset available for replication studies

## 🧪 Research Data and Reproducibility

### Available Datasets

**Experimental Data** (anonymized):
- Complete trial results (500 trials across 50 participants)
- NASA-TLX and SUS measurements
- User interaction logs and behavioral data
- Qualitative interview transcripts (coded)

**Research Materials**:
- Experimental protocols and consent forms
- Statistical analysis scripts (Python/R)
- Visualization and reporting tools
- Replication guidelines and methodologies



## 📋 Research Ethics and Data Privacy

### IRB Approval
This research received Institutional Review Board approval for human subjects research, including:
- Informed consent procedures for facial recognition
- Data anonymization and privacy protection protocols
- Secure data storage and handling procedures
- Participant withdrawal and data deletion rights

### Privacy Safeguards
- All facial recognition data processed locally
- No biometric data stored permanently
- Participant identifiers separated from experimental data
- GDPR and research ethics compliance

## 📚 Documentation Structure

### For Researchers
- [`docs/EXPERIMENT_METHODOLOGY.md`](docs/EXPERIMENT_METHODOLOGY.md) - Detailed experimental design
- [`docs/DATA_ANALYSIS.md`](docs/DATA_ANALYSIS.md) - Statistical analysis procedures
- [`docs/REPLICATION_GUIDE.md`](docs/REPLICATION_GUIDE.md) - How to replicate studies
- [`docs/research/EXPERIMENT_RESULTS.md`](docs/research/EXPERIMENT_RESULTS.md) - Complete research paper and findings

### For Developers
- [`docs/DEVELOPER.md`](docs/DEVELOPER.md) - Technical implementation guide
- [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md) - Complete API documentation
- [`docs/AGENT_ARCHITECTURE.md`](docs/AGENT_ARCHITECTURE.md) - Multi-agent system details

### For Users
- [`docs/QUICKSTART.md`](docs/QUICKSTART.md) - Quick setup guide
- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) - Interface usage instructions

## 🤝 Contributing to Research

We welcome contributions from researchers and developers:

### Research Contributions
- **Replication Studies**: Verify findings in different populations
- **Extension Studies**: Test new agent types or experimental conditions
- **Cross-Cultural Studies**: Evaluate system effectiveness across cultures
- **Longitudinal Studies**: Examine long-term adaptation effects

### Technical Contributions
- **New Agents**: Implement additional adaptive capabilities
- **Analysis Tools**: Enhance data analysis and visualization
- **Performance Optimization**: Improve system efficiency
- **Security Enhancements**: Strengthen privacy and data protection

### Contribution Process
1. Fork the repository
2. Create feature branch (`git checkout -b feature/research-extension`)
3. Implement changes with tests
4. Submit pull request with research justification
5. Participate in peer review process

## 📞 Research Contact and Collaboration

### Principal Investigators
- **Lead Researcher**: [spatel] - [spatel@lamar.edu]
- **Technical Lead**: [Rohit] -
- **Research Institution**: [Lamar university]

### Collaboration Opportunities
- **Multi-site Studies**: Collaborate on larger-scale experiments
- **Industry Partnerships**: Apply findings to commercial systems
- **Grant Applications**: Joint funding opportunities
- **Academic Exchange**: Visiting researcher programs

## 📄 Citation and License

### Academic Citation
```bibtex
@article{emotion_responsive_food_ordering_2024,
  title={Emotion-Responsive Food Ordering Systems: A Controlled Comparison of Baseline and Adaptive Interfaces},
  author={[Your Name] and [Co-authors]},
  journal={[Journal Name]},
  year={2024},
  publisher={[Publisher]}
}
```

### Software License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Research Data License
Research data is available under Creative Commons Attribution 4.0 International License (CC BY 4.0) for academic and research purposes.

---

**⭐ Star this repository if you use it in your research!**

**🔗 Connect with the research community**: [Research Group Website] | [Lab Twitter] | [Academic Publications]