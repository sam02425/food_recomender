// Weather Agent: Fetch accurate weather for user's location and filter recommendations
export async function getWeatherForLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      resolve({ temp: null, weather: 'unknown' });
      return;
    }
    navigator.geolocation.getCurrentPosition(async (pos) => {
      const { latitude, longitude } = pos.coords;
      const url = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current_weather=true`;
      const res = await fetch(url);
      const data = await res.json();
      const temp = data.current_weather?.temperature;
      const weather = temp > 28 ? 'hot' : temp < 15 ? 'cold' : 'mild';
      resolve({ temp, weather });
    }, () => resolve({ temp: null, weather: 'unknown' }));
  });
}

// Weather Agent: Filter recommendations based on weather
export function recommendByWeather(weather, recs) {
  if (weather === 'hot') {
    return recs.filter(r => r.sauce !== 'Red Spicy Sauce');
  }
  return recs;
}