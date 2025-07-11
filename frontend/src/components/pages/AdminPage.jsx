import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AdminPage = () => {
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const [username, setUsername] = useState('');
  const [promoteMsg, setPromoteMsg] = useState('');
  const [experimentNumber, setExperimentNumber] = useState(1);
  const [experimentDesc, setExperimentDesc] = useState('');
  const [setupMsg, setSetupMsg] = useState('');
  const [analytics, setAnalytics] = useState(null);
  const [analyticsExpNo, setAnalyticsExpNo] = useState('');
  const [analyticsMsg, setAnalyticsMsg] = useState('');
  const [csvUrl, setCsvUrl] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is admin
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/');
      return;
    }
    fetch(`${API_URL}/api/auth/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        if (!data.is_admin) navigate('/');
        setIsAdmin(!!data.is_admin);
      })
      .catch(() => navigate('/'));
  }, [navigate, API_URL]);

  const promoteUser = async () => {
    setPromoteMsg('');
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_URL}/api/experiment/promote-user`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ username })
    });
    const data = await res.json();
    setPromoteMsg(data.message || data.detail || '');
  };

  const setupExperiment = async () => {
    setSetupMsg('');
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_URL}/api/experiment/setup-experiment`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ experiment_number: Number(experimentNumber), description: experimentDesc })
    });
    const data = await res.json();
    setSetupMsg(data.message || data.detail || '');
  };

  const getAnalytics = async () => {
    setAnalyticsMsg('');
    setAnalytics(null);
    setCsvUrl('');
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_URL}/api/experiment/analytics/${analyticsExpNo}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    const data = await res.json();
    if (data.success) setAnalytics(data.analytics);
    else setAnalyticsMsg(data.detail || 'Failed to fetch analytics');
  };

  const exportCSV = async () => {
    setCsvUrl('');
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_URL}/api/experiment/export-csv/${analyticsExpNo}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (res.ok) {
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      setCsvUrl(url);
    } else {
      setAnalyticsMsg('Failed to export CSV');
    }
  };

  return (
    <div className="admin-page bg-gray-50 min-h-screen p-8">
      <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-2xl p-8">
        <h1 className="text-3xl font-bold mb-6 text-center">Admin/Experimenter Panel</h1>
        <div className="mb-6">
          <label className="block font-semibold">Promote User to Admin</label>
          <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" className="border p-2 rounded mr-2" />
          <button onClick={promoteUser} className="bg-blue-600 text-white px-4 py-2 rounded">Promote</button>
          {promoteMsg && <div className="mt-2 text-sm text-green-700">{promoteMsg}</div>}
        </div>
        <div className="mb-6">
          <label className="block font-semibold">Set Up New Experiment</label>
          <input type="number" value={experimentNumber} onChange={e => setExperimentNumber(e.target.value)} placeholder="Experiment Number" className="border p-2 rounded mr-2 w-24" />
          <input value={experimentDesc} onChange={e => setExperimentDesc(e.target.value)} placeholder="Description" className="border p-2 rounded mr-2 w-64" />
          <button onClick={setupExperiment} className="bg-green-600 text-white px-4 py-2 rounded">Set Up</button>
          {setupMsg && <div className="mt-2 text-sm text-green-700">{setupMsg}</div>}
        </div>
        <div className="mb-6">
          <label className="block font-semibold">View Analytics for Experiment</label>
          <input type="number" value={analyticsExpNo} onChange={e => setAnalyticsExpNo(e.target.value)} placeholder="Experiment Number" className="border p-2 rounded mr-2 w-24" />
          <button onClick={getAnalytics} className="bg-purple-600 text-white px-4 py-2 rounded">Get Analytics</button>
          <button onClick={exportCSV} className="bg-yellow-600 text-white px-4 py-2 rounded ml-2">Export CSV</button>
          {csvUrl && <a href={csvUrl} download={`experiment_${analyticsExpNo}_participants.csv`} className="ml-4 text-blue-700 underline">Download CSV</a>}
          {analyticsMsg && <div className="mt-2 text-sm text-red-700">{analyticsMsg}</div>}
          {analytics && (
            <div className="mt-4 bg-gray-50 p-4 rounded shadow">
              <h3 className="font-semibold mb-2">Analytics</h3>
              <pre className="text-xs text-gray-800">{JSON.stringify(analytics, null, 2)}</pre>
              {/* Time-based stats */}
              {analytics.time_stats && (
                <div className="mt-2">
                  <h4 className="font-semibold">Time-based Stats</h4>
                  <pre className="text-xs text-gray-800">{JSON.stringify(analytics.time_stats, null, 2)}</pre>
                </div>
              )}
              {/* Response breakdowns */}
              {analytics.response_breakdown && (
                <div className="mt-2">
                  <h4 className="font-semibold">Response Breakdown</h4>
                  <pre className="text-xs text-gray-800">{JSON.stringify(analytics.response_breakdown, null, 2)}</pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPage;