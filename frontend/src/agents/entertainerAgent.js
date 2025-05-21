// Entertainer Agent: Provide fun facts or engagement
export function getFunFact() {
  return 'Did you know? Paneer is a great source of protein!';
}

// Entertainer Agent: Fun, context-aware fallback dish name generator
const defaultPatterns = {
  weather: {
    sunny: ["Sunshine", "Solar", "Bright", "Daylight"],
    rainy: ["Rainy Day", "Monsoon", "Downpour", "Drizzle"],
    cloudy: ["Cloudy", "Overcast", "Gray Sky", "Misty"],
    snowy: ["Snowy", "Frosty", "Winter", "Flurry"],
    hot: ["Sizzling", "Spicy Heat", "Fiery", "Scorching"],
    cold: ["Chilled", "Cool", "Frosty", "Arctic"]
  },
  mood: {
    happy: ["Happy", "Joyful", "Cheerful", "Smiling"],
    sad: ["Comfort", "Soulful", "Uplifting", "Warming"],
    neutral: ["Classic", "Balanced", "Special", "Signature"],
    tired: ["Energizing", "Revitalizing", "Refreshing", "Boost"],
    stressed: ["Calming", "Zen", "Tranquil", "Relaxing"],
    surprised: ["Surprising", "Adventurous", "Bold", "Unexpected"],
    angry: ["Cooling", "Balanced", "Harmonious", "Soothing"]
  },
  protein: {
    Chicken: ["Tender", "Juicy", "Grilled", "Roasted"],
    Egg: ["Golden", "Farm-Fresh", "Sunny", "Perfect"],
    "Paneer/Indian Cheese": ["Creamy", "Authentic", "Soft", "Melty"],
    Soya: ["Plant-Powered", "Green", "Earth", "Protein-Packed"],
    Potato: ["Fluffy", "Golden", "Hearty", "Comforting"],
    Pepperoni: ["Savory", "Spiced", "Italian", "Zesty"]
  },
  base_type: {
    Bowl: ["Bowl", "Bowl of Joy", "Power Bowl", "Fusion Bowl"],
    Wrap: ["Wrap", "Roll", "Fusion Wrap", "Hand-Rolled Wrap"],
    Sandwich: ["Sandwich", "Fusion Sandwich", "Stacked Sandwich", "Delight Sandwich"],
    Biryani: ["Biryani", "Royal Biryani", "Aromatic Biryani", "Flavorful Biryani"]
  }
};

function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

export function generateDishName({ protein, base_type, weather, mood }) {
  const weatherTerm = pick(defaultPatterns.weather[weather] || ["Special"]);
  const moodTerm = pick(defaultPatterns.mood[mood] || ["Signature"]);
  const proteinAdj = pick(defaultPatterns.protein[protein] || ["Delicious"]);
  const baseFormat = pick(defaultPatterns.base_type[base_type] || ["Dish"]);
  return `${weatherTerm} ${moodTerm} ${proteinAdj} ${baseFormat}`;
}