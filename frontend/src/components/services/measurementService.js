/**
 * Measurement Service for tracking user interactions and performance metrics
 * Integrates with the MPID measurement system
 */

class MeasurementService {
  constructor() {
    this.sessionId = this.generateSessionId();
    this.condition = this.determineCondition();
    this.taskStartTime = null;
    this.stepStartTimes = {};
    this.errors = [];
    this.decisionChanges = [];
    this.userInteractions = [];
    this.isTracking = false;
  }

  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  determineCondition() {
    // Randomly assign condition for A/B testing
    // In a real experiment, this would be controlled by experiment parameters
    return Math.random() > 0.5 ? 'emotion_responsive' : 'traditional';
  }

  startTracking() {
    this.isTracking = true;
    this.taskStartTime = new Date();
    console.log(`Measurement tracking started for session: ${this.sessionId}`);
  }

  stopTracking() {
    this.isTracking = false;
    console.log(`Measurement tracking stopped for session: ${this.sessionId}`);
  }

  startStep(stepName) {
    if (!this.isTracking) return;
    this.stepStartTimes[stepName] = new Date();
  }

  endStep(stepName, success = true) {
    if (!this.isTracking || !this.stepStartTimes[stepName]) return;

    const endTime = new Date();
    const duration = endTime - this.stepStartTimes[stepName];

    this.userInteractions.push({
      step: stepName,
      duration_ms: duration,
      success: success,
      timestamp: endTime.toISOString()
    });
  }

  trackError(errorType, description, context = {}, recovered = false) {
    if (!this.isTracking) return;

    const errorData = {
      error_type: errorType,
      error_description: description,
      context: context,
      recovered: recovered,
      timestamp: new Date().toISOString()
    };

    this.errors.push(errorData);

    // Send to backend
    this.submitErrorTracking(errorData);
  }

  trackDecisionChange(changeType, originalChoice, newChoice, reason = '') {
    if (!this.isTracking) return;

    const changeData = {
      change_type: changeType,
      original_choice: originalChoice,
      new_choice: newChoice,
      reason: reason,
      timestamp: new Date().toISOString()
    };

    this.decisionChanges.push(changeData);

    // Send to backend
    this.submitDecisionChange(changeData);
  }

  async submitTaskCompletion(taskType, success, stepsCompleted, totalSteps) {
    if (!this.isTracking || !this.taskStartTime) return;

    try {
      const response = await fetch('/api/measurements/task-completion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          condition: this.condition,
          task_start_time: this.taskStartTime.toISOString(),
          task_end_time: new Date().toISOString(),
          task_type: taskType,
          success: success,
          steps_completed: stepsCompleted,
          total_steps: totalSteps
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Task completion tracked:', result);
        return result;
      }
    } catch (error) {
      console.error('Error tracking task completion:', error);
    }
  }

  async submitErrorTracking(errorData) {
    try {
      const response = await fetch('/api/measurements/error-tracking', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...errorData,
          session_id: this.sessionId,
          condition: this.condition
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Error tracked:', result);
        return result;
      }
    } catch (error) {
      console.error('Error submitting error tracking:', error);
    }
  }

  async submitDecisionChange(changeData) {
    try {
      const response = await fetch('/api/measurements/decision-change', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...changeData,
          session_id: this.sessionId,
          condition: this.condition
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Decision change tracked:', result);
        return result;
      }
    } catch (error) {
      console.error('Error submitting decision change:', error);
    }
  }

  async requestNASATLX() {
    // This would typically be called after task completion
    // For now, we'll simulate realistic values based on the session
    const simulatedTLX = this.generateSimulatedNASATLX();

    try {
      const response = await fetch('/api/measurements/nasa-tlx', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...simulatedTLX,
          session_id: this.sessionId,
          condition: this.condition
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('NASA-TLX submitted:', result);
        return result;
      }
    } catch (error) {
      console.error('Error submitting NASA-TLX:', error);
    }
  }

  async requestSUS() {
    // Simulate SUS responses based on the user experience
    const simulatedSUS = this.generateSimulatedSUS();

    try {
      const response = await fetch('/api/measurements/sus', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...simulatedSUS,
          session_id: this.sessionId,
          condition: this.condition
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('SUS submitted:', result);
        return result;
      }
    } catch (error) {
      console.error('Error submitting SUS:', error);
    }
  }

  async requestSatisfaction() {
    // Simulate satisfaction responses
    const simulatedSatisfaction = this.generateSimulatedSatisfaction();

    try {
      const response = await fetch('/api/measurements/satisfaction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...simulatedSatisfaction,
          session_id: this.sessionId,
          condition: this.condition
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Satisfaction submitted:', result);
        return result;
      }
    } catch (error) {
      console.error('Error submitting satisfaction:', error);
    }
  }

  generateSimulatedNASATLX() {
    // Generate realistic NASA-TLX values based on session characteristics
    const baseValues = {
      mental_demand: 30 + Math.floor(Math.random() * 40), // 30-70
      physical_demand: 10 + Math.floor(Math.random() * 20), // 10-30
      temporal_demand: 20 + Math.floor(Math.random() * 30), // 20-50
      performance: 60 + Math.floor(Math.random() * 30), // 60-90
      effort: 25 + Math.floor(Math.random() * 35), // 25-60
      frustration: 10 + Math.floor(Math.random() * 30) // 10-40
    };

    // Adjust based on errors and decision changes
    if (this.errors.length > 2) {
      baseValues.frustration += 15;
      baseValues.mental_demand += 10;
    }

    if (this.decisionChanges.length > 3) {
      baseValues.temporal_demand += 10;
      baseValues.effort += 10;
    }

    // Ensure values stay within bounds
    Object.keys(baseValues).forEach(key => {
      baseValues[key] = Math.max(0, Math.min(100, baseValues[key]));
    });

    return baseValues;
  }

  generateSimulatedSUS() {
    // Generate realistic SUS responses
    const baseCondition = this.condition === 'emotion_responsive' ? 4 : 3;

    return {
      q1_use_frequently: Math.max(1, Math.min(5, baseCondition + Math.floor(Math.random() * 2) - 1)),
      q2_unnecessarily_complex: Math.max(1, Math.min(5, 3 - baseCondition + Math.floor(Math.random() * 2))),
      q3_easy_to_use: Math.max(1, Math.min(5, baseCondition + Math.floor(Math.random() * 2))),
      q4_need_support: Math.max(1, Math.min(5, 3 - baseCondition + Math.floor(Math.random() * 2))),
      q5_well_integrated: Math.max(1, Math.min(5, baseCondition + Math.floor(Math.random() * 2) - 1)),
      q6_too_much_inconsistency: Math.max(1, Math.min(5, 3 - baseCondition + Math.floor(Math.random() * 2))),
      q7_learn_quickly: Math.max(1, Math.min(5, baseCondition + Math.floor(Math.random() * 2))),
      q8_very_cumbersome: Math.max(1, Math.min(5, 3 - baseCondition + Math.floor(Math.random() * 2))),
      q9_very_confident: Math.max(1, Math.min(5, baseCondition + Math.floor(Math.random() * 2) - 1)),
      q10_learn_lot_before: Math.max(1, Math.min(5, 3 - baseCondition + Math.floor(Math.random() * 2)))
    };
  }

  generateSimulatedSatisfaction() {
    // Generate satisfaction ratings (1-7 scale)
    const baseCondition = this.condition === 'emotion_responsive' ? 5 : 4;

    return {
      overall_satisfaction: Math.max(1, Math.min(7, baseCondition + Math.floor(Math.random() * 3) - 1)),
      ease_of_use: Math.max(1, Math.min(7, baseCondition + Math.floor(Math.random() * 3))),
      recommendation_quality: Math.max(1, Math.min(7, baseCondition + Math.floor(Math.random() * 3) - 1)),
      perceived_personalization: Math.max(1, Math.min(7, baseCondition + Math.floor(Math.random() * 3))),
      decision_confidence: Math.max(1, Math.min(7, baseCondition + Math.floor(Math.random() * 3) - 1)),
      enjoyment: Math.max(1, Math.min(7, baseCondition + Math.floor(Math.random() * 3))),
      return_intention: Math.max(1, Math.min(7, baseCondition + Math.floor(Math.random() * 3) - 1))
    };
  }

  async getSessionSummary() {
    try {
      const response = await fetch(`/api/measurements/session-summary/${this.sessionId}`);
      if (response.ok) {
        const summary = await response.json();
        console.log('Session summary retrieved:', summary);
        return summary;
      }
    } catch (error) {
      console.error('Error getting session summary:', error);
    }
    return null;
  }

  // Utility method to get current session info
  getSessionInfo() {
    return {
      sessionId: this.sessionId,
      condition: this.condition,
      isTracking: this.isTracking,
      errorCount: this.errors.length,
      decisionChangeCount: this.decisionChanges.length,
      interactionCount: this.userInteractions.length
    };
  }
}

// Create a singleton instance
const measurementService = new MeasurementService();

export default measurementService;