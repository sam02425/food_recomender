import React from 'react';

/**
 * Component for gathering feedback on recommendations.
 * Provides three options: Ignore, Accept, or provide Custom feedback.
 */
const RecommendationFeedback = ({
  onIgnore,
  onAccept,
  onCustom,
  customValue = '',
  setCustomValue,
  itemType,
  recommendedItem = null
}) => {
  return (
    <div className="my-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
      <h3 className="text-lg font-medium mb-3">What do you think of our recommendation?</h3>

      {recommendedItem && (
        <div className="mb-4 p-3 bg-blue-50 rounded-md">
          <p className="font-medium">We recommend: <span className="text-blue-600">{recommendedItem}</span></p>
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={onIgnore}
          className="flex-1 py-2 px-4 bg-gray-200 hover:bg-gray-300 rounded-md text-gray-800 transition-colors"
        >
          Ignore
        </button>

        <button
          onClick={onAccept}
          className="flex-1 py-2 px-4 bg-green-600 hover:bg-green-700 rounded-md text-white transition-colors"
        >
          Accept
        </button>

        <div className="flex-1 flex gap-2">
          <input
            type="text"
            value={customValue}
            onChange={(e) => setCustomValue(e.target.value)}
            placeholder={`My ${itemType}...`}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={() => onCustom(customValue)}
            disabled={!customValue.trim()}
            className={`px-3 py-2 rounded-md text-white transition-colors ${
              customValue.trim() ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-400 cursor-not-allowed'
            }`}
          >
            Apply
          </button>
        </div>
      </div>
    </div>
  );
};

export default RecommendationFeedback;