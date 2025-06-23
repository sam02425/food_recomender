import React, { useState, useEffect } from 'react';

const AgentStatus = () => {
  const [agentData, setAgentData] = useState(null);
  const [isVisible, setIsVisible] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchAgentStatus = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/agent-status`);
      const data = await response.json();
      setAgentData(data);
    } catch (error) {
      console.error('Error fetching agent status:', error);
    }
  };

  useEffect(() => {
    if (autoRefresh) {
      fetchAgentStatus();
      const interval = setInterval(fetchAgentStatus, 2000); // Update every 2 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getStatusColor = (status) => {
    if (status.includes('Error')) return 'text-red-600 bg-red-100';
    if (status.includes('Processing') || status.includes('Generating')) return 'text-blue-600 bg-blue-100';
    if (status.includes('completed') || status.includes('generated')) return 'text-green-600 bg-green-100';
    return 'text-gray-600 bg-gray-100';
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return 'Never';
    return new Date(timestamp).toLocaleTimeString();
  };

  const startAutomatedExperiments = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/start-automated-experiments`, {
        method: 'POST'
      });
      const result = await response.json();
      if (result.success) {
        alert('Automated experiments started! Check the backend logs for progress.');
      } else {
        alert(`Failed to start experiments: ${result.error}`);
      }
    } catch (error) {
      alert(`Error starting experiments: ${error.message}`);
    }
  };

  if (!isVisible) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setIsVisible(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-blue-700 transition-colors"
        >
          Show Agent Status
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 bg-white border border-gray-300 rounded-lg shadow-xl p-4 max-w-md">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-bold text-lg">Agent Activity Monitor</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-2 py-1 rounded text-sm ${
              autoRefresh ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
            }`}
          >
            {autoRefresh ? 'Auto' : 'Manual'}
          </button>
          <button
            onClick={() => setIsVisible(false)}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
      </div>

      {agentData && (
        <div className="space-y-2">
          {Object.entries(agentData.agents).map(([agentName, agentInfo]) => (
            <div key={agentName} className="border border-gray-200 rounded p-2">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="font-medium text-sm capitalize">
                    {agentName.replace('_agent', '').replace('_', ' ')}
                  </div>
                  <div className={`text-xs px-2 py-1 rounded mt-1 ${getStatusColor(agentInfo.status)}`}>
                    {agentInfo.status}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Last: {formatTime(agentInfo.last_activity)}
                  </div>
                </div>
                <div className="text-xs text-gray-500 ml-2">
                  Count: {agentInfo.activity_count}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-4 pt-3 border-t border-gray-200">
        <div className="flex gap-2">
          <button
            onClick={fetchAgentStatus}
            className="flex-1 bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
          >
            Refresh
          </button>
          <button
            onClick={startAutomatedExperiments}
            className="flex-1 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
          >
            Start 200 Tests
          </button>
        </div>
      </div>

      {agentData && (
        <div className="text-xs text-gray-500 mt-2 text-center">
          Updated: {formatTime(agentData.timestamp)}
        </div>
      )}
    </div>
  );
};

export default AgentStatus;