// Face Agent: Mood detection from face data (simulated)
export function detectMoodFromFace(faceData) {
  // Simulate: return 'happy' if smile probability > 0.5, else 'neutral'
  return faceData.smile > 0.5 ? 'happy' : 'neutral';
}