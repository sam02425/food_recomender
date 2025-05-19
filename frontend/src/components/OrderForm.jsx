import React, { useState, useEffect } from 'react';
import MenuSelectionGrid from './MenuSelectionGrid';
import BaseSelectionGrid from './BaseSelectionGrid';
import RecommendationFeedback from './RecommendationFeedback';
import * as apiService from './services/api';
import CustomerIdentification from './CustomerIdentification';
import ActivitySelection from './ActivitySelection';
import OrderSummary from './OrderSummary';
import SocialSharing from './SocialSharing';

/**
 * Enhanced order form component that manages the entire ordering flow.
 * Added ability to go back, remove items, and improved navigation.
 */
const OrderForm = () => {
  // State for the current step in the ordering process
  const [currentStep, setCurrentStep] = useState('start');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Order data
  const [orderData, setOrderData] = useState(null);

  // Initialize recommendations with empty arrays to prevent map errors
  const [recommendations, setRecommendations] = useState({
    proteins: [],
    sauces: [],
    base_types: [],
    veggies: [],
    reasoning: ""
  });

  // Selection state
  const [protein, setProtein] = useState('');
  const [sauce, setSauce] = useState('');
  const [baseType, setBaseType] = useState('');
  const [baseOption, setBaseOption] = useState('');
  const [veggies, setVeggies] = useState([]);
  const [dishName, setDishName] = useState('');

  // Customer data
  const [customerData, setCustomerData] = useState(null);
  const [previousOrders, setPreviousOrders] = useState([]);

  // Order items array
  const [orderItems, setOrderItems] = useState([]);

  // Custom suggestion inputs
  const [customProtein, setCustomProtein] = useState('');
  const [customBase, setCustomBase] = useState('');
  const [customDishName, setCustomDishName] = useState('');

  // Suggested items - initialize with empty values
  const [suggestedDishNames, setSuggestedDishNames] = useState({
    name: "",
    alternatives: [],
    format_used: ""
  });

  // Menu data with proper objects for proteins that include price and description
  const [menuData, setMenuData] = useState(null);
  const proteins = [
    { name: "Chicken", price: 4.50, description: "Grilled chicken pieces" },
    { name: "Egg", price: 3.00, description: "Boiled or fried egg" },
    { name: "Paneer/Indian Cheese", price: 4.00, description: "Fresh Indian cheese cubes" },
    { name: "Soya", price: 3.50, description: "Marinated soya chunks" },
    { name: "Potato", price: 2.50, description: "Spiced potato cubes" },
    { name: "Pepperoni", price: 4.50, description: "Sliced pepperoni" }
  ];

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
        if (orderResponse?.success) {
          setOrderData(orderResponse.order_data);
        }

        // Get menu data
        const menuResponse = await apiService.getMenuData();
        if (menuResponse?.success) {
          setMenuData(menuResponse.menu_data);
        }

      } catch (error) {
        setError("Failed to initialize order. Please try again.");
        console.error("Order initialization error:", error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeOrder();
  }, []);

  // Handle customer identification
  const handleCustomerIdentified = async (customerInfo) => {
    setIsLoading(true);

    try {
      // Save the customer data
      setCustomerData(customerInfo);

      // Fetch previous orders for this customer if we have a phone number
      if (customerInfo.phoneNumber) {
        // This would be a new API call to get customer's previous orders
        const response = await apiService.getCustomerPreviousOrders(customerInfo.phoneNumber);
        if (response?.success) {
          setPreviousOrders(response.orders || []);
        }
      }

      setCurrentStep('activity');
    } catch (error) {
      setError("Failed to retrieve customer data.");
      console.error("Customer data error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle base selection (updates both type and option)
  const handleBaseSelection = (type, option) => {
    // If reselecting the same base, allow deselection
    if (type === baseType && option === baseOption) {
      setBaseType('');
      setBaseOption('');
    } else {
      setBaseType(type);
      setBaseOption(option);

      // If we're on the base step, move to the next step after selection
      if (currentStep === 'base') {
        setCurrentStep('dishName');
      }
    }
  };

  // Get health recommendations
  const getHealthRecommendations = async (activityLevel) => {
    try {
      setIsLoading(true);
      const response = await apiService.getHealthRecommendations(
        activityLevel,
        customerData?.phoneNumber // Pass phone number for personalized recommendations
      );

      if (response?.success) {
        // Update recommendations state with health data
        const healthRecs = response.recommendations || {};
        setRecommendations(prev => ({
          ...prev,
          proteins: healthRecs.proteins || [],
          sauces: healthRecs.sauces || [],
          base_types: healthRecs.base_types || [],
          veggies: healthRecs.veggies || [],
          reasoning: healthRecs.reasoning || ""
        }));
      } else {
        // Set default recommendations if request failed
        setRecommendations({
          proteins: ["Chicken", "Paneer/Indian Cheese"],
          sauces: ["Curry Special", "Mint Sauce"],
          base_types: ["Bowl"],
          veggies: ["Bell Pepper", "Spinach", "Tomato"],
          reasoning: "Default recommendations for your activity level."
        });
      }
    } catch (error) {
      setError("Failed to get health recommendations.");
      console.error("Health recommendations error:", error);
      // Set default recommendations on error
      setRecommendations({
        proteins: ["Chicken", "Paneer/Indian Cheese"],
        sauces: ["Curry Special", "Mint Sauce"],
        base_types: ["Bowl"],
        veggies: ["Bell Pepper", "Spinach", "Tomato"],
        reasoning: "Default recommendations for your activity level."
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Get weather recommendations
  const getWeatherRecommendations = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getWeatherRecommendations(
        customerData?.phoneNumber // Pass phone number for personalized recommendations
      );

      if (response?.success) {
        // Update recommendations state with weather data
        const weatherRecs = response.recommendations || {};
        setRecommendations(prev => ({
          ...prev,
          base_types: weatherRecs.base_types || prev.base_types || [],
          suggested_base: weatherRecs.suggested_base || "",
          reasoning: weatherRecs.reasoning || prev.reasoning || ""
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
      const selections = {
        protein: protein || "Chicken",
        base_type: baseType || "Bowl",
        customer_name: customerData?.name // Pass customer name for personalization
      };

      const response = await apiService.getDishName(selections);

      if (response?.success) {
        // Add defaults if properties are missing
        const suggestions = response.suggestions || {};
        setSuggestedDishNames({
          name: suggestions.name || "Customer's Special Creation",
          alternatives: suggestions.alternatives || ["Flavor Fiesta", "Curry Creation"],
          format_used: suggestions.format_used || "Standard format"
        });
      } else {
        // Set default values if request failed
        setSuggestedDishNames({
          name: "Customer's Special Creation",
          alternatives: ["Flavor Fiesta", "Curry Creation"],
          format_used: "Default format"
        });
      }
    } catch (error) {
      setError("Failed to get dish name suggestions.");
      console.error("Dish name suggestions error:", error);
      // Set defaults on error
      setSuggestedDishNames({
        name: "Customer's Special Creation",
        alternatives: ["Flavor Fiesta", "Curry Creation"],
        format_used: "Default format when error occurred"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCompleteOrder = async () => {
    try {
      setIsLoading(true);

      // Pass customer data with the order
      const response = await apiService.completeOrder(
        customerData?.phoneNumber,
        customerData?.name
      );

      if (response?.success) {
        // Handle successful order completion
        alert("Your order has been completed successfully!");
        setCurrentStep('social_sharing');
      } else {
        setError("Failed to complete order. Please try again.");
      }
    } catch (error) {
      setError("An error occurred while completing your order.");
      console.error("Complete order error:", error);
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
        customValue,
        customerData?.phoneNumber // Pass phone number to associate feedback with customer
      );

      return response?.success || false;
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
      const recommendedProtein = recommendations?.proteins?.[0] || "Chicken";
      setProtein(recommendedProtein);
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
      const recommendedBase = recommendations?.suggested_base || recommendations?.base_types?.[0] || "Bowl";
      setBaseType(recommendedBase);

      // Set default base option
      if (recommendedBase === "Biryani") {
        setBaseOption("Rice");
      } else if (recommendedBase === "Sandwich & Subs") {
        setBaseOption("Sourdough");
      } else if (recommendedBase === "Wrap") {
        setBaseOption("Naan");
      } else if (recommendedBase === "Bowl") {
        setBaseOption("Bowl");
      }

      await handleRecommendationFeedback('weather', 'accept');
    } else if (response === 'custom' && customValue) {
      setBaseType(customValue);

      // Set default base option
      if (customValue === "Biryani") {
        setBaseOption("Rice");
      } else if (customValue === "Sandwich & Subs") {
        setBaseOption("Sourdough");
      } else if (customValue === "Wrap") {
        setBaseOption("Naan");
      } else if (customValue === "Bowl") {
        setBaseOption("Bowl");
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
      setDishName(suggestedDishNames?.name || "Custom Creation");
      await handleRecommendationFeedback('dish_name', 'accept');
    } else if (response === 'custom' && customValue) {
      setDishName(customValue);
      await handleRecommendationFeedback('dish_name', 'custom', customValue);
    } else {
      await handleRecommendationFeedback('dish_name', 'ignore');
    }

    setCurrentStep('sauce_selection');
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
        dish_name: dishName,
        customer_phone: customerData?.phoneNumber, // Include customer phone in selections
        customer_name: customerData?.name // Include customer name in selections
      };

      // Create new order item
      const newItem = {
        protein,
        sauce,
        base_type: baseType,
        base_option: baseOption,
        veggies,
        dish_name: dishName || "Custom Creation",
        price: calculateTotal()
      };

      // Add to order items array
      setOrderItems([...orderItems, newItem]);

      // Call API
      const response = await apiService.addOrderItem(selections);

      if (response?.success) {
        setCurrentStep('review');
        return true;
      } else {
        setError("Failed to add item to order.");
        return false;
      }
    } catch (error) {
      setError("Failed to add item to order.");
      console.error("Add item error:", error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Remove item from order
  const removeOrderItem = (index) => {
    const newItems = [...orderItems];
    newItems.splice(index, 1);
    setOrderItems(newItems);
  };

  // Edit existing item
  const editOrderItem = (index) => {
    const itemToEdit = orderItems[index];

    // Populate form with item data
    setProtein(itemToEdit.protein);
    setSauce(itemToEdit.sauce);
    setBaseType(itemToEdit.base_type);
    setBaseOption(itemToEdit.base_option);
    setVeggies(itemToEdit.veggies);
    setDishName(itemToEdit.dish_name);

    // Remove the item from the list
    removeOrderItem(index);

    // Take user back to protein selection step
    setCurrentStep('protein');
  };

  // Handle social sharing
  const handleSocialShare = (shareData) => {
    // In a real app, this would integrate with social media APIs
    console.log("Sharing to social media:", shareData);
    setCurrentStep('complete');
  };

  // Calculate total price
  const calculateTotal = () => {
    let total = 0;

    // Add protein price - use the price from the object
    if (protein) {
      const selectedProtein = proteins.find(p => p.name === protein);
      if (selectedProtein) {
        total += selectedProtein.price;
      } else {
        total += 4.50; // Default price if not found
      }
    }

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

    return parseFloat(total.toFixed(2));
  };

  // Handle activity selection
  const handleActivitySelection = async (activity) => {
    await getHealthRecommendations(activity);
    setCurrentStep('protein');
  };

  // Start order button
  const handleStartOrder = () => {
    setCurrentStep('identify'); // Changed from 'activity' to 'identify' to ensure we capture customer info
  };

  // Clear current selection
  const clearSelections = () => {
    // Clear protein
    if (currentStep === 'protein') {
      setProtein('');
    }
    // Clear base
    else if (currentStep === 'base') {
      setBaseType('');
      setBaseOption('');
    }
    // Clear dish name
    else if (currentStep === 'dishName') {
      setDishName('');
    }
    // Clear sauce
    else if (currentStep === 'sauce_selection') {
      setSauce('');
    }
    // Clear veggies
    else if (currentStep === 'veggie_selection') {
      setVeggies([]);
    }
  };

  // Go back to previous step with current selections maintained
  const goToPreviousStep = () => {
    switch (currentStep) {
      case 'identify':
        setCurrentStep('start');
        break;
      case 'activity':
        setCurrentStep('identify');
        break;
      case 'protein':
        setCurrentStep('activity');
        break;
      case 'base':
        setCurrentStep('protein');
        break;
      case 'dishName':
        setCurrentStep('base');
        break;
      case 'sauce_selection':
        setCurrentStep('dishName');
        break;
      case 'veggie_selection':
        setCurrentStep('sauce_selection');
        break;
      case 'review':
        setCurrentStep('veggie_selection');
        break;
      default:
        break;
    }
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
          <>
            <ActivitySelection
              onActivitySelected={handleActivitySelection}
              isLoading={isLoading}
            />

            {/* Display previous orders if available */}
            {previousOrders.length > 0 && (
              <div className="mt-8 bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h3 className="text-lg font-semibold mb-2">Your Previous Orders</h3>
                <div className="max-h-60 overflow-y-auto">
                  {previousOrders.map((order, idx) => (
                    <div key={idx} className="bg-white p-3 mb-2 rounded shadow-sm">
                      <p className="font-medium">{order.dish_name || 'Custom Order'}</p>
                      <p className="text-sm text-gray-600">
                        {order.protein} with {order.sauce} on {order.base_option}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Back button */}
            <div className="mt-4">
              <button
                onClick={goToPreviousStep}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
              >
                Back
              </button>
            </div>
          </>
        );

      case 'protein':
        return (
          <>
            <MenuSelectionGrid
              title="Select Your Protein"
              items={proteins}
              recommendations={recommendations?.proteins || []}
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
              recommendedItem={recommendations?.proteins?.[0] || ""}
            />

            <div className="mt-4 flex justify-between">
              {/* Clear/Remove selection button */}
              <button
                onClick={clearSelections}
                disabled={!protein}
                className={`px-6 py-2 ${!protein ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-red-200 text-red-800 hover:bg-red-300'} rounded-md transition-colors`}
              >
                Clear Selection
              </button>

              {/* Back button to activity selection */}
              <button
                onClick={goToPreviousStep}
                className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
              >
                Back
              </button>

              {protein && (
                <button
                  onClick={() => handleProteinFeedback('ignore')}
                  disabled={isLoading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                >
                  {isLoading ? 'Loading...' : 'Continue'}
                </button>
              )}
            </div>
          </>
        );

      case 'base':
        return (
          <>
            <BaseSelectionGrid
              title="Select Your Base"
              baseTypes={baseTypes}
              recommendations={recommendations?.base_types || []}
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
              recommendedItem={recommendations?.suggested_base || recommendations?.base_types?.[0] || ""}
            />

            <div className="mt-4 flex justify-between">
              {/* Clear/Remove selection button */}
              <button
                onClick={clearSelections}
                disabled={!baseType}
                className={`px-6 py-2 ${!baseType ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-red-200 text-red-800 hover:bg-red-300'} rounded-md transition-colors`}
              >
                Clear Selection
              </button>

              {/* Back button to protein selection */}
              <button
                onClick={goToPreviousStep}
                className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
              >
                Back
              </button>

              {baseType && baseOption && (
                <button
                  onClick={() => handleBaseFeedback('ignore')}
                  disabled={isLoading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                >
                  {isLoading ? 'Loading...' : 'Continue'}
                </button>
              )}
            </div>
          </>
        );

      case 'dishName':
        return (
          <>
            <div className="w-full mb-6">
              <h2 className="text-xl font-bold mb-3">Your Personalized Dish Name</h2>

              <div className="mb-6 p-6 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-100 text-center">
                <h3 className="text-2xl font-bold text-orange-700 mb-2">🎉 {suggestedDishNames?.name || "Custom Creation"}</h3>
                <p className="text-gray-600">Personalized just for you!</p>
              </div>

              <div className="mb-4">
                <h3 className="text-lg font-medium mb-2">Alternative names:</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {(suggestedDishNames?.alternatives || []).map((name, index) => (
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
              recommendedItem={suggestedDishNames?.name || ""}
            />

            <div className="mt-4 flex justify-between">
              {/* Clear/Remove selection button */}
              <button
                onClick={clearSelections}
                className="px-6 py-2 bg-red-200 text-red-800 rounded-md hover:bg-red-300 transition-colors"
              >
                Clear Selection
              </button>

              {/* Back button to base selection */}
              <button
                onClick={goToPreviousStep}
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

      case 'sauce_selection':
        return (
          <>
            <MenuSelectionGrid
              title="Select Your Sauce"
              items={sauces}
              recommendations={recommendations?.sauces || []}
              category="Sauce"
              selectedItems={sauce}
              onSelect={setSauce}
            />

            <div className="mt-4 flex justify-between">
              {/* Clear/Remove selection button */}
              <button
                onClick={clearSelections}
                disabled={!sauce}
                className={`px-6 py-2 ${!sauce ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-red-200 text-red-800 hover:bg-red-300'} rounded-md transition-colors`}
              >
                Clear Selection
              </button>

              {/* Back button to dish name */}
              <button
                onClick={goToPreviousStep}
                className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
              >
                Back
              </button>

              {sauce && (
                <button
                  onClick={() => setCurrentStep('veggie_selection')}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Continue
                </button>
              )}
            </div>
          </>
        );

      case 'veggie_selection':
        return (
          <>
            <MenuSelectionGrid
              title="Select Your Veggies"
              items={veggieOptions}
              recommendations={recommendations?.veggies || []}
              category="Veggies"
              selectedItems={veggies}
              onSelect={setVeggies}
              maxFreeSelections={5}
              premiumItems={premiumVeggies}
              premiumPrice={3.0}
              extraPrice={1.0}
            />

            <div className="mt-4 flex justify-between">
              {/* Clear/Remove selection button */}
              <button
                onClick={clearSelections}
                disabled={veggies.length === 0}
                className={`px-6 py-2 ${veggies.length === 0 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-red-200 text-red-800 hover:bg-red-300'} rounded-md transition-colors`}
              >
                Clear Selections
              </button>

              {/* Back button to sauce selection */}
              <button
                onClick={goToPreviousStep}
                className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
              >
                Back
              </button>

              {/* Add button to add item to order */}
              <button
                onClick={addItemToOrder}
                disabled={!protein || !sauce || !baseType || !baseOption}
                className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:bg-gray-400"
              >
                Add to Order
              </button>
            </div>
          </>
        );

      case 'review':
        // If no items have been added yet, use current selections to create one
        const currentOrderItems = orderItems.length > 0 ? orderItems : [{
          dish_name: dishName || "Custom Creation",
          protein: protein || "",
          sauce: sauce || "",
          base_type: baseType || "",
          base_option: baseOption || "",
          veggies: veggies || [],
          price: calculateTotal()
        }];

        return (
          <OrderSummary
            orderItems={currentOrderItems}
            totalPrice={currentOrderItems.reduce((sum, item) => sum + item.price, 0)}
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
            onRemoveItem={(index) => {
              // Handle removing item
              if (orderItems.length > 0) {
                removeOrderItem(index);
              } else {
                // Reset selections
                setProtein('');
                setSauce('');
                setBaseType('');
                setBaseOption('');
                setVeggies([]);
                setDishName('');

                // Go back to protein step
                setCurrentStep('protein');
              }
            }}
            onEditItem={(index) => {
              // Handle editing item
              if (orderItems.length > 0) {
                editOrderItem(index);
              } else {
                // Just go back to protein step to continue editing current selections
                setCurrentStep('protein');
              }
            }}
            customerData={customerData}
            goToPreviousStep={goToPreviousStep}
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

      case 'complete':
        return (
          <div className="text-center py-8">
            <div className="text-5xl mb-4">🎉</div>
            <h2 className="text-2xl font-bold mb-4">Order Complete!</h2>
            <p className="text-gray-600 mb-6">
              Your order has been placed and will be ready shortly.
            </p>
            {customerData && (
              <div className="bg-green-50 p-4 rounded-lg mb-6 inline-block">
                <p className="text-green-800 font-medium">Thank you, {customerData.name || "valued customer"}!</p>
                <p className="text-green-600">We'll use your preferences for better recommendations next time.</p>
              </div>
            )}
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
                setRecommendations({
                  proteins: [],
                  sauces: [],
                  base_types: [],
                  veggies: [],
                  reasoning: ""
                });
                setSuggestedDishNames({
                  name: "",
                  alternatives: [],
                  format_used: ""
                });
                setOrderData(null);
                setOrderItems([]);
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
    if (currentStep === 'start' || currentStep === 'activity' || currentStep === 'identify') {
      return null;
    }

    const steps = [
      { id: 'protein', label: 'Protein' },
      { id: 'base', label: 'Base' },
      { id: 'dishName', label: 'Name' },
      { id: 'sauce_selection', label: 'Sauce' },
      { id: 'veggie_selection', label: 'Veggies' },
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

      <div className="bg-white rounded-lg shadow-md p-6 relative">
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