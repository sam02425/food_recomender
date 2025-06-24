import React, { useState, useEffect, useRef } from 'react';

const ExperimentFlow = () => {
  // Experiment state
  const [phase, setPhase] = useState('setup'); // setup, trial_a, break, trial_b, complete
  const [currentTrialInPhase, setCurrentTrialInPhase] = useState(1);
  const [breakCountdown, setBreakCountdown] = useState(300); // 5 minutes
  const [participantName, setParticipantName] = useState('');
  const [orders, setOrders] = useState([]);
  const [showInstructions, setShowInstructions] = useState(true);

  // AI Agent states
  const [faceRecognitionActive, setFaceRecognitionActive] = useState(false);
  const [currentMood, setCurrentMood] = useState('neutral');
  const [aiRecommendations, setAiRecommendations] = useState([]);
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);

  // Refs for timers
  const breakTimerRef = useRef(null);
  const moodDetectionRef = useRef(null);

  // Initialize experiment
  const startExperiment = (name) => {
    setParticipantName(name);
    setPhase('trial_a');
    setShowInstructions(false);
  };

  // Start break timer
  const startBreak = () => {
    setPhase('break');
    setBreakCountdown(300); // 5 minutes

    breakTimerRef.current = setInterval(() => {
      setBreakCountdown(prev => {
        if (prev <= 1) {
          clearInterval(breakTimerRef.current);
          setPhase('trial_b');
          setCurrentTrialInPhase(1);
          setFaceRecognitionActive(true);
          startMoodDetection();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  // Start mood detection for Trial B
  const startMoodDetection = () => {
    setCurrentMood('analyzing');

    moodDetectionRef.current = setInterval(() => {
      const moods = ['happy', 'neutral', 'focused', 'excited', 'contemplative'];
      const randomMood = moods[Math.floor(Math.random() * moods.length)];

      setCurrentMood(randomMood);
      generateAIRecommendations(randomMood);
    }, 3000);
  };

  // Generate AI recommendations
  const generateAIRecommendations = (mood) => {
    const recommendations = {
      happy: [
        { type: 'protein', item: 'Chicken', reason: 'Light protein to maintain your positive energy' },
        { type: 'sauce', item: 'Curry Special', reason: 'Flavorful choice that matches your mood' },
        { type: 'base', item: 'Rice Bowl', reason: 'Satisfying base for a good mood' }
      ],
      focused: [
        { type: 'protein', item: 'Paneer', reason: 'Brain-boosting protein for concentration' },
        { type: 'sauce', item: 'Malai Masala', reason: 'Creamy comfort to aid focus' },
        { type: 'base', item: 'Rice Bowl', reason: 'Steady energy release' }
      ],
      excited: [
        { type: 'protein', item: 'Pepperoni', reason: 'Bold choice for your energetic mood' },
        { type: 'sauce', item: 'Curry Masala', reason: 'Exciting flavors to match your energy' },
        { type: 'base', item: 'Naan Wrap', reason: 'Fun, handheld option' }
      ],
      neutral: [
        { type: 'protein', item: 'Egg', reason: 'Balanced protein choice' },
        { type: 'sauce', item: 'Curry Special', reason: 'Our most popular sauce' },
        { type: 'base', item: 'Rice Bowl', reason: 'Classic, reliable option' }
      ],
      contemplative: [
        { type: 'protein', item: 'Soya', reason: 'Mindful, healthy protein choice' },
        { type: 'sauce', item: 'Malai Masala', reason: 'Gentle, soothing flavors' },
        { type: 'base', item: 'Salad Bowl', reason: 'Light, thoughtful option' }
      ]
    };

    setAiRecommendations(recommendations[mood] || recommendations.neutral);
  };

  // Handle order completion
  const handleOrderComplete = (orderData) => {
    const newOrder = {
      trialPhase: phase,
      trialNumber: currentTrialInPhase,
      order: orderData,
      timestamp: new Date().toISOString(),
      usedRecommendation: selectedRecommendation !== null,
      recommendationData: selectedRecommendation,
      mood: currentMood,
      participantName
    };

    setOrders(prev => [...prev, newOrder]);

    if (currentTrialInPhase < 5) {
      setCurrentTrialInPhase(prev => prev + 1);
      setSelectedRecommendation(null);
    } else {
      if (phase === 'trial_a') {
        startBreak();
      } else if (phase === 'trial_b') {
        setPhase('complete');
        if (moodDetectionRef.current) {
          clearInterval(moodDetectionRef.current);
        }
      }
    }
  };

  // Clean up timers on unmount
  useEffect(() => {
    return () => {
      if (breakTimerRef.current) clearInterval(breakTimerRef.current);
      if (moodDetectionRef.current) clearInterval(moodDetectionRef.current);
    };
  }, []);

  // Format time for display
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Handle recommendation selection
  const handleRecommendationClick = (recommendation) => {
    setSelectedRecommendation(recommendation);
  };

  // Render setup phase
  if (phase === 'setup') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-xl p-8">
            <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">
              🧪 Food Ordering Experiment
            </h1>

            {showInstructions && (
              <div className="bg-blue-50 border-l-4 border-blue-400 p-6 mb-8">
                <h2 className="text-xl font-semibold mb-4">Experiment Overview</h2>
                <div className="space-y-3 text-gray-700">
                  <p><strong>Duration:</strong> ~45 minutes total</p>
                  <p><strong>Structure:</strong></p>
                  <ul className="list-disc ml-6 space-y-2">
                    <li><strong>Trial A (Baseline):</strong> 5 orders with standard interface</li>
                    <li><strong>5-minute break:</strong> Automated rest period</li>
                    <li><strong>Trial B (AI-Powered):</strong> 5 orders with emotion recognition & recommendations</li>
                  </ul>
                  <p><strong>What we measure:</strong> Order choices, time, satisfaction, and interaction patterns</p>
                </div>
              </div>
            )}

            <div className="text-center">
              <div className="mb-4">
                <label htmlFor="participantName" className="block text-lg font-medium mb-4">
                  Enter your name to begin:
                </label>
                <input
                  id="participantName"
                  type="text"
                  value={participantName}
                  onChange={(e) => setParticipantName(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-lg w-64 text-center mb-6"
                  placeholder="Your name"
                />
              </div>
              <button
                onClick={() => startExperiment(participantName)}
                disabled={!participantName.trim()}
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Start Experiment
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Render break phase
  if (phase === 'break') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-xl p-8 text-center max-w-md">
          <h2 className="text-2xl font-bold mb-4 text-gray-800">Break Time</h2>
          <div className="text-6xl mb-4">☕</div>
          <p className="text-gray-600 mb-6">
            Great job completing Trial A! Take a short break before we continue with Trial B.
          </p>
          <div className="text-3xl font-mono font-bold text-blue-600 mb-4">
            {formatTime(breakCountdown)}
          </div>
          <p className="text-sm text-gray-500">
            Trial B will start automatically with emotion recognition enabled.
          </p>
        </div>
      </div>
    );
  }

  // Render completion phase
  if (phase === 'complete') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-xl p-8 text-center max-w-2xl">
          <h2 className="text-3xl font-bold mb-6 text-gray-800">🎉 Experiment Complete!</h2>
          <p className="text-lg text-gray-600 mb-8">
            Thank you, {participantName}! You&apos;ve completed both trials successfully.
          </p>

          <div className="grid grid-cols-2 gap-6 mb-8">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-800">Trial A (Baseline)</h3>
              <p className="text-2xl font-bold text-blue-600">5 orders</p>
              <p className="text-sm text-blue-600">Standard interface</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h3 className="font-semibold text-purple-800">Trial B (AI-Powered)</h3>
              <p className="text-2xl font-bold text-purple-600">5 orders</p>
              <p className="text-sm text-purple-600">With AI recommendations</p>
            </div>
          </div>

          <div className="bg-gray-50 p-6 rounded-lg">
            <h4 className="font-semibold mb-2">Experiment Summary</h4>
            <p className="text-sm text-gray-600">
              Your data has been automatically saved and will contribute to our research on emotion-responsive interfaces.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Render active trial phase
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Trial Header */}
      <div className={`w-full py-4 px-6 ${phase === 'trial_a' ? 'bg-blue-600' : 'bg-purple-600'} text-white`}>
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold">
              {phase === 'trial_a' ? '🔬 Trial A: Baseline Interface' : '🤖 Trial B: AI-Powered Interface'}
            </h1>
            <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm">
              Order {currentTrialInPhase} of 5
            </span>
          </div>

          <div className="flex items-center space-x-6">
            <span className="text-sm">Participant: {participantName}</span>

            {phase === 'trial_b' && faceRecognitionActive && (
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-sm">Face Recognition Active</span>
              </div>
            )}

            {phase === 'trial_b' && currentMood && (
              <div className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm">
                Mood: {currentMood.charAt(0).toUpperCase() + currentMood.slice(1)}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI Recommendations Panel (Trial B only) */}
      {phase === 'trial_b' && aiRecommendations.length > 0 && (
        <div className="bg-gradient-to-r from-purple-100 to-pink-100 border-b border-purple-200 p-4">
          <div className="max-w-7xl mx-auto">
            <h3 className="text-lg font-semibold text-purple-800 mb-3">
              🎯 AI Recommendations Based on Your Mood ({currentMood})
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {aiRecommendations.map((rec, index) => (
                <div
                  key={index}
                  className={`bg-white rounded-lg p-4 border-2 cursor-pointer transition-all ${
                    selectedRecommendation?.item === rec.item
                      ? 'border-purple-500 bg-purple-50'
                      : 'border-gray-200 hover:border-purple-300'
                  }`}
                  onClick={() => handleRecommendationClick(rec)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      handleRecommendationClick(rec);
                    }
                  }}
                >
                  <div className="font-semibold text-purple-700">{rec.type.toUpperCase()}: {rec.item}</div>
                  <div className="text-sm text-gray-600 mt-1">{rec.reason}</div>
                  {selectedRecommendation?.item === rec.item && (
                    <div className="mt-2 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                      ✓ Selected
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Order {currentTrialInPhase}</h2>
          <p className="text-gray-600 mb-4">
            {phase === 'trial_a'
              ? 'Use the standard interface to place your order. No AI recommendations will be provided.'
              : 'AI recommendations are shown above. You can select suggested items or make your own choices.'
            }
          </p>

          {/* Simple order form for now */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="space-y-2">
              <label htmlFor="protein-select" className="block font-medium">Protein</label>
              <select id="protein-select" className="w-full p-2 border border-gray-300 rounded">
                <option>Chicken</option>
                <option>Paneer</option>
                <option>Egg</option>
                <option>Soya</option>
                <option>Pepperoni</option>
              </select>
            </div>

            <div className="space-y-2">
              <label htmlFor="sauce-select" className="block font-medium">Sauce</label>
              <select id="sauce-select" className="w-full p-2 border border-gray-300 rounded">
                <option>Curry Special</option>
                <option>Malai Masala</option>
                <option>Curry Masala</option>
              </select>
            </div>

            <div className="space-y-2">
              <label htmlFor="base-select" className="block font-medium">Base</label>
              <select id="base-select" className="w-full p-2 border border-gray-300 rounded">
                <option>Rice Bowl</option>
                <option>Naan Wrap</option>
                <option>Salad Bowl</option>
              </select>
            </div>
          </div>

          <button
            onClick={() => handleOrderComplete({
              protein: 'Chicken',
              sauce: 'Curry Special',
              base: 'Rice Bowl',
              timestamp: new Date().toISOString()
            })}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg"
          >
            Complete Order {currentTrialInPhase}
          </button>
        </div>
      </div>

      {/* Orders History Sidebar */}
      <div className="fixed right-0 top-0 h-full w-80 bg-white shadow-xl border-l border-gray-200 overflow-y-auto">
        <div className="p-4 bg-gray-50 border-b">
          <h3 className="font-semibold text-gray-800">Order History</h3>
        </div>
        <div className="p-4 space-y-4">
          {orders.map((order, index) => (
            <div key={index} className={`p-3 rounded-lg border ${
              order.trialPhase === 'trial_a' ? 'bg-blue-50 border-blue-200' : 'bg-purple-50 border-purple-200'
            }`}>
              <div className="flex justify-between items-start mb-2">
                <span className="text-sm font-medium">
                  {order.trialPhase === 'trial_a' ? 'Trial A' : 'Trial B'} - Order {order.trialNumber}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(order.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div className="text-sm text-gray-600">
                <div>{order.order.protein} • {order.order.sauce}</div>
                <div>{order.order.base}</div>
                {order.usedRecommendation && (
                  <div className="text-xs text-purple-600 mt-1 flex items-center">
                    🤖 Used AI suggestion: {order.recommendationData?.item}
                  </div>
                )}
                {order.mood && order.mood !== 'neutral' && (
                  <div className="text-xs text-gray-500 mt-1">
                    Mood: {order.mood}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ExperimentFlow;