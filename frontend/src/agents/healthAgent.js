// Health Agent: Filter recommendations by health/dietary preferences
export function filterByHealth(recs, preferences) {
  if (preferences.vegetarian) {
    return recs.filter(r => r.protein !== 'Chicken' && r.protein !== 'Egg');
  }
  return recs;
}