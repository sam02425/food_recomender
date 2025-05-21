import { getShareLink } from '../socialAgent';

test('creates a mailto link', () => {
  expect(getShareLink({ mood: 'happy' })).toMatch(/^mailto:/);
});