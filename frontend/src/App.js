import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import OrderForm from './components/OrderForm';
import ExperimentReport from './components/ExperimentReport';
import AgentStatus from './components/AgentStatus';
import MeasurementDemo from './components/MeasurementDemo';
import ExperimentSetup from './components/ExperimentSetup';

import { OrderProvider } from './components/OrderContext';
import { ExperimentProvider } from './context/ExperimentContext';

function App() {
  const [experimentConfig, setExperimentConfig] = useState({
    participantId: 'demo',
    trialType: 'A',
    experimentMode: 'demo'
  });
  const [showExperimentSetup, setShowExperimentSetup] = useState(false);

    // Experiment cycle state
  const [experimentCycleActive, setExperimentCycleActive] = useState(false);
  const [currentPhase, setCurrentPhase] = useState('setup'); // setup, trial_a, break, trial_b, complete
  const [currentTrialInPhase, setCurrentTrialInPhase] = useState(1);
  const [participantName, setParticipantName] = useState('');

  // AI Agent states
  const [faceRecognitionActive, setFaceRecognitionActive] = useState(false);
  const [currentMood, setCurrentMood] = useState('neutral');
  const [aiRecommendations, setAiRecommendations] = useState([]);

  const handleExperimentStart = (config) => {
    setExperimentConfig(config);
    setShowExperimentSetup(false);
  };

  const handleExperimentReset = () => {
    setExperimentConfig(null);
    setShowExperimentSetup(true);
    setExperimentCycleActive(false);
    setCurrentPhase('setup');
    setCurrentTrialInPhase(1);
    setFaceRecognitionActive(false);
    setCurrentMood('neutral');
    setAiRecommendations([]);
  };

  const startExperimentCycle = (name) => {
    setParticipantName(name);
    setExperimentCycleActive(true);
    setCurrentPhase('trial_a');
    setCurrentTrialInPhase(1);
    setExperimentConfig({
      participantId: `P001_${Date.now()}`,
      trialType: 'A',
      experimentMode: 'cycle'
    });
    setShowExperimentSetup(false);
  };

  // Handle order completion in experiment cycle
  const handleExperimentOrderComplete = () => {
    if (currentTrialInPhase < 5) {
      setCurrentTrialInPhase(prev => prev + 1);
    } else {
      // Completed 5 trials in current phase
      if (currentPhase === 'trial_a') {
        // Start break and transition to trial B
        setCurrentPhase('break');
        setTimeout(() => {
          setCurrentPhase('trial_b');
          setCurrentTrialInPhase(1);
          setFaceRecognitionActive(true);
          setCurrentMood('analyzing');
          setExperimentConfig(prev => ({
            ...prev,
            trialType: 'B'
          }));
          startMoodDetection();
        }, 5000); // 5 second break for demo (normally would be 5 minutes)
      } else if (currentPhase === 'trial_b') {
        // Complete experiment
        setCurrentPhase('complete');
        setFaceRecognitionActive(false);
      }
    }
  };

  // Get current order type for Trial B
  const getCurrentOrderType = () => {
    if (currentPhase !== 'trial_b') return 'standard';

    // Trial B pattern: 1=free, 2=free, 3=task, 4=free, 5=task
    const taskOrders = [3, 5];
    return taskOrders.includes(currentTrialInPhase) ? 'given_task' : 'free_choice';
  };

  // Get order instructions based on trial and order number
  const getOrderInstructions = () => {
    if (currentPhase === 'trial_a') {
      // Define specific tasks for Trial A orders
      const trialATasks = {
        1: {
          protein: 'Chicken',
          base: 'Rice Bowl',
          sauce: 'Curry Special',
          veggies: ['Grilled Onion', 'Bell Pepper'],
          garnishes: ['Fresh Cilantro']
        },
        2: {
          protein: 'Egg',
          base: 'Naan Wrap',
          sauce: 'Malai Masala',
          veggies: ['Spinach', 'Tomato'],
          garnishes: ['Crispy Onions']
        },
        3: {
          protein: 'Paneer',
          base: 'Sandwich & Subs - Sourdough',
          sauce: 'Curry Masala',
          veggies: ['Avocado', 'Bell Pepper', 'Cilantro'],
          garnishes: ['Toasted Almonds']
        },
        4: {
          protein: 'Soya',
          base: 'Bowl - Bowl',
          sauce: 'Yogurt/Raita',
          veggies: ['Corn', 'Cabbage', 'Spinach'],
          garnishes: ['Pomegranate Seeds']
        },
        5: {
          protein: 'Potato',
          base: 'Biryani - Rice',
          sauce: 'Green Spicy Sauce',
          veggies: ['Jalapeño', 'Fried Onions'],
          garnishes: ['Fresh Cilantro']
        }
      };

      const currentTasks = trialATasks[currentTrialInPhase] || trialATasks[1];

      return {
        type: 'standard',
        title: 'Order is given - Select the following items exactly:',
        description: 'Please select the items listed below exactly as instructed for this trial.',
        tasks: currentTasks
      };
    } else if (currentPhase === 'trial_b') {
      const orderType = getCurrentOrderType();
      if (orderType === 'given_task') {
        // Define specific tasks for "given task" orders
        const taskSets = {
          3: {
            protein: 'Chicken',
            base: 'Rice Bowl',
            sauce: 'Curry Special',
            veggies: ['Grilled Onion', 'Bell Pepper'],
            garnishes: ['Fresh Cilantro']
          },
          5: {
            protein: 'Paneer',
            base: 'Naan Wrap',
            sauce: 'Malai Masala',
            veggies: ['Spinach', 'Tomato', 'Corn'],
            garnishes: ['Crispy Onions']
          }
        };

        const currentTasks = taskSets[currentTrialInPhase] || taskSets[3];

        return {
          type: 'given_task',
          title: 'Order is given to perform the task - Select exactly:',
          description: 'Please select the following items exactly as instructed:',
          tasks: currentTasks
        };
      } else {
        return {
          type: 'free_choice',
          title: 'Order as you like',
          description: 'Please order as you like. AI suggestions are provided based on your activity, location temperature, and previous orders.',
          tasks: null
        };
      }
    }
    return { type: 'standard', title: 'Complete your order', description: 'Please complete your food order.', tasks: null };
  };

  // Start mood detection and AI recommendations
  const startMoodDetection = () => {
    const moodInterval = setInterval(() => {
      const moods = ['happy', 'neutral', 'focused', 'excited', 'contemplative'];
      const randomMood = moods[Math.floor(Math.random() * moods.length)];
      setCurrentMood(randomMood);
      generateAIRecommendations(randomMood);
    }, 3000);

    // Store interval to clear later
    window.moodInterval = moodInterval;
  };

  // Generate AI recommendations based on mood
  const generateAIRecommendations = (mood) => {
    // Base recommendations that can be modified based on context
    const baseRecommendations = {
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

    // Get base recommendations for the mood
    let recommendations = baseRecommendations[mood] || baseRecommendations.neutral;

    // Enhance recommendations based on trial context
    if (currentPhase === 'trial_b') {
      const orderType = getCurrentOrderType();
      const trialNumber = currentTrialInPhase;

      // Simulate activity-based recommendations
      const activities = ['workout', 'study', 'work', 'leisure', 'meeting'];
      const currentActivity = activities[trialNumber % activities.length];

      // Simulate temperature-based recommendations
      const temperatures = ['cold', 'mild', 'warm', 'hot'];
      const currentTemp = temperatures[trialNumber % temperatures.length];

      // Modify recommendations based on context
      recommendations = recommendations.map(rec => {
        let enhancedReason = rec.reason;

        // Add activity context
        if (currentActivity === 'workout' && rec.type === 'protein') {
          enhancedReason += ` (Great for post-${currentActivity} recovery)`;
        } else if (currentActivity === 'study' && rec.type === 'base') {
          enhancedReason += ` (Perfect for sustained energy during ${currentActivity})`;
        }

        // Add temperature context
        if (currentTemp === 'cold' && rec.type === 'sauce') {
          enhancedReason += ` (Warming choice for ${currentTemp} weather)`;
        } else if (currentTemp === 'hot' && rec.type === 'base') {
          enhancedReason += ` (Light option for ${currentTemp} weather)`;
        }

        // Add previous order learning simulation
        if (trialNumber > 1) {
          enhancedReason += ` (Based on your previous preferences)`;
        }

        return {
          ...rec,
          reason: enhancedReason,
          context: {
            activity: currentActivity,
            temperature: currentTemp,
            orderType: orderType,
            trialNumber: trialNumber
          }
        };
      });
    }

    setAiRecommendations(recommendations);
  };

  // Show experiment setup if no experiment is configured
  if (showExperimentSetup) {
    return (
      <ExperimentProvider>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-8">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-xl p-8">
              <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">
                🍛 Curry Creations Food Recommender
              </h1>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                {/* Single Experiment Option */}
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                  <h2 className="text-xl font-semibold mb-4 text-gray-800">Single Experiment</h2>
                  <p className="text-gray-600 mb-4">
                    Configure and run individual trials (A or B) for research purposes.
                  </p>
                  <ExperimentSetup onExperimentStart={handleExperimentStart} />
                </div>

                {/* Experiment Cycle Option */}
                <div className="bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
                  <h2 className="text-xl font-semibold mb-4 text-purple-800">
                    🧪 Complete Experiment Cycle
                  </h2>
                  <p className="text-gray-600 mb-4">
                    Run the full experiment: Trial A (Baseline) → Break → Trial B (AI-Powered)
                  </p>
                  <div className="space-y-4">
                    <div className="text-sm text-gray-600">
                      <p><strong>Duration:</strong> ~45 minutes</p>
                      <p><strong>Structure:</strong> 5 orders + break + 5 orders</p>
                      <p><strong>Features:</strong> AI agents, mood detection, recommendations</p>
                    </div>
                    <div>
                      <label htmlFor="participant-name" className="block text-sm font-medium mb-2">
                        Participant Name:
                      </label>
                      <input
                        id="participant-name"
                        type="text"
                        value={participantName}
                        onChange={(e) => setParticipantName(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4"
                        placeholder="Enter participant name"
                      />
                      <button
                        onClick={() => startExperimentCycle(participantName)}
                        disabled={!participantName.trim()}
                        className="w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Start Complete Experiment Cycle
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </ExperimentProvider>
    );
  }

  return (
    <ExperimentProvider>
      <OrderProvider>
        <Router>
          <div className="min-h-screen bg-gray-100 py-8">
            {/* Experiment Header */}
            <div className={`shadow-sm border-b mb-8 ${
              experimentCycleActive
                ? (currentPhase === 'trial_a' ? 'bg-blue-600 text-white' :
                   currentPhase === 'trial_b' ? 'bg-purple-600 text-white' :
                   'bg-green-600 text-white')
                : 'bg-white'
            }`}>
              <div className="max-w-6xl mx-auto px-6 py-4">
                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-4">
                    <h1 className="text-xl font-semibold">
                      🍛 Curry Creations Experiment
                    </h1>

                    {!experimentCycleActive && (
                      <div className="flex items-center space-x-3">
                        <button
                          onClick={() => {
                            const name = prompt("Enter participant name:");
                            if (name && name.trim()) {
                              startExperimentCycle(name.trim());
                            }
                          }}
                          className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold text-base animate-pulse shadow-lg border-2 border-purple-400"
                        >
                          🧪 Start Experiment Cycle
                        </button>
                        <button
                          onClick={() => setShowExperimentSetup(true)}
                          className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-xs"
                        >
                          Single Trial Setup
                        </button>
                      </div>
                    )}

                    {experimentCycleActive ? (
                      <>
                        <div className="px-3 py-1 rounded-full text-sm font-medium bg-white bg-opacity-20">
                          {currentPhase === 'trial_a' ? '🔬 Trial A: Baseline Interface' :
                           currentPhase === 'trial_b' ? '🤖 Trial B: AI-Powered Interface' :
                           currentPhase === 'break' ? '☕ Break Time' :
                           '🎉 Complete'}
                        </div>
                        <span className="text-sm bg-white bg-opacity-20 px-2 py-1 rounded">
                          Order {currentTrialInPhase} of 5
                        </span>
                        <span className="text-sm">
                          Participant: {participantName}
                        </span>

                        {currentPhase === 'trial_b' && faceRecognitionActive && (
                          <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                            <span className="text-sm">Face Recognition Active</span>
                          </div>
                        )}

                        {currentPhase === 'trial_b' && currentMood && (
                          <div className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm">
                            Mood: {currentMood.charAt(0).toUpperCase() + currentMood.slice(1)}
                          </div>
                        )}
                      </>
                    ) : (
                      <>
                        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                          experimentConfig?.trialType === 'A'
                            ? 'bg-orange-100 text-orange-800'
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {experimentConfig?.trialType === 'A' ? 'Trial A: Baseline' : 'Trial B: Emotion-Responsive'}
                        </div>
                        <span className="text-sm text-gray-500">
                          Participant: {experimentConfig?.participantId}
                        </span>
                      </>
                    )}
                  </div>
                  <button
                    onClick={handleExperimentReset}
                    className={`px-4 py-2 text-sm rounded-lg transition-colors ${
                      experimentCycleActive
                        ? 'bg-white bg-opacity-20 hover:bg-opacity-30 text-white'
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
                    }`}
                  >
                    Reset Experiment
                  </button>
                </div>
              </div>
            </div>

            {/* AI Recommendations Panel (Trial B only) */}
            {experimentCycleActive && currentPhase === 'trial_b' && aiRecommendations.length > 0 && (
              <div className="bg-gradient-to-r from-purple-100 to-pink-100 border-b border-purple-200 p-4 mb-8">
                <div className="max-w-6xl mx-auto">
                  <h3 className="text-lg font-semibold text-purple-800 mb-3">
                    🎯 AI Recommendations Based on Your Mood ({currentMood})
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {aiRecommendations.map((rec, index) => (
                      <div
                        key={index}
                        className="bg-white rounded-lg p-4 border-2 border-purple-200 hover:border-purple-400 transition-all"
                      >
                        <div className="font-semibold text-purple-700">{rec.type.toUpperCase()}: {rec.item}</div>
                        <div className="text-sm text-gray-600 mt-1">{rec.reason}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            <nav style={{ display: 'flex', justifyContent: 'flex-end', padding: '0 24px 16px 0' }}>
              <Link to="/" style={{ marginRight: 16, fontWeight: 500 }}>Order</Link>
              <Link to="/report" style={{ marginRight: 16, fontWeight: 500 }}>Report</Link>
              <Link to="/measurements" style={{ fontWeight: 500 }}>Measurements</Link>
            </nav>

            {/* Break Screen */}
            {experimentCycleActive && currentPhase === 'break' && (
              <div className="flex items-center justify-center min-h-96">
                <div className="bg-white rounded-lg shadow-xl p-8 text-center max-w-md">
                  <h2 className="text-2xl font-bold mb-4 text-gray-800">Break Time</h2>
                  <div className="text-6xl mb-4">☕</div>
                  <p className="text-gray-600 mb-6">
                    Great job completing Trial A! Moving to Trial B with AI recommendations in 5 seconds...
                  </p>
                  <div className="text-sm text-gray-500">
                    Trial B will start automatically with emotion recognition enabled.
                  </div>
                </div>
              </div>
            )}

            {/* Complete Screen */}
            {experimentCycleActive && currentPhase === 'complete' && (
              <div className="flex items-center justify-center min-h-96">
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
            )}

            {/* Main Routes - Only show if not in break or complete phase */}
            {(!experimentCycleActive || (currentPhase !== 'break' && currentPhase !== 'complete')) && (
              <Routes>
                <Route path="/" element={
                  <OrderForm
                    experimentConfig={experimentConfig}
                    onExperimentOrderComplete={experimentCycleActive ? handleExperimentOrderComplete : undefined}
                    experimentCycleActive={experimentCycleActive}
                    currentPhase={currentPhase}
                    currentTrialInPhase={currentTrialInPhase}
                    aiRecommendations={aiRecommendations}
                    orderInstructions={experimentCycleActive ? getOrderInstructions() : null}
                    orderType={experimentCycleActive ? getCurrentOrderType() : 'standard'}
                    participantName={participantName}
                  />
                } />
                <Route path="/report" element={<ExperimentReport />} />
                <Route path="/measurements" element={<MeasurementDemo />} />
              </Routes>
            )}

            <AgentStatus />
          </div>
        </Router>
      </OrderProvider>
    </ExperimentProvider>
  );
}

export default App;