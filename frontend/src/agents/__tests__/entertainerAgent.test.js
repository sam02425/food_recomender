import { getFunFact } from '../entertainerAgent';

test('returns a fun fact', () => {
  expect(getFunFact()).toMatch(/Did you know/);
});