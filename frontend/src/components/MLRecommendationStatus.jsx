import React from 'react';

const MLRecommendationStatus = ({
  mlRecommendations,
  mlConfidence,
  recommendationMode,
  onModeChange,
  explanations = {}
}) => {
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSourceIcon = (source) => {
    switch (source) {
      case 'ml_primary': return '🤖';
      case 'traditional_fallback': return '🏛️';
      case 'hybrid': return '🔀';
      default: return '📊';
    }
  };

  if (!mlRecommendations) return null;

  return (
    <div className="bg-gray-50 rounded-lg p-4 mb-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700">
          Recommendation System Status
        </h3>

        {/* Mode Toggle */}
        <div className="flex gap-1 text-xs">
          <button
            onClick={() => onModeChange('smart')}
            className={`px-2 py-1 rounded ${
              recommendationMode === 'smart'
                ? 'bg-blue-500 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            Smart
          </button>
          <button
            onClick={() => onModeChange('ml_only')}
            className={`px-2 py-1 rounded ${
              recommendationMode === 'ml_only'
                ? 'bg-purple-500 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            ML Only
          </button>
          <button
            onClick={() => onModeChange('traditional_only')}
            className={`px-2 py-1 rounded ${
              recommendationMode === 'traditional_only'
                ? 'bg-gray-500 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            Traditional
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        {/* Source and Confidence */}
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">{getSourceIcon(mlRecommendations.source)}</span>
            <span className="font-medium">
              {mlRecommendations.source === 'ml_primary' ? 'ML-Powered' :
               mlRecommendations.source === 'traditional_fallback' ? 'Traditional' :
               mlRecommendations.source === 'hybrid' ? 'Hybrid' : 'Smart'}
            </span>
          </div>
          <div className="text-xs text-gray-600">
            Confidence: <span className={`font-semibold ${getConfidenceColor(mlConfidence)}`}>
              {Math.round(mlConfidence * 100)}%
            </span>
          </div>
        </div>

        {/* Recommendation Count */}
        <div>
          <div className="font-medium mb-1">
            {mlRecommendations.recommendations?.length || 0} Recommendations
          </div>
          <div className="text-xs text-gray-600">
            {mlRecommendations.sources && Object.keys(mlRecommendations.sources).length > 0 && (
              <span>
                Sources: {Object.keys(mlRecommendations.sources).join(', ')}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Explanation */}
      {explanations.overview && (
        <div className="mt-3 p-2 bg-blue-50 rounded text-xs text-blue-800">
          <strong>Why these recommendations:</strong> {explanations.overview}
        </div>
      )}

      {/* Debug Info (only in development) */}
      {process.env.NODE_ENV === 'development' && mlRecommendations && (
        <details className="mt-2">
          <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
            Debug Info
          </summary>
          <pre className="text-xs bg-gray-100 p-2 rounded mt-1 overflow-auto max-h-32">
            {JSON.stringify({
              mode: recommendationMode,
              confidence: mlConfidence,
              source: mlRecommendations.source,
              recommendations: mlRecommendations.recommendations?.length,
              timestamp: mlRecommendations.timestamp
            }, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
};

export default MLRecommendationStatus;