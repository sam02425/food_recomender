import React, { useState } from 'react';
import './ParticipantRegistration.css';

const ParticipantRegistration = ({ onRegistrationComplete }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    age: '',
    gender: '',
    country: '',
    ethnicity: '',
    occupation: '',
    tech_proficiency: 'intermediate',
    ordering_frequency: 'medium',
    activity_preferences: ['work'],
    protein_preferences: ['Chicken'],
    feedback_pattern: 'selective',
    baseline_emotions: ['neutral'],
    decision_style: 'cautious_deliberate'
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleMultiSelect = (field, value, checked) => {
    setFormData(prev => ({
      ...prev,
      [field]: checked
        ? [...prev[field], value]
        : prev[field].filter(item => item !== value)
    }));
  };

  const validateForm = () => {
    if (!formData.name.trim()) return 'Name is required';
    if (!formData.email.trim()) return 'Email is required';
    if (!formData.age || formData.age < 18 || formData.age > 100) return 'Age must be between 18 and 100';
    if (!formData.gender) return 'Gender is required';
    if (!formData.country) return 'Country is required';
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch('http://localhost:8000/api/participants/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          age: parseInt(formData.age),
          personality_traits: {
            openness: 0.7,
            conscientiousness: 0.8,
            extraversion: 0.6,
            agreeableness: 0.7,
            neuroticism: 0.3
          }
        })
      });

      const result = await response.json();

      if (response.ok) {
        setSuccess(`Registration successful! Your participant ID is: ${result.participant_id}`);
        if (onRegistrationComplete) {
          onRegistrationComplete(result.participant_id, formData);
        }
      } else {
        setError(result.detail || 'Registration failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="participant-registration">
      <div className="registration-header">
        <h2>🧪 Participant Registration</h2>
        <p>Please provide your information to participate in the food ordering experiment</p>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <form onSubmit={handleSubmit} className="registration-form">
        <div className="form-section">
          <h3>Basic Information</h3>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="name">Full Name *</label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email Address *</label>
              <input
                type="email"
                id="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="phone">Phone Number</label>
              <input
                type="tel"
                id="phone"
                value={formData.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="age">Age *</label>
              <input
                type="number"
                id="age"
                min="18"
                max="100"
                value={formData.age}
                onChange={(e) => handleInputChange('age', e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="gender">Gender *</label>
              <select
                id="gender"
                value={formData.gender}
                onChange={(e) => handleInputChange('gender', e.target.value)}
                required
              >
                <option value="">Select gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="non-binary">Non-binary</option>
                <option value="prefer-not-to-say">Prefer not to say</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="country">Country *</label>
              <select
                id="country"
                value={formData.country}
                onChange={(e) => handleInputChange('country', e.target.value)}
                required
              >
                <option value="">Select country</option>
                <option value="India">India</option>
                <option value="Bangladesh">Bangladesh</option>
                <option value="USA">United States</option>
                <option value="UK">United Kingdom</option>
                <option value="Canada">Canada</option>
                <option value="Australia">Australia</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="ethnicity">Ethnicity</label>
              <input
                type="text"
                id="ethnicity"
                value={formData.ethnicity}
                onChange={(e) => handleInputChange('ethnicity', e.target.value)}
                placeholder="e.g., Indian, American, etc."
              />
            </div>

            <div className="form-group">
              <label htmlFor="occupation">Occupation</label>
              <input
                type="text"
                id="occupation"
                value={formData.occupation}
                onChange={(e) => handleInputChange('occupation', e.target.value)}
                placeholder="e.g., Student, Engineer, etc."
              />
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Technical & Behavioral Information</h3>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="tech_proficiency">Technical Proficiency</label>
              <select
                id="tech_proficiency"
                value={formData.tech_proficiency}
                onChange={(e) => handleInputChange('tech_proficiency', e.target.value)}
              >
                <option value="basic">Basic</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="ordering_frequency">Food Ordering Frequency</label>
              <select
                id="ordering_frequency"
                value={formData.ordering_frequency}
                onChange={(e) => handleInputChange('ordering_frequency', e.target.value)}
              >
                <option value="low">Low (1-2 times/month)</option>
                <option value="medium">Medium (1-2 times/week)</option>
                <option value="high">High (3+ times/week)</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Activity Preferences (Select all that apply)</label>
            <div className="checkbox-group">
              {['work', 'study', 'gym', 'active', 'chilling'].map(activity => (
                <label key={activity} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.activity_preferences.includes(activity)}
                    onChange={(e) => handleMultiSelect('activity_preferences', activity, e.target.checked)}
                  />
                  {activity.charAt(0).toUpperCase() + activity.slice(1)}
                </label>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Protein Preferences (Select all that apply)</label>
            <div className="checkbox-group">
              {['Chicken', 'Paneer/Indian Cheese', 'Egg', 'Soya', 'Potato'].map(protein => (
                <label key={protein} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.protein_preferences.includes(protein)}
                    onChange={(e) => handleMultiSelect('protein_preferences', protein, e.target.checked)}
                  />
                  {protein}
                </label>
              ))}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="feedback_pattern">Feedback Pattern</label>
              <select
                id="feedback_pattern"
                value={formData.feedback_pattern}
                onChange={(e) => handleInputChange('feedback_pattern', e.target.value)}
              >
                <option value="selective">Selective (only when needed)</option>
                <option value="mostly_accept">Mostly Accept</option>
                <option value="custom_focused">Custom Focused</option>
                <option value="experimental">Experimental</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="decision_style">Decision Style</label>
              <select
                id="decision_style"
                value={formData.decision_style}
                onChange={(e) => handleInputChange('decision_style', e.target.value)}
              >
                <option value="quick_decisive">Quick & Decisive</option>
                <option value="analytical_thorough">Analytical & Thorough</option>
                <option value="cautious_deliberate">Cautious & Deliberate</option>
                <option value="exploratory_adaptive">Exploratory & Adaptive</option>
              </select>
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading} className="submit-button">
            {loading ? '🔄 Registering...' : '✅ Register for Experiment'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ParticipantRegistration;