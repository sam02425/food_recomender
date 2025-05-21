import { recommendByWeather } from '../weatherAgent';

test('filters spicy sauce in hot weather', () => {
  const recs = [{ sauce: 'Red Spicy Sauce' }, { sauce: 'Mint Sauce' }];
  expect(recommendByWeather('hot', recs)).toEqual([{ sauce: 'Mint Sauce' }]);
});