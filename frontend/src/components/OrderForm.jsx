import React, { useState, useEffect } from 'react';
import MenuSelectionGrid from './MenuSelectionGrid';
import BaseSelectionGrid from './BaseSelectionGrid';
import RecommendationFeedback from './RecommendationFeedback';
import * as apiService from '../services/api';
import CustomerIdentification from './CustomerIdentification';
import ActivitySelection from './ActivitySelection';
import OrderSummary from './OrderSummary';
import SocialSharing from './SocialSharing';

/**
 * Main order form component that manages the entire ordering flow.
 * Integrates all the specialized components and manages state.
 */
const OrderForm = () => {
  // State for the current step in the ordering process
  const [currentStep, setCurrentStep] = useState('protein');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Order data
  const [orderData, setOrderData] = useState(null);

  // Recommendations
  const [recommendations, setRecommendations] = useState({
    proteins: ['Chicken', 'Paneer/Indian Cheese'],
    sauces: ['Curry Special', 'Mint Sauce'],
    baseTypes: ['Bowl'],
    veggies: ['Bell Pepper', 'Spinach', 'Tomato']
  });

  // Selection state
  const [protein, setProtein] = useState('');
  const [sauce, setSauce] = useState('');
  const [baseType, setBaseType] = useState('');
  const [baseOption, setBaseOption] = useState('');
  const [veggies, setVeggies] = useState([]);
  const [dishName, setDishName] = useState('');

  // Custom suggestion inputs
  const [customProtein, setCustomProtein] = useState('');
  const [customBase, setCustomBase] = useState('');
  const [customDishName, setCustomDishName] = useState('');

  // Suggested items
  const [suggestedDishNames, setSuggestedDishNames] = useState({
    name: "Customer's Special Creation",
    alternatives: ["Flavor Fiesta", "Curry Creation"]
  });

  // Menu data
  const [menuData, setMenuData] = useState(null);
  const proteins = ['Chicken', 'Egg', 'Paneer/Indian Cheese', 'Soya', 'Potato', 'Pepperoni'];
  const sauces = ['Curry Special', 'Malai Masala', 'Curry Masala', 'Marinara', 'Yogurt/Raita', 'Red Spicy Sauce', 'Mint Sauce', 'Green Spicy Sauce'];
  const baseTypes = {
    'Biryani': [
      { name: 'Rice', price: 2.00, description: 'Fragrant basmati rice' }
    ],
    'Sandwich & Subs': [
      { name: 'Sourdough', price: 2.50, description: 'Tangy artisan bread' },
      { name: 'Ciabatta', price: 2.50, description: 'Italian white bread' },
      { name: 'White Bread', price: 2.00, description: 'Classic soft bread' },
      { name: 'Hoagie Bun', price: 2.50, description: 'Submarine sandwich roll' }
    ],
    'Wrap': [
      { name: 'Naan', price: 2.00, description: 'Traditional Indian flatbread' },
      { name: 'Pita', price: 2.00, description: 'Mediterranean pocket bread' }
    ],
    'Bowl': [
      { name: 'Bowl', price: 2.00, description: 'Served in a bowl, no bread' }
    ]
  };
  const veggieOptions = [
    'Grilled Onion', 'Bell Pepper', 'Tomato', 'Cilantro', 'Avocado',
    'Pineapple', 'Spinach', 'Jalapeño', 'Banana Pepper', 'Fried Onions',
    'Corn', 'Cabbage', 'Ghee', 'Mango Chutney'
  ];
  const premiumVeggies = ['Avocado'];

  // Initialize order on component mount
  useEffect(() => {
    const initializeOrder = async () => {
      try {
        setIsLoading(true);

        // Start a new order
        const orderResponse = await apiService.startOrder();
        if (orderResponse.success) {
          setOrderData(orderResponse.order_data);
        }

        // Get menu data
        /*
         * In a production app, we would uncomment this and use the data from the API
         * For now, we're using hardcoded menu data for demonstration

        const menuResponse = await apiService.getMenuData();
        if (menuResponse.success) {
          setMenuData(menuResponse.menu_data);
        }
        */

      } catch (error) {
        setError("Failed to initialize order. Please try again.");
        console.error("Order initialization error:", error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeOrder();
  }, []);

  // Handle base selection (updates both type and option)
  const handleBaseSelection = (type, option) => {
    setBaseType(type);
    setBaseOption(option);

    // If we're on the base step, move to the next step after selection
    if (currentStep === 'base') {
      setCurrentStep('dishName');
    }
  };

  // Get health recommendations
  const getHealthRecommendations = async (activityLevel) => {
    try {
      setIsLoading(true);
      const response = await apiService.getHealthRecommendations(activityLevel);

      if (response.success) {
        // Update recommendations state with health data
        const healthRecs = response.recommendations;
        setRecommendations(prev => ({
          ...prev,
          proteins: healthRecs.proteins || prev.proteins,
          veggies: healthRecs.veggies || prev.veggies
        }));
      }
    } catch (error) {
      setError("Failed to get health recommendations.");
      console.error("Health recommendations error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Get weather recommendations
  const getWeatherRecommendations = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getWeatherRecommendations();

      if (response.success) {
        // Update recommendations state with weather data
        const weatherRecs = response.recommendations;
        setRecommendations(prev => ({
          ...prev,
          baseTypes: weatherRecs.baseTypes || prev.baseTypes
        }));
      }
    } catch (error) {
      setError("Failed to get weather recommendations.");
      console.error("Weather recommendations error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Get dish name suggestions
  const getDishNameSuggestions = async () => {
    try {
      setIsLoading(true);
      const selections = { protein, baseType };

      const response = await apiService.getDishName(selections);

      if (response.success) {
        setSuggestedDishNames(response.suggestions);
      }
    } catch (error) {
      setError("Failed to get dish name suggestions.");
      console.error("Dish name suggestions error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle recommendation feedback
  const handleRecommendationFeedback = async (type, feedback, customValue = null) => {
    try {
      setIsLoading(true);

      const response = await apiService.submitRecommendationFeedback(
        type,
        feedback,
        customValue
      );

      if (response.success) {
        // Proceed based on feedback type
        return true;
      }

      return false;
    } catch (error) {
      setError(`Failed to process ${type} feedback.`);
      console.error("Feedback submission error:", error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Handle protein feedback
  const handleProteinFeedback = async (response, customValue = null) => {
    if (response === 'accept') {
      setProtein(recommendations.proteins[0] || 'Chicken');
      await handleRecommendationFeedback('health', 'accept');
    } else if (response === 'custom' && customValue) {
      setProtein(customValue);
      await handleRecommendationFeedback('health', 'custom', customValue);
    } else {
      await handleRecommendationFeedback('health', 'ignore');
    }

    // Get weather recommendations for next step
    await getWeatherRecommendations();
    setCurrentStep('base');
  };

  // Handle base feedback
  const handleBaseFeedback = async (response, customValue = null) => {
    if (response === 'accept') {
      const recommendedBase = recommendations.baseTypes[0] || 'Bowl';
      setBaseType(recommendedBase);

      // Set a default option based on the type
      if (recommendedBase === 'Biryani') {
        setBaseOption('Rice');
      } else if (recommendedBase === 'Sandwich & Subs') {
        setBaseOption('Sourdough');
      } else if (recommendedBase === 'Wrap') {
        setBaseOption('Naan');
      } else if (recommendedBase === 'Bowl') {
        setBaseOption('Bowl');
      }

      await handleRecommendationFeedback('weather', 'accept');
    } else if (response === 'custom' && customValue) {
      setBaseType(customValue);

      // Set a default option based on the type
      if (customValue === 'Biryani') {
        setBaseOption('Rice');
      } else if (customValue === 'Sandwich & Subs') {
        setBaseOption('Sourdough');
      } else if (customValue === 'Wrap') {
        setBaseOption('Naan');
      } else if (customValue === 'Bowl') {
        setBaseOption('Bowl');
      }

      await handleRecommendationFeedback('weather', 'custom', customValue);
    } else {
      await handleRecommendationFeedback('weather', 'ignore');
    }

    // Get dish name suggestions for next step
    await getDishNameSuggestions();
    setCurrentStep('dishName');
  };

  // Handle dish name feedback
  const handleDishNameFeedback = async (response, customValue = null) => {
    if (response === 'accept') {
      setDishName(suggestedDishNames.name);
      await handleRecommendationFeedback('dish_name', 'accept');
    } else if (response === 'custom' && customValue) {
      setDishName(customValue);
      await handleRecommendationFeedback('dish_name', 'custom', customValue);
    } else {
      await handleRecommendationFeedback('dish_name', 'ignore');
    }

    setCurrentStep('sauce');
  };

  // Add item to order
  const addItemToOrder = async () => {
    try {
      setIsLoading(true);

      const selections = {
        protein,
        sauce,
        base_type: baseType,
        base_option: baseOption,
        veggies,
        dish_name: dishName
      };

      const response = await apiService.addOrderItem(selections);

      if (response.success) {
        // In a real application, you would update the order state here
        return true;
      }

      return false;
    } catch (error) {
      setError("Failed to add item to order.");
      console.error("Add item error:", error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Complete order
  const completeOrder = async () => {
    try {
      setIsLoading(true);

      const response = await apiService.completeOrder();

      if (response.success) {
        alert("Your order has been completed successfully!");
        return true;
      }

      return false;
    } catch (error) {
      setError("Failed to complete order.");
      console.error("Complete order error:", error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate total price
  const calculateTotal = () => {
    let total = 0;

    // Add protein price (simple fixed prices)
    if (protein) total += 4.50; // Simplified, would normally look up actual prices

    // Add sauce price
    if (sauce) total += 1.50; // Simplified

    // Add base price
    if (baseType && baseOption) {
      const options = baseTypes[baseType] || [];
      const selectedOption = options.find(opt => opt.name === baseOption);
      if (selectedOption) {
        total += selectedOption.price;
      }
    }

    // Add veggie prices (first 5 free, extras $1 each, avocado $3)
    let regularVeggieCount = 0;
    veggies.forEach(veggie => {
      if (premiumVeggies.includes(veggie)) {
        total += 3.00; // Premium veggie
      } else {
        regularVeggieCount++;
        if (regularVeggieCount > 5) {
          total += 1.00; // Extra regular veggie
        }
      }
    });

    return total;
  };

  // Handle activity selection
  const handleActivitySelection = async (activity) => {
    await getHealthRecommendations(activity);
    setCurrentStep('protein');
  };

  // Start order button
  const handleStartOrder = () => {
    setCurrentStep('activity');
  };

  // Render the appropriate step
  const renderStep = () => {
    switch (currentStep) {
      case 'start':
        return (
          <div className="text-center py-12">
            <h1 className="text-4xl font-bold text-orange-700 mb-6">Welcome to Curry Creations!</h1>
            <p className="text-xl text-gray-600 mb-8">Ready to create your perfect meal?</p>
            <button
              onClick={handleStartOrder}
              disabled={isLoading}
              className="px-8 py-3 bg-orange-600 text-white text-lg rounded-lg hover:bg-orange-700 transition-colors disabled:bg-gray-400"
            >
              {isLoading ? 'Loading...' : 'Start Order'}
            </button>
          </div>
        );
    case 'identify':
      return (
        <CustomerIdentification
          onCustomerIdentified={handleCustomerIdentified}
          isLoading={isLoading}
        />
      );

    case 'activity':
      return (
        <ActivitySelection
          onActivitySelected={handleActivitySelection}
          isLoading={isLoading}
        />
      );


      case 'protein':
        return (
          <>
            <MenuSelectionGrid
              title="Select Your Protein"
              items={proteins}
              recommendations={recommendations.proteins}
              category="Protein"
              selectedItems={protein}
              onSelect={setProtein}
            />

            <RecommendationFeedback
              onIgnore={() => handleProteinFeedback('ignore')}
              onAccept={() => handleProteinFeedback('accept')}
              onCustom={(value) => handleProteinFeedback('custom', value)}
              customValue={customProtein}
              setCustomValue={setCustomProtein}
              itemType="protein"
              recommendedItem={recommendations.proteins[0]}
            />

            {protein && (
              <div className="mt-4 flex justify-end">
                <button
                  onClick={() => handleProteinFeedback('ignore')}
                  disabled={isLoading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                >
                  {isLoading ? 'Loading...' : 'Continue'}
                </button>
              </div>
            )}
          </>
        );

      case 'base':
        return (
          <>
            <BaseSelectionGrid
              title="Select Your Base"
              baseTypes={baseTypes}
              recommendations={recommendations.baseTypes}
              selectedBaseType={baseType}
              selectedBaseOption={baseOption}
              onSelect={handleBaseSelection}
            />

            <RecommendationFeedback
              onIgnore={() => handleBaseFeedback('ignore')}
              onAccept={() => handleBaseFeedback('accept')}
              onCustom={(value) => handleBaseFeedback('custom', value)}
              customValue={customBase}
              setCustomValue={setCustomBase}
              itemType="base type"
              recommendedItem={recommendations.baseTypes[0]}
            />

            {baseType && baseOption && (
              <div className="mt-4 flex justify-between">
                <button
                  onClick={() => setCurrentStep('protein')}
                  className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={() => handleBaseFeedback('ignore')}
                  disabled={isLoading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                >
                  {isLoading ? 'Loading...' : 'Continue'}
                </button>
              </div>
            )}
          </>
        );

      case 'dishName':
        return (
          <>
            <div className="w-full mb-6">
              <h2 className="text-xl font-bold mb-3">Your Personalized Dish Name</h2>

              <div className="mb-6 p-6 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-100 text-center">
                <h3 className="text-2xl font-bold text-orange-700 mb-2">🎉 {suggestedDishNames.name}</h3>
                <p className="text-gray-600">Personalized just for you!</p>
              </div>

              <div className="mb-4">
                <h3 className="text-lg font-medium mb-2">Alternative names:</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {suggestedDishNames.alternatives.map((name, index) => (
                    <div
                      key={index}
                      onClick={() => setSuggestedDishNames({...suggestedDishNames, name})}
                      className="p-3 bg-white rounded-md border border-gray-200 cursor-pointer hover:border-orange-300 hover:bg-orange-50 transition-colors"
                    >
                      {name}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <RecommendationFeedback
              onIgnore={() => handleDishNameFeedback('ignore')}
              onAccept={() => handleDishNameFeedback('accept')}
              onCustom={(value) => handleDishNameFeedback('custom', value)}
              customValue={customDishName}
              setCustomValue={setCustomDishName}
              itemType="dish name"
              recommendedItem={suggestedDishNames.name}
            />

            <div className="mt-4 flex justify-between">
              <button
                onClick={() => setCurrentStep('base')}
                className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
              >
                Back
              </button>
              <button
                onClick={() => handleDishNameFeedback('ignore')}
                disabled={isLoading}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400"
              >
                {isLoading ? 'Loading...' : 'Continue'}
              </button>
            </div>
          </>
        );

      case 'sauce':
        return (
          <>
            <MenuSelectionGrid
              title="Select Your Sauce"
              items={sauces}
              recommendations={recommendations.sauces}
              category="Sauce"
              selectedItems={sauce}
              onSelect={setSauce}
            />

            {sauce && (
              <div className="mt-4 flex justify-between">
                <button
                  onClick={() => setCurrentStep('dishName')}
                  className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={() => setCurrentStep('veggies')}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Continue
                </button>
              </div>
            )}
          </>
        );

      case 'veggies':
        return (
          <>
            <MenuSelectionGrid
              title="Select Your Veggies"
              items={veggieOptions}
              recommendations={recommendations.veggies}
              category="Veggies"
              selectedItems={veggies}
              onSelect={setVeggies}
              maxFreeSelections={5}
              premiumItems={premiumVeggies}
              premiumPrice={3.0}
              extraPrice={1.0}
            />

            <div className="mt-4 flex justify-between">
              <button
                onClick={() => setCurrentStep('sauce')}
                className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
              >
                Back
              </button>
              <button
                onClick={() => setCurrentStep('review')}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Review Order
              </button>
            </div>
          </>
        );

        case 'review':
            return (
              <OrderSummary
                orderItems={[
                  {
                    dish_name: dishName,
                    protein: protein,
                    sauce: sauce,
                    base_type: baseType,
                    base_option: baseOption,
                    veggies: veggies,
                    price: calculateTotal()
                  }
                ]}
                totalPrice={calculateTotal()}
                onAddAnother={() => {
                  // Reset selections and go back to protein step
                  setProtein('');
                  setSauce('');
                  setBaseType('');
                  setBaseOption('');
                  setVeggies([]);
                  setDishName('');
                  setCurrentStep('protein');
                }}
                onComplete={handleCompleteOrder}
                isLoading={isLoading}
              />
            );

          case 'social_sharing':
            return (
              <SocialSharing
                dishName={dishName || "Custom Creation"}
                customerName={customerData?.name || "Guest"}
                onShare={handleSocialShare}
                onSkip={() => setCurrentStep('complete')}
                isLoading={isLoading}
              />
            );

        // Add handling for 'complete' step
        case 'complete':
            return (
              <div className="text-center py-8">
                <div className="text-5xl mb-4">🎉</div>
                <h2 className="text-2xl font-bold mb-4">Order Complete!</h2>
                <p className="text-gray-600 mb-6">
                  Your order has been placed and will be ready shortly.
                </p>
                <button
                  onClick={() => {
                    // Reset everything
                    setCurrentStep('start');
                    setProtein('');
                    setSauce('');
                    setBaseType('');
                    setBaseOption('');
                    setVeggies([]);
                    setDishName('');
                    setOrderData(null);
                  }}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Start New Order
                </button>
              </div>
            );

          default:
            return <div>Invalid step</div>;
        }
      };

  // Render progress bar
  const renderProgressBar = () => {
    if (currentStep === 'start' || currentStep === 'activity') {
      return null;
    }

    const steps = [
      { id: 'protein', label: 'Protein' },
      { id: 'base', label: 'Base' },
      { id: 'dishName', label: 'Name' },
      { id: 'sauce', label: 'Sauce' },
      { id: 'veggies', label: 'Veggies' },
      { id: 'review', label: 'Review' }
    ];

    const currentIndex = steps.findIndex(step => step.id === currentStep);

    return (
      <div className="mb-8">
        <div className="flex justify-between mb-2">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`flex flex-col items-center ${index <= currentIndex ? 'text-blue-600' : 'text-gray-400'}`}
              style={{ width: `${100 / steps.length}%` }}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center mb-1
                  ${index < currentIndex ? 'bg-blue-600 text-white' :
                    index === currentIndex ? 'border-2 border-blue-600 text-blue-600' :
                    'border-2 border-gray-300 text-gray-400'}`}
              >
                {index < currentIndex ? '✓' : index + 1}
              </div>
              <span className="text-sm text-center">{step.label}</span>
            </div>
          ))}
        </div>

        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div
            className="bg-blue-600 h-2.5 rounded-full transition-all"
            style={{ width: `${(currentIndex / (steps.length - 1)) * 100}%` }}
          ></div>
        </div>
      </div>
    );
  };

  // Show error message
  const renderError = () => {
    if (!error) return null;

    return (
      <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md flex justify-between items-center">
        <span>{error}</span>
        <button onClick={() => setError(null)} className="ml-4 text-red-700">
          &times;
        </button>
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-orange-700">Curry Creations</h1>
        <p className="text-gray-600">Create your perfect meal!</p>
      </div>

      {renderError()}
      {renderProgressBar()}

      <div className="bg-white rounded-lg shadow-md p-6">
        {isLoading && currentStep !== 'start' && (
          <div className="absolute inset-0 bg-white bg-opacity-70 flex items-center justify-center z-10">
            <div className="text-center">
              <div className="animate-spin h-10 w-10 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
              <p className="text-blue-600">Loading...</p>
            </div>
          </div>
        )}

        {renderStep()}
      </div>
    </div>
  );
};

export default OrderForm;