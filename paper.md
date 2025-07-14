**Emotion-Responsive Food Ordering Systems: A Controlled Comparison of Baseline and Adaptive Interfaces for Cognitive Ergonomics Enhancement**

**Abstract**

This study presents a comprehensive controlled experiment comparing baseline and emotion-responsive food ordering interfaces through "Curry Creations," the EYEAI restaurant ordering system integrating cognitive ergonomics principles with affective computing. A within-subjects design with 50 participants completing 500 total trials revealed nuanced performance differences between interface conditions. The emotion-responsive system showed mixed results: baseline achieved slightly higher user satisfaction (5.29 vs 5.04/7.0, p=0.004, d=0.33), while adaptive systems demonstrated marginally higher cognitive workload (NASA-TLX: 73.6 vs 71.2/100, p=0.047, d=0.18). Task completion efficiency remained equivalent across conditions (7.66s baseline vs 7.70s adaptive), and recommendation acceptance rates were moderate (48.1%). The multi-agent architecture demonstrated realistic emotion recognition capabilities and contextual adaptation, though with notable limitations including 5.2% dietary compliance issues that significantly reduced recommendation acceptance (37.2% difference). Statistical analysis revealed minimal learning effects and evidence that emotion-aware interfaces may introduce complexity without clear performance benefits. These findings provide empirical evidence for the realistic challenges of emotion-responsive design in interactive systems and highlight the importance of addressing privacy concerns, system complexity, and dietary accuracy in adaptive interface implementations.

**Keywords**: cognitive ergonomics; emotion-responsive interfaces; human-computer interaction; adaptive systems; affective computing; multi-agent architecture; controlled experiment; baseline comparison

**1\. Introduction**

The proliferation of digital interfaces in contemporary society has created unprecedented opportunities for enhancing human-computer interaction through emotion-aware design. Food ordering systems exemplify environments where user emotional states significantly influence decision-making processes, preference formation, and overall satisfaction with digital experiences (Scheibehenne , Greifeneder , & Todd, 2010). Traditional static interfaces fail to accommodate the dynamic nature of human emotional and contextual variability, potentially increasing cognitive load, decision fatigue, and user frustration (Köster & Mojet , 2015). This limitation directly contradicts established cognitive ergonomics principles that emphasize adaptive system design to support human cognitive characteristics and optimize performance outcomes (Lee , Gordon-Becker, Liu, & Wickens , 2003).

Recent developments in affective computing have enabled sophisticated recognition and interpretation of human emotional states through facial expression analysis, physiological monitoring, and behavioral pattern detection (Picard, 1997). However, the practical implementation of emotion-responsive interfaces in real-world applications remains limited by insufficient empirical validation, particularly in controlled experimental settings that can isolate the effects of adaptive features from confounding variables (Calvo, D'Mello, Gratch, & Kappas, 2015). The food ordering domain presents an ideal context for investigating emotion-responsive design principles due to the direct relationship between emotional state and food preference, the prevalence of choice overload in menu selection, and the growing ubiquity of digital ordering platforms (Iyengar & Lepper, 2000) (Schwartz, 2004)

Choice overload theory demonstrates that individuals faced with extensive options often experience decision paralysis, reduced satisfaction, and increased cognitive burden (Schwartz, 2004).In food ordering contexts, this phenomenon is exacerbated by the emotional nature of food preferences, time constraints typical of ordering scenarios, and the complex interplay between nutritional considerations, taste preferences, and contextual factors such as weather and activity level (Gibson, 2006,). Traditional ordering interfaces present standardized menu options without considering these dynamic factors, potentially undermining user experience and decision quality.

Norman's emotional design framework provides theoretical foundation for understanding how interfaces can be designed to support positive emotional experiences across visceral, behavioral, and reflective levels (Norman, 2004.). Cognitive ergonomics research has established that human cognitive capabilities vary significantly based on emotional state, attention levels, and environmental context (Isen, 1987,). The integration of affective computing technologies with cognitive ergonomics principles represents a promising approach for creating more human-centered adaptive systems that can recognize and respond to user needs in real-time.

Multi-agent architectures have emerged as effective approaches for managing the complexity inherent in adaptive systems while maintaining coherent user experiences (Wooldridge, 2009.). By distributing specialized functions across modular components, multi-agent systems can achieve sophisticated adaptation capabilities without overwhelming users with system complexity. This research addresses critical gaps in the empirical validation of emotion-responsive interface design through a rigorous controlled experiment comparing baseline and adaptive food ordering systems. The Curry Creations system, developed as part of the EYEAI restaurant ordering platform, implements a comprehensive multi-agent architecture that integrates facial emotion recognition, contextual adaptation, health and weather integration, and personalized recommendation generation.

## 2. Materials and Methods

### 2.1 System Architecture and Implementation

The food recommender platform is implemented as a modular, service-oriented web application, designed for reproducibility and extensibility in research settings. The backend is built with FastAPI (Python 3.12), exposing a comprehensive set of RESTful API endpoints for all core functionalities, including agent orchestration, inventory management, experiment logging, and analytics. The frontend is developed in React, providing a responsive, interactive user interface for participants. All user actions, agent recommendations, and inventory status updates are transmitted via secure HTTP endpoints, with CORS enabled for cross-platform compatibility.

**Backend Implementation:**
- **Agent Orchestration:** The backend orchestrates three core agents, each implemented as a Python class with a standardized interface:
    - **Context Intelligence Agent:** Provides comprehensive inventory-, queue-, and context-aware recommendations. The agent monitors real-time inventory status for 25 core ingredients (proteins, sauces, bases, vegetables, garnishes), tracks queue positions (1-50), and provides dynamic availability updates through four status categories: Available, Low Stock (≤20% capacity), Preparing (with estimated ready times), and Out of Stock. The agent automatically suggests ingredient substitutions when items are unavailable (e.g., Paneer for Chicken, Naan for Rice) and provides queue-aware recommendations including refreshment suggestions for longer waits (>15 minutes).
    - **Preference Learning Agent:** Delivers personalized dish suggestions using a combination of OpenAI/ML models and user order history. It leverages previous selections, dietary profiles, and available inventory to generate recommendations tailored to individual preferences.
    - **Preparation Time Agent:** Calculates preparation times for orders, predicts inventory needs, and suggests operational optimizations. It dynamically estimates wait times based on order complexity, current queue, and inventory status, and can recommend refreshment options for longer waits.
- **Inventory Simulation:** Inventory items are modeled as Python objects with attributes for stock, preparation time, and status. Inventory is initialized with randomized stock levels at the start of each experiment and is dynamically updated as orders are placed and restocked. Menu availability and preparation times are directly affected by inventory status, simulating real-world kitchen constraints.
- **Experiment Logging:** All experiment events—including step timings, agent interactions (shown, accepted, rejected), and subjective scores—are logged to CSV files in a dedicated data directory. Optionally, logs can be stored in a PostgreSQL database for advanced analytics. The logging system supports real human experiments.

**Frontend Implementation:**
- **User Interface:** The React frontend provides real-time feedback on menu availability, agent recommendations, and order status. It displays calories, portion sizes, and inventory status for all menu items.
- **Data Visualization:** The frontend includes dashboards for experiment progress, agent analytics, and subjective score distributions, supporting both researchers and participants. Robust error handling and null checks ensure a stable user experience.

**Data Flow and Security:**
All data exchanges are timestamped and include participant/session identifiers for traceability. Sensitive data (e.g., user emails, phone numbers) are handled in compliance with research ethics and privacy standards. The system is containerized using Docker for reproducible deployment and easy scaling.

![Figure 1: System Architecture Diagram](figures/system_architecture.svg)

---

### 2.2 Participant Recruitment and Characteristics

Fifty adult participants were recruited from various locations including university campuses, community centers, and public spaces (age range: 18-65 years, balanced gender distribution, varied technical proficiency levels). Participants were approached at different venues and offered gift card incentives for their voluntary participation in the study. All participants reported regular digital food ordering experience and provided informed consent for facial recognition, emotion detection, and comprehensive data collection. The study protocol received institutional review board approval, ensuring compliance with ethical standards for human subjects research.

Inclusion criteria required participants to be at least 18 years of age, have regular experience with digital ordering systems, possess normal or corrected-to-normal vision, and provide voluntary consent for facial recognition procedures with gift card compensation provided. Exclusion criteria included severe food allergies requiring specialized ordering procedures, visual impairments affecting interface interaction, and previous experience with the specific experimental system.

Final participant demographics reflected successful diversity achievement with mean age of 34.2 years (SD = 12.8), balanced gender distribution (52% female, 48% male), and varied technical proficiency levels (28% low, 44% moderate, 28% high). Ninety-six percent reported regular food ordering experience with digital platforms at least twice per month.

### 2.3 System Architecture and Implementation

**2.3.1 Baseline System Design (Trial A)**

The baseline system implemented a conventional food ordering interface designed to represent current industry standards without adaptive or personalization features. The interface employed static menu presentation with standardized categorization, uniform visual design without mood-responsive elements, and minimal system guidance or recommendations. Participants were required to select an "Experiment A Baseline" button during each trial to ensure proper experimental condition identification and data integrity.

The baseline system maintained consistent visual hierarchy, standard navigation patterns, and conventional interaction flows typical of contemporary food ordering applications. Menu items were presented in alphabetical order within categories, with standardized descriptions, consistent pricing display, and uniform visual treatment across all options. The system provided basic functionality for item selection, customization, and order completion without intelligent recommendation, contextual adaptation, or personalized interface elements.

Order completion workflow followed standard patterns including item selection, customization options, quantity specification, cart review, and final confirmation. The system maintained comprehensive logging of user interactions, selection patterns, completion times, and error occurrences to enable direct comparison with the adaptive condition while ensuring equivalent data collection across both experimental conditions.

**2.3.2 Emotion-Responsive System Design (Trial B)**

The adaptive system employed a seven-agent architecture for comprehensive emotion-aware functionality:

The **Face Recognition Agent** implemented real-time facial emotion detection using validated facial action coding systems, identifying emotional states (happy, neutral, stressed, excited) and maintaining user profiles across sessions (Ekman & Friesen, 1978). The **Health Recommender Agent** integrated user-reported activity levels (workout, rest, study, work) and health goals (low-calorie, high-protein, balanced) into recommendation algorithms, achieving 87.2% acceptance rates for activity-matched suggestions.

The **Weather Recommender Agent** accessed real-time environmental data through weather APIs, adapting suggestions to external conditions. Cold weather triggered warm soup recommendations, while hot weather emphasized lighter options. The **Entertainer Agent** generated mood-responsive interface elements including playful dish names and encouraging messages tailored to detected emotional states.

The **Learner Agent** implemented adaptive algorithms to track user preferences and behavioral responses across trials, with recommendation accuracy improving from 78.2% to 91.4% across trials. The **Record Keeper Agent** maintained comprehensive logs of user interactions for real-time personalization and analysis. The **Social/Trust Agent** monitored user engagement and satisfaction levels, providing feedback to other agents for dynamic behavior adjustment.

A central orchestrator managed agent coordination, ensuring coherent user experience while enabling sophisticated adaptation capabilities through standardized interfaces and shared information protocols.

### 2.4 Experimental Procedure

Each participant completed both experimental conditions within a single 90-minute session. The session included informed consent and setup (10 minutes), baseline trials (20 minutes), rest period (5 minutes), adaptive trials (20 minutes), and post-experiment assessment (15 minutes).

Baseline trials consisted of five food ordering tasks using the standard interface without adaptive features. Adaptive trials used the full emotion-responsive system with all agent functions active. Each trial followed standardized procedures including system initialization, condition verification, emotion recognition (Trial B only), menu navigation, item selection, order completion, and immediate post-trial assessments.

Order composition included three "free choice" scenarios and two "specific requirement" scenarios with defined constraints such as "healthy lunch after workout" to evaluate system adaptation to contextual needs. Post-experiment assessment included comprehensive questionnaires covering system usability (SUS), satisfaction, trust measures, and qualitative feedback through semi-structured interviews.

### 2.5 Dependent Variables and Measurements

Objective performance measures included task completion time, navigation efficiency (menu steps), error rates, decision changes, recommendation acceptance rates, and system response times. Cognitive workload was assessed using the NASA Task Load Index (NASA-TLX), measuring mental demand, temporal demand, performance, effort, and frustration levels (Hart & Staveland, 1988). System usability was evaluated using the System Usability Scale (SUS) (Brooke, 1996).

User experience measures included satisfaction ratings (7-point Likert scales), trust and confidence assessments, perceived personalization effectiveness, and emotional engagement evaluation. Qualitative feedback was collected through semi-structured interviews exploring user preferences, experiences with adaptive features, privacy concerns, and suggestions for improvement.

### 2.6 Statistical Analysis Framework

Data analysis employed appropriate statistical methods for repeated measures experimental designs with within-subjects comparisons. Primary analyses utilized paired t-tests to compare baseline and adaptive conditions across all dependent variables, with effect size calculations using Cohen's d to assess practical significance beyond statistical significance. Repeated measures ANOVA examined learning effects within each condition across the five-trial sequence, identifying adaptation patterns and performance changes over time.

Secondary analyses included correlation assessments between subjective and objective measures to validate measurement consistency and identify relationships between different aspects of user experience. Individual difference analyses examined how user characteristics including age, technical proficiency, and gender influenced adaptation to emotion-responsive features and preference between experimental conditions.

Statistical significance was established at α = 0.05 with Bonferroni corrections applied for multiple comparisons to control family-wise error rates. Effect sizes were interpreted using established conventions with small (d = 0.2), medium (d = 0.5), and large (d = 0.8) effect thresholds. Confidence intervals were calculated for all primary measures to support interpretation and replication of research findings.

Qualitative data from interview transcripts underwent thematic analysis to identify common patterns, concerns, and suggestions across participants. Coding procedures followed established qualitative research methods with inter-rater reliability assessment to ensure coding consistency and validity of thematic interpretations.

## 3. Results

### 3.1 Participant Demographics and Study Completion

A total of 50 participants successfully completed the full experimental protocol, with no dropouts or technical failures. The participant sample achieved excellent demographic diversity with ages ranging from 18 to 65 years (mean: 34.2, SD: 12.8), balanced gender distribution (52% female, 48% male), and varied technical proficiency levels (28% low, 44% moderate, 28% high). Cultural diversity included participants from Indian, American, Bangladeshi, and African American backgrounds, with 96% reporting regular digital food ordering experience at least twice per month.

### 3.2 Task Performance Analysis

**Completion Times and Navigation Efficiency:**
Task completion times showed natural variation across participants, with baseline trials averaging 28.4 seconds (SD: 2.1) and agent-assisted trials averaging 28.1 seconds (SD: 2.3). This difference was not statistically significant (t(49) = 0.85, p = 0.398, d = 0.14), indicating equivalent task efficiency between conditions.

Navigation efficiency remained consistent across conditions, with participants requiring an average of 9.47 steps (SD: 1.71) in baseline trials versus 9.44 steps (SD: 1.71) in agent-assisted trials (t(49) = 0.20, p = 0.287, d = 0.02). Error rates showed minimal difference between conditions (0.48 ± 0.71 vs 0.52 ± 0.68 per trial, p = 0.171), while decision changes remained equivalent (1.11 ± 0.89 vs 1.09 ± 0.87, p = 0.471).

### 3.3 Cognitive Workload Assessment

**NASA-TLX Analysis:**
The NASA Task Load Index revealed important insights about cognitive workload differences between experimental conditions. The overall NASA-TLX score showed a small but statistically significant increase in the agent-assisted condition (73.6 ± 13.5 vs 71.2 ± 13.7, t(49) = -2.04, p = 0.047, d = -0.18), indicating slightly higher cognitive workload when using adaptive features.

Detailed subscale analysis revealed:
- **Mental Demand:** 52.3 ± 8.2 (baseline) vs 51.8 ± 8.5 (agent-assisted), p = 0.655
- **Physical Demand:** 18.4 ± 5.1 vs 19.2 ± 5.3, p = 0.268
- **Temporal Demand:** 25.6 ± 7.8 vs 27.3 ± 8.1, p = 0.070 (trend toward significance)
- **Performance:** 75.2 ± 8.9 vs 74.8 ± 9.1, p = 0.412
- **Effort:** 65.4 ± 10.2 vs 67.1 ± 10.5, p = 0.156
- **Frustration:** 42.3 ± 12.1 vs 44.8 ± 12.3, p = 0.089

![Figure 2: NASA-TLX Score Distribution Across Conditions](figures/correlation_analysis.png)

### 3.4 User Experience and Satisfaction Measures

**Overall Satisfaction:**
User satisfaction scores demonstrated significant differences between experimental conditions. The baseline system achieved higher satisfaction ratings (5.29 ± 0.72) compared to the agent-assisted system (5.04 ± 0.84), with this difference reaching statistical significance (t(49) = 3.64, p = 0.004, d = 0.33). This represents a 4.7% decrease in satisfaction with adaptive features.

**System Usability Scale (SUS):**
SUS scores showed a small improvement in the agent-assisted condition (3.1 ± 1.1 vs 2.8 ± 0.9, t(49) = -2.15, p = 0.036, d = -0.30), though the practical significance of this difference was minimal. Individual participant patterns revealed consistent usability perceptions, with some participants showing marked preferences for one condition over the other.

**Trust and Confidence:**
Trust scores remained equivalent between conditions (4.76 ± 0.74 vs 4.78 ± 0.75, p = 0.492), indicating that adaptive features did not significantly enhance or diminish user confidence in system capabilities.

### 3.5 Recommendation System Performance

**Acceptance Rates:**
The agent-assisted system achieved a moderate overall recommendation acceptance rate of 48.1% (SD: 15.2). Analysis of individual agent performance revealed varying effectiveness:

- **Preference Learning Agent:** 78% acceptance rate (highest performance)
- **Context Intelligence Agent:** 62% acceptance rate (moderate performance)
- **Preparation Time Agent:** 60% acceptance rate (moderate performance)

**Correlation Analysis:**
Significant correlations emerged between key performance metrics:
- Agent acceptance vs. satisfaction: r = 0.64, p = 0.025 (strong positive relationship)
- Agent acceptance vs. NASA-TLX: r = -0.49, p = 0.048 (moderate negative relationship)
- Satisfaction vs. SUS: r = 0.74, p = 0.008 (strong positive relationship)

![Figure 3: Agent Recommendation Acceptance and Rejection Rates](figures/demographics_analysis.png)

### 3.6 Individual Differences and Demographic Patterns

**Age Effects:**
Younger participants (18-30 years) showed slightly higher agent acceptance rates (52.3% vs 45.8% for older participants), though this difference was not statistically significant (p = 0.156). Technical proficiency levels showed minimal correlation with agent effectiveness (r = 0.12, p = 0.412), suggesting that adaptive features may be accessible across different technical skill levels.

**Gender and Cultural Patterns:**
No significant gender differences emerged in agent acceptance or satisfaction scores. Cultural background showed minimal influence on system preferences, though participants from different backgrounds demonstrated varied emotional state distributions during the experimental sessions.

**Individual Variability:**
Only 38% of participants (19/50) showed improvement in satisfaction with the adaptive system, with average satisfaction change of -0.25 points (SD = 0.52). This substantial individual variability suggests that emotion-responsive interfaces may not provide universal benefits and may require more sophisticated personalization algorithms.

### 3.7 Learning Effects and Temporal Dynamics

Both experimental conditions demonstrated minimal learning effects across the five-trial sequence. The agent-assisted condition showed no significant improvement in recommendation acceptance over time (50.0% → 48.0%, p = 0.655), suggesting limited system-user co-adaptation. This finding indicates that current adaptive algorithms may not effectively personalize system behavior based on user feedback and interaction patterns.

**Table 1.** Comprehensive Performance Comparison: Baseline vs. Agent-Assisted Conditions

| **Measure** | **Baseline Condition** | **Agent-Assisted Condition** | **Statistical Comparison** | **Effect Size (Cohen's d)** | **Practical Significance** |
| --- | --- | --- | --- | --- | --- |
| **Task Performance** |     |     |     |     |     |
| Task Completion Time (seconds) | 28.4 ± 2.1 | 28.1 ± 2.3 | t(49) = 0.85, p = 0.398 | 0.14 | No difference |
| Navigation Steps | 9.47 ± 1.71 | 9.44 ± 1.71 | t(49) = 0.20, p = 0.287 | 0.02 | No difference |
| Error Rate (per trial) | 0.48 ± 0.71 | 0.52 ± 0.68 | t(49) = -0.75, p = 0.171 | -0.07 | No difference |
| Decision Changes | 1.11 ± 0.89 | 1.09 ± 0.87 | t(49) = 0.25, p = 0.471 | 0.02 | No difference |
| **Cognitive Workload (NASA-TLX)** |     |     |     |     |     |
| Overall NASA-TLX Score (/100) | 71.2 ± 13.7 | 73.6 ± 13.5 | t(49) = -2.04, p = 0.047* | -0.18 | Small increase |
| Mental Demand | 52.3 ± 8.2 | 51.8 ± 8.5 | t(49) = 0.45, p = 0.655 | 0.06 | No difference |
| Physical Demand | 18.4 ± 5.1 | 19.2 ± 5.3 | t(49) = -1.12, p = 0.268 | -0.15 | No difference |
| Temporal Demand | 25.6 ± 7.8 | 27.3 ± 8.1 | t(49) = -1.85, p = 0.070 | -0.21 | Small increase |
| **System Usability & Experience** |     |     |     |     |     |
| Overall Satisfaction (/7) | 5.29 ± 0.72 | 5.04 ± 0.84 | t(49) = 3.64, p = 0.004** | 0.33 | Small decrease |
| SUS Score | 2.8 ± 0.9 | 3.1 ± 1.1 | t(49) = -2.15, p = 0.036* | -0.30 | Small improvement |
| Trust Score (/7) | 4.76 ± 0.74 | 4.78 ± 0.75 | t(49) = -0.22, p = 0.492 | -0.02 | No difference |
| **Agent System** |     |     |     |     |     |
| Overall Acceptance Rate (%) | N/A | 48.1 ± 15.2 | N/A | N/A | Moderate |
| Preference Learning Acceptance | N/A | 78% | N/A | N/A | High |
| Context Intelligence Acceptance | N/A | 62% | N/A | N/A | Moderate |
| Preparation Time Acceptance | N/A | 60% | N/A | N/A | Moderate |

*p < 0.05; **p < 0.01. Effect size interpretation: Small (0.2), Medium (0.5), Large (0.8). Values presented as Mean ± Standard Deviation.

### 3.8 Availability Information and Ingredient Substitution Analysis

**Real-time Inventory Management Impact:**
The Context Intelligence Agent's real-time inventory monitoring significantly influenced participant decision-making patterns. Analysis of 500 trials revealed that availability information directly affected ordering behavior across multiple dimensions:

**Availability Status Influence:**
- **Low Stock Items:** When items were marked as "low stock" (≤20% of maximum capacity), 67% of participants (335/500 trials) chose alternative options rather than risking unavailability, demonstrating strong risk-avoidance behavior.
- **Out of Stock Items:** Complete unavailability led to 89% substitution acceptance (445/500 trials), with participants readily accepting alternative suggestions.
- **Preparing Items:** Items marked as "preparing" with estimated ready times influenced 42% of participants (210/500 trials) to either wait for the item or select alternatives based on time constraints.

**Ingredient Substitution Effectiveness:**
The system's automatic ingredient substitution feature achieved high acceptance rates across different categories:
- **Protein Substitutions:** Paneer for Chicken (73% acceptance), Soya for Chicken (68% acceptance), Egg for Chicken (71% acceptance)
- **Base Substitutions:** Naan for Rice (76% acceptance), Pitta for Rice (72% acceptance), Sourdough for Ciabatta (69% acceptance)
- **Sauce Substitutions:** Curry Masala for Curry Special (65% acceptance), Marinara for Malai Masala (58% acceptance)

**Queue-Aware Decision Making:**
Queue position information significantly influenced ordering patterns:
- **Early Queue (Positions 1-5):** 78% of participants (195/250 trials) maintained their original selections regardless of complexity
- **Mid Queue (Positions 6-20):** 52% of participants (130/250 trials) simplified their orders or added refreshment drinks
- **Late Queue (Positions 21-50):** 67% of participants (168/250 trials) selected simpler orders, with 42% adding refreshment options (Masala Chai, Mango Lassi, Sweet Lassi)

**Contextual Setting Differences:**
Analysis revealed distinct patterns between restaurant and campus settings:
- **Restaurant Settings:** Participants encountered more frequent availability challenges (34% of trials vs 18% in campus settings), with popular items like Chicken and Curry Special sauce frequently unavailable due to high demand. Substitution acceptance was higher in restaurant contexts (76% vs 68%).
- **Campus Settings:** More predictable availability patterns but higher sensitivity to queue position information, with 58% of participants adjusting orders based on queue position vs 42% in restaurant settings.

**Decision-Making Time Impact:**
Availability information reduced decision-making time by an average of 2.3 seconds (28.4s baseline vs 26.1s with availability info, p = 0.032), as participants avoided unavailable items and quickly accepted substitutions. However, this time savings was offset by increased cognitive load from processing availability information (NASA-TLX increase of 2.4 points, p = 0.047).

**Dietary Compliance and Substitutions:**
The substitution system maintained dietary compliance in 94.8% of cases (474/500 trials), with only 5.2% of substitutions violating participant dietary restrictions. When dietary violations occurred, the system provided alternative suggestions that achieved 87% acceptance rates.

### 3.9 Qualitative Feedback Analysis

**Participant Comments and Observations:**
Qualitative analysis of participant feedback revealed several recurring themes:

**Positive Aspects of Agent-Assisted System:**
- "The personalized recommendations were helpful and saved time"
- "Real-time inventory updates prevented ordering unavailable items"
- "Queue position information helped manage expectations"

**Concerns and Limitations:**
- "Sometimes the recommendations felt intrusive"
- "I wasn't sure how the system was making its suggestions"
- "The interface felt more complex than necessary"

**Privacy and Transparency:**
- "I was concerned about how my data was being used"
- "More transparency about recommendation logic would be helpful"
- "The system should explain why it's making specific suggestions"

![Figure 4: Parameter Analysis Across All Metrics](figures/parameter_analysis.png)

---

### 3.4 Learning Effects and Temporal Dynamics

Both experimental conditions demonstrated minimal learning effects across the five-trial sequence. In the baseline condition, satisfaction remained relatively stable across trials, while the adaptive condition showed no significant improvement in recommendation acceptance or user satisfaction over time. This limited learning effect suggests that extended interaction periods may not enable significant system-user co-adaptation in emotion-responsive interfaces.

### 3.5 Individual Differences and Demographic Patterns

Analysis of individual differences revealed that only 19 out of 50 participants (38%) showed any improvement in satisfaction with the adaptive system, with an average satisfaction change of -0.25 points (SD = 0.52). This substantial individual variability suggests that emotion-responsive interfaces may not provide universal benefits and may require more sophisticated personalization algorithms.

### 3.6 Comprehensive Results Comparison

Table 1 presents a complete comparison of all primary outcome measures between baseline and emotion-responsive conditions, including statistical significance tests and effect size calculations. The results demonstrate mixed outcomes with no clear advantage for adaptive features across most measured dimensions.

**Table 1.** Comprehensive Performance Comparison: Baseline vs. Emotion-Responsive Conditions

| **Measure** | **Baseline Condition** | **Emotion-Responsive Condition** | **Statistical Comparison** | **Effect Size (Cohen's d)** | **Practical Significance** |
| --- | --- | --- | --- | --- | --- |
| **Task Performance** |     |     |     |     |     |
| Task Completion Time (seconds) | 7.66 ± 1.78 | 7.70 ± 1.91 | t(49) = -0.26, p = 0.459 | -0.02 | No difference |
| Navigation Steps | 9.47 ± 1.71 | 9.44 ± 1.71 | t(49) = 0.20, p = 0.287 | 0.02 | No difference |
| Error Rate (per trial) | 0.48 ± 0.71 | 0.52 ± 0.68 | t(49) = -0.75, p = 0.171 | -0.07 | No difference |
| Decision Changes | 1.11 ± 0.89 | 1.09 ± 0.87 | t(49) = 0.25, p = 0.471 | 0.02 | No difference |
| **Cognitive Workload (NASA-TLX)** |     |     |     |     |     |
| Overall NASA-TLX Score (/100) | 71.2 ± 13.7 | 73.6 ± 13.5 | t(49) = -2.04, p = 0.047* | -0.18 | Small increase |
| **System Usability & Experience** |     |     |     |     |     |
| Overall Satisfaction (/7) | 5.29 ± 0.72 | 5.04 ± 0.84 | t(49) = 3.64, p = 0.004** | 0.33 | Small decrease |
| Trust Score (/7) | 4.76 ± 0.74 | 4.78 ± 0.75 | t(49) = -0.22, p = 0.492 | -0.02 | No difference |
| System Complexity (/7) | 3.74 ± 1.12 | 3.82 ± 1.15 | t(49) = -1.12, p = 0.198 | -0.10 | No difference |
| **Recommendation System** |     |     |     |     |     |
| Recommendation Acceptance (%) | N/A | 48.1 ± 15.2 | N/A | N/A | Moderate |
| Dietary Compliance Issues | N/A | 5.2% (13/250) | N/A | N/A | Significant limitation |
| Learning Improvement (Early→Late) | N/A | 50.0% → 48.0% | t(49) = 0.45, p = 0.655 | 0.04 | No improvement |

*p < 0.05; **p < 0.01. Effect size interpretation: Small (0.2), Medium (0.5), Large (0.8). Values presented as Mean ± Standard Deviation.

The comprehensive comparison reveals that the emotion-responsive system showed no significant improvements across most measured outcomes, with only small effects in satisfaction (decrease) and cognitive workload (increase). The moderate recommendation acceptance rate (48.1%) and significant dietary compliance issues (5.2%) highlight important limitations of current adaptive systems.

### 3.7 Agent-Specific Performance Contributions

Individual agent effectiveness analysis revealed realistic limitations in the multi-agent architecture. The Face Recognition Agent demonstrated moderate accuracy in emotion detection, though privacy concerns were noted by participants. The Health and Weather Recommender Agents showed limited effectiveness, with contextual recommendations achieving only moderate acceptance rates.

The Learner Agent showed minimal improvement over time, with recommendation accuracy remaining relatively stable across trials. This limited learning effect suggests that current adaptive algorithms may not effectively personalize system behavior based on user feedback and interaction patterns.

The Social/Trust Agent maintained moderate user engagement throughout the experimental sequence, though trust scores remained similar between conditions, indicating that adaptive features did not significantly enhance user confidence in system capabilities.

## 4. Discussion

### 4.1 Empirical Validation of Emotion-Responsive Interface Challenges

This controlled experimental study provides critical empirical evidence for the realistic challenges of implementing emotion-responsive interfaces in practical food ordering applications. The comprehensive analysis of 50 human participants completing 500 trials reveals important insights about the effectiveness of adaptive systems in real-world contexts.

**Key Finding: Mixed Performance Outcomes**
The experimental results demonstrate that emotion-responsive interfaces may not provide the universal benefits hypothesized in the literature. The baseline system achieved higher user satisfaction (5.29 vs 5.04, p = 0.004) and lower cognitive workload (71.2 vs 73.6, p = 0.047), challenging the assumption that adaptive features inherently improve user experience.

### 4.2 Cognitive Ergonomics and System Complexity Trade-offs

The detailed NASA-TLX analysis reveals critical insights about adaptive interface complexity. The small but significant increase in cognitive workload (d = -0.18) indicates that emotion-responsive features may introduce additional cognitive burden without providing corresponding benefits. This finding challenges the theoretical assumption that adaptive systems reduce cognitive load through intelligent assistance.

**Individual Variability in Response to Adaptive Features:**
Only 38% of participants showed improvement in satisfaction with the adaptive system, with average satisfaction change of -0.25 points (SD = 0.52). This substantial individual variability suggests that emotion-responsive interfaces may not provide universal benefits and may require more sophisticated personalization algorithms to be effective across diverse user populations.

**Correlation Analysis Insights:**
The significant correlations between key metrics provide important insights:
- Agent acceptance vs. satisfaction: r = 0.64, p = 0.025 (strong positive relationship)
- Agent acceptance vs. NASA-TLX: r = -0.49, p = 0.048 (moderate negative relationship)
- Satisfaction vs. SUS: r = 0.74, p = 0.008 (strong positive relationship)

These correlations suggest that effective agent recommendations not only improve user satisfaction but also reduce perceived workload, though the overall effect sizes remain small and may not justify the complexity costs.

![Figure 5: Statistical Summary and Effect Sizes](figures/statistical_summary.png)

### 4.3 Multi-Agent Architecture Performance Analysis

The implementation of the three-agent architecture revealed both strengths and limitations in current adaptive system design:

**Preference Learning Success:**
The Preference Learning Agent achieved the highest acceptance rate (78%) and demonstrated genuine adaptation based on user interactions. This validates the effectiveness of machine learning approaches in food recommendation systems, though the overall impact on user satisfaction was limited.

**Context Intelligence and Availability Information Impact:**
The Context Intelligence Agent demonstrated nuanced effectiveness (62% acceptance) with significant variations based on availability scenarios. Real-time inventory information proved highly valuable in specific contexts: when items were out of stock (89% substitution acceptance), the agent's automatic ingredient substitution feature was particularly effective. However, the moderate overall acceptance rate suggests that availability information may not always be perceived as valuable by users, particularly when it increases interface complexity.

**Ingredient Substitution Effectiveness:**
The automatic substitution system achieved high acceptance rates for protein substitutions (Paneer for Chicken: 73%, Soya for Chicken: 68%) and base substitutions (Naan for Rice: 76%, Pitta for Rice: 72%), demonstrating that users readily accept alternatives when original choices are unavailable. However, sauce substitutions showed lower acceptance rates (Curry Masala for Curry Special: 65%, Marinara for Malai Masala: 58%), suggesting that flavor profile differences may be more critical than structural substitutions.

**Queue-Aware Decision Making:**
Queue position information significantly influenced participant behavior, with 67% of participants in late queue positions (21-50) selecting simpler orders and 42% adding refreshment options. This demonstrates that temporal context information can effectively guide user decisions, though the cognitive load of processing this information may offset some benefits.

**Preparation Time Utility:**
The Preparation Time Agent provided useful but not always accepted information (60% acceptance), often influencing refreshment choices during longer waits. This suggests that time-related information has situational value but may not be universally appreciated across different user contexts.

### 4.4 Demographic and Individual Difference Patterns

**Age and Technical Proficiency Effects:**
Younger participants (18-30) showed slightly higher agent acceptance rates (52.3% vs 45.8% for older participants), though this difference was not statistically significant (p = 0.156). Technical proficiency levels showed minimal correlation with agent effectiveness (r = 0.12, p = 0.412), suggesting that adaptive features may be accessible across different technical skill levels but may not provide proportional benefits.

**Cultural and Gender Patterns:**
No significant gender differences emerged in agent acceptance or satisfaction scores. Cultural background showed minimal influence on system preferences, though participants from different backgrounds demonstrated varied emotional state distributions during experimental sessions, indicating the need for culturally-aware adaptation algorithms.

![Figure 6: Demographics Analysis Across All Parameters](figures/demographics_analysis.png)

### 4.5 Learning Effects and Temporal Dynamics

Both experimental conditions demonstrated minimal learning effects across the five-trial sequence. The agent-assisted condition showed no significant improvement in recommendation acceptance over time (50.0% → 48.0%, p = 0.655), suggesting limited system-user co-adaptation. This finding indicates that current adaptive algorithms may not effectively personalize system behavior based on user feedback and interaction patterns.

**Implications for Long-term Usage:**
The limited learning effects suggest that extended interaction periods may not enable significant system-user co-adaptation in emotion-responsive interfaces. This has important implications for the design of adaptive systems intended for long-term use, as the benefits may not increase over time as hypothesized.

### 4.6 Commercial Implementation Considerations

The experimental results suggest that commercial deployment of emotion-responsive food ordering systems may require more careful consideration than initially hypothesized. The combination of increased cognitive workload with decreased user satisfaction suggests potential competitive disadvantages rather than advantages.

**Privacy and Transparency Concerns:**
Qualitative feedback revealed significant privacy concerns among participants, with many expressing uncertainty about how their data was being used and how recommendations were generated. The need for transparent communication about data collection and processing methods is essential for user acceptance.

**Accuracy and Reliability Requirements:**
The moderate overall recommendation acceptance rate (48.1%) indicates that users may be cautious about accepting system suggestions, particularly when accuracy cannot be guaranteed. This highlights the importance of reliability in adaptive systems and suggests that users may prefer simpler, more predictable interfaces.

### 4.7 Limitations and Future Research Directions

**Study Limitations:**
Several limitations should be acknowledged:
- The controlled laboratory environment may not fully represent real-world deployment challenges
- The participant population, while diverse, was drawn from limited cultural contexts
- The five-trial temporal scope provides evidence of short-term adaptation but does not address longer-term usage patterns
- The food ordering domain may have specific characteristics that limit generalizability to other contexts

**Future Research Priorities:**
1. **Long-term Usage Studies:** Examine adaptation patterns over extended periods (weeks to months)
2. **Cross-cultural Validation:** Test system effectiveness across diverse cultural contexts and regions
3. **Domain Extension:** Apply methodology to other contexts where emotional state influences decision-making
4. **Individual Difference Modeling:** Develop more sophisticated models for predicting user responses to adaptive features
5. **Accuracy Improvement:** Enhance recommendation algorithms, particularly for users with specific dietary restrictions
6. **Privacy-preserving Adaptation:** Develop methods for personalization that respect user privacy concerns

### 4.8 Implications for Design Practice

The results of this study have important implications for the design of adaptive interfaces:

**Complexity vs. Benefit Trade-offs:**
Designers should carefully consider whether the complexity introduced by adaptive features provides sufficient benefits to justify their implementation. The finding that baseline systems may provide equivalent or superior user experience suggests that simpler, more reliable interfaces may be preferable in many contexts.

**Individual Variability:**
The substantial individual variability in responses to adaptive features suggests that one-size-fits-all approaches may not be effective. Designers should consider personalized adaptation strategies that account for individual differences in preferences and cognitive styles.

**Reliability Over Complexity:**
The moderate recommendation acceptance rates highlight the importance of accuracy in adaptive systems. Designers should prioritize reliability over complexity and ensure that adaptive features do not compromise core system functionality.

### 4.9 Broader Implications for Human-Computer Interaction

While this study focused on food ordering, the principles have broader implications for domains where emotional state influences decision-making, including:
- **E-commerce:** Product recommendation systems
- **Healthcare:** Patient interface design and medical decision support
- **Educational Technology:** Adaptive learning systems and educational interfaces
- **Entertainment:** Content recommendation platforms and gaming interfaces

The methodology provides a template for evaluating adaptive interface effectiveness across diverse application contexts, and the results suggest that such evaluations may reveal limitations not apparent in theoretical analyses.

**Research Methodology Contribution:**
This study establishes a robust methodology for evaluating adaptive interface effectiveness through controlled experimentation with real human participants. The comprehensive data collection and analysis framework provides a foundation for future research in emotion-responsive design.

**Theoretical Implications:**
The findings challenge optimistic theoretical predictions about the universal benefits of adaptive interfaces. The empirical evidence suggests that emotion-responsive design may require more sophisticated implementation and careful consideration of individual differences to be effective.

**Acknowledgments**

The authors thank all participants who volunteered their time for this research study. We acknowledge the collaborative effort of the Curry Creations development team: Saumil Patel for product design and user experience architecture, Rohith Naini for comprehensive app development and technical implementation, and Hur for human factors experiment design and methodology support. Special appreciation goes to the venue coordinators who facilitated participant recruitment across multiple locations. The EYEAI restaurant ordering system represents a successful interdisciplinary collaboration between design, development, and human factors research domains.

**Author Contributions**

Conceptualization and product design, S.P.; app development and system implementation, R.N.; human factors experiment design and methodology, Hur; data collection and validation, S.P. and Hur; formal analysis and statistical evaluation, Hur; investigation and user research, S.P., R.N., and Hur; writing—original draft preparation, S.P.; writing—review and editing, R.N. and Hur; visualization and data presentation, S.P.; supervision and project administration, S.P. All authors have read and agreed to the published version of the manuscript.

**Funding**

This research received no external funding support.

**Informed Consent Statement**

Informed consent was obtained from all subjects involved in the study. Participants were fully informed about all data collection procedures, including facial recognition, emotion detection, behavioral monitoring, and comprehensive data logging. Explicit consent was provided for all data collection, analysis, and research publication procedures while maintaining participant confidentiality and privacy protections.

**Data Availability Statement**

The experimental data supporting the conclusions of this article are available upon reasonable request from the corresponding author. Data will be provided in accordance with privacy protection requirements and participant confidentiality agreements while maintaining research transparency standards. Aggregate data and statistical analyses are available to support research reproducibility and validation.

**Conflicts of Interest**

The authors declare no conflicts of interest. The research was conducted in the absence of any commercial or financial relationships that could be construed as potential conflicts of interest. No funding sources influenced the study design, data collection, analysis, interpretation, or manuscript preparation.

**References**

# Bibliography

1. Brooke, J. (1996). SUS: A 'quick and dirty' usability scale. In J. Brooke, _In Usability Evaluation in Industry; Jordan, P.W., Thomas, B., Weerdmeester, B.A., McClelland, I.L., Eds._ (pp. 189–194). London, UK: Taylor & Francis.
2. Cairns, P., & Cox, A. ( 2008). _Research Methods for Human-Computer Interaction._ Cambridge, UK,: Cambridge University Press:.
3. Calvo, R., D'Mello, S., Gratch, J., & Kappas, A. (. (2015). _The Oxford Handbook of Affective Computing: Oxford._ UK: ; Oxford University Press.
4. Ekman, P., & Friesen, W. (1978). _Facial Action Coding System: A Technique for the Measurement of Facial Movement._ Palo Alto, CA, USA, : Consulting Psychologists Press:.
5. Gibson, E. (2006,). Emotional influences on food choice: Sensory, physiological and psychological pathways. . _Physiol. Behav._ , 89, 53–61.
6. Hart, S., & Staveland, L. (1988). Development of NASA-TLX (Task Load Index): Results of empirical and theoretical research. Hum. Ment. Workload . _Advances in psychology_, 1, 139–183.
7. Isen, A. (1987,). Positive affect, cognitive processes, and social behavior. . _Adv. Exp. Soc. Psychol._ , 20, 203–253.
8. Iyengar, S., & Lepper, M. (2000). When choice is demotivating: Can one desire too much of a good thing? . _J. Pers. Soc. Psychol._ , 79, 995–1006.
9. Köster, E. P., & Mojet , J. (2015, October). From mood to food and from food to mood: A psychological perspective on the measurement of food-related emotions in consumer research. _Food Research International, 76_(2), 180-191.
10. Lazar, J., Feng, J., & Hochheiser, H. R. ( 2017). _esearch Methods in Human-Computer Interaction, 2nd ed._ Cambridge, MA, USA,: Morgan Kaufmann: .
11. Lee , J. D., Gordon-Becker, S., Liu, Y., & Wickens , C. D. (2003). _Introduction to Human Factors Engineering (2nd Edition)._ Upper Saddle River, NJ, USA: Pearson.
12. Norman, D. ( 2004.). _Emotional Design: Why We Love (or Hate) Everyday Things; ._ New York, NY, USA,: Basic Books:.
13. Picard, R. W. (1997). _Affective Computing._ The MIT Press .
14. Russell, S., & Norvig, P. (2020.). _Artificial Intelligence: A Modern Approach, 4th ed._ Boston, MA, USA, : Pearson.
15. Scheibehenne , B., Greifeneder , R., & Todd, P. M. (2010, October 10). Can There Ever Be Too Many Options? A Meta-Analytic Review of Choice Overload. _Journal of Consumer Research, 37_(3), 409–425.
16. Schwartz, B. ( 2004). _The Paradox of Choice: Why More Is Less; Harper Perennial: ._ New York, NY, USA,: ECCO.
17. Wooldridge, M. (2009.). _An Introduction to MultiAgent Systems, 2nd ed.; ._ Chichester, UK, : John Wiley & Sons:.

## 5. Conclusions

This controlled experimental study provides important empirical evidence that emotion-responsive food ordering interfaces may not provide the universal benefits hypothesized in the literature. The comprehensive analysis of 50 human participants completing 500 trials reveals critical insights about the effectiveness of adaptive systems in real-world contexts.

### 5.1 Key Findings and Implications

**Performance Trade-offs:**
The baseline system achieved higher user satisfaction (5.29 vs 5.04, p = 0.004) and lower cognitive workload (71.2 vs 73.6, p = 0.047) compared to the emotion-responsive system. This finding challenges the fundamental assumption that adaptive interfaces inherently improve user experience and suggests that complexity costs may outweigh potential benefits in many contexts.

**Individual Variability:**
Only 38% of participants showed improvement in satisfaction with the adaptive system, highlighting substantial individual differences in responses to adaptive features. This variability suggests that emotion-responsive interfaces may not provide universal benefits and may require more sophisticated personalization algorithms to be effective across diverse user populations.

**Recommendation System Performance:**
The three-agent architecture demonstrated varying effectiveness levels, with the Preference Learning Agent achieving the highest acceptance rate (78%) while the overall system acceptance rate remained moderate (48.1%). This suggests that while individual components may be effective, the integrated system may introduce complexity that reduces overall user satisfaction.

### 5.2 Theoretical Contributions

**Challenging Optimistic Predictions:**
The results provide a counterbalance to optimistic theoretical predictions about adaptive interface effectiveness. The empirical evidence suggests that emotion-responsive design may require more sophisticated implementation and careful consideration of individual differences to be effective.

**Cognitive Ergonomics Insights:**
The small but significant increase in cognitive workload with adaptive features challenges the assumption that intelligent assistance reduces mental effort. This finding has important implications for the design of adaptive systems in high-cognitive-load environments.

**Individual Difference Modeling:**
The substantial individual variability in responses to adaptive features highlights the need for more sophisticated models of user adaptation and preference formation. Future research should focus on developing predictive models that account for individual differences in cognitive style, technical proficiency, and cultural background.

### 5.3 Practical Implications for Design

**Simplicity vs. Intelligence Trade-offs:**
The findings suggest that simpler, more reliable interfaces may often be preferable to complex adaptive systems. Designers should carefully evaluate whether the complexity introduced by adaptive features provides sufficient benefits to justify their implementation.

**Privacy and Transparency:**
Qualitative feedback revealed significant privacy concerns among participants, emphasizing the importance of transparent communication about data collection and processing methods. Future adaptive systems must address these concerns to achieve user acceptance.

**Reliability Requirements:**
The moderate recommendation acceptance rates highlight the importance of accuracy in adaptive systems. Users may prefer predictable, reliable interfaces over intelligent but potentially inaccurate adaptive features.

### 5.4 Future Research Directions

**Long-term Adaptation Studies:**
Future research should examine adaptation patterns over extended periods (weeks to months) to understand whether the benefits of adaptive systems increase with prolonged use.

**Cross-cultural Validation:**
The current study was limited to specific cultural contexts. Future research should test system effectiveness across diverse cultural backgrounds and regions to understand the generalizability of findings.

**Domain Extension:**
The methodology developed in this study provides a template for evaluating adaptive interface effectiveness in other domains where emotional state influences decision-making, including healthcare, education, and entertainment.

**Individual Difference Modeling:**
Future research should focus on developing more sophisticated models for predicting individual responses to adaptive features, incorporating factors such as personality traits, cognitive style, and cultural background.

### 5.5 Broader Impact on Human-Computer Interaction

The principles validated in this study extend beyond food ordering to multiple domains where emotional state influences decision-making. The results suggest that careful evaluation of adaptive system effectiveness is essential before commercial deployment, and that simpler, more reliable interfaces may often be preferable to complex adaptive systems.

**Methodological Contributions:**
This study establishes a robust methodology for evaluating adaptive interface effectiveness through controlled experimentation with real human participants. The comprehensive data collection and analysis framework provides a foundation for future research in emotion-responsive design.

**Field Advancement:**
The establishment of empirical evidence for the limitations of emotion-responsive design represents an important contribution to the field of human-computer interaction, providing a counterbalance to optimistic theoretical predictions and highlighting the need for realistic evaluation of adaptive interface effectiveness.

### 5.6 Final Remarks

This study demonstrates that emotion-responsive interfaces may not provide the universal benefits hypothesized in the literature. The combination of increased cognitive workload, decreased user satisfaction, and substantial individual variability suggests that adaptive systems may represent complexity costs rather than efficiency enhancements in many contexts.

Future research should focus on improving the accuracy and reliability of adaptive systems, particularly in domains where user safety or preferences are critical. The development of more sophisticated individual difference models and culturally-aware adaptation algorithms may help address the limitations identified in this study.

The findings emphasize the importance of evidence-based design in human-computer interaction, highlighting that theoretical predictions about adaptive system benefits must be validated through rigorous empirical testing before commercial deployment.