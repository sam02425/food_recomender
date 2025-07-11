import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const AgentRecommendations = ({
  isVisible = false,
  orderDetails = {},
  onRefreshmentSelect,
  onAgentInteraction
}) => {
  const [agentData, setAgentData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedRefreshment, setSelectedRefreshment] = useState(null);

  const fetchAgentRecommendations = async () => {
    if (!isVisible || !orderDetails) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/agent-recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'user_123',
          context: {
            mood: 'neutral',
            activityLevel: 'work',
            timeOfDay: new Date().getHours() < 12 ? 'morning' : 'afternoon'
          },
          order_details: orderDetails
        })
      });

      if (!response.ok) {
        throw new Error('Failed to fetch agent recommendations');
      }

      const data = await response.json();
      setAgentData(data);

      // Track agent interaction for experiment
      if (onAgentInteraction) {
        onAgentInteraction({
          type: 'agent_recommendations_fetched',
          agents_called: data.agents_called,
          preparation_time: data.preparation_time,
          timestamp: new Date().toISOString()
        });
      }

    } catch (err) {
      setError(err.message);
      console.error('Error fetching agent recommendations:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isVisible && orderDetails) {
      fetchAgentRecommendations();
    }
  }, [isVisible, orderDetails]);

  const handleRefreshmentSelect = (refreshment) => {
    setSelectedRefreshment(refreshment);
    if (onRefreshmentSelect) {
      onRefreshmentSelect(refreshment);
    }
  };

  const getAgentIcon = (agentType) => {
    const icons = {
      context_intelligence: '🧠',
      preference_learning: '📚',
      preparation_time: '⏱️'
    };
    return icons[agentType] || '🤖';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      high: 'text-red-600 bg-red-50 border-red-200',
      medium: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      low: 'text-green-600 bg-green-50 border-green-200'
    };
    return colors[priority] || colors.low;
  };

  if (!isVisible) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">
          🤖 AI Agent Recommendations
        </h3>
        <div className="flex items-center space-x-2">
          {isLoading && (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          )}
          <button
            onClick={fetchAgentRecommendations}
            disabled={isLoading}
            className="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
          >
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
          <p className="text-red-600 text-sm">Error: {error}</p>
        </div>
      )}

      {agentData && (
        <div className="space-y-4">
          {/* Preparation Time Display */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-semibold text-blue-900">⏱️ Preparation Time</h4>
                <p className="text-sm text-blue-700">
                  Queue Position: #{agentData.preparation_time.queue_position}
                </p>
                {agentData.preparation_time.complexity_multiplier > 1.0 && (
                  <p className="text-sm text-blue-700">
                    Complexity: {agentData.preparation_time.complexity_multiplier}x
                  </p>
                )}
                {agentData.preparation_time.additional_wait_time > 0 && (
                  <p className="text-sm text-orange-700">
                    ⚠️ Additional wait: {agentData.preparation_time.additional_wait_time} minutes
                  </p>
                )}
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-blue-900">
                  {agentData.preparation_time.formatted_duration}
                </div>
                <div className="text-sm text-blue-700">
                  Ready at {agentData.preparation_time.ready_time}
                </div>
              </div>
            </div>
          </div>

          {/* Inventory Status */}
          {(agentData.preparation_time.unavailable_items?.length > 0 ||
            agentData.preparation_time.low_stock_items?.length > 0 ||
            agentData.preparation_time.preparing_items?.length > 0) && (
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <h4 className="font-semibold text-orange-900 mb-3">📦 Inventory Status</h4>

              {agentData.preparation_time.unavailable_items?.length > 0 && (
                <div className="mb-2">
                  <div className="text-sm font-medium text-red-700">❌ Out of Stock:</div>
                  <div className="text-xs text-red-600 ml-2">
                    {agentData.preparation_time.unavailable_items.join(', ')}
                  </div>
                </div>
              )}

              {agentData.preparation_time.low_stock_items?.length > 0 && (
                <div className="mb-2">
                  <div className="text-sm font-medium text-yellow-700">⚠️ Low Stock:</div>
                  <div className="text-xs text-yellow-600 ml-2">
                    {agentData.preparation_time.low_stock_items.join(', ')}
                  </div>
                </div>
              )}

              {agentData.preparation_time.preparing_items?.length > 0 && (
                <div className="mb-2">
                  <div className="text-sm font-medium text-blue-700">🔄 Being Prepared:</div>
                  <div className="text-xs text-blue-600 ml-2">
                    {agentData.preparation_time.preparing_items.join(', ')}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Agent Recommendations */}
          <div className="space-y-3">
            <h4 className="font-semibold text-gray-900">Agent Insights</h4>

            {Object.entries(agentData.recommendations).map(([agentType, recommendations]) => (
              <div key={agentType} className="border border-gray-200 rounded-md p-3">
                <div className="flex items-center mb-2">
                  <span className="text-lg mr-2">{getAgentIcon(agentType)}</span>
                  <h5 className="font-medium text-gray-900 capitalize">
                    {agentType.replace('_', ' ')} Agent
                  </h5>
                </div>

                {recommendations.map((rec, index) => (
                  <div
                    key={index}
                    className={`border rounded-md p-2 mb-2 ${getPriorityColor(rec.priority)}`}
                  >
                    <div className="font-medium text-sm">{rec.title}</div>
                    <div className="text-xs mt-1">{rec.message}</div>
                  </div>
                ))}
              </div>
            ))}
          </div>

          {/* Refreshment Suggestions */}
          {agentData.refreshment_suggestions && agentData.refreshment_suggestions.length > 0 && (
            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-3">
                🥤 While You Wait - Refreshment Suggestions
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {agentData.refreshment_suggestions.map((drink, index) => (
                  <div
                    key={index}
                    className={`border rounded-md p-3 cursor-pointer transition-colors ${
                      selectedRefreshment?.name === drink.name
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleRefreshmentSelect(drink)}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-medium text-gray-900">{drink.name}</div>
                        <div className="text-sm text-gray-600 mt-1">{drink.reason}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold text-gray-900">${drink.price}</div>
                        {selectedRefreshment?.name === drink.name && (
                          <div className="text-blue-600 text-sm">✓ Selected</div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Optimization Strategies */}
          {agentData.optimization_strategies && agentData.optimization_strategies.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="font-semibold text-yellow-900 mb-3">
                💡 Optimization Suggestions
              </h4>
              {agentData.optimization_strategies.map((strategy, index) => (
                <div key={index} className="mb-3 last:mb-0">
                  <div className="font-medium text-yellow-900">{strategy.title}</div>
                  <div className="text-sm text-yellow-800 mt-1">{strategy.message}</div>
                  {strategy.suggestions && (
                    <div className="text-xs text-yellow-700 mt-2">
                      <strong>Suggestions:</strong> {strategy.suggestions.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Agent Status Footer */}
          <div className="text-xs text-gray-500 border-t pt-3">
            <div className="flex items-center justify-between">
              <span>Agents Active: {agentData.agents_called.join(', ')}</span>
              <span>Last Updated: {new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

AgentRecommendations.propTypes = {
  isVisible: PropTypes.bool,
  orderDetails: PropTypes.object,
  onRefreshmentSelect: PropTypes.func,
  onAgentInteraction: PropTypes.func
};

export default AgentRecommendations;