import React, { useState } from 'react';
import './MasterRecommendationPanel.css';

const MasterRecommendationPanel = ({ userId }) => {
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
  const [showAdvanced, setShowAdvanced] = useState(false);

  const activityLevelOptions = ['work', 'gym', 'study', 'chilling', 'active'];
  const moodOptions = ['happy', 'sad', 'stressed', 'energetic', 'relaxed', 'excited', 'tired', 'neutral'];

  const handleContextChange = (field, value) => {
    setUserContext(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const getComprehensiveRecommendations = async () => {
    setLoading(true);
    try {
      // Simulate recommendations based on context
      const mockRecommendations = [
        { item: 'Grilled Chicken', category: 'protein', confidence: 0.9, reasoning: 'Based on your active lifestyle' },
        { item: 'Brown Rice', category: 'base', confidence: 0.85, reasoning: 'Healthy carb option for sustained energy' },
        { item: 'Mixed Vegetables', category: 'vegetables', confidence: 0.8, reasoning: 'Nutrient-rich option for work day' }
      ];

      setTimeout(() => {
        setRecommendations(mockRecommendations);
        setLoading(false);
      }, 1000);

    } catch (error) {
      console.error('Error getting recommendations:', error);
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
            <label htmlFor="activity-select">Activity Level:</label>
            <select
              id="activity-select"
              value={userContext.activity_level}
              onChange={(e) => handleContextChange('activity_level', e.target.value)}
            >
              {activityLevelOptions.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>

          <div className="context-group">
            <label htmlFor="mood-select">Current Mood:</label>
            <select
              id="mood-select"
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
                {rec.reasoning && <p>&quot;{rec.reasoning}&quot;</p>}
              </div>
            ))}
          </div>
        ) : (
          <p>No recommendations yet. Click &quot;Get AI Recommendations&quot; to start!</p>
        )}
      </div>
    </div>
  );
};

export default MasterRecommendationPanel;
