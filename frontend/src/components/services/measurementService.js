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
      const response = await fetch('http://localhost:8000/api/measurements/task-completion', {
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
      const response = await fetch('http://localhost:8000/api/measurements/error-tracking', {
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
      const response = await fetch('http://localhost:8000/api/measurements/decision-change', {
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
    // This should be called after task completion with real user input
    // For now, return null to indicate manual input is required
    console.log('NASA-TLX requires manual user input - cannot be simulated');
    return null;
  }

  async requestSUS() {
    // SUS requires real user responses - cannot be simulated
    console.log('SUS requires manual user input - cannot be simulated');
    return null;
  }

  async requestSatisfaction() {
    // Satisfaction requires real user responses - cannot be simulated
    console.log('Satisfaction requires manual user input - cannot be simulated');
    return null;
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