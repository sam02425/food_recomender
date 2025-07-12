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
      // Call the real 3-agent system endpoint
      const response = await fetch('http://localhost:8000/api/agent-recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userContext.user_id,
          context: {
            activity_level: userContext.activity_level,
            mood: userContext.mood,
            time_of_day: userContext.time_of_day,
            weather: userContext.weather,
            location: userContext.location
          },
          order_details: {} // Empty for initial recommendations
        })
      });

      if (response.ok) {
        const data = await response.json();

        // Transform agent recommendations into displayable format
        const transformedRecommendations = [];

        if (data.recommendations) {
          // Add context intelligence recommendations
          if (data.recommendations.context_intelligence) {
            data.recommendations.context_intelligence.forEach(rec => {
              transformedRecommendations.push({
                item: rec.title,
                category: 'context_intelligence',
                confidence: 0.8,
                reasoning: rec.message,
                priority: rec.priority
              });
            });
          }

          // Add preference learning recommendations
          if (data.recommendations.preference_learning) {
            data.recommendations.preference_learning.forEach(rec => {
              transformedRecommendations.push({
                item: rec.title,
                category: 'preference_learning',
                confidence: rec.confidence || 0.7,
                reasoning: rec.reasoning || rec.message,
                priority: rec.priority
              });
            });
          }

          // Add preparation time recommendations
          if (data.recommendations.preparation_time) {
            data.recommendations.preparation_time.forEach(rec => {
              transformedRecommendations.push({
                item: rec.title,
                category: 'preparation_time',
                confidence: 0.9,
                reasoning: rec.message,
                priority: rec.priority
              });
            });
          }
        }

        setRecommendations(transformedRecommendations);
      } else {
        console.error('Failed to get recommendations:', response.status);
        setRecommendations([]);
      }
    } catch (error) {
      console.error('Error getting recommendations:', error);
      setRecommendations([]);
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
                <p>Priority: {rec.priority}</p>
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
