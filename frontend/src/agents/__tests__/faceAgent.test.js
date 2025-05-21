import { detectMoodFromFace } from '../faceAgent';

test('detects happy mood from face data', () => {
  expect(detectMoodFromFace({ smile: 0.8 })).toBe('happy');
  expect(detectMoodFromFace({ smile: 0.2 })).toBe('neutral');
});