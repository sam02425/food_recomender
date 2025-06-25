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
  relaxed: '😌',
  tired: '😴',
  stressed: '😰',
  disappointed: '😞',
  confused: '😕'
};

// Real ML-based mood detection using backend API
const detectMoodWithML = async (imageData) => {
  try {
    const response = await fetch('http://localhost:8000/api/mood-detection', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image_data: imageData
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    if (result.success) {
      return {
        mood: result.mood,
        confidence: result.confidence,
        success: true
      };
    } else {
      throw new Error(result.error || 'Mood detection failed');
    }
  } catch (error) {
    console.error('ML mood detection error:', error);
    // NO FALLBACK FOR EXPERIMENT INTEGRITY - RETURN ERROR STATE
    return {
      mood: "",
      confidence: 0.0,
      success: false,
      error: error.message,
      ml_available: false
    };
  }
};

const FaceMoodCapture = ({ step, onFaceDetectionChange }) => {
  const webcamRef = useRef(null);
  const [mood, setMoodState] = useState('neutral');
  const [confidence, setConfidence] = useState(0);
  const [cameraError, setCameraError] = useState(null);
  const [faceDetected, setFaceDetected] = useState(false);
  const [detectionCount, setDetectionCount] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [lastAnalysis, setLastAnalysis] = useState(null);
  const { setMood } = useExperiment();

  useEffect(() => {
    let interval;

    // Start analyzing after camera loads
    const startAnalysis = () => {
      setIsAnalyzing(true);

      interval = setInterval(async () => {
        if (webcamRef.current && webcamRef.current.video) {
          const video = webcamRef.current.video;

          // Check if video is playing (face likely present)
          if (video.readyState === 4 && video.videoWidth > 0) {
            try {
              // Capture image from webcam
              const imageSrc = webcamRef.current.getScreenshot();

              if (imageSrc) {
                console.log('🧠 Analyzing facial expression with ML...');

                // Use real ML-based mood detection
                const result = await detectMoodWithML(imageSrc);

                                if (result.success && result.mood) {
                  console.log(`✅ ML Detected mood: ${result.mood} (confidence: ${(result.confidence * 100).toFixed(1)}%)`);
                  setMoodState(result.mood);
                  setConfidence(result.confidence);
                  setMood(step, result.mood);
                  setFaceDetected(true);
                  setDetectionCount(prev => prev + 1);
                  setLastAnalysis(new Date().toLocaleTimeString());

                  if (onFaceDetectionChange) {
                    onFaceDetectionChange(true, result.mood);
                  }
                } else {
                  console.log(`❌ ML detection failed: ${result.error || 'No mood detected'}`);
                  // NO MOOD DATA - EXPERIMENT INTEGRITY REQUIREMENT
                  setMoodState("");
                  setConfidence(0.0);
                  setFaceDetected(false);

                  if (onFaceDetectionChange) {
                    onFaceDetectionChange(false, null);
                  }
                }
              }
            } catch (error) {
              console.error('Face analysis error:', error);
              setFaceDetected(false);
              if (onFaceDetectionChange) {
                onFaceDetectionChange(false, null);
              }
            }
          } else {
            setFaceDetected(false);
            if (onFaceDetectionChange) {
              onFaceDetectionChange(false, null);
            }
          }
        }
      }, 3000); // Analyze every 3 seconds to allow processing time
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
          <div className="text-blue-700 text-sm text-center font-medium">Initializing ML Analysis...</div>
          <div className="text-blue-600 text-xs text-center mt-1">Preparing emotion detection AI</div>
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
              <div className="text-yellow-600 text-xs">ML AI is ready to detect your mood</div>
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
          {faceDetected && mood ? (
            <>
              Detected: <span className="font-medium capitalize">{mood}</span>
              {confidence > 0 && (
                <span className="text-xs text-gray-500 ml-2">
                  ({(confidence * 100).toFixed(1)}% confidence)
                </span>
              )}
            </>
          ) : mood === "" ? (
            <span className="text-red-600">⚠️ ML Detection Unavailable</span>
          ) : (
            'Analyzing your expression with AI...'
          )}
        </div>
        {faceDetected && (
          <div className="text-xs text-green-600 mt-1">
            ✅ ML emotion detection active
            {lastAnalysis && (
              <div className="text-xs text-gray-400">
                Last scan: {lastAnalysis}
              </div>
            )}
          </div>
        )}
        {isAnalyzing && !faceDetected && (
          <div className="text-xs text-blue-600 mt-1">
            🧠 ML AI scanning for facial expressions...
          </div>
        )}
      </div>
    </div>
  );
};

export default FaceMoodCapture;