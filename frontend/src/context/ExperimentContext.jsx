import React, { createContext, useContext, useState, useRef } from 'react';

const ExperimentContext = createContext();

export const useExperiment = () => useContext(ExperimentContext);

export const ExperimentProvider = ({ children }) => {
  const [stepData, setStepData] = useState({});
  const [experimentConfig, setExperimentConfig] = useState(null);
  const [participantData, setParticipantData] = useState(null);
  const [currentTrial, setCurrentTrial] = useState(1);
  const [trialResults, setTrialResults] = useState([]);

  // Persistent dietary preferences across trials
  const [persistentDietaryPreferences, setPersistentDietaryPreferences] = useState({
    restrictions: [],
    allergens: [],
    setInTrial: null, // Track which trial they were first set
    lastUpdated: null
  });

  const [stepLock, setStepLock] = useState(false);

  const timerRef = useRef({});
  const moodRef = useRef({});

  // Initialize experiment configuration
  const initializeExperiment = (config) => {
    const experimentSetup = {
      participantId: config.participantId || `P${Date.now()}`,
      trialType: config.trialType, // 'A' for baseline, 'B' for emotion-responsive
      totalTrials: 5,
      startTime: new Date().toISOString(),
      ...config
    };

    setExperimentConfig(experimentSetup);
    setCurrentTrial(1);
    setTrialResults([]);

    // Generate trial schedule (3 free choice + 2 specific order)
    const trialSchedule = generateTrialSchedule();
    experimentSetup.trialSchedule = trialSchedule;

    return experimentSetup;
  };

  // Set dietary preferences (persistent across trials)
  const setDietaryPreferences = (restrictions = [], allergens = []) => {
    const preferences = {
      restrictions,
      allergens,
      setInTrial: currentTrial,
      lastUpdated: new Date().toISOString()
    };

    setPersistentDietaryPreferences(preferences);

    // Also store in localStorage for browser session persistence
    try {
      localStorage.setItem('foodapp_dietary_preferences', JSON.stringify(preferences));
    } catch (error) {
      console.warn('Could not save dietary preferences to localStorage:', error);
    }

    return preferences;
  };

  // Get dietary preferences
  const getDietaryPreferences = () => {
    // Try to load from localStorage if we don't have any set
    if (!persistentDietaryPreferences.setInTrial) {
      try {
        const stored = localStorage.getItem('foodapp_dietary_preferences');
        if (stored) {
          const parsed = JSON.parse(stored);
          setPersistentDietaryPreferences(parsed);
          return parsed;
        }
      } catch (error) {
        console.warn('Could not load dietary preferences from localStorage:', error);
      }
    }

    return persistentDietaryPreferences;
  };

  // Check if dietary preferences have been set
  const hasDietaryPreferences = () => {
    const prefs = getDietaryPreferences();
    return prefs.restrictions.length > 0 || prefs.allergens.length > 0;
  };

  // Clear dietary preferences
  const clearDietaryPreferences = () => {
    setPersistentDietaryPreferences({
      restrictions: [],
      allergens: [],
      setInTrial: null,
      lastUpdated: null
    });

    try {
      localStorage.removeItem('foodapp_dietary_preferences');
    } catch (error) {
      console.warn('Could not remove dietary preferences from localStorage:', error);
    }
  };

  // Generate randomized trial schedule
  const generateTrialSchedule = () => {
    const trials = [];

    // 3 free choice trials, 2 specific order trials
    for (let i = 1; i <= 5; i++) {
      trials.push({
        trialNumber: i,
        isSpecificOrder: i > 3, // Last 2 trials are specific order
        orderType: i > 3 ? 'specific' : 'free'
      });
    }

    return trials;
  };

  // Get current trial configuration
  const getCurrentTrialConfig = () => {
    if (!experimentConfig) return null;
    const trialSchedule = experimentConfig.trialSchedule || [];
    const trialInfo = trialSchedule.find(t => t.trialNumber === currentTrial);
    if (!trialInfo) {
      console.warn('[ExperimentContext] No trialInfo found for currentTrial', currentTrial, 'Returning experimentConfig fallback.');
      return {
        ...experimentConfig,
        trialNumber: currentTrial
      };
    }
    return {
      ...experimentConfig,
      ...trialInfo,
      trialNumber: currentTrial
    };
  };

  // Start a new trial
  const startTrial = (trialNumber = null) => {
    const trialNum = trialNumber || currentTrial;
    const trialConfig = getCurrentTrialConfig();

    console.log(`Starting Trial ${trialNum}:`, trialConfig);

    // Reset step data for new trial
    setStepData({});
    timerRef.current = {};
    moodRef.current = {};

    return trialConfig;
  };

  // Complete current trial and record results
  const completeTrial = (trialData) => {
    const trialConfig = getCurrentTrialConfig();

    const trialResult = {
      ...trialConfig,
      trialNumber: currentTrial,
      completedAt: new Date().toISOString(),
      stepData: { ...stepData },
      trialData: trialData,
      participantFollowedSuggestion: trialData?.followedSuggestion || null,
      orderPlaced: trialData?.orderItems || [],
      totalTime: calculateTotalTrialTime(),
      moodProgression: extractMoodProgression()
    };

    setTrialResults(prev => [...prev, trialResult]);

    // Move to next trial
    if (currentTrial < 5) {
      setCurrentTrial(prev => prev + 1);
    }

    return trialResult;
  };

  // Calculate total time spent in current trial
  const calculateTotalTrialTime = () => {
    return Object.values(stepData).reduce((total, step) => {
      return total + (step.time || 0);
    }, 0);
  };

  // Extract mood progression for analysis
  const extractMoodProgression = () => {
    const moodTimeline = [];

    Object.entries(stepData).forEach(([step, data]) => {
      if (data.moodTimeline) {
        moodTimeline.push({
          step,
          timeline: data.moodTimeline
        });
      }
    });

    return moodTimeline;
  };

  // Export experiment results for analysis
  const exportExperimentData = () => {
    return {
      experimentConfig,
      participantData,
      trialResults,
      completedTrials: trialResults.length,
      totalExperimentTime: trialResults.reduce((total, trial) => total + (trial.totalTime || 0), 0),
      exportTimestamp: new Date().toISOString(),
      summary: generateExperimentSummary()
    };
  };

  // Generate experiment summary
  const generateExperimentSummary = () => {
    const isTrialA = experimentConfig?.trialType === 'A';
    const specificOrderTrials = trialResults.filter(t => t.isSpecificOrder);
    const freeChoiceTrials = trialResults.filter(t => !t.isSpecificOrder);

    return {
      trialType: experimentConfig?.trialType,
      isBaseline: isTrialA,
      totalTrials: trialResults.length,
      specificOrderTrialsCompleted: specificOrderTrials.length,
      freeChoiceTrialsCompleted: freeChoiceTrials.length,
      averageTrialTime: trialResults.length > 0
        ? trialResults.reduce((sum, t) => sum + (t.totalTime || 0), 0) / trialResults.length
        : 0,
      participantFollowedSuggestions: specificOrderTrials.filter(t => t.participantFollowedSuggestion).length,
      baselineMode: isTrialA,
      emotionResponseMode: !isTrialA
    };
  };

  // Check if experiment is complete
  const isExperimentComplete = () => {
    return currentTrial > 5 || trialResults.length >= 5;
  };

  // Record participant decision on suggestions
  const recordSuggestionDecision = (followedSuggestion, customOrder = null) => {
    setStepData(prev => ({
      ...prev,
      suggestionDecision: {
        followed: followedSuggestion,
        customOrder: customOrder,
        timestamp: new Date().toISOString()
      }
    }));
  };

  // Start timer for a step
  const startStep = (step) => {
    timerRef.current[step] = Date.now();
    moodRef.current[step] = { mood: 'neutral', startTime: Date.now() };
    setStepData((prev) => ({
      ...prev,
      [step]: {
        ...prev[step],
        moodTimeline: [
          { mood: 'neutral', startTime: Date.now() }
        ],
      },
    }));
  };

  // Stop timer and record elapsed time for a step
  const stopStep = (step) => {
    const start = timerRef.current[step];
    if (start) {
      const elapsed = Date.now() - start;
      setStepData((prev) => ({
        ...prev,
        [step]: {
          ...prev[step],
          time: elapsed,
        },
      }));
      timerRef.current[step] = null;
    }

    // End the last mood interval
    if (moodRef.current[step]) {
      setStepData((prev) => {
        const timeline = prev[step]?.moodTimeline || [];
        if (timeline.length > 0 && !timeline[timeline.length - 1].endTime) {
          timeline[timeline.length - 1].endTime = Date.now();
        }
        return {
          ...prev,
          [step]: {
            ...prev[step],
            moodTimeline: timeline,
          },
        };
      });
      moodRef.current[step] = null;
    }
  };

  // Add a mood change for a step
  const addMoodChange = (step, newMood) => {
    setStepData((prev) => {
      const timeline = prev[step]?.moodTimeline ? [...prev[step].moodTimeline] : [];
      const now = Date.now();

      // End previous mood interval
      if (timeline.length > 0 && !timeline[timeline.length - 1].endTime) {
        timeline[timeline.length - 1].endTime = now;
      }

      // Start new mood interval
      timeline.push({ mood: newMood, startTime: now });
      moodRef.current[step] = { mood: newMood, startTime: now };

      return {
        ...prev,
        [step]: {
          ...prev[step],
          moodTimeline: timeline,
        },
      };
    });
  };

  // Legacy export for backward compatibility
  const exportData = () => stepData;

  const contextValue = {
    // Experiment management
    experimentConfig,
    participantData,
    currentTrial,
    trialResults,

    // Trial management
    initializeExperiment,
    startTrial,
    completeTrial,
    getCurrentTrialConfig,
    isExperimentComplete,

    // Data collection
    recordSuggestionDecision,
    exportExperimentData,

    // Step and mood tracking (legacy)
    stepData,
    startStep,
    stopStep,
    addMoodChange,
    exportData,

    // Dietary preferences
    setDietaryPreferences,
    getDietaryPreferences,
    hasDietaryPreferences,
    clearDietaryPreferences
  };

  return (
    <ExperimentContext.Provider value={contextValue}>
      {children}
    </ExperimentContext.Provider>
  );
};