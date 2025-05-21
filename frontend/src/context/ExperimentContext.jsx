import React, { createContext, useContext, useState, useRef } from 'react';

const ExperimentContext = createContext();

export const useExperiment = () => useContext(ExperimentContext);

export const ExperimentProvider = ({ children }) => {
  const [stepData, setStepData] = useState({});
  const timerRef = useRef({});

  // Start timer for a step
  const startStep = (step) => {
    timerRef.current[step] = Date.now();
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
  };

  // Set mood for a step
  const setMood = (step, mood) => {
    setStepData((prev) => ({
      ...prev,
      [step]: {
        ...prev[step],
        mood,
      },
    }));
  };

  // Export data
  const exportData = () => stepData;

  return (
    <ExperimentContext.Provider value={{ stepData, startStep, stopStep, setMood, exportData }}>
      {children}
    </ExperimentContext.Provider>
  );
};