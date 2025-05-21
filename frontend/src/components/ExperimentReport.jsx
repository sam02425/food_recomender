import React, { useState } from 'react';
import { useExperiment } from '../context/ExperimentContext';

const ADMIN_PASSWORD = 'admin123'; // Change this for production

const BRAND_COLOR = '#e17009';
const BRAND_NAME = 'Curry Creations';

const expressionMap = {
  happy: '😊',
  sad: '😢',
  angry: '😠',
  surprised: '😲',
  disgusted: '🤢',
  fearful: '😨',
  neutral: '😐',
};

function formatTime(ts) {
  if (!ts) return '-';
  const d = new Date(ts);
  return d.toLocaleTimeString();
}

function formatDuration(ms) {
  if (!ms) return '-';
  const s = Math.floor(ms / 1000);
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  return `${m}m ${s % 60}s`;
}

function toCSV(stepData) {
  let csv = 'Step,Mood,Start,End,Duration\n';
  Object.entries(stepData).forEach(([step, data]) => {
    (data.moodTimeline || []).forEach((m) => {
      csv += `"${step}","${m.mood}","${formatTime(m.startTime)}","${formatTime(m.endTime)}","${m.endTime ? formatDuration(m.endTime - m.startTime) : '-'}"\n`;
    });
  });
  return csv;
}

// Analytics helpers
function getAverageStepTime(stepData) {
  const times = Object.values(stepData).map(d => d.time).filter(Boolean);
  if (!times.length) return '-';
  const avg = times.reduce((a, b) => a + b, 0) / times.length;
  return formatDuration(avg);
}
function getMoodCounts(stepData) {
  const counts = {};
  Object.values(stepData).forEach(data => {
    (data.moodTimeline || []).forEach(m => {
      counts[m.mood] = (counts[m.mood] || 0) + 1;
    });
  });
  return counts;
}
function getMostCommonMood(stepData) {
  const counts = getMoodCounts(stepData);
  let max = 0, mood = 'neutral';
  Object.entries(counts).forEach(([k, v]) => {
    if (v > max) { max = v; mood = k; }
  });
  return mood;
}

const ExperimentReport = () => {
  const { stepData, exportData } = useExperiment();
  const [entered, setEntered] = useState(false);
  const [input, setInput] = useState('');
  const [error, setError] = useState('');

  const handleExportJSON = () => {
    const dataStr = JSON.stringify(exportData(), null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `experiment-report-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportCSV = () => {
    const csv = toCSV(stepData);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `experiment-report-${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input === ADMIN_PASSWORD) {
      setEntered(true);
      setError('');
    } else {
      setError('Incorrect password.');
    }
  };

  // Analytics summary
  const sessionCount = 1; // For now, 1 session per report (can be extended for multi-user)
  const avgStepTime = getAverageStepTime(stepData);
  const mostCommonMood = getMostCommonMood(stepData);
  const moodCounts = getMoodCounts(stepData);

  if (!entered) {
    return (
      <div style={{ maxWidth: 400, margin: '80px auto', padding: 32, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px #0001' }}>
        <h2 style={{ marginBottom: 16 }}>Admin Access</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="password"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Enter admin password"
            style={{ width: '100%', padding: 8, fontSize: 16, marginBottom: 12, borderRadius: 4, border: '1px solid #ccc' }}
          />
          <button type="submit" style={{ width: '100%', padding: 10, fontSize: 16, borderRadius: 4, background: '#1976d2', color: '#fff', border: 'none', cursor: 'pointer' }}>
            Enter
          </button>
        </form>
        {error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 24 }}>
      {/* Branding */}
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 24 }}>
        <div style={{ width: 56, height: 56, borderRadius: '50%', background: BRAND_COLOR, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 32, color: '#fff', fontWeight: 700, marginRight: 16 }}>
          CC
        </div>
        <div>
          <h1 style={{ margin: 0, fontSize: 32, color: BRAND_COLOR, fontWeight: 800 }}>{BRAND_NAME}</h1>
          <div style={{ fontWeight: 500, color: '#444' }}>Admin Experiment Dashboard</div>
        </div>
      </div>
      {/* Analytics summary */}
      <div style={{ background: '#fffbe6', border: `1px solid ${BRAND_COLOR}`, borderRadius: 8, padding: 20, marginBottom: 32, boxShadow: '0 2px 8px #0001', display: 'flex', gap: 32, flexWrap: 'wrap' }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: 18 }}>Sessions</div>
          <div style={{ fontSize: 24, color: BRAND_COLOR }}>{sessionCount}</div>
        </div>
        <div>
          <div style={{ fontWeight: 600, fontSize: 18 }}>Avg. Step Time</div>
          <div style={{ fontSize: 24 }}>{avgStepTime}</div>
        </div>
        <div>
          <div style={{ fontWeight: 600, fontSize: 18 }}>Most Common Mood</div>
          <div style={{ fontSize: 24 }}>{expressionMap[mostCommonMood] || '😐'} <span style={{ fontSize: 16 }}>({mostCommonMood})</span></div>
        </div>
        <div>
          <div style={{ fontWeight: 600, fontSize: 18 }}>Mood Distribution</div>
          <div style={{ fontSize: 20 }}>
            {Object.entries(moodCounts).map(([m, c]) => (
              <span key={m} style={{ marginRight: 12 }}>{expressionMap[m] || '😐'} {c}</span>
            ))}
          </div>
        </div>
      </div>
      <h2 style={{ fontWeight: 700, fontSize: 28, marginBottom: 24 }}>Experiment Test Report</h2>
      {Object.entries(stepData).map(([step, data]) => (
        <div key={step} style={{ marginBottom: 32, background: '#f9f9f9', borderRadius: 8, padding: 16, boxShadow: '0 2px 8px #0001' }}>
          <h3 style={{ marginBottom: 8, fontWeight: 600, fontSize: 22 }}>{step.charAt(0).toUpperCase() + step.slice(1)}</h3>
          <div style={{ marginBottom: 8 }}>Total Time: <b>{formatDuration(data.time)}</b></div>
          <table style={{ width: '100%', marginTop: 8, borderCollapse: 'collapse', background: '#fff', borderRadius: 4 }}>
            <thead>
              <tr>
                <th style={{ borderBottom: '1px solid #ccc', padding: 6 }}>Mood</th>
                <th style={{ borderBottom: '1px solid #ccc', padding: 6 }}>Start</th>
                <th style={{ borderBottom: '1px solid #ccc', padding: 6 }}>End</th>
                <th style={{ borderBottom: '1px solid #ccc', padding: 6 }}>Duration</th>
              </tr>
            </thead>
            <tbody>
              {(data.moodTimeline || []).map((m, idx) => (
                <tr key={idx}>
                  <td style={{ textAlign: 'center', fontSize: 20, padding: 6 }}>{expressionMap[m.mood] || '😐'} <span style={{ fontSize: 14 }}>({m.mood})</span></td>
                  <td style={{ padding: 6 }}>{formatTime(m.startTime)}</td>
                  <td style={{ padding: 6 }}>{formatTime(m.endTime)}</td>
                  <td style={{ padding: 6 }}>{m.endTime ? formatDuration(m.endTime - m.startTime) : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
      <div style={{ display: 'flex', gap: 12 }}>
        <button onClick={handleExportJSON} style={{ padding: '8px 16px', fontSize: 16, borderRadius: 4, background: '#1976d2', color: '#fff', border: 'none', cursor: 'pointer' }}>
          Export Report as JSON
        </button>
        <button onClick={handleExportCSV} style={{ padding: '8px 16px', fontSize: 16, borderRadius: 4, background: '#388e3c', color: '#fff', border: 'none', cursor: 'pointer' }}>
          Export Report as CSV
        </button>
      </div>
    </div>
  );
};

export default ExperimentReport;