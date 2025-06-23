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
  const [experimentConfig, setExperimentConfig] = useState(null);
  const [showExperimentSetup, setShowExperimentSetup] = useState(true);

  const handleExperimentStart = (config) => {
    setExperimentConfig(config);
    setShowExperimentSetup(false);
  };

  const handleExperimentReset = () => {
    setExperimentConfig(null);
    setShowExperimentSetup(true);
  };

  // Show experiment setup if no experiment is configured
  if (showExperimentSetup) {
    return (
      <ExperimentProvider>
        <ExperimentSetup onExperimentStart={handleExperimentStart} />
      </ExperimentProvider>
    );
  }

  return (
    <ExperimentProvider>
      <OrderProvider>
        <Router>
          <div className="min-h-screen bg-gray-100 py-8">
            {/* Experiment Header */}
            <div className="bg-white shadow-sm border-b mb-8">
              <div className="max-w-6xl mx-auto px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <h1 className="text-xl font-semibold text-gray-900">
                      🍛 Curry Creations Experiment
                    </h1>
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
                  </div>
                  <button
                    onClick={handleExperimentReset}
                    className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                  >
                    Reset Experiment
                  </button>
                </div>
              </div>
            </div>

            <nav style={{ display: 'flex', justifyContent: 'flex-end', padding: '0 24px 16px 0' }}>
              <Link to="/" style={{ marginRight: 16, fontWeight: 500 }}>Order</Link>
              <Link to="/report" style={{ marginRight: 16, fontWeight: 500 }}>Report</Link>
              <Link to="/measurements" style={{ fontWeight: 500 }}>Measurements</Link>
            </nav>

            <Routes>
              <Route path="/" element={<OrderForm experimentConfig={experimentConfig} />} />
              <Route path="/report" element={<ExperimentReport />} />
              <Route path="/measurements" element={<MeasurementDemo />} />
            </Routes>

            <AgentStatus />
          </div>
        </Router>
      </OrderProvider>
    </ExperimentProvider>
  );
}

export default App;