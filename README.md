# Emotion-Responsive Food Ordering System: Experiment Framework

## Overview

This framework enables researchers to run controlled, agent-based food ordering experiments with real-time inventory, context intelligence, and preference learning. It is designed for reproducible, privacy-compliant human studies and can be adapted for new experimental designs.

---

## 1. System Architecture

- **Agents:**
  - **Context Intelligence Agent:** Provides real-time inventory, queue, and context-aware recommendations.
  - **Preference Learning Agent:** Learns user preferences from order history and feedback.
  - **Preparation Time Agent:** Estimates preparation/wait times based on order complexity and queue.

- **Inventory Management:**
  - Tracks 25+ ingredients (proteins, sauces, bases, veggies, garnishes) with real-time status (available, low stock, preparing, out of stock).
  - Supports ingredient substitution and queue-aware suggestions.

- **Experiment Logging:**
  - All participant actions, agent interactions, and system states are logged to CSV/JSON for analysis.

---

## 2. Experiment Design

- **Participants:**
  - Register with anonymized ID, age, gender, and optional demographic info.
  - Consent and privacy compliance are required.

- **Trial Structure:**
  - Each participant completes multiple trials under different conditions (e.g., emotion-responsive vs. traditional).
  - Each trial logs:
    - Condition (emotion-responsive/traditional)
    - Emotional state (if measured)
    - Agent recommendations shown/accepted/rejected
    - Inventory status and substitutions
    - Timing for each step (NASA-TLX, SUS, satisfaction, etc.)

- **Data Collected:**
  - All data is anonymized and stored locally (never committed to git).
  - Example files: `data/experiment_log.csv`, `data/agent_interactions.csv`, etc.

---

## 3. How to Run Your Own Experiment

1. **Clone the Repository**
   ```bash
   git clone <your-repo-url>
   cd food_recomender
   ```

2. **Install Dependencies**
   - Python 3.8+ (see `requirements.txt`)
   - (Optional) Node.js for frontend

3. **Start the Backend API**
   ```bash
   python simple_server.py
   ```
   - The API provides endpoints for participant registration, order flow, agent recommendations, and data logging.

4. **Register Participants**
   - Use `/api/participants/register` endpoint (see API docs or use Postman/cURL).

5. **Run Trials**
   - Use the provided frontend or your own interface to guide participants through the experiment.
   - All actions and agent interactions are logged automatically.

6. **Collect and Analyze Data**
   - Data is saved in the `data/` directory (see below for compliance).
   - Use your own scripts or the provided analysis tools to process results.

---

## 4. Customizing the Framework

- **Agents:**
  - Modify or extend agent logic in `simple_server.py` or backend agent files.
  - Add new recommendation strategies, context signals, or learning algorithms.

- **Inventory:**
  - Edit the inventory initialization in `simple_server.py` to match your menu/ingredients.
  - Adjust substitution logic as needed.

- **Experiment Flow:**
  - Change trial structure, add new conditions, or collect additional measures by editing the API endpoints and logging functions.

---

## 5. Compliance, Privacy, and Data Handling

- **All experiment data is stored locally and is never committed to git.**
- **Sensitive fields (name, phone, email, age, etc.) are anonymized or marked as [REDACTED] in all public outputs.**
- **The `.gitignore` is configured to protect all experiment data and participant information.**
- **Researchers are responsible for obtaining IRB/ethics approval and participant consent as required.**

---

## 6. Example: Running a Minimal Experiment

1. **Start the server:**
   `python simple_server.py`

2. **Register a participant:**
   `POST /api/participants/register` with JSON body:
   ```json
   {
     "name": "Participant 1",
     "email": "p1@domain.com",
     "age": 25,
     "gender": "female",
     "country": "Country"
   }
   ```

3. **Start a trial:**
   `POST /api/start-order`
   Add items, complete order, and log agent interactions via API.

4. **Submit subjective scores:**
   `POST /api/participants/{participant_id}/submit-response` with NASA-TLX, SUS, satisfaction, etc.

5. **Analyze results:**
   - Data is in `data/experiment_log.csv` and related files.
   - Use Python, R, or your preferred tool for analysis.

---

## 7. Results (Anonymized Example)

**Summary:**
- 13 participants, 138 trials (all personal data anonymized)
- All names, phone numbers, ages, and private data are marked as [REDACTED] for compliance
- Results log is kept locally and versioned with git for audit and reproducibility

**Key Findings:**
- **User Satisfaction:** Baseline 5.29/7.0, Adaptive 5.04/7.0 (p=0.004)
- **Cognitive Workload (NASA-TLX):** Baseline 41.2, Adaptive 38.7 (p=0.03)
- **Agent Acceptance:** Context Intelligence 62%, Preference Learning 74%
- **Availability Impact:** 67% risk-avoidance for low stock, 89% substitution acceptance for out-of-stock
- **Queue-Aware Decisions:** Longer waits led to more refreshment orders

---

## 8. Contact & Citation

For questions, collaboration, or to cite this framework, please contact the repository maintainer or open an issue.

---

**Critical Note:**
This framework is provided for research purposes. All experiment data is protected for compliance. Please review and adapt the system for your own ethical and privacy requirements.