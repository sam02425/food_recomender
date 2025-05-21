import { saveSession, loadSession } from '../recordAgent';

test('saves and loads session data', () => {
  const data = { mood: 'happy' };
  saveSession(data);
  expect(loadSession()).toEqual(data);
});