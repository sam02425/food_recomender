import React, { useState, useEffect } from 'react';
import './MeasurementDemo.css';

const MeasurementDemo = () => {
  const [sessionId, setSessionId] = useState('');
  const [condition, setCondition] = useState('emotion_responsive');
  const [currentStep, setCurrentStep] = useState('intro');
  const [measurements, setMeasurements] = useState({
    nasaTlx: {},
    sus: {},
    taskCompletion: {},
    satisfaction: {},
    errors: [],
    decisionChanges: []
  });
  const [taskStartTime, setTaskStartTime] = useState(null);
  const [sessionSummary, setSessionSummary] = useState(null);

  useEffect(() => {
    // Generate a unique session ID when component mounts
    setSessionId(`demo_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  }, []);

  const submitNASATLX = async (nasaTlxData) => {
    try {
      const response = await fetch('http://localhost:8000/api/measurements/nasa-tlx', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...nasaTlxData,
          session_id: sessionId,
          condition: condition
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('NASA-TLX submitted successfully:', result);
        setMeasurements(prev => ({ ...prev, nasaTlx: nasaTlxData }));
        return true;
      }
    } catch (error) {
      console.error('Error submitting NASA-TLX:', error);
    }
    return false;
  };

  const submitSUS = async (susData) => {
    try {
      const response = await fetch('http://localhost:8000/api/measurements/sus', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...susData,
          session_id: sessionId,
          condition: condition
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('SUS submitted successfully:', result);
        setMeasurements(prev => ({ ...prev, sus: susData }));
        return true;
      }
    } catch (error) {
      console.error('Error submitting SUS:', error);
    }
    return false;
  };

  const submitTaskCompletion = async (taskData) => {
    try {
      const response = await fetch('http://localhost:8000/api/measurements/task-completion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...taskData,
          session_id: sessionId,
          condition: condition
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Task completion submitted successfully:', result);
        setMeasurements(prev => ({ ...prev, taskCompletion: taskData }));
        return true;
      }
    } catch (error) {
      console.error('Error submitting task completion:', error);
    }
    return false;
  };

  const submitSatisfaction = async (satisfactionData) => {
    try {
      const response = await fetch('http://localhost:8000/api/measurements/satisfaction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...satisfactionData,
          session_id: sessionId,
          condition: condition
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Satisfaction submitted successfully:', result);
        setMeasurements(prev => ({ ...prev, satisfaction: satisfactionData }));
        return true;
      }
    } catch (error) {
      console.error('Error submitting satisfaction:', error);
    }
    return false;
  };

  const submitError = async (errorData) => {
    try {
      const response = await fetch('http://localhost:8000/api/measurements/error-tracking', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...errorData,
          session_id: sessionId,
          condition: condition,
          timestamp: new Date().toISOString()
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Error tracking submitted successfully:', result);
        setMeasurements(prev => ({
          ...prev,
          errors: [...prev.errors, errorData]
        }));
        return true;
      }
    } catch (error) {
      console.error('Error submitting error tracking:', error);
    }
    return false;
  };

  const getSessionSummary = async () => {
    try {
      const response = await fetch(`/api/measurements/session-summary/${sessionId}`);
      if (response.ok) {
        const summary = await response.json();
        setSessionSummary(summary);
        return summary;
      }
    } catch (error) {
      console.error('Error getting session summary:', error);
    }
    return null;
  };

  const startTask = () => {
    setTaskStartTime(new Date());
    setCurrentStep('task');
  };

  const completeTask = async () => {
    const endTime = new Date();
    const taskData = {
      task_start_time: taskStartTime.toISOString(),
      task_end_time: endTime.toISOString(),
      task_type: 'measurement_demo',
      success: true,
      steps_completed: 5,
      total_steps: 5
    };

    await submitTaskCompletion(taskData);
    setCurrentStep('nasa_tlx');
  };

  const renderIntro = () => (
    <div className="measurement-step">
      <h2>Measurement System Demo</h2>
      <p>This demo showcases the integrated measurement capabilities:</p>
      <ul>
        <li><strong>NASA-TLX:</strong> Task Load Index for workload assessment</li>
        <li><strong>SUS:</strong> System Usability Scale</li>
        <li><strong>Task Completion:</strong> Time and success tracking</li>
        <li><strong>Error Tracking:</strong> User error monitoring</li>
        <li><strong>Satisfaction:</strong> Multi-dimensional satisfaction measurement</li>
      </ul>

      <div className="condition-selector">
        <label>
          Experimental Condition:
          <select value={condition} onChange={(e) => setCondition(e.target.value)}>
            <option value="emotion_responsive">Emotion-Responsive System</option>
            <option value="traditional">Traditional System</option>
            <option value="standard">Standard</option>
          </select>
        </label>
      </div>

      <p><strong>Session ID:</strong> {sessionId}</p>

      <button onClick={startTask} className="primary-button">
        Start Demo Task
      </button>
    </div>
  );

  const renderTask = () => (
    <div className="measurement-step">
      <h2>Demo Task: Food Ordering Simulation</h2>
      <p>Simulate interacting with the food ordering system...</p>

      <div className="task-simulation">
        <div className="task-step">✓ Browse menu items</div>
        <div className="task-step">✓ Select protein option</div>
        <div className="task-step">✓ Choose sauce preferences</div>
        <div className="task-step">✓ Add vegetables</div>
        <div className="task-step">✓ Complete order</div>
      </div>

      <button onClick={() => submitError({
        error_type: 'selection_error',
        error_description: 'User accidentally selected wrong protein',
        context: { step: 'protein_selection', attempted_action: 'select_chicken' },
        recovered: true
      })} className="error-button">
        Simulate Error
      </button>

      <button onClick={completeTask} className="primary-button">
        Complete Task
      </button>
    </div>
  );

  const renderNASATLX = () => {
    const [tlxData, setTlxData] = useState({
      mental_demand: 50,
      physical_demand: 20,
      temporal_demand: 30,
      performance: 80,
      effort: 40,
      frustration: 25
    });

    const handleSubmit = async () => {
      const success = await submitNASATLX(tlxData);
      if (success) {
        setCurrentStep('sus');
      }
    };

    return (
      <div className="measurement-step">
        <h2>NASA Task Load Index (NASA-TLX)</h2>
        <p>Rate your experience on each dimension (0-100):</p>

        <div className="tlx-form">
          {Object.entries(tlxData).map(([key, value]) => (
            <div key={key} className="measurement-item">
              <label>
                {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={value}
                  onChange={(e) => setTlxData(prev => ({
                    ...prev,
                    [key]: parseInt(e.target.value)
                  }))}
                />
                <span className="range-value">{value}</span>
              </label>
            </div>
          ))}
        </div>

        <button onClick={handleSubmit} className="primary-button">
          Submit NASA-TLX
        </button>
      </div>
    );
  };

  const renderSUS = () => {
    const [susData, setSusData] = useState({
      q1_use_frequently: 3,
      q2_unnecessarily_complex: 2,
      q3_easy_to_use: 4,
      q4_need_support: 2,
      q5_well_integrated: 4,
      q6_too_much_inconsistency: 2,
      q7_learn_quickly: 4,
      q8_very_cumbersome: 2,
      q9_very_confident: 4,
      q10_learn_lot_before: 2
    });

    const susQuestions = [
      "I think that I would like to use this system frequently",
      "I found the system unnecessarily complex",
      "I thought the system was easy to use",
      "I think that I would need the support of a technical person",
      "I found the various functions in this system were well integrated",
      "I thought there was too much inconsistency in this system",
      "I would imagine that most people would learn to use this system very quickly",
      "I found the system very cumbersome to use",
      "I felt very confident using the system",
      "I needed to learn a lot of things before I could get going with this system"
    ];

    const handleSubmit = async () => {
      const success = await submitSUS(susData);
      if (success) {
        setCurrentStep('satisfaction');
      }
    };

    return (
      <div className="measurement-step">
        <h2>System Usability Scale (SUS)</h2>
        <p>Rate your agreement with each statement (1=Strongly Disagree, 5=Strongly Agree):</p>

        <div className="sus-form">
          {susQuestions.map((question, index) => {
            const key = `q${index + 1}_${Object.keys(susData)[index].split('_').slice(1).join('_')}`;
            return (
              <div key={key} className="measurement-item">
                <label>
                  {question}
                  <select
                    value={susData[Object.keys(susData)[index]]}
                    onChange={(e) => setSusData(prev => ({
                      ...prev,
                      [Object.keys(susData)[index]]: parseInt(e.target.value)
                    }))}
                  >
                    <option value={1}>1 - Strongly Disagree</option>
                    <option value={2}>2 - Disagree</option>
                    <option value={3}>3 - Neutral</option>
                    <option value={4}>4 - Agree</option>
                    <option value={5}>5 - Strongly Agree</option>
                  </select>
                </label>
              </div>
            );
          })}
        </div>

        <button onClick={handleSubmit} className="primary-button">
          Submit SUS
        </button>
      </div>
    );
  };

  const renderSatisfaction = () => {
    const [satisfactionData, setSatisfactionData] = useState({
      overall_satisfaction: 5,
      ease_of_use: 5,
      recommendation_quality: 6,
      perceived_personalization: 6,
      decision_confidence: 5,
      enjoyment: 5,
      return_intention: 6
    });

    const handleSubmit = async () => {
      const success = await submitSatisfaction(satisfactionData);
      if (success) {
        setCurrentStep('summary');
        await getSessionSummary();
      }
    };

    return (
      <div className="measurement-step">
        <h2>Satisfaction Measurement</h2>
        <p>Rate your satisfaction on each dimension (1-7):</p>

        <div className="satisfaction-form">
          {Object.entries(satisfactionData).map(([key, value]) => (
            <div key={key} className="measurement-item">
              <label>
                {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                <input
                  type="range"
                  min="1"
                  max="7"
                  value={value}
                  onChange={(e) => setSatisfactionData(prev => ({
                    ...prev,
                    [key]: parseInt(e.target.value)
                  }))}
                />
                <span className="range-value">{value}</span>
              </label>
            </div>
          ))}
        </div>

        <button onClick={handleSubmit} className="primary-button">
          Submit Satisfaction
        </button>
      </div>
    );
  };

  const renderSummary = () => (
    <div className="measurement-step">
      <h2>Session Summary</h2>

      {sessionSummary ? (
        <div className="summary-content">
          <div className="summary-section">
            <h3>Session Information</h3>
            <p><strong>Session ID:</strong> {sessionSummary.session_id}</p>
            <p><strong>Condition:</strong> {sessionSummary.condition}</p>
            <p><strong>Timestamp:</strong> {new Date(sessionSummary.timestamp).toLocaleString()}</p>
          </div>

          {sessionSummary.nasa_tlx && (
            <div className="summary-section">
              <h3>NASA-TLX Results</h3>
              <p><strong>Overall Workload:</strong> {sessionSummary.nasa_tlx.overall_workload}</p>
              <p><strong>Mental Demand:</strong> {sessionSummary.nasa_tlx.mental_demand}</p>
              <p><strong>Frustration:</strong> {sessionSummary.nasa_tlx.frustration}</p>
            </div>
          )}

          {sessionSummary.sus_score && (
            <div className="summary-section">
              <h3>SUS Results</h3>
              <p><strong>SUS Score:</strong> {sessionSummary.sus_score} / 100</p>
              <p className="sus-interpretation">
                {sessionSummary.sus_score >= 80 ? 'Excellent' :
                 sessionSummary.sus_score >= 70 ? 'Good' :
                 sessionSummary.sus_score >= 50 ? 'OK' : 'Poor'} usability
              </p>
            </div>
          )}

          {sessionSummary.task_completion && (
            <div className="summary-section">
              <h3>Task Performance</h3>
              <p><strong>Completion Time:</strong> {sessionSummary.task_completion.completion_time_minutes} minutes</p>
              <p><strong>Success:</strong> {sessionSummary.task_completion.success ? 'Yes' : 'No'}</p>
              <p><strong>Completion Rate:</strong> {(sessionSummary.task_completion.completion_rate * 100).toFixed(1)}%</p>
            </div>
          )}

          {sessionSummary.satisfaction && (
            <div className="summary-section">
              <h3>Satisfaction Results</h3>
              <p><strong>Overall Satisfaction:</strong> {sessionSummary.satisfaction.overall_satisfaction} / 7</p>
              <p><strong>Recommendation Quality:</strong> {sessionSummary.satisfaction.recommendation_quality} / 7</p>
              <p><strong>Perceived Personalization:</strong> {sessionSummary.satisfaction.perceived_personalization} / 7</p>
            </div>
          )}

          <div className="summary-section">
            <h3>Error and Decision Tracking</h3>
            <p><strong>Error Count:</strong> {sessionSummary.error_count}</p>
            <p><strong>Decision Changes:</strong> {sessionSummary.decision_changes}</p>
          </div>
        </div>
      ) : (
        <p>Loading session summary...</p>
      )}

      <button onClick={() => {
        setCurrentStep('intro');
        setSessionId(`demo_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
        setSessionSummary(null);
        setMeasurements({
          nasaTlx: {},
          sus: {},
          taskCompletion: {},
          satisfaction: {},
          errors: [],
          decisionChanges: []
        });
      }} className="primary-button">
        Start New Demo
      </button>
    </div>
  );

  return (
    <div className="measurement-demo">
      <div className="demo-header">
        <h1>MPID Measurement System Demo</h1>
        <div className="progress-indicator">
          <span className={currentStep === 'intro' ? 'active' : 'completed'}>Intro</span>
          <span className={currentStep === 'task' ? 'active' : currentStep === 'intro' ? '' : 'completed'}>Task</span>
          <span className={currentStep === 'nasa_tlx' ? 'active' : ['intro', 'task'].includes(currentStep) ? '' : 'completed'}>NASA-TLX</span>
          <span className={currentStep === 'sus' ? 'active' : ['intro', 'task', 'nasa_tlx'].includes(currentStep) ? '' : 'completed'}>SUS</span>
          <span className={currentStep === 'satisfaction' ? 'active' : ['intro', 'task', 'nasa_tlx', 'sus'].includes(currentStep) ? '' : 'completed'}>Satisfaction</span>
          <span className={currentStep === 'summary' ? 'active' : ''}>Summary</span>
        </div>
      </div>

      <div className="demo-content">
        {currentStep === 'intro' && renderIntro()}
        {currentStep === 'task' && renderTask()}
        {currentStep === 'nasa_tlx' && renderNASATLX()}
        {currentStep === 'sus' && renderSUS()}
        {currentStep === 'satisfaction' && renderSatisfaction()}
        {currentStep === 'summary' && renderSummary()}
      </div>
    </div>
  );
};

export default MeasurementDemo;