import { filterByHealth } from '../healthAgent';

test('filters out non-vegetarian proteins', () => {
  const recs = [{ protein: 'Chicken' }, { protein: 'Paneer' }];
  expect(filterByHealth(recs, { vegetarian: true })).toEqual([{ protein: 'Paneer' }]);
});