import React, { createContext, useContext, useState, useRef } from 'react';

const ExperimentContext = createContext();

export const useExperiment = () => useContext(ExperimentContext);

export const ExperimentProvider = ({ children }) => {
  const [stepData, setStepData] = useState({});
  const timerRef = useRef({});
  const moodRef = useRef({}); // To track last mood and its start time for each step

  // Start timer for a step
  const startStep = (step) => {
    timerRef.current[step] = Date.now();
    // Start mood tracking for this step
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

  // Add a mood change for a step, recording the previous mood's end time
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
      // Update ref for next change
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

  // Export data
  const exportData = () => stepData;

  return (
    <ExperimentContext.Provider value={{ stepData, startStep, stopStep, addMoodChange, exportData }}>
      {children}
    </ExperimentContext.Provider>
  );
};