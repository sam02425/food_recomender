import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useOrder } from '../context/OrderContext';
import { useCustomer } from '../context/CustomerContext';
import { api } from '../services/api';
import LoadingSpinner from '../LoadingSpinner';
import ErrorBoundary from '../ErrorBoundary';

const HomePage = () => {
  const navigate = useNavigate();
  const { startOrder } = useOrder();
  const { setCustomer, customer } = useCustomer();

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [faceDetectionEnabled, setFaceDetectionEnabled] = useState(false);
  const [moodTracking, setMoodTracking] = useState(null);
  const [currentMood, setCurrentMood] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const moodTrackingInterval = useRef(null);

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (moodTrackingInterval.current) {
        clearInterval(moodTrackingInterval.current);
      }
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setFaceDetectionEnabled(true);
      setMessage('Camera ready! Look at the camera for face detection.');
    } catch (err) {
      setError('Camera access denied. You can still proceed manually.');
      console.error('Camera error:', err);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setFaceDetectionEnabled(false);
    if (moodTrackingInterval.current) {
      clearInterval(moodTrackingInterval.current);
      moodTrackingInterval.current = null;
    }
  };

  const captureImage = () => {
    if (!canvasRef.current || !videoRef.current) return null;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);

    return canvas.toDataURL('image/jpeg', 0.8);
  };

  const handleFaceRecognition = async () => {
    if (!faceDetectionEnabled) {
      await startCamera();
      setTimeout(handleFaceRecognition, 2000); // Wait for camera to be ready
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const imageData = captureImage();
      if (!imageData) {
        throw new Error('Failed to capture image');
      }

      const response = await fetch('/api/face-recognition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_data: imageData })
      });

      const result = await response.json();

      if (result.success && result.recognized) {
        // Customer recognized
        setCustomer(result.customer_data);
        setSessionId(result.session_id);
        setMessage(`Welcome back, ${result.customer_data.name}! Starting your order...`);

        // Start mood tracking
        if (result.mood_tracking_enabled) {
          startMoodTracking(result.customer_data.customer_id);
        }

        // Start order and navigate
        setTimeout(() => {
          startOrder();
          navigate('/order');
        }, 2000);

      } else {
        // New customer
        setMessage('New customer detected! Please provide your information.');
        setTimeout(() => {
          navigate('/customer-info');
        }, 1500);
      }
    } catch (err) {
      setError('Face recognition failed. Please try again or proceed manually.');
      console.error('Face recognition error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const startMoodTracking = (customerId) => {
    setMoodTracking({ enabled: true, customerId });

    // Track mood every 3 seconds
    moodTrackingInterval.current = setInterval(async () => {
      try {
        const imageData = captureImage();
        if (imageData) {
          const response = await fetch('/api/track-mood', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              image_data: imageData,
              customer_id: customerId,
              context: 'homepage_interaction'
            })
          });

          const result = await response.json();

          if (result.success && result.mood_analysis) {
            setCurrentMood(result.mood_analysis);
          }
        }
      } catch (err) {
        console.error('Mood tracking error:', err);
      }
    }, 3000);
  };

  const handleManualStart = async () => {
    setIsLoading(true);
    try {
      startOrder();
      navigate('/customer-info');
    } catch (err) {
      setError('Failed to start order. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderMoodIndicator = () => {
    if (!currentMood || !currentMood.success) return null;

    const mood = currentMood.mood;
    const confidence = currentMood.confidence;
    const feedback = currentMood.feedback_interpretation;

    return (
      <div className="mood-indicator">
        <div className="mood-display">
          <span className="mood-emoji">{getMoodEmoji(mood)}</span>
          <span className="mood-text">
            {mood} ({Math.round(confidence * 100)}%)
          </span>
        </div>
        {feedback && (
          <div className={`feedback-indicator ${feedback.feedback_type}`}>
            <small>{feedback.interpretation}</small>
          </div>
        )}
      </div>
    );
  };

  const getMoodEmoji = (mood) => {
    const emojis = {
      happy: '😊',
      excited: '🤩',
      satisfied: '😌',
      neutral: '😐',
      confused: '😕',
      disappointed: '😞',
      angry: '😠',
      frustrated: '😤',
      surprised: '😲',
      tired: '😴',
      stressed: '😰'
    };
    return emojis[mood] || '😐';
  };

  return (
    <ErrorBoundary>
      <div className="home-page">
        <div className="welcome-container">
          <div className="welcome-header">
            <h1>🍛 Welcome to Curry Creations</h1>
            <p>Your AI-powered personalized dining experience</p>
          </div>

          {/* Camera Section */}
          <div className="camera-section">
            <div className="video-container">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{
                  width: '100%',
                  maxWidth: '400px',
                  borderRadius: '12px',
                  display: faceDetectionEnabled ? 'block' : 'none'
                }}
              />
              <canvas ref={canvasRef} style={{ display: 'none' }} />

              {!faceDetectionEnabled && (
                <div className="camera-placeholder">
                  <div className="camera-icon">📷</div>
                  <p>Face recognition ready</p>
                </div>
              )}
            </div>

            {/* Mood Tracking Display */}
            {moodTracking?.enabled && renderMoodIndicator()}
          </div>

          {/* Action Buttons */}
          <div className="action-buttons">
            <button
              className="primary-button face-recognition-btn"
              onClick={handleFaceRecognition}
              disabled={isLoading}
            >
              {isLoading ? (
                <LoadingSpinner size="small" />
              ) : faceDetectionEnabled ? (
                '📸 Recognize Me'
              ) : (
                '👤 Start with Face Recognition'
              )}
            </button>

            <div className="divider">
              <span>OR</span>
            </div>

            <button
              className="secondary-button manual-btn"
              onClick={handleManualStart}
              disabled={isLoading}
            >
              📝 Start Manual Order
            </button>
          </div>

          {/* Status Messages */}
          {message && (
            <div className="status-message success">
              {message}
            </div>
          )}

          {error && (
            <div className="status-message error">
              {error}
            </div>
          )}

          {/* Features Section */}
          <div className="features-section">
            <h3>🌟 Enhanced Features</h3>
            <div className="features-grid">
              <div className="feature">
                <span className="feature-icon">🎯</span>
                <div>
                  <strong>Smart Recognition</strong>
                  <p>Instant login with face detection</p>
                </div>
              </div>
              <div className="feature">
                <span className="feature-icon">😊</span>
                <div>
                  <strong>Mood Tracking</strong>
                  <p>Real-time feedback analysis</p>
                </div>
              </div>
              <div className="feature">
                <span className="feature-icon">🌤️</span>
                <div>
                  <strong>Weather Integration</strong>
                  <p>Location-aware recommendations</p>
                </div>
              </div>
              <div className="feature">
                <span className="feature-icon">🤖</span>
                <div>
                  <strong>AI Powered</strong>
                  <p>Intelligent suggestions that learn</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <style jsx>{`
          .home-page {
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
          }

          .welcome-container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
          }

          .welcome-header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            color: #333;
          }

          .welcome-header p {
            color: #666;
            font-size: 1.1rem;
            margin-bottom: 30px;
          }

          .camera-section {
            margin: 30px 0;
          }

          .video-container {
            position: relative;
            margin-bottom: 20px;
          }

          .camera-placeholder {
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            border-radius: 12px;
            padding: 40px;
            color: #6c757d;
          }

          .camera-icon {
            font-size: 3rem;
            margin-bottom: 10px;
          }

          .mood-indicator {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 15px;
            margin-top: 15px;
          }

          .mood-display {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            font-size: 1.1rem;
          }

          .mood-emoji {
            font-size: 1.5rem;
          }

          .feedback-indicator {
            margin-top: 10px;
            padding: 8px;
            border-radius: 8px;
            font-size: 0.9rem;
          }

          .feedback-indicator.positive {
            background: #d4edda;
            color: #155724;
          }

          .feedback-indicator.negative {
            background: #f8d7da;
            color: #721c24;
          }

          .feedback-indicator.neutral {
            background: #e2e3e5;
            color: #383d41;
          }

          .action-buttons {
            margin: 30px 0;
          }

          .primary-button, .secondary-button {
            width: 100%;
            padding: 15px 25px;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 10px 0;
          }

          .primary-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
          }

          .primary-button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
          }

          .secondary-button {
            background: #f8f9fa;
            color: #495057;
            border: 2px solid #dee2e6;
          }

          .secondary-button:hover:not(:disabled) {
            background: #e9ecef;
            border-color: #adb5bd;
          }

          .divider {
            margin: 20px 0;
            position: relative;
            color: #6c757d;
          }

          .divider::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background: #dee2e6;
            z-index: 1;
          }

          .divider span {
            background: white;
            padding: 0 15px;
            position: relative;
            z-index: 2;
          }

          .status-message {
            padding: 12px;
            border-radius: 8px;
            margin: 15px 0;
          }

          .status-message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
          }

          .status-message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
          }

          .features-section {
            margin-top: 40px;
            text-align: left;
          }

          .features-section h3 {
            text-align: center;
            margin-bottom: 20px;
            color: #333;
          }

          .features-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
          }

          .feature {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 12px;
          }

          .feature-icon {
            font-size: 1.5rem;
          }

          .feature strong {
            display: block;
            color: #333;
            margin-bottom: 4px;
          }

          .feature p {
            margin: 0;
            color: #666;
            font-size: 0.9rem;
          }

          @media (max-width: 768px) {
            .welcome-container {
              padding: 20px;
            }

            .welcome-header h1 {
              font-size: 2rem;
            }

            .features-grid {
              grid-template-columns: 1fr;
            }
          }
        `}</style>
      </div>
    </ErrorBoundary>
  );
};

export default HomePage;
