import React, { useState } from 'react';

const emojiOptions = [
  { value: 'amazing', label: '😃 Amazing' },
  { value: 'good', label: '🙂 Good' },
  { value: 'neutral', label: '😐 Neutral' },
  { value: 'confused', label: '😕 Confused' },
  { value: 'angry', label: '😡 Angry' }
];

const genderOptions = [
  { value: '', label: 'Select gender' },
  { value: 'Male', label: 'Male' },
  { value: 'Female', label: 'Female' },
  { value: 'Non-binary', label: 'Non-binary' },
  { value: 'Prefer not to say', label: 'Prefer not to say' }
];

const ExperimentComplete = ({ results }) => {
  const [submitted, setSubmitted] = useState(false);
  const [emoji, setEmoji] = useState('');
  const [stars, setStars] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [email, setEmail] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');

  if (submitted) {
    return (
      <div style={{ maxWidth: 400, margin: '0 auto', padding: 24, background: '#fff', borderRadius: 8 }}>
        <h2>Thank you for participating!</h2>
        <p>Your results have been securely sent to the Curry Creations research team.</p>
        <p>If you have questions, contact <a href="mailto:currycreationsfood@gmail.com">currycreationsfood@gmail.com</a></p>
      </div>
    );
  }

  return (
    <form
      action="https://formsubmit.co/currycreationsfood@gmail.com"
      method="POST"
      onSubmit={() => setSubmitted(true)}
      style={{ maxWidth: 400, margin: '0 auto', padding: 24, background: '#fff', borderRadius: 8 }}
    >
      <h2 style={{ marginBottom: 12 }}>How was your experience?</h2>
      <div style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: 8 }}>Emoji rating:</div>
        {emojiOptions.map(opt => (
          <label key={opt.value} style={{ marginRight: 10, cursor: 'pointer', fontSize: 22 }}>
            <input
              type="radio"
              name="emoji_rating"
              value={opt.value}
              checked={emoji === opt.value}
              onChange={() => setEmoji(opt.value)}
              style={{ marginRight: 4 }}
              required={stars === 0}
            />
            {opt.label}
          </label>
        ))}
      </div>
      <div style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: 8 }}>Or rate with stars:</div>
        {[1, 2, 3, 4, 5].map(n => (
          <span
            key={n}
            style={{
              fontSize: 28,
              cursor: 'pointer',
              color: n <= stars ? '#e17009' : '#ccc'
            }}
            onClick={() => setStars(n)}
            role="button"
            aria-label={`${n} star${n > 1 ? 's' : ''}`}
          >★</span>
        ))}
        <input type="hidden" name="star_rating" value={stars} />
      </div>
      <label style={{ display: 'block', margin: '12px 0 4px' }}>
        Age:
        <input
          type="number"
          name="age"
          value={age}
          onChange={e => setAge(e.target.value)}
          min="1"
          max="120"
          style={{ width: '100%', padding: 8, marginTop: 4, borderRadius: 4, border: '1px solid #ccc' }}
          required
        />
      </label>
      <label style={{ display: 'block', margin: '12px 0 4px' }}>
        Gender:
        <select
          name="gender"
          value={gender}
          onChange={e => setGender(e.target.value)}
          style={{ width: '100%', padding: 8, marginTop: 4, borderRadius: 4, border: '1px solid #ccc' }}
          required
        >
          {genderOptions.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </label>
      <label style={{ display: 'block', margin: '12px 0 4px' }}>
        Any suggestions or comments?
        <textarea
          name="feedback"
          value={feedback}
          onChange={e => setFeedback(e.target.value)}
          rows={3}
          style={{ width: '100%', padding: 8, marginTop: 4, borderRadius: 4, border: '1px solid #ccc' }}
          placeholder="Your feedback helps us improve!"
        />
      </label>
      <label style={{ display: 'block', margin: '12px 0 4px' }}>
        Your email (optional):
        <input
          type="email"
          name="participant_email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="you@example.com"
          style={{ width: '100%', padding: 8, marginTop: 4, borderRadius: 4, border: '1px solid #ccc' }}
        />
      </label>
      {/* Hidden field with all experiment data */}
      <input type="hidden" name="results" value={JSON.stringify(results)} />
      <button
        type="submit"
        style={{ marginTop: 16, padding: 10, fontSize: 16, borderRadius: 4, background: '#e17009', color: '#fff', border: 'none' }}
      >
        Submit Results
      </button>
      <p style={{ fontSize: 12, color: '#888', marginTop: 8 }}>
        Your results will be sent securely to the Curry Creations research team.
      </p>
    </form>
  );
};

export default ExperimentComplete;