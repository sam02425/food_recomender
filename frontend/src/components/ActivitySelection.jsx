// frontend/src/components/ActivitySelection.jsx
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * Production-level component for activity selection with experimental design support
 * Supports Trial A (Baseline) and Trial B (Emotion-responsive) configurations
 */
const ActivitySelection = ({ onActivitySelected, onSelect, isLoading = false, experimentConfig = null }) => {
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [orderInstructions, setOrderInstructions] = useState('');

  // Determine if this is Trial A (baseline) or Trial B (emotion-responsive)
  const isTrialA = experimentConfig?.trialType === 'A';
  const isTrialB = experimentConfig?.trialType === 'B';
  const trialNumber = experimentConfig?.trialNumber || 1;
  const isSpecificOrderTrial = experimentConfig?.isSpecificOrder || false;

  // Predefined specific orders for trials
  const specificOrders = [
    "Bowl + Chicken Protein + Marinara Sauce + Onion + Pineapple Toppings",
    "Wrap + Beef Protein + Pesto Sauce + Bell Peppers + Mushroom Toppings",
    "Salad + Tofu Protein + Ranch Sauce + Tomatoes + Cucumber Toppings",
    "Bowl + Salmon Protein + Teriyaki Sauce + Broccoli + Corn Toppings",
    "Wrap + Turkey Protein + BBQ Sauce + Spinach + Cheese Toppings"
  ];

  // Get specific order for this trial
  const getSpecificOrder = () => {
    const orderIndex = (trialNumber - 1) % specificOrders.length;
    return specificOrders[orderIndex];
  };

  // Activity data with baseline option for Trial A
  const getActivities = () => {
    const baseActivities = [
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

    // Add baseline option for Trial A, disable for Trial B
    if (isTrialA) {
      baseActivities.unshift({
        id: 'experiment_baseline',
        label: 'Experiment A Baseline',
        icon: '🔬',
        description: 'Standard interface with no personalized suggestions',
        recommendation: 'No AI recommendations will be provided',
        isBaseline: true
      });
    } else if (isTrialB) {
      // In Trial B, add baseline option but disabled
      baseActivities.unshift({
        id: 'experiment_baseline',
        label: 'Experiment A Baseline',
        icon: '🔬',
        description: 'Not available in emotion-responsive trials',
        recommendation: 'This option is disabled for Trial B',
        isBaseline: true,
        disabled: true
      });
    }

    return baseActivities;
  };

  // Generate order instructions based on trial configuration
  useEffect(() => {
    if (!experimentConfig) return;

    let instructions = '';

    if (isSpecificOrderTrial) {
      const specificOrder = getSpecificOrder();
      if (isTrialA) {
        instructions = `Please place this specific order: ${specificOrder}`;
      } else if (isTrialB) {
        instructions = `Suggestion: ${specificOrder} (You may change this order if you prefer)`;
      }
    } else {
      instructions = "Please place an order as you like";
    }

    setOrderInstructions(instructions);
  }, [experimentConfig, trialNumber, isSpecificOrderTrial, isTrialA, isTrialB]);

  // Handle activity selection
  const handleSelect = (activityId) => {
    const activities = getActivities();
    const activity = activities.find(a => a.id === activityId);

    // Prevent selection of disabled options
    if (activity?.disabled) {
      return;
    }

    setSelectedActivity(activityId);
  };

  // Submit the selected activity with experimental data
  const handleSubmit = () => {
    if (selectedActivity) {
      const experimentData = {
        trialType: experimentConfig?.trialType || 'unknown',
        trialNumber: experimentConfig?.trialNumber || 1,
        isSpecificOrder: experimentConfig?.isSpecificOrder || false,
        orderInstructions: orderInstructions,
        selectedActivity: selectedActivity,
        isBaseline: selectedActivity === 'experiment_baseline',
        timestamp: new Date().toISOString()
      };

      const callback = typeof onActivitySelected === 'function' ? onActivitySelected : (typeof onSelect === 'function' ? onSelect : null);
      if (callback) {
        callback(selectedActivity, experimentData);
      } else {
        console.error('No valid activity selection callback provided.');
      }
    }
  };

  const activities = getActivities();

  return (
    <div className="py-6 animate-fadeIn" role="region" aria-label="Activity Selection">
      {/* Experimental Trial Header */}
      {experimentConfig && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="text-center">
            <h3 className="font-bold text-lg text-blue-800">
              {isTrialA && "Trial A: Baseline Study"}
              {isTrialB && "Trial B: Emotion-Responsive Study"}
            </h3>
            <p className="text-blue-600 mt-1">
              Trial {trialNumber} of 5 {isSpecificOrderTrial ? "(Guided Order)" : "(Free Choice)"}
            </p>
          </div>
        </div>
      )}

      {/* Order Instructions */}
      {orderInstructions && (
        <div className={`mb-6 p-4 rounded-lg border-l-4 ${
          isSpecificOrderTrial
            ? (isTrialA ? 'bg-orange-50 border-orange-400' : 'bg-green-50 border-green-400')
            : 'bg-gray-50 border-gray-400'
        }`}>
          <h4 className="font-semibold mb-2">
            {isSpecificOrderTrial
              ? (isTrialA ? "Required Order:" : "Suggested Order:")
              : "Instructions:"
            }
          </h4>
          <p className="text-gray-700">{orderInstructions}</p>
          {isTrialB && isSpecificOrderTrial && (
            <p className="text-sm text-green-600 mt-2">
              💡 Feel free to modify this suggestion based on your preferences
            </p>
          )}
        </div>
      )}

      <h2 className="text-2xl font-bold mb-3 text-center" id="activity-heading">What are you up to today?</h2>
      <p className="text-gray-600 mb-6 text-center">
        {isTrialA && selectedActivity === 'experiment_baseline'
          ? "Standard interface mode - no personalized recommendations"
          : "We'll customize your recommendations based on your activity"
        }
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
              ${activity.disabled
                ? 'border-gray-300 bg-gray-100 cursor-not-allowed opacity-50'
                : selectedActivity === activity.id
                  ? (activity.isBaseline
                      ? 'border-orange-500 bg-orange-50 shadow-md transform scale-[1.02]'
                      : 'border-blue-500 bg-blue-50 shadow-md transform scale-[1.02]')
                  : 'border-gray-200 hover:border-blue-300 hover:shadow-sm'
              }
            `}
            role="radio"
            aria-checked={selectedActivity === activity.id}
            tabIndex={activity.disabled ? -1 : 0}
            aria-label={`${activity.label}: ${activity.description}`}
            aria-disabled={activity.disabled}
          >
            <div className="text-3xl mr-4">{activity.icon}</div>
            <div className="flex-1">
              <h3 className={`font-medium text-lg ${activity.disabled ? 'text-gray-500' : ''}`}>
                {activity.label}
              </h3>
              <p className={`text-sm ${activity.disabled ? 'text-gray-400' : 'text-gray-600'}`}>
                {activity.description}
              </p>

              {selectedActivity === activity.id && !activity.disabled && (
                <p className={`text-sm mt-1 animate-fadeIn ${
                  activity.isBaseline ? 'text-orange-600' : 'text-blue-600'
                }`}>
                  <span className="font-medium">
                    {activity.isBaseline ? 'Mode:' : 'Recommended:'}
                  </span> {activity.recommendation}
                </p>
              )}
            </div>

            {selectedActivity === activity.id && !activity.disabled && (
              <div className={`ml-3 ${activity.isBaseline ? 'text-orange-600' : 'text-blue-600'}`}>
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
              : selectedActivity === 'experiment_baseline'
                ? 'bg-orange-600 hover:bg-orange-700 transform hover:scale-105'
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
          ) : (
            <>
              {selectedActivity === 'experiment_baseline' ? '🔬 Start Baseline Trial' : 'Continue'}
            </>
          )}
        </button>
      </div>

      {/* Experimental Notes */}
      {experimentConfig && (
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>
            Participant will complete {isTrialA ? "5 baseline trials" : "5 emotion-responsive trials"}
            {isTrialA ? " (no AI suggestions)" : " (with mood tracking)"}
          </p>
        </div>
      )}
    </div>
  );
};

ActivitySelection.propTypes = {
  onActivitySelected: PropTypes.func,
  onSelect: PropTypes.func,
  isLoading: PropTypes.bool,
  experimentConfig: PropTypes.shape({
    trialType: PropTypes.oneOf(['A', 'B']),
    trialNumber: PropTypes.number,
    isSpecificOrder: PropTypes.bool,
    participantId: PropTypes.string
  })
};

export default ActivitySelection;