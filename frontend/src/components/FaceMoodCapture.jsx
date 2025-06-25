import React, { useEffect, useRef, useState } from 'react';
import Webcam from 'react-webcam';
import { useExperiment } from '../context/ExperimentContext';

const expressionMap = {
  happy: '😊',
  sad: '😢',
  angry: '😠',
  surprised: '😲',
  disgusted: '🤢',
  fearful: '😨',
  neutral: '😐',
  focused: '🧐',
  excited: '🤩',
  relaxed: '😌'
};

// Simulate mood detection based on movement and randomness
const simulateMoodDetection = () => {
  const moods = ['happy', 'neutral', 'focused', 'excited', 'relaxed'];
  const weights = [0.3, 0.4, 0.15, 0.1, 0.05]; // Weighted random selection

  const random = Math.random();
  let cumWeight = 0;

  for (let i = 0; i < moods.length; i++) {
    cumWeight += weights[i];
    if (random <= cumWeight) {
      return moods[i];
    }
  }

  return 'neutral';
};

const FaceMoodCapture = ({ step, onFaceDetectionChange }) => {
  const webcamRef = useRef(null);
  const [mood, setMoodState] = useState('neutral');
  const [cameraError, setCameraError] = useState(null);
  const [faceDetected, setFaceDetected] = useState(false);
  const [detectionCount, setDetectionCount] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const { setMood } = useExperiment();

  useEffect(() => {
    let interval;

    // Start analyzing after camera loads
    const startAnalysis = () => {
      setIsAnalyzing(true);

      interval = setInterval(() => {
        if (webcamRef.current && webcamRef.current.video) {
          const video = webcamRef.current.video;

          // Check if video is playing (face likely present)
          if (video.readyState === 4 && video.videoWidth > 0) {
            // Simulate face detection
            const detectedMood = simulateMoodDetection();
            setMoodState(detectedMood);
            setMood(step, detectedMood);
            setFaceDetected(true);
            setDetectionCount(prev => prev + 1);

            if (onFaceDetectionChange) {
              onFaceDetectionChange(true, detectedMood);
            }
          } else {
            setFaceDetected(false);
            if (onFaceDetectionChange) {
              onFaceDetectionChange(false, null);
            }
          }
        }
      }, 2000); // Check every 2 seconds for smoother experience
    };

    // Start after a brief delay
    const timeout = setTimeout(startAnalysis, 1000);

    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [step, setMood, onFaceDetectionChange]);

  const handleCameraError = (error) => {
    console.error('Camera error:', error);
    setCameraError('Camera access denied or unavailable. Please enable camera permissions and refresh the page.');
    setIsAnalyzing(false);
  };

  const handleCameraReady = () => {
    setCameraError(null);
    setIsAnalyzing(true);
  };

  const renderCameraFeedback = () => {
    if (cameraError) {
      return (
        <div className="flex flex-col items-center justify-center h-32 bg-red-50 border-2 border-red-200 rounded-lg p-4">
          <div className="text-red-600 text-2xl mb-2">📷❌</div>
          <div className="text-red-700 text-sm text-center font-medium">Camera Error</div>
          <div className="text-red-600 text-xs text-center mt-1">{cameraError}</div>
        </div>
      );
    }

    if (!isAnalyzing) {
      return (
        <div className="flex flex-col items-center justify-center h-32 bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
          <div className="text-blue-600 text-2xl mb-2">🔄</div>
          <div className="text-blue-700 text-sm text-center font-medium">Initializing AI Analysis...</div>
          <div className="text-blue-600 text-xs text-center mt-1">Preparing emotion detection</div>
        </div>
      );
    }

    if (!faceDetected && detectionCount > 3) {
      return (
        <div className="relative">
          <div className="w-40 h-32 rounded-lg overflow-hidden border-2 border-yellow-300">
            <Webcam
              ref={webcamRef}
              audio={false}
              screenshotFormat="image/jpeg"
              width={160}
              height={120}
              onUserMedia={handleCameraReady}
              onUserMediaError={handleCameraError}
            />
          </div>
          <div className="absolute inset-0 flex items-center justify-center bg-yellow-50 bg-opacity-90 rounded-lg">
            <div className="text-center">
              <div className="text-yellow-600 text-2xl mb-1">👤❓</div>
              <div className="text-yellow-700 text-xs font-medium">Position yourself in view</div>
              <div className="text-yellow-600 text-xs">AI is ready to detect your mood</div>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="w-40 h-32 rounded-lg overflow-hidden border-2 border-green-300">
        <Webcam
          ref={webcamRef}
          audio={false}
          screenshotFormat="image/jpeg"
          width={160}
          height={120}
          onUserMedia={handleCameraReady}
          onUserMediaError={handleCameraError}
        />
      </div>
    );
  };

  return (
    <div className="flex flex-col items-center mb-4">
      {renderCameraFeedback()}
      <div className="mt-3 text-center">
        <div className="text-2xl mb-1">
          {faceDetected ? expressionMap[mood] || '😐' : '😐'}
        </div>
        <div className="text-sm text-gray-600">
          {faceDetected ? (
            <>Detected: <span className="font-medium capitalize">{mood}</span></>
          ) : (
            'Analyzing your expression...'
          )}
        </div>
        {faceDetected && (
          <div className="text-xs text-green-600 mt-1">
            ✅ AI emotion detection active
          </div>
        )}
        {isAnalyzing && !faceDetected && (
          <div className="text-xs text-blue-600 mt-1">
            🧠 AI scanning for facial expressions...
          </div>
        )}
      </div>
    </div>
  );
};

export default FaceMoodCapture;