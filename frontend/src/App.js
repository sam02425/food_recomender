import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import OrderForm from './components/OrderForm';
import ExperimentReport from './components/ExperimentReport';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100 py-8">
        <nav style={{ display: 'flex', justifyContent: 'flex-end', padding: '0 24px 16px 0' }}>
          <Link to="/" style={{ marginRight: 16, fontWeight: 500 }}>Order</Link>
          <Link to="/report" style={{ fontWeight: 500 }}>Report</Link>
        </nav>
        <Routes>
          <Route path="/" element={<OrderForm />} />
          <Route path="/report" element={<ExperimentReport />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;