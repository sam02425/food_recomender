// Learner Agent: Update recommendation weights based on feedback
export function updateWeights(weights, mood, activity, feedback) {
  if (feedback === 'accept') {
    weights[mood][activity] *= 1.05;
  } else if (feedback === 'ignore') {
    weights[mood][activity] *= 0.98;
  }
  return weights;
}