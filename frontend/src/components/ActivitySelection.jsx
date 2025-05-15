// frontend/src/components/ActivitySelection.jsx
import React, { useState } from 'react';
import PropTypes from 'prop-types';

/**
 * Production-level component for activity selection with
 * animations, accessibility features, and thorough documentation.
 */
const ActivitySelection = ({ onActivitySelected, isLoading = false }) => {
  const [selectedActivity, setSelectedActivity] = useState(null);

  // Activity data with icons, descriptions, and recommendations
  const activities = [
    {
      id: 'study',
      label: 'Study',
      icon: '📚',
      description: 'Brain-boosting food for focus and concentration',
      recommendation: 'Balanced protein and complex carbs'
    },
    {
      id: 'active',
      label: 'Active/Gym',
      icon: '💪',
      description: 'Energy-rich options for an active lifestyle',
      recommendation: 'Protein-rich with moderate carbs'
    },
    {
      id: 'work',
      label: 'Work',
      icon: '💼',
      description: 'Balanced meals to keep you productive',
      recommendation: 'Varied nutrients with sustained energy'
    },
    {
      id: 'chilling',
      label: 'Chilling',
      icon: '🛋️',
      description: 'Comfort food for relaxation time',
      recommendation: 'Flavorful options with satisfaction'
    }
  ];

  // Handle activity selection
  const handleSelect = (activityId) => {
    setSelectedActivity(activityId);
  };

  // Submit the selected activity
  const handleSubmit = () => {
    if (selectedActivity) {
      onActivitySelected(selectedActivity);
    }
  };

  return (
    <div className="py-6 animate-fadeIn" role="region" aria-label="Activity Selection">
      <h2 className="text-2xl font-bold mb-3 text-center" id="activity-heading">What are you up to today?</h2>
      <p className="text-gray-600 mb-6 text-center">
        We'll customize your recommendations based on your activity
      </p>

      <div
        className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto mb-8"
        role="radiogroup"
        aria-labelledby="activity-heading"
      >
        {activities.map((activity) => (
          <div
            key={activity.id}
            onClick={() => handleSelect(activity.id)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleSelect(activity.id);
              }
            }}
            className={`
              p-4 rounded-lg border-2 cursor-pointer transition-all flex items-center
              ${selectedActivity === activity.id
                ? 'border-blue-500 bg-blue-50 shadow-md transform scale-[1.02]'
                : 'border-gray-200 hover:border-blue-300 hover:shadow-sm'}
            `}
            role="radio"
            aria-checked={selectedActivity === activity.id}
            tabIndex={0}
            aria-label={`${activity.label}: ${activity.description}`}
          >
            <div className="text-3xl mr-4">{activity.icon}</div>
            <div className="flex-1">
              <h3 className="font-medium text-lg">{activity.label}</h3>
              <p className="text-gray-600 text-sm">{activity.description}</p>

              {selectedActivity === activity.id && (
                <p className="text-blue-600 text-sm mt-1 animate-fadeIn">
                  <span className="font-medium">Recommended:</span> {activity.recommendation}
                </p>
              )}
            </div>

            {selectedActivity === activity.id && (
              <div className="ml-3 text-blue-600">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="flex justify-center">
        <button
          onClick={handleSubmit}
          disabled={!selectedActivity || isLoading}
          className={`
            px-6 py-2 rounded-md text-white transition-colors flex items-center
            ${!selectedActivity || isLoading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 transform hover:scale-105'}
          `}
          aria-busy={isLoading ? 'true' : 'false'}
        >
          {isLoading ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </>
          ) : 'Continue'}
        </button>
      </div>
    </div>
  );
};

ActivitySelection.propTypes = {
  onActivitySelected: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default ActivitySelection;