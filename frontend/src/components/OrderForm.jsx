import React, { useState, useEffect, useCallback } from 'react';
import MenuSelectionGrid from './MenuSelectionGrid';
import BaseSelectionGrid from './BaseSelectionGrid';
import RecommendationFeedback from './RecommendationFeedback';
import * as apiService from './services/api';
import CustomerIdentification from './CustomerIdentification';
import ActivitySelection from './ActivitySelection';
import OrderSummary from './OrderSummary';
import SocialSharing from './SocialSharing';
import CalorieCalculator from './CalorieCalculator';
import TrialHeader from './TrialHeader';
import { useOrder } from './OrderContext';
import { CustomerProvider, useCustomer } from './context/CustomerContext';
import { useExperiment } from '../context/ExperimentContext';
import measurementService from './services/measurementService';

/**
 * Enhanced order form component that manages the entire ordering flow.
 * Added ability to go back, remove items, and improved navigation.
 */
const OrderForm = ({ experimentConfig = null }) => {
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const { getCurrentTrialConfig, startTrial, completeTrial, recordSuggestionDecision } = useExperiment();

  // State for the current step in the ordering process
  const [currentStep, setCurrentStep] = useState('start');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Get current trial configuration
  const currentTrialConfig = getCurrentTrialConfig();
  const isTrialA = currentTrialConfig?.trialType === 'A';
  const isTrialB = currentTrialConfig?.trialType === 'B';

  // Order data
  const [orderData, setOrderData] = useState(null);

  // Initialize recommendations with empty arrays to prevent map errors
  const [recommendations, setRecommendations] = useState({
    base_types: [],
    proteins: [],
    sauces: [],
    garnishes: [],
  });
  const [healthRecommendations, setHealthRecommendations] = useState(null);
  const [weatherRecommendations, setWeatherRecommendations] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [dishNameData, setDishNameData] = useState(null);
  const [activity, setActivity] = useState('');
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);

  // Selection state
  const [protein, setProtein] = useState([]);
  const [sauce, setSauce] = useState([]);
  const [baseType, setBaseType] = useState('');
  const [baseOption, setBaseOption] = useState('');
  const [veggies, setVeggies] = useState([]);
  const [garnishes, setGarnishes] = useState([]);
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

  // Measurement system state
  const [showMeasurementModal, setShowMeasurementModal] = useState(false);
  const [measurementStep, setMeasurementStep] = useState('nasa_tlx');
  const [measurementData, setMeasurementData] = useState({
    nasaTlx: {},
    sus: {},
    satisfaction: {},
    taskStartTime: null
  });

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

  const garnishOptions = [
    'Crispy Onions', 'Fresh Cilantro', 'Pomegranate Seeds', 'Toasted Almonds'
  ];

  // Initialize order on component mount
  useEffect(() => {
    const initializeOrder = async () => {
      try {
        setIsLoading(true);

        // Start measurement tracking
        measurementService.startTracking();
        setMeasurementData(prev => ({ ...prev, taskStartTime: new Date() }));

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
    // Track decision change if user is changing their selection
    if (baseType && baseType !== type) {
      measurementService.trackDecisionChange(
        'base_change',
        `${baseType} - ${baseOption}`,
        `${type} - ${option}`,
        'User changed base selection'
      );
    }

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

  const getRecommendations = useCallback(async () => {
    if (!activity || !customerData) return;

    // For Trial A (baseline), provide empty recommendations - no agent suggestions
    if (isTrialA) {
      setRecommendations({
        base_types: [],
        proteins: [],
        sauces: [],
        garnishes: [],
        veggies: []
      });
      setHealthRecommendations(null);
      setWeatherRecommendations(null);
      setWeatherData(null);
      return;
    }

    // For Trial B or non-experiment mode, get full recommendations
    setLoadingRecommendations(true);
    try {
      const [healthRes, weatherRes] = await Promise.all([
        fetch(`${API_URL}/api/health-recommendations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ activity_level: activity, customer_id: customerData.customer_id }),
        }),
        fetch(`${API_URL}/api/weather-recommendations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ time_of_day: 'afternoon', customer_id: customerData.customer_id }),
        }),
      ]);

      const healthRecs = await healthRes.json();
      const weatherRecs = await weatherRes.json();

      setHealthRecommendations(healthRecs);
      setWeatherRecommendations(weatherRecs);
      setWeatherData(weatherRecs.weather_data);

      const combined = {
        base_types: [...new Set([...(healthRecs.base_types || []), ...(weatherRecs.base_types || [])])],
        proteins: [...new Set([...(healthRecs.proteins || []), ...(weatherRecs.proteins || [])])],
        veggies: [...new Set([...(healthRecs.veggies || []), ...(weatherRecs.veggies || [])])],
        sauces: [...new Set([...(healthRecs.sauces || []), ...(weatherRecs.sauces || [])])],
        garnishes: [...new Set([...(healthRecs.garnishes || []), ...(weatherRecs.garnishes || [])])],
      };
      setRecommendations(combined);
    } catch (err) {
      setError('Failed to get recommendations.');
      console.error(err);
    } finally {
      setLoadingRecommendations(false);
    }
  }, [activity, customerData, API_URL, isTrialA]);

  const getDishName = useCallback(async () => {
    if (!baseType || !customerData) return;
    try {
      const response = await fetch(`${API_URL}/api/dish-name`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          selections: {
            protein,
            base_type: baseType,
            veggies,
            sauce,
            garnishes,
            customer_name: customerData.name,
          },
        }),
      });
      const data = await response.json();
      setDishName(data.primary);
      setDishNameData(data);
    } catch (err) {
      console.error('Error fetching dish name:', err);
    }
  }, [protein, baseType, veggies, sauce, garnishes, customerData, API_URL]);

  useEffect(() => {
    if (currentStep === 'base' && activity) {
      getRecommendations();
    }
    if (currentStep === 'summary') { // Assuming summary is the step before complete
      getDishName();
    }
  }, [currentStep, activity, getRecommendations, getDishName]);

  const handleCompleteOrder = async () => {
    const orderId = `ORD-${Date.now()}`;
    const finalOrder = {
      id: orderId,
      base: `${baseType} - ${baseOption}`,
      protein: protein.length > 0 ? protein[0] : 'None',
      veggies,
      sauce: sauce.length > 0 ? sauce[0] : 'None',
      garnishes,
      dishName,
      customer: customerData,
    };

    const experimentData = {
      experiment_id: orderId,
      customer_id: customerData?.customer_id,
      customer_name: customerData?.name,
      face_recognized: !!(customerData?.face_id || customerData?.recognized),
      activity_level_input: activity,
      health_agent_recommendations: healthRecommendations,
      weather_condition: weatherData,
      weather_agent_recommendations: weatherRecommendations,
      selected_base: `${baseType} - ${baseOption}`,
      selected_protein: protein.length > 0 ? protein[0] : null,
      selected_veggies: veggies,
      selected_sauce: sauce.length > 0 ? sauce[0] : null,
      final_order_details: finalOrder,
      dish_name_agent_suggestions: dishNameData,
      final_dish_name: dishName,
    };

    try {
      const response = await fetch(`${API_URL}/api/complete-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(experimentData),
      });

      if (!response.ok) {
        const errorBody = await response.text();
        throw new Error(`Failed to complete order: ${response.status} ${errorBody}`);
      }

      // Submit task completion measurement
      await measurementService.submitTaskCompletion(
        'food_ordering',
        true,
        6, // Total steps completed (customer, activity, recommendations, base, sauce, complete)
        6  // Total steps in the process
      );

      setOrderData(finalOrder);
      setCurrentStep('complete');

      // Show measurement modal after order completion
      setShowMeasurementModal(true);
      setMeasurementStep('nasa_tlx');
    } catch (err) {
      setError('Error completing order.');
      console.error(err);

      // Track error
      measurementService.trackError(
        'order_completion_error',
        err.message,
        { step: 'complete_order', orderId: orderId }
      );
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
      setProtein([recommendedProtein]);
      await handleRecommendationFeedback('health', 'accept');
    } else if (response === 'custom' && customValue) {
      setProtein([customValue]);
      await handleRecommendationFeedback('health', 'custom', customValue);
    } else {
      await handleRecommendationFeedback('health', 'ignore');
    }

    await getRecommendations();
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
    await getDishName();
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
        protein: protein[0],
        sauce: sauce[0],
        base_type: baseType,
        base_option: baseOption,
        veggies,
        garnishes,
        dish_name: dishName,
        customer_phone: customerData?.phoneNumber,
        customer_name: customerData?.name,
      };

      const newItem = {
        ...selections,
        price: calculateItemPrice(selections),
      };

      const updatedItems = [...orderItems, newItem];
      setOrderItems(updatedItems);
      setCurrentStep('summary');

    } catch (error) {
      setError('Failed to add item to order.');
      console.error('Add item error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const clearSelections = () => {
    setProtein([]);
    setSauce([]);
    setBaseType('');
    setBaseOption('');
    setVeggies([]);
    setGarnishes([]);
    setDishName('');
  };

  const calculateItemPrice = (item) => {
    let itemPrice = 0;
    const proteinInfo = proteins.find(p => p.name === item.protein);
    if (proteinInfo) {
      itemPrice += proteinInfo.price;
    }

    const baseOptions = baseTypes[item.base_type];
    if (baseOptions) {
      const baseOptionInfo = baseOptions.find(b => b.name === item.base_option);
      if (baseOptionInfo) {
        itemPrice += baseOptionInfo.price;
      }
    }

    if (item.veggies) {
      itemPrice += item.veggies.filter(v => premiumVeggies.includes(v)).length * 1.00;
    }

    // placeholder for sauces and garnishes price
    if (item.sauce) {
      itemPrice += 0.50;
    }
    if (item.garnishes) {
      itemPrice += item.garnishes.length * 0.25;
    }

    return itemPrice;
  };

  const removeOrderItem = (index) => {
    const newItems = [...orderItems];
    newItems.splice(index, 1);
    setOrderItems(newItems);
  };

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
  const handleActivitySelection = async (selectedActivity) => {
    setActivity(selectedActivity);

    // Start trial when activity is selected
    if (currentTrialConfig) {
      startTrial(currentTrialConfig.trialNumber);
    }

    // For Trial A (baseline), skip recommendations entirely
    if (isTrialA && selectedActivity === 'experiment_a_baseline') {
      // No agent suggestions for baseline trial
      setCurrentStep('protein');
      return;
    }

    // For Trial B or non-experiment mode, proceed with recommendations
    setCurrentStep('protein');
  };

  // Start order button
  const handleStartOrder = async () => {
    setCurrentStep('camera_recognition'); // New step for automatic camera recognition

    try {
      // Start camera automatically
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'user',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });

      // Set up video element for recognition
      const video = document.createElement('video');
      video.srcObject = mediaStream;
      video.autoplay = true;
      video.playsInline = true;

      // Wait for video to be ready
      await new Promise((resolve) => {
        video.onloadedmetadata = () => {
          video.play();
          resolve();
        };
      });

      // Wait a moment for camera to stabilize
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Capture image for recognition
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext('2d');
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      const imageData = canvas.toDataURL('image/jpeg', 0.8);

      // Stop camera stream
      mediaStream.getTracks().forEach(track => track.stop());

      // Send image for face recognition
      const response = await fetch('http://localhost:8000/api/face-recognition', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image_data: imageData })
      });

      const result = await response.json();

      if (result.success && result.recognized) {
        // Customer recognized - populate data and go to activity selection
        setCustomerData({
          name: result.customer_data.name,
          phoneNumber: result.customer_data.phone_number,
          customerId: result.customer_data.customer_id,
          recognized: true
        });
        setCurrentStep('activity');
      } else {
        // Customer not recognized - go to customer identification
        setCurrentStep('customer');
      }

    } catch (error) {
      console.error('Camera recognition failed:', error);
      // Fallback to manual customer identification
      setCurrentStep('customer');
    }
  };

  const goToPreviousStep = () => {
    switch (currentStep) {
      case 'activity':
        setCurrentStep('customer');
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
      case 'sauce':
        setCurrentStep('dishName');
        break;
      case 'veggies':
        setCurrentStep('sauce');
        break;
      case 'garnishes':
        setCurrentStep('veggies');
        break;
      case 'summary':
        setCurrentStep('garnishes');
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
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Welcome to Food Recommender</h2>
            <button
              onClick={handleStartOrder}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start Order
            </button>
          </div>
        );

      case 'camera_recognition':
        return (
          <div className="text-center">
            <div className="mb-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            </div>
            <h2 className="text-xl font-semibold mb-2">Recognizing Customer...</h2>
            <p className="text-gray-600">Please look at the camera</p>
            <p className="text-sm text-gray-500 mt-2">Camera will automatically capture your image for recognition</p>
          </div>
        );

      case 'customer':
        return (
          <CustomerIdentification
            onCustomerIdentified={handleCustomerIdentified}
            previousOrders={previousOrders}
          />
        );

      case 'activity':
        return (
          <ActivitySelection
            onActivitySelected={handleActivitySelection}
            customerData={customerData}
            experimentConfig={currentTrialConfig}
          />
        );

      case 'base':
        return (
          <div>
            <h2 className="text-xl font-semibold mb-4">Choose Your Base</h2>
            <BaseSelectionGrid
              baseTypes={baseTypes}
              selectedType={baseType}
              selectedOption={baseOption}
              onSelect={handleBaseSelection}
              recommendations={recommendations.base_types}
            />
            {baseType && baseOption && <CalorieCalculator />}

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
                  onClick={async () => {
                    await getDishName();
                    setCurrentStep('dishName');
                  }}
                  disabled={isLoading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                >
                  {isLoading ? 'Loading...' : 'Continue'}
                </button>
              )}
            </div>
          </div>
        );

      case 'protein':
        return (
          <div>
            <h2 className="text-xl font-semibold mb-4">Select Your Protein</h2>
            <MenuSelectionGrid
              items={proteins}
              selectedItems={protein}
              onSelect={setProtein}
              recommendations={recommendations.proteins}
              maxSelections={1}
            />
            {protein.length > 0 && <CalorieCalculator />}

            <div className="mt-4 flex justify-between">
              {/* Clear/Remove selection button */}
              <button
                onClick={clearSelections}
                disabled={protein.length === 0}
                className={`px-6 py-2 ${protein.length === 0 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-red-200 text-red-800 hover:bg-red-300'} rounded-md transition-colors`}
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

              {protein.length > 0 && (
                <button
                  onClick={async () => {
                    await getRecommendations();
                    setCurrentStep('base');
                  }}
                  disabled={isLoading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                >
                  {isLoading ? 'Loading...' : 'Continue'}
                </button>
              )}
            </div>
          </div>
        );

      case 'sauce':
        return (
          <div>
            <h2 className="text-xl font-semibold mb-4">Choose Your Sauce</h2>
            <MenuSelectionGrid
              items={sauces.map(name => ({ name }))}
              selectedItems={sauce}
              onSelect={setSauce}
              recommendations={recommendations.sauces}
              maxSelections={1}
            />
            {sauce.length > 0 && <CalorieCalculator />}

            <div className="mt-4 flex justify-between">
              {/* Clear/Remove selection button */}
              <button
                onClick={clearSelections}
                disabled={sauce.length === 0}
                className={`px-6 py-2 ${sauce.length === 0 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-red-200 text-red-800 hover:bg-red-300'} rounded-md transition-colors`}
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

              {sauce.length > 0 && (
                <button
                  onClick={() => setCurrentStep('veggies')}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Continue
                </button>
              )}
            </div>
          </div>
        );

      case 'veggies':
        return (
          <div>
            <h2 className="text-xl font-semibold mb-4">Add Vegetables</h2>
            <MenuSelectionGrid
              items={veggieOptions.map(name => ({ name }))}
              selectedItems={veggies}
              onSelect={setVeggies}
              recommendations={recommendations.veggies}
              premiumItems={premiumVeggies}
            />
            {veggies.length > 0 && <CalorieCalculator />}

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

              <button
                onClick={() => setCurrentStep('garnishes')}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Continue
              </button>
            </div>
          </div>
        );

      case 'garnishes':
        return (
          <div>
            <h2 className="text-xl font-semibold mb-4">Add Garnishes</h2>
            <MenuSelectionGrid
              items={garnishOptions.map(name => ({ name }))}
              selectedItems={garnishes}
              onSelect={setGarnishes}
              recommendations={recommendations.garnishes}
            />
            <div className="mt-4 flex justify-between">
              <button
                onClick={goToPreviousStep}
                className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
              >
                Back
              </button>
              <button
                onClick={addItemToOrder}
                disabled={!protein.length || !sauce.length || !baseType || !baseOption}
                className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:bg-gray-400"
              >
                Add to Order
              </button>
            </div>
          </div>
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
                      onClick={() => setDishName(name)}
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
              onCustom={(customValue) => handleDishNameFeedback('custom', customValue)}
              customValue={customDishName}
              setCustomValue={setCustomDishName}
              itemType="dish name"
              recommendedItem={dishName}
            />

            <div className="mt-4 flex justify-between">
              {/* Clear/Remove selection button */}
              <button
                onClick={clearSelections}
                className="px-6 py-2 bg-red-200 text-red-800 rounded-md hover:bg-red-300 transition-colors"
              >
                Clear Selection
              </button>

              <button
                onClick={goToPreviousStep}
                className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
              >
                Back
              </button>

              <button
                onClick={() => setCurrentStep('sauce')}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Continue
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
                disabled={sauce.length === 0}
                className={`px-6 py-2 ${sauce.length === 0 ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-red-200 text-red-800 hover:bg-red-300'} rounded-md transition-colors`}
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

              {sauce.length > 0 && (
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

      case 'summary':
        return (
          <OrderSummary
            orderItems={orderItems}
            totalPrice={calculateTotal()}
            onAddAnother={() => {
              clearSelections();
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
                setProtein([]);
                setSauce([]);
                setBaseType('');
                setBaseOption('');
                setVeggies([]);
                setDishName('');
                setRecommendations({
                  proteins: [],
                  sauces: [],
                  base_types: [],
                  veggies: [],
                  garnishes: [],
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
        return null;
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
      { id: 'dishName', label: 'Dish Name' },
      { id: 'sauce', label: 'Sauce' },
      { id: 'veggies', label: 'Veggies' },
      { id: 'garnishes', label: 'Garnishes' },
      { id: 'summary', label: 'Review' }
    ];

    const activeIndex = steps.findIndex(step => step.id === currentStep);

    return (
      <div className="mb-8">
        <div className="flex justify-between mb-2">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`flex flex-col items-center ${index <= activeIndex ? 'text-blue-600' : 'text-gray-400'}`}
              style={{ width: `${100 / steps.length}%` }}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center mb-1
                  ${index < activeIndex ? 'bg-blue-600 text-white' :
                    index === activeIndex ? 'border-2 border-blue-600 text-blue-600' :
                    'border-2 border-gray-300 text-gray-400'}`}
              >
                {index < activeIndex ? '✓' : index + 1}
              </div>
              <span className="text-sm text-center">{step.label}</span>
            </div>
          ))}
        </div>

        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div
            className="bg-blue-600 h-2.5 rounded-full transition-all"
            style={{ width: `${(activeIndex / (steps.length - 1)) * 100}%` }}
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

  // NASA-TLX Form Component
  const NASATLXForm = ({ onSubmit }) => {
    const [tlxData, setTlxData] = useState({
      mental_demand: 50,
      physical_demand: 20,
      temporal_demand: 30,
      performance: 80,
      effort: 40,
      frustration: 25
    });

    const handleSubmit = async () => {
      const success = await onSubmit(tlxData);
      if (!success) {
        alert('Failed to submit NASA-TLX data. Please try again.');
      }
    };

    return (
      <div>
        <p className="text-gray-600 mb-4">Rate your experience on each dimension (0-100):</p>
        <div className="space-y-4">
          {Object.entries(tlxData).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between">
              <label className="flex-1 text-sm font-medium text-gray-700 capitalize">
                {key.replace('_', ' ')}:
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={value}
                onChange={(e) => setTlxData(prev => ({
                  ...prev,
                  [key]: parseInt(e.target.value)
                }))}
                className="flex-1 mx-4"
              />
              <span className="w-12 text-sm font-bold text-blue-600">{value}</span>
            </div>
          ))}
        </div>
        <button
          onClick={handleSubmit}
          className="w-full mt-6 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Continue to SUS
        </button>
      </div>
    );
  };

  // SUS Form Component
  const SUSForm = ({ onSubmit }) => {
    const [susData, setSusData] = useState({
      q1_use_frequently: 3,
      q2_unnecessarily_complex: 2,
      q3_easy_to_use: 4,
      q4_need_support: 2,
      q5_well_integrated: 4,
      q6_too_much_inconsistency: 2,
      q7_learn_quickly: 4,
      q8_very_cumbersome: 2,
      q9_very_confident: 4,
      q10_learn_lot_before: 2
    });

    const susQuestions = [
      "I think that I would like to use this system frequently",
      "I found the system unnecessarily complex",
      "I thought the system was easy to use",
      "I think that I would need the support of a technical person",
      "I found the various functions in this system were well integrated",
      "I thought there was too much inconsistency in this system",
      "I would imagine that most people would learn to use this system very quickly",
      "I found the system very cumbersome to use",
      "I felt very confident using the system",
      "I needed to learn a lot of things before I could get going with this system"
    ];

    const handleSubmit = async () => {
      const success = await onSubmit(susData);
      if (!success) {
        alert('Failed to submit SUS data. Please try again.');
      }
    };

    return (
      <div>
        <p className="text-gray-600 mb-4">Rate your agreement with each statement (1=Strongly Disagree, 5=Strongly Agree):</p>
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {susQuestions.map((question, index) => {
            const key = Object.keys(susData)[index];
            return (
              <div key={key} className="border-b pb-3">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {question}
                </label>
                <select
                  value={susData[key]}
                  onChange={(e) => setSusData(prev => ({
                    ...prev,
                    [key]: parseInt(e.target.value)
                  }))}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value={1}>1 - Strongly Disagree</option>
                  <option value={2}>2 - Disagree</option>
                  <option value={3}>3 - Neutral</option>
                  <option value={4}>4 - Agree</option>
                  <option value={5}>5 - Strongly Agree</option>
                </select>
              </div>
            );
          })}
        </div>
        <button
          onClick={handleSubmit}
          className="w-full mt-6 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Continue to Satisfaction
        </button>
      </div>
    );
  };

  // Satisfaction Form Component
  const SatisfactionForm = ({ onSubmit }) => {
    const [satisfactionData, setSatisfactionData] = useState({
      overall_satisfaction: 5,
      ease_of_use: 5,
      recommendation_quality: 6,
      perceived_personalization: 6,
      decision_confidence: 5,
      enjoyment: 5,
      return_intention: 6
    });

    const handleSubmit = async () => {
      const success = await onSubmit(satisfactionData);
      if (!success) {
        alert('Failed to submit satisfaction data. Please try again.');
      }
    };

    return (
      <div>
        <p className="text-gray-600 mb-4">Rate your satisfaction on each dimension (1-7):</p>
        <div className="space-y-4">
          {Object.entries(satisfactionData).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between">
              <label className="flex-1 text-sm font-medium text-gray-700 capitalize">
                {key.replace('_', ' ')}:
              </label>
              <input
                type="range"
                min="1"
                max="7"
                value={value}
                onChange={(e) => setSatisfactionData(prev => ({
                  ...prev,
                  [key]: parseInt(e.target.value)
                }))}
                className="flex-1 mx-4"
              />
              <span className="w-12 text-sm font-bold text-blue-600">{value}</span>
            </div>
          ))}
        </div>
        <button
          onClick={handleSubmit}
          className="w-full mt-6 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
        >
          Complete Survey
        </button>
      </div>
    );
  };

  // Render measurement modal
  const renderMeasurementModal = () => {
    if (!showMeasurementModal) return null;

    const submitNASATLX = async (tlxData) => {
      try {
        const response = await fetch(`${API_URL}/api/measurements/nasa-tlx`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...tlxData,
            session_id: measurementService.sessionId,
            condition: measurementService.condition
          }),
        });

        if (response.ok) {
          setMeasurementData(prev => ({ ...prev, nasaTlx: tlxData }));
          setMeasurementStep('sus');
          return true;
        }
      } catch (error) {
        console.error('Error submitting NASA-TLX:', error);
      }
      return false;
    };

    const submitSUS = async (susData) => {
      try {
        const response = await fetch(`${API_URL}/api/measurements/sus`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...susData,
            session_id: measurementService.sessionId,
            condition: measurementService.condition
          }),
        });

        if (response.ok) {
          setMeasurementData(prev => ({ ...prev, sus: susData }));
          setMeasurementStep('satisfaction');
          return true;
        }
      } catch (error) {
        console.error('Error submitting SUS:', error);
      }
      return false;
    };

    const submitSatisfaction = async (satisfactionData) => {
      try {
        const response = await fetch(`${API_URL}/api/measurements/satisfaction`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...satisfactionData,
            session_id: measurementService.sessionId,
            condition: measurementService.condition
          }),
        });

        if (response.ok) {
          setMeasurementData(prev => ({ ...prev, satisfaction: satisfactionData }));
          setShowMeasurementModal(false);
          console.log('All measurements completed and saved to CSV!');
          return true;
        }
      } catch (error) {
        console.error('Error submitting satisfaction:', error);
      }
      return false;
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-gray-900">
                {measurementStep === 'nasa_tlx' && 'NASA Task Load Index'}
                {measurementStep === 'sus' && 'System Usability Scale'}
                {measurementStep === 'satisfaction' && 'Satisfaction Survey'}
              </h2>
              <div className="text-sm text-gray-500">
                Step {measurementStep === 'nasa_tlx' ? '1' : measurementStep === 'sus' ? '2' : '3'} of 3
              </div>
            </div>

            {measurementStep === 'nasa_tlx' && (
              <NASATLXForm onSubmit={submitNASATLX} />
            )}

            {measurementStep === 'sus' && (
              <SUSForm onSubmit={submitSUS} />
            )}

            {measurementStep === 'satisfaction' && (
              <SatisfactionForm onSubmit={submitSatisfaction} />
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-orange-700">Curry Creations</h1>
        <p className="text-gray-600">Create your perfect meal!</p>
      </div>

      {/* Display trial information and instructions */}
      <TrialHeader experimentConfig={currentTrialConfig} />

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

      {renderMeasurementModal()}
    </div>
  );
};

export default OrderForm;