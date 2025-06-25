import React, { useState, useEffect } from 'react';
import * as apiService from './services/api';
import './MasterRecommendationPanel.css';

const MasterRecommendationPanel = ({ userId, onRecommendationsChange }) => {
  const [userContext, setUserContext] = useState({
    user_id: userId || 'guest',
    location: '',
    weather: { condition: 'sunny', temperature: 22 },
    time_of_day: 'afternoon',
    activity_level: 'work',
    mood: 'neutral',
    health_conditions: [],
    dietary_restrictions: [],
    allergens: [],
    order_history: [],
    session_context: {},
    social_context: {}
  });

  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [explanations, setExplanations] = useState({});
  const [agentContributions, setAgentContributions] = useState({});
  const [systemHealth, setSystemHealth] = useState({});
  const [processingTime, setProcessingTime] = useState(0);
  const [confidence, setConfidence] = useState(0);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const timeOfDayOptions = ['morning', 'afternoon', 'evening'];
  const activityLevelOptions = ['work', 'gym', 'study', 'chilling', 'active'];
  const moodOptions = ['happy', 'sad', 'stressed', 'energetic', 'relaxed', 'excited', 'tired', 'neutral'];

  useEffect(() => {
    checkSystemHealth();
  }, []);

  const checkSystemHealth = async () => {
    try {
      const response = await apiService.get('/master/health');
      setSystemHealth(response.data);
    } catch (error) {
      console.error('Error checking system health:', error);
      setSystemHealth({ status: 'error', components: {} });
    }
  };

  const handleContextChange = (field, value) => {
    setUserContext(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const getComprehensiveRecommendations = async () => {
    setLoading(true);
    try {
      const response = await apiService.post('/master/recommendations/comprehensive', {
        user_context: userContext,
        n_recommendations: 5,
        include_explanations: true
      });

      if (response.data.success) {
        setRecommendations(response.data.recommendations);
        setExplanations(response.data.explanations || {});
        setAgentContributions(response.data.agent_contributions || {});
        setProcessingTime(response.data.processing_time_ms || 0);
        setConfidence(response.data.confidence || 0);
      }
    } catch (error) {
      console.error('Error getting comprehensive recommendations:', error);
      alert('Error getting recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="master-recommendation-panel">
      <div className="panel-header">
        <h2>🎯 AI Recommendation Engine</h2>
        <button onClick={() => setShowAdvanced(!showAdvanced)}>
          {showAdvanced ? '📊 Hide Advanced' : '⚙️ Show Advanced'}
        </button>
      </div>

      <div className="context-configuration">
        <h3>🎨 User Context</h3>
        <div className="context-grid">
          <div className="context-group">
            <label>Activity Level:</label>
            <select
              value={userContext.activity_level}
              onChange={(e) => handleContextChange('activity_level', e.target.value)}
            >
              {activityLevelOptions.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>

          <div className="context-group">
            <label>Current Mood:</label>
            <select
              value={userContext.mood}
              onChange={(e) => handleContextChange('mood', e.target.value)}
            >
              {moodOptions.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="action-buttons">
        <button onClick={getComprehensiveRecommendations} disabled={loading}>
          {loading ? '🔄 Processing...' : '🚀 Get AI Recommendations'}
        </button>
      </div>

      <div className="recommendations-section">
        <h3>🍽️ Personalized Recommendations</h3>
        {recommendations.length > 0 ? (
          <div className="recommendations-grid">
            {recommendations.map((rec, index) => (
              <div key={index} className="recommendation-card">
                <h4>{rec.item}</h4>
                <p>Category: {rec.category}</p>
                <p>Confidence: {(rec.confidence * 100).toFixed(0)}%</p>
                {rec.reasoning && <p>{rec.reasoning}</p>}
              </div>
            ))}
          </div>
        ) : (
          <p>No recommendations yet. Click "Get AI Recommendations" to start!</p>
        )}
      </div>
    </div>
  );
};

export default MasterRecommendationPanel;
