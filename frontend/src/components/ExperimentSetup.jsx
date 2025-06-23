import React, { useState } from 'react';
import { useExperiment } from '../context/ExperimentContext';

const ExperimentSetup = ({ onExperimentStart }) => {
  const { initializeExperiment } = useExperiment();
  const [participantId, setParticipantId] = useState('');
  const [selectedTrialType, setSelectedTrialType] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleStartExperiment = async () => {
    if (!participantId.trim() || !selectedTrialType) {
      alert('Please enter participant ID and select trial type');
      return;
    }

    setIsLoading(true);

    try {
      const config = {
        participantId: participantId.trim(),
        trialType: selectedTrialType,
        startTime: new Date().toISOString()
      };

      const experimentConfig = initializeExperiment(config);

      console.log('Experiment initialized:', experimentConfig);

      if (onExperimentStart) {
        onExperimentStart(experimentConfig);
      }
    } catch (error) {
      console.error('Error starting experiment:', error);
      alert('Error starting experiment. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-6">
      <div className="bg-white rounded-xl shadow-2xl p-8 max-w-2xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🍛 Curry Creations Experiment
          </h1>
          <p className="text-gray-600">
            Comparative Study: Baseline vs Emotion-Responsive Interface
          </p>
        </div>

        <div className="space-y-6">
          {/* Participant ID Input */}
          <div>
            <label htmlFor="participantId" className="block text-sm font-medium text-gray-700 mb-2">
              Participant ID
            </label>
            <input
              id="participantId"
              type="text"
              value={participantId}
              onChange={(e) => setParticipantId(e.target.value)}
              placeholder="Enter participant ID (e.g., P001)"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
          </div>

          {/* Trial Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Select Trial Type
            </label>
            <div className="space-y-3">
              {/* Trial A - Baseline */}
              <div
                onClick={() => !isLoading && setSelectedTrialType('A')}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  selectedTrialType === 'A'
                    ? 'border-orange-500 bg-orange-50'
                    : 'border-gray-200 hover:border-orange-300'
                } ${isLoading ? 'cursor-not-allowed opacity-50' : ''}`}
              >
                <div className="flex items-center">
                  <input
                    type="radio"
                    name="trialType"
                    value="A"
                    checked={selectedTrialType === 'A'}
                    onChange={() => !isLoading && setSelectedTrialType('A')}
                    className="mr-3 text-orange-600"
                    disabled={isLoading}
                  />
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg text-orange-800">
                      🔬 Trial A: Baseline Study
                    </h3>
                    <p className="text-gray-600 text-sm mt-1">
                      Standard interface with no AI recommendations or mood tracking
                    </p>
                    <ul className="text-sm text-orange-700 mt-2 space-y-1">
                      <li>• 5 trials total</li>
                      <li>• 3 free choice orders + 2 guided orders</li>
                      <li>• No personalized suggestions</li>
                      <li>• Baseline performance measurement</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Trial B - Emotion-Responsive */}
              <div
                onClick={() => !isLoading && setSelectedTrialType('B')}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  selectedTrialType === 'B'
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-green-300'
                } ${isLoading ? 'cursor-not-allowed opacity-50' : ''}`}
              >
                <div className="flex items-center">
                  <input
                    type="radio"
                    name="trialType"
                    value="B"
                    checked={selectedTrialType === 'B'}
                    onChange={() => !isLoading && setSelectedTrialType('B')}
                    className="mr-3 text-green-600"
                    disabled={isLoading}
                  />
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg text-green-800">
                      😊 Trial B: Emotion-Responsive Study
                    </h3>
                    <p className="text-gray-600 text-sm mt-1">
                      Enhanced interface with face recognition, mood tracking, and AI suggestions
                    </p>
                    <ul className="text-sm text-green-700 mt-2 space-y-1">
                      <li>• 5 trials total</li>
                      <li>• 3 free choice orders + 2 flexible guided orders</li>
                      <li>• Real-time mood tracking</li>
                      <li>• Weather and health-based recommendations</li>
                      <li>• Face recognition authentication</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Experimental Design Information */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-800 mb-2">📋 Experimental Design</h4>
            <div className="text-sm text-blue-700 space-y-1">
              <p><strong>Study Structure:</strong> 50 participants × 5 trials each = 250 data points per trial type</p>
              <p><strong>Trial Order:</strong> All participants complete Trial A first, then Trial B</p>
              <p><strong>Free Choice Trials:</strong> Trials 1, 2, 3 - participants order as they like</p>
              <p><strong>Guided Trials:</strong> Trials 4, 5 - specific orders provided</p>
              <p><strong>Measurements:</strong> Time, NASA-TLX workload, SUS usability, mood progression</p>
            </div>
          </div>

          {/* Start Button */}
          <div className="flex justify-center pt-4">
            <button
              onClick={handleStartExperiment}
              disabled={!participantId.trim() || !selectedTrialType || isLoading}
              className={`
                px-8 py-3 rounded-lg text-white font-semibold transition-all flex items-center
                ${!participantId.trim() || !selectedTrialType || isLoading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : selectedTrialType === 'A'
                    ? 'bg-orange-600 hover:bg-orange-700 transform hover:scale-105'
                    : 'bg-green-600 hover:bg-green-700 transform hover:scale-105'}
              `}
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Initializing...
                </>
              ) : (
                <>
                  {selectedTrialType === 'A' ? '🔬 Start Baseline Study' : '😊 Start Emotion-Responsive Study'}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExperimentSetup;