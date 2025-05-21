import { updateWeights } from '../learnerAgent';

test('increases weight on accept', () => {
  const weights = { happy: { work: 1.0 } };
  expect(updateWeights(weights, 'happy', 'work', 'accept').happy.work).toBeCloseTo(1.05);
});