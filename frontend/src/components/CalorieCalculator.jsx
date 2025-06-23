import React, { useState, useEffect } from 'react';
import { useOrder } from './OrderContext';

const CalorieCalculator = () => {
  const { currentItem } = useOrder();
  const [calorieInfo, setCalorieInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const calculateCalories = async () => {
      if (!currentItem.baseType || !currentItem.baseOption) return;

      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/calculate-calories`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            base_type: currentItem.baseType,
            base_option: currentItem.baseOption,
            protein: currentItem.protein,
            sauce: currentItem.sauce,
            veggies: currentItem.veggies || [],
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to calculate calories');
        }

        const data = await response.json();
        setCalorieInfo(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    calculateCalories();
  }, [currentItem]);

  if (loading) {
    return <div className="text-center p-4">Calculating calories...</div>;
  }

  if (error) {
    return <div className="text-red-500 p-4">Error: {error}</div>;
  }

  if (!calorieInfo) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mt-4">
      <h3 className="text-xl font-semibold mb-4">Nutrition Information</h3>

      <div className="mb-4">
        <div className="text-2xl font-bold text-primary">
          Total Calories: {calorieInfo.total_calories}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        {Object.entries(calorieInfo.breakdown).map(([type, calories]) => (
          <div key={type} className="bg-gray-50 p-3 rounded">
            <div className="text-sm text-gray-600 capitalize">{type}</div>
            <div className="text-lg font-semibold">{calories} cal</div>
          </div>
        ))}
      </div>

      <div className="mt-4">
        <h4 className="font-semibold mb-2">Item Breakdown</h4>
        <div className="space-y-2">
          {calorieInfo.items.map((item, index) => (
            <div key={index} className="flex justify-between items-center border-b pb-2">
              <span className="capitalize">{item.name}</span>
              <span className="font-medium">{item.calories} cal</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CalorieCalculator;