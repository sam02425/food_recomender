import React, { useState, useEffect, useCallback } from 'react';
import MenuSelectionGrid from './MenuSelectionGrid';
import BaseSelectionGrid from './BaseSelectionGrid';
import RecommendationFeedback from './RecommendationFeedback';
import * as apiService from './services/api';
import { getSmartRecommendations, submitMLFeedback } from './services/api';
import CustomerIdentification from './CustomerIdentification';
import ActivitySelection from './ActivitySelection';
import DietaryRestrictionsPanel from './DietaryRestrictionsPanel';
import OrderSummary from './OrderSummary';
import SocialSharing from './SocialSharing';
import CalorieCalculator from './CalorieCalculator';
import AgentRecommendations from './AgentRecommendations';
import PreviousOrders from './PreviousOrders';
// Removed unused imports for now
import MasterRecommendationPanel from './MasterRecommendationPanel';
import { useExperiment } from '../context/ExperimentContext';
import measurementService from './services/measurementService';

/**
 * Enhanced order form component that manages the entire ordering flow.
 * Added ability to go back, remove items, and improved navigation.
 */
const OrderForm = ({
  experimentConfig = null,
  onExperimentOrderComplete = null,
  experimentCycleActive = false,
  currentPhase = null,
  currentTrialInPhase = 1,
  aiRecommendations = [],
  orderInstructions = null,
  orderType = 'standard',
  participantName = null,
  onStepChange = () => {}
}) => {
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const { getCurrentTrialConfig, startTrial, completeTrial, recordSuggestionDecision } = useExperiment();

  // State for the current step in the ordering process
  const [stepLock, setStepLock] = useState(false);
  const [currentStep, _setCurrentStep] = useState('start');
  const setStep = (step) => {
    if (stepLock && step !== 'activity') {
      console.log(`[STEP] Step change to '${step}' blocked by stepLock.`);
      return;
    }
    console.log(`[STEP] Changing step to: ${step}`);
    _setCurrentStep(step);
  };

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Get current trial configuration
  const currentTrialConfig = getCurrentTrialConfig();

  // Enhanced trial detection - check multiple sources
  const isTrialA = currentTrialConfig?.trialType === 'A' || currentPhase === 'trial_a';
  const isTrialB = currentTrialConfig?.trialType === 'B' || currentPhase === 'trial_b';

  console.log('🔍 Enhanced Trial Detection:', {
    currentTrialConfig,
    currentPhase,
    isTrialA,
    isTrialB,
    experimentCycleActive
  });

  // Get dietary preferences functions from context
  const {
    setDietaryPreferences,
    getDietaryPreferences,
    hasDietaryPreferences
  } = useExperiment();

  // Customer data - moved before useEffect to fix hoisting issue
  const [customerData, setCustomerData] = useState(null);

  // Dietary restrictions state - moved before useEffect
  const [userDietaryRestrictions, setUserDietaryRestrictions] = useState([]);
  const [userAllergens, setUserAllergens] = useState([]);

  // Load persistent dietary preferences on component mount and when customer changes
  useEffect(() => {
    const loadCustomerDietaryPreferences = async () => {
      // Load available restrictions and allergens data
      try {
        const [restrictionsRes, allergensRes] = await Promise.all([
          fetch(`${API_URL}/api/dietary/restrictions/available`),
          fetch(`${API_URL}/api/dietary/allergens/available`)
        ]);

        if (restrictionsRes.ok) {
          const data = await restrictionsRes.json();
          setAvailableRestrictions(data.data?.restrictions || {});
        } else {
          console.error('Failed to load restrictions:', restrictionsRes.status);
          setAvailableRestrictions({});
        }

        if (allergensRes.ok) {
          const data = await allergensRes.json();
          setAvailableAllergens(data.data?.allergens || {});
        } else {
          console.error('Failed to load allergens:', allergensRes.status);
          setAvailableAllergens({});
        }
      } catch (error) {
        console.error('Error loading available dietary options:', error);
        setAvailableRestrictions({});
        setAvailableAllergens({});
      }

      // Try to load from global experiment context first
      const persistentPrefs = getDietaryPreferences();
      if (persistentPrefs.restrictions?.length > 0 || persistentPrefs.allergens?.length > 0) {
        setUserDietaryRestrictions(persistentPrefs.restrictions || []);
        setUserAllergens(persistentPrefs.allergens || []);
        return;
      }

      // If we have customer data, try to load their specific preferences
      if (customerData?.customerId || customerData?.phoneNumber) {
        try {
          const identifier = customerData.customerId || customerData.phoneNumber;
          const response = await fetch(`${API_URL}/api/dietary/profile/${identifier}`);
          if (response.ok) {
            const result = await response.json();
            if (result.success && result.data) {
              const { dietary_restrictions = [], allergens = [] } = result.data;
              setUserDietaryRestrictions(dietary_restrictions);
              setUserAllergens(allergens);

              // Also save to experiment context for session persistence
              setDietaryPreferences(dietary_restrictions, allergens);

              console.log(`Loaded dietary preferences for customer ${identifier}:`, {
                restrictions: dietary_restrictions,
                allergens: allergens
              });
            }
          }
        } catch (error) {
          console.error('Error loading customer dietary preferences:', error);
        }
      }
    };

    loadCustomerDietaryPreferences();
  }, [getDietaryPreferences, customerData, setDietaryPreferences, API_URL]);

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

  // ML-powered recommendation state
  const [mlRecommendations, setMlRecommendations] = useState(null);
  const [userPreferences, setUserPreferences] = useState(null);
  const [recommendationMode, setRecommendationMode] = useState('smart'); // 'smart', 'ml_only', 'traditional_only'
  const [mlConfidence, setMlConfidence] = useState(0);
  const [recommendationExplanations, setRecommendationExplanations] = useState({});

  // Dietary restrictions state
  const [showDietaryPanel, setShowDietaryPanel] = useState(false);
  const [availableRestrictions, setAvailableRestrictions] = useState({});
  const [availableAllergens, setAvailableAllergens] = useState({});

  // Master recommendation panel state
  const [showMasterPanel, setShowMasterPanel] = useState(false);
  const [masterRecommendations, setMasterRecommendations] = useState([]);

  // Selection state
  const [protein, setProtein] = useState([]);
  const [sauce, setSauce] = useState([]);
  const [baseType, setBaseType] = useState('');
  const [baseOption, setBaseOption] = useState('');
  const [veggies, setVeggies] = useState([]);
  const [garnishes, setGarnishes] = useState([]);
  const [dishName, setDishName] = useState('');

  // Customer data declarations moved up to fix hoisting issue

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

  // Menu data from backend
  const [menuData, setMenuData] = useState(null);

  // Helper function to get menu items with proper structure
  const getMenuItems = (category) => {
    if (!menuData || !menuData[category]) return [];
    return menuData[category];
  };

  // Get proteins with portion sizes
  const getProteins = () => {
    return getMenuItems('proteins');
  };

  // Get sauces
  const getSauces = () => {
    return getMenuItems('sauces');
  };

  // Get base types
  const getBaseTypes = () => {
    return menuData?.base_types || {};
  };

  // Get veggies
  const getVeggies = () => {
    return getMenuItems('veggies');
  };

  // Get garnishes
  const getGarnishes = () => {
    return getMenuItems('garnishes');
  };

  // Premium veggies (for pricing logic)
  const premiumVeggies = ['Avocado'];

  // State for tracking task compliance
  const [taskInstructions, setTaskInstructions] = useState(null);
  const [taskCompliance, setTaskCompliance] = useState({
    instructed: {},
    selected: {},
    compliance: {}
  });

  // Track selection compliance
  const trackSelectionCompliance = useCallback((category, selectedValue) => {
    if (taskInstructions) {
      setTaskCompliance(prev => {
        const newSelected = { ...prev.selected, [category]: selectedValue };
        const newCompliance = { ...prev.compliance };

        // Check compliance for each category
        if (category === 'protein') {
          newCompliance.protein = selectedValue === taskInstructions.protein;
        } else if (category === 'base') {
          newCompliance.base = selectedValue === taskInstructions.base;
        } else if (category === 'sauce') {
          newCompliance.sauce = selectedValue === taskInstructions.sauce;
        } else if (category === 'veggies') {
          const instructedVeggies = taskInstructions.veggies || [];
          const selectedVeggies = Array.isArray(selectedValue) ? selectedValue : [];
          newCompliance.veggies = instructedVeggies.length === selectedVeggies.length &&
            instructedVeggies.every(veggie => selectedVeggies.includes(veggie));
        } else if (category === 'garnishes') {
          const instructedGarnishes = taskInstructions.garnishes || [];
          const selectedGarnishes = Array.isArray(selectedValue) ? selectedValue : [];
          newCompliance.garnishes = instructedGarnishes.length === selectedGarnishes.length &&
            instructedGarnishes.every(garnish => selectedGarnishes.includes(garnish));
        }

        return {
          ...prev,
          selected: newSelected,
          compliance: newCompliance
        };
      });
    }
  }, [taskInstructions]);

  // Update task instructions when orderInstructions change
  useEffect(() => {
    if (orderInstructions?.tasks) {
      setTaskInstructions(orderInstructions.tasks);
      setTaskCompliance({
        instructed: orderInstructions.tasks,
        selected: {},
        compliance: {}
      });
    } else {
      setTaskInstructions(null);
      setTaskCompliance({
        instructed: {},
        selected: {},
        compliance: {}
      });
    }
  }, [orderInstructions]);

  // Auto-select AI recommendations in Trial B
  useEffect(() => {
    // Only apply auto-selection if we're in Trial B free choice mode and have recommendations
    if (experimentCycleActive && currentPhase === 'trial_b' && aiRecommendations.length > 0 && orderType === 'free_choice') {
      console.log('=== AI AUTO-SELECTION STARTING ===');
      console.log('Current step:', currentStep);
      console.log('AI recommendations:', aiRecommendations);

      // Apply auto-selections with a small delay to ensure state is ready
      setTimeout(() => {
        let hasChanges = false;

        aiRecommendations.forEach((rec, index) => {
          console.log(`Processing recommendation ${index + 1}:`, rec);

          // Auto-select protein
          if (rec.type === 'protein' && protein.length === 0) {
            console.log('🔄 Auto-selecting protein:', rec.item);
            setProtein([rec.item]);
            trackSelectionCompliance('protein', rec.item);
            hasChanges = true;
          }

          // Auto-select base
          if (rec.type === 'base' && !baseType) {
            console.log('🔄 Auto-selecting base:', rec.item);

            if (rec.item === 'Rice Bowl') {
              setBaseType('Bowl');
              setBaseOption('Bowl');
              trackSelectionCompliance('base', 'Bowl - Bowl');
            } else if (rec.item === 'Naan Wrap') {
              setBaseType('Wrap');
              setBaseOption('Naan');
              trackSelectionCompliance('base', 'Wrap - Naan');
            } else if (rec.item === 'Salad Bowl') {
              setBaseType('Salad');
              setBaseOption('Mixed Greens');
              trackSelectionCompliance('base', 'Salad - Mixed Greens');
            } else if (rec.item.includes('Sandwich')) {
              setBaseType('Sandwich & Subs');
              setBaseOption('Sourdough');
              trackSelectionCompliance('base', 'Sandwich & Subs - Sourdough');
            } else if (rec.item.includes('Biryani')) {
              setBaseType('Biryani');
              setBaseOption('Rice');
              trackSelectionCompliance('base', 'Biryani - Rice');
            } else {
              setBaseType('Bowl');
              setBaseOption('Bowl');
              trackSelectionCompliance('base', 'Bowl - Bowl');
            }
            hasChanges = true;
          }

          // Auto-select sauce
          if (rec.type === 'sauce' && sauce.length === 0) {
            console.log('🔄 Auto-selecting sauce:', rec.item);
            setSauce([rec.item]);
            trackSelectionCompliance('sauce', rec.item);
            hasChanges = true;
          }

          // Auto-select veggies
          if (rec.type === 'veggies' && veggies.length === 0 && rec.items) {
            console.log('🔄 Auto-selecting veggies:', rec.items);
            setVeggies(rec.items);
            trackSelectionCompliance('veggies', rec.items);
            hasChanges = true;
          }

          // Auto-select garnishes
          if (rec.type === 'garnishes' && garnishes.length === 0 && rec.items) {
            console.log('🔄 Auto-selecting garnishes:', rec.items);
            setGarnishes(rec.items);
            trackSelectionCompliance('garnishes', rec.items);
            hasChanges = true;
          }
        });

        if (hasChanges) {
          console.log('✅ AI auto-selections applied successfully');
          console.log('Current selections:', {
            protein,
            baseType,
            baseOption,
            sauce,
            veggies,
            garnishes
          });
        }
      }, 1000); // 1 second delay to ensure everything is ready
    } else {
      console.log('❌ Auto-selection conditions not met:', {
        experimentCycleActive,
        currentPhase,
        aiRecommendationsLength: aiRecommendations.length,
        orderType
      });
    }
  }, [aiRecommendations, currentPhase, experimentCycleActive, orderType]);

  // Initialize order on component mount
  useEffect(() => {
    const initializeOrder = async () => {
      try {
        setIsLoading(true);

        // Start measurement tracking
        measurementService.startTracking();
        setMeasurementData(prev => ({ ...prev, taskStartTime: new Date() }));

        // Initialize inventory for new experiment trial (Trial B)
        if (experimentCycleActive && currentPhase === 'trial_b') {
          try {
            const inventoryResponse = await fetch(`${API_URL}/api/inventory/initialize`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
            });
            if (inventoryResponse.ok) {
              const inventoryData = await inventoryResponse.json();
              console.log('Inventory initialized for new trial:', inventoryData.inventory_summary);
            } else {
              console.error('Failed to initialize inventory:', inventoryResponse.status);
            }
          } catch (error) {
            console.error('Error initializing inventory:', error);
          }
        }

        // In experiment mode, set up mock customer data automatically
        if (experimentCycleActive && participantName) {
          setCustomerData({
            name: participantName,
            phoneNumber: 'experiment-user',
            customerId: `exp-${Date.now()}`,
            recognized: false
          });
          // Only set step to 'activity' if not Trial B
          if (currentPhase === 'trial_b') {
            setStep('dietary');
          } else {
            setStep('activity');
          }
        } else {
          setStep('start');
        }

        // Start a new order
        const orderResponse = await apiService.startOrder();
        if (orderResponse?.success) {
          setOrderData(orderResponse.order_data);
        }

        // Get menu data
        const menuResponse = await apiService.getMenuData();
        if (menuResponse) {
          setMenuData(menuResponse);
        }

      } catch (error) {
        setError("Failed to initialize order. Please try again.");
        console.error("Order initialization error:", error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeOrder();
  }, [experimentCycleActive, participantName, currentPhase]);

  // On mount, if in Trial B, always set step to 'dietary' and block all other step changes until user continues
  useEffect(() => {
    if (experimentCycleActive && (currentPhase === 'trial_b')) {
      setStepLock(true);
      _setCurrentStep('dietary');
    }
  }, [experimentCycleActive, currentPhase]);

  // Dietary and activity set flags
  const [dietarySet, setDietarySet] = useState(false);
  const [activitySet, setActivitySet] = useState(false);

  // Only allow recommendations after both are set
  const canFetchRecommendations = dietarySet && activitySet;

  // Patch getRecommendations to require both dietary and activity
  const getRecommendations = useCallback(async (selectedActivity) => {
    if (!canFetchRecommendations || !selectedActivity || !customerData) {
      console.log('⏳ Waiting for dietary and activity before fetching recommendations');
      return;
    }
    // ... existing recommendation logic ...
  }, [canFetchRecommendations, customerData, userDietaryRestrictions, userAllergens, isTrialA, API_URL]);

  // When dietary restrictions are set and user clicks continue, unlock and go to activity
  const handleDietaryContinue = () => {
    setDietaryPreferences(userDietaryRestrictions, userAllergens);
    saveDietaryPreferencesToBackend(userDietaryRestrictions, userAllergens);
    setDietarySet(true);
    setStepLock(false);
    setStep('activity');
  };

  // When activity is selected, set activity and mark as set
  const handleActivitySelection = async (selectedActivity) => {
    setActivity(selectedActivity);
    setActivitySet(true);
    // Only fetch recommendations if both dietary and activity are set (for Trial B)
    if ((isTrialB || currentPhase === 'trial_b') && dietarySet) {
      await getRecommendations(selectedActivity);
      setStep('protein');
    } else {
      setStep('protein');
    }
  };

  // Add a warning if currentTrialConfig is null and patch logic to use currentPhase as fallback for trial type
  useEffect(() => {
    if (!currentTrialConfig) {
      console.warn('[OrderForm] currentTrialConfig is null! Using currentPhase as fallback for trial type.');
    }
  }, [currentTrialConfig, currentPhase]);

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

          // If we're in experiment cycle mode, call the completion handler
          if (onExperimentOrderComplete) {
            onExperimentOrderComplete();
          }

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

  // Save dietary preferences to backend when they change
  const saveDietaryPreferencesToBackend = async (restrictions, allergens) => {
    if (customerData?.customerId || customerData?.phoneNumber) {
      const identifier = customerData.customerId || customerData.phoneNumber;

      try {
        // Save restrictions
        if (restrictions.length > 0) {
          await fetch(`${API_URL}/api/dietary/restrictions/${identifier}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              restrictions: restrictions
            })
          });
        }

        // Save allergens
        if (allergens.length > 0) {
          await fetch(`${API_URL}/api/dietary/allergens/${identifier}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              allergens: allergens
            })
          });
        }

        console.log(`Saved dietary preferences for customer ${identifier}:`, {
          restrictions,
          allergens
        });
      } catch (error) {
        console.error('Error saving dietary preferences to backend:', error);
      }
    }
  };

  // Log all props on mount
  useEffect(() => {
    console.log('[OrderForm] MOUNTED with props:', {
      experimentConfig,
      onExperimentOrderComplete,
      experimentCycleActive,
      currentPhase,
      currentTrialInPhase,
      aiRecommendations,
      orderInstructions,
      orderType,
      participantName
    });
    return () => {
      console.log('[OrderForm] UNMOUNTED');
    };
  }, []);

  // Call onStepChange on every step change
  useEffect(() => {
    onStepChange(currentStep);
  }, [currentStep, onStepChange]);

  // Add this function before renderStep or in the main body of OrderForm
  const handleStartOrder = () => {
    // Advance to the next step after 'start'. Adjust as needed for your flow.
    setStep('customer');
  };

  // Add these stubs before renderStep
  const handleCustomerIdentified = (customer) => {
    setCustomerData(customer);
    // Check if customer has previous orders
    if (customer.phoneNumber && customer.phoneNumber !== 'experiment-user') {
      setStep('previous_orders');
    } else {
    setStep('dietary');
    }
  };

  const goToPreviousStep = () => {
    // Simple back navigation: go to 'customer' from 'dietary', or adjust as needed
    if (currentStep === 'dietary') setStep('customer');
    if (currentStep === 'previous_orders') setStep('customer');
    // Add more logic for other steps if needed
  };

  const handleLoadDietaryPreferences = (dietaryProfile) => {
    setUserDietaryRestrictions(dietaryProfile.restrictions || []);
    setUserAllergens(dietaryProfile.allergies || []);
    setDietaryPreferences(dietaryProfile.restrictions || [], dietaryProfile.allergies || []);
  };

  const handlePreviousOrdersSkip = () => {
    setStep('dietary');
  };

  const handlePreviousOrdersAddItem = (orderItems) => {
    // Load the previous order items
    if (orderItems.protein) setProtein(orderItems.protein);
    if (orderItems.sauce) setSauce(orderItems.sauce);
    if (orderItems.base_type) setBaseType(orderItems.base_type);
    if (orderItems.base_option) setBaseOption(orderItems.base_option);
    if (orderItems.veggies) setVeggies(orderItems.veggies);
    if (orderItems.garnishes) setGarnishes(orderItems.garnishes);
    if (orderItems.dish_name) setDishName(orderItems.dish_name);

    setStep('summary');
  };

  const handlePreviousOrdersCheckout = () => {
    setStep('summary');
  };

  const handleCompleteOrder = async () => {
    try {
      setIsLoading(true);

      // Save order to customer history if not experiment user
      if (customerData?.phoneNumber && customerData.phoneNumber !== 'experiment-user') {
        await saveCustomerOrder();
      }

      // Complete experiment trial if active
      if (experimentCycleActive) {
        await completeTrial();
      }

      setStep('complete');
    } catch (error) {
      setError("Error completing order. Please try again.");
      console.error("Order completion error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveCustomerOrder = async () => {
    try {
      const orderDetails = {
        protein: protein,
        sauce: sauce,
        base_type: baseType,
        base_option: baseOption,
        veggies: veggies,
        garnishes: garnishes,
        dish_name: dishName
      };

      await fetch(`${API_URL}/api/customer/save-order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          customer_phone: customerData.phoneNumber,
          order_details: orderDetails
        })
      });

      // Also save dietary preferences
      if (userDietaryRestrictions.length > 0 || userAllergens.length > 0) {
        await fetch(`${API_URL}/api/customer/save-dietary`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            customer_phone: customerData.phoneNumber,
            restrictions: userDietaryRestrictions,
            allergens: userAllergens
          })
        });
      }
    } catch (error) {
      console.error("Error saving customer order:", error);
    }
  };

  // Now define renderStep
  const renderStep = () => {
    // 🚨 COMPREHENSIVE DEBUG LOGGING FOR TRIAL B ISSUES
    console.log('🔍 === RENDER STEP DEBUG ===');
    console.log('Current Step:', currentStep);
    console.log('Current Phase:', currentPhase);
    console.log('Experiment Cycle Active:', experimentCycleActive);
    console.log('Current Trial Config:', currentTrialConfig);
    console.log('Is Trial A:', isTrialA);
    console.log('Is Trial B:', isTrialB);
    console.log('Current Trial In Phase:', currentTrialInPhase);
    console.log('Customer Data:', customerData);
    console.log('Activity:', activity);
    console.log('Protein:', protein);
    console.log('Base Type/Option:', baseType, baseOption);
    console.log('Sauce:', sauce);
    console.log('Veggies:', veggies);
    console.log('Garnishes:', garnishes);
    console.log('Dish Name:', dishName);
    console.log('🔍 === END DEBUG ===');

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
          />
        );
      case 'previous_orders':
        return (
          <div>
            <h2 className="text-xl font-semibold mb-6">📋 Select from Previously Ordered</h2>
            <PreviousOrders
              customerPhone={customerData?.phoneNumber}
              onSkip={handlePreviousOrdersSkip}
              onAddItem={handlePreviousOrdersAddItem}
              onCheckout={handlePreviousOrdersCheckout}
              onLoadDietaryPreferences={handleLoadDietaryPreferences}
            />
            <div className="mt-4">
              <button onClick={goToPreviousStep} className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors">
                Back
              </button>
            </div>
          </div>
        );
      case 'dietary':
        return (
          <div>
            <h2 className="text-xl font-semibold mb-6">🥗 Dietary Preferences & Allergies</h2>
            <DietaryRestrictionsPanel
              customerId={customerData?.customerId || customerData?.phoneNumber}
              onRestrictionsChange={(restrictions) => {
                setUserDietaryRestrictions(restrictions);
                setDietarySet(false); // Reset dietarySet to force re-fetch
              }}
              onAllergensChange={(allergens) => {
                setUserAllergens(allergens);
                setDietarySet(false); // Reset dietarySet to force re-fetch
              }}
            />
            <div className="mt-4 flex justify-between">
              <button onClick={goToPreviousStep} className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors">Back</button>
              <button onClick={handleDietaryContinue} className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">Continue to Activity Selection</button>
            </div>
          </div>
        );
      case 'activity':
        return (
          <ActivitySelection
            onActivitySelected={handleActivitySelection}
            customerData={customerData}
            experimentConfig={currentTrialConfig}
          />
        );
      case 'protein':
        return (
          <div>
            <h2 className="text-xl font-semibold mb-6">🥩 Select Your Protein</h2>
            {(userDietaryRestrictions.length > 0 || userAllergens.length > 0) && (
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                <p className="text-sm text-blue-800">
                  🛡️ <strong>Filtered for your safety:</strong> Only showing proteins compatible with your dietary preferences and allergies.
                </p>
              </div>
            )}
            <MenuSelectionGrid
              title="Choose Your Protein"
              items={getFilteredProteins()}
              category="Protein"
              selectedItems={protein}
              onSelect={setProtein}
              recommendations={recommendations.proteins || []}
              showPortionSizes={true}
              showCalories={true}
              multiSelect={false}
            />
            <div className="mt-4 flex justify-between">
              <button onClick={() => setStep('activity')} className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors">Back</button>
              <button
                onClick={() => setStep('base')}
                disabled={protein.length === 0}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Continue to Base Selection
              </button>
            </div>
          </div>
        );
      case 'base':
        return (
          <div>
            <h2 className="text-xl font-semibold mb-6">🍚 Select Your Base</h2>
            <BaseSelectionGrid
              title="Choose Your Base"
              baseTypes={getBaseTypes()}
              selectedBaseType={baseType}
              selectedBaseOption={baseOption}
              onSelect={(type, option) => {
                setBaseType(type);
                setBaseOption(option);
              }}
              recommendations={recommendations.base_types || []}
            />
            <div className="mt-4 flex justify-between">
              <button onClick={() => setStep('protein')} className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors">Back</button>
              <button
                onClick={() => setStep('sauce')}
                disabled={!baseType || !baseOption}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Continue to Sauce Selection
              </button>
            </div>
          </div>
        );
      case 'sauce':
        return (
          <div>
            <h2 className="text-xl font-semibold mb-6">🥘 Select Your Sauce</h2>
            <MenuSelectionGrid
              title="Choose Your Sauce"
              items={getSauces()}
              category="Sauce"
              selectedItems={sauce}
              onSelect={setSauce}
              recommendations={recommendations.sauces || []}
              showCalories={true}
              showPortionSizes={true}
              multiSelect={false}
            />
            <div className="mt-4 flex justify-between">
              <button onClick={() => setStep('base')} className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors">Back</button>
              <button
                onClick={() => setStep('veggies')}
                disabled={sauce.length === 0}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Continue to Veggies Selection
              </button>
            </div>
          </div>
        );
      case 'veggies':
        return (
          <div>
            <h2 className="text-xl font-semibold mb-6">🥬 Select Your Veggies</h2>
            <MenuSelectionGrid
              title="Choose Your Veggies"
              items={getVeggies()}
              category="Veggies"
              selectedItems={veggies}
              onSelect={setVeggies}
              maxFreeSelections={5}
              premiumItems={premiumVeggies}
              premiumPrice={1.00}
              extraPrice={0.50}
              showCalories={true}
              showPortionSizes={true}
              multiSelect={true}
            />
            <div className="mt-4 flex justify-between">
              <button onClick={() => setStep('sauce')} className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors">Back</button>
              <button
                onClick={() => setStep('garnishes')}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Continue to Garnishes Selection
              </button>
            </div>
          </div>
        );
      case 'garnishes':
        return (
          <div>
            <h2 className="text-xl font-semibold mb-6">🌿 Select Your Garnishes</h2>
            <MenuSelectionGrid
              title="Choose Your Garnishes"
              items={getGarnishes()}
              category="Garnishes"
              selectedItems={garnishes}
              onSelect={setGarnishes}
              maxFreeSelections={2}
              extraPrice={0.25}
              showCalories={true}
              showPortionSizes={true}
              multiSelect={true}
            />
            <div className="mt-4 flex justify-between">
              <button onClick={() => setStep('veggies')} className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors">Back</button>
              <button
                onClick={() => setStep('dish-name')}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Continue to Dish Name
              </button>
            </div>
          </div>
        );
      case 'dish-name':
        return (
          <div>
            <h2 className="text-xl font-semibold mb-6">🍽️ Name Your Dish</h2>

            {/* Suggested Names Section */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                💡 Suggested names for your creation:
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-4">
                {generateSuggestedDishNames().map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => setDishName(suggestion)}
                    className={`p-3 text-left rounded-lg border-2 transition-all hover:border-blue-300 ${
                      dishName === suggestion
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    <span className="font-medium text-gray-800">{suggestion}</span>
                    {dishName === suggestion && (
                      <span className="ml-2 text-blue-600">✓</span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Name Input */}
            <div className="mb-4">
              <label htmlFor="dish-name" className="block text-sm font-medium text-gray-700 mb-2">
                ✏️ Or create your own custom name:
              </label>
              <input
                type="text"
                id="dish-name"
                value={dishName}
                onChange={(e) => setDishName(e.target.value)}
                placeholder="e.g., Spicy Chicken Curry Bowl"
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Current Selection Preview */}
            {dishName && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
                <p className="text-sm text-green-800">
                  <strong>Your dish will be called:</strong> "{dishName}"
                </p>
              </div>
            )}

            <div className="mt-4 flex justify-between">
              <button onClick={() => setStep('garnishes')} className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors">Back</button>
              <button
                onClick={() => setStep('summary')}
                disabled={!dishName.trim()}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Review Order
              </button>
            </div>
          </div>
        );
      case 'summary':
        return (
          <div>
            <h2 className="text-xl font-semibold mb-6">📋 Order Summary</h2>

            {/* Agent Recommendations for Trial B */}
            {isTrialB && (
              <AgentRecommendations
                isVisible={true}
                orderDetails={{
                  protein,
                  sauce,
                  baseType,
                  baseOption,
                  veggies,
                  garnishes,
                  dishName
                }}
                onRefreshmentSelect={(refreshment) => {
                  console.log('Refreshment selected:', refreshment);
                  // Add refreshment to order
                }}
                onAgentInteraction={(interaction) => {
                  console.log('Agent interaction:', interaction);
                  // Track for experiment
                }}
              />
            )}

            <OrderSummary
              protein={protein}
              baseType={baseType}
              baseOption={baseOption}
              sauce={sauce}
              veggies={veggies}
              garnishes={garnishes}
              dishName={dishName}
              onEdit={() => setStep('protein')}
              onComplete={handleCompleteOrder}
              customerData={customerData}
            />
          </div>
        );
      case 'complete':
        return (
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4 text-green-600">✅ Order Complete!</h2>
            <p className="text-gray-600 mb-6">Thank you for your order. Your food will be ready soon!</p>
            <SocialSharing dishName={dishName} />
          </div>
        );
      default:
        return null;
    }
  };

          // Helper to generate suggested dish names
  const generateSuggestedDishNames = () => {
    const customerName = customerData?.name || participantName || 'Chef';
    const proteinName = protein.length > 0 ? (typeof protein[0] === 'object' ? protein[0].name : protein[0]) : 'Special';
    const baseTypeName = baseType || 'Bowl';
    const sauceName = sauce.length > 0 ? (typeof sauce[0] === 'object' ? sauce[0].name : sauce[0]) : 'Special';

    // Clean up names for better formatting
    const cleanCustomerName = customerName.split(' ')[0]; // Use first name only
    const cleanProteinName = proteinName.replace('/', ' ').replace('Indian Cheese', 'Paneer');
    const cleanBaseTypeName = baseTypeName.replace(' & ', ' ').replace('Sandwich', 'Sub');
    const cleanSauceName = sauceName.replace('Special', 'Signature').replace('Masala', 'Spice');

    // Create variations based on selections
    const suggestions = [
      `${cleanCustomerName}'s ${cleanProteinName} ${cleanBaseTypeName}`,
      `${cleanCustomerName}'s Special ${cleanBaseTypeName}`,
      `${cleanProteinName} ${cleanSauceName} ${cleanBaseTypeName}`,
      `${cleanCustomerName}'s ${cleanSauceName} Creation`,
      `${cleanProteinName} ${cleanBaseTypeName} Delight`,
      `${cleanCustomerName}'s Signature ${cleanBaseTypeName}`,
      `${cleanSauceName} ${cleanProteinName} ${cleanBaseTypeName}`,
      `${cleanCustomerName}'s Ultimate ${cleanBaseTypeName}`
    ];

    // Add dietary-specific suggestions
    if (userDietaryRestrictions.length > 0) {
      const restriction = userDietaryRestrictions[0];
      const restrictionLabel = restriction.charAt(0).toUpperCase() + restriction.slice(1).replace('_', ' ');
      suggestions.push(
        `${cleanCustomerName}'s ${restrictionLabel} ${cleanBaseTypeName}`,
        `${restrictionLabel} ${cleanProteinName} ${cleanBaseTypeName}`
      );
    }

    // Add veggie-based suggestions if veggies are selected
    if (veggies.length > 0) {
      const veggieName = typeof veggies[0] === 'object' ? veggies[0].name : veggies[0];
      const cleanVeggieName = veggieName.replace('Grilled ', '').replace('Bell ', '');
      suggestions.push(
        `${cleanCustomerName}'s ${cleanVeggieName} ${cleanBaseTypeName}`,
        `${cleanVeggieName} ${cleanProteinName} ${cleanBaseTypeName}`
      );
    }

    return suggestions.slice(0, 6); // Return top 6 suggestions
  };

    // Auto-suggest dish name when reaching the dish-name step
  useEffect(() => {
    if (currentStep === 'dish-name' && !dishName.trim()) {
      const suggestions = generateSuggestedDishNames();
      if (suggestions.length > 0) {
        setDishName(suggestions[0]); // Auto-select the first suggestion
      }
    }
  }, [currentStep, dishName, customerData, participantName, protein, baseType, sauce, veggies, userDietaryRestrictions]);

  // Helper to filter proteins based on dietary restrictions and allergies
  const getFilteredProteins = () => {
    const allProteins = getProteins();

    // If data is still loading, return all proteins
    if (!availableRestrictions || !availableAllergens) {
      return allProteins;
    }

    // First, filter by dietary restrictions
    let filteredProteins = allProteins;

    if (userDietaryRestrictions.length > 0) {
      // Get allowed proteins from all selected dietary restrictions
      const allowedProteins = new Set();

      userDietaryRestrictions.forEach(restriction => {
        // Get allowed proteins for this restriction from the backend data
        const restrictionData = availableRestrictions[restriction];
        if (restrictionData?.allowed_proteins) {
          restrictionData.allowed_proteins.forEach(protein => {
            allowedProteins.add(protein.toLowerCase());
          });
        }
      });

      // Filter proteins based on allowed list
      filteredProteins = allProteins.filter(protein => {
        const proteinName = protein.name.toLowerCase();
        return allowedProteins.has(proteinName);
      });
    }

    // Then, filter by allergies (this applies regardless of dietary restrictions)
    if (userAllergens.length > 0) {
      filteredProteins = filteredProteins.filter(protein => {
        const proteinName = protein.name.toLowerCase();

        const isAllergic = userAllergens.some(allergen => {
          const allergenData = availableAllergens[allergen];
          if (allergenData?.ingredients) {
            return allergenData.ingredients.some(ingredient =>
              ingredient.toLowerCase() === proteinName
            );
          }
          return false;
        });

        return !isAllergic;
      });
    }

    return filteredProteins;
  };

  return (
    <div className="max-w-7xl mx-auto px-6">
      {/* 🚨 DEBUG BANNER - REMOVE AFTER TESTING */}
      <div className="mb-4 p-4 bg-red-100 border-2 border-red-500 rounded-lg">
        <h3 className="font-bold text-red-800">🔧 DEBUG MODE - Changes Active!</h3>
        <div className="text-sm text-red-700 grid grid-cols-2 gap-2 mb-2">
          <div><strong>Current Step:</strong> {currentStep}</div>
          <div><strong>Current Phase:</strong> {currentPhase}</div>
          <div><strong>Is Trial B:</strong> {isTrialB ? '✅ YES' : '❌ NO'}</div>
          <div><strong>Experiment Active:</strong> {experimentCycleActive ? '✅ YES' : '❌ NO'}</div>
        </div>
        <div className="border-t border-red-300 pt-2">
          <h4 className="font-bold text-red-800 mb-1">Current Selections:</h4>
          <div className="text-xs grid grid-cols-3 gap-2">
            <div><strong>Protein:</strong> {protein.length > 0 ? protein.map(p => typeof p === 'object' ? p.name : p).join(', ') : 'None'}</div>
            <div><strong>Base:</strong> {baseType && baseOption ? `${baseType} - ${baseOption}` : 'None'}</div>
            <div><strong>Sauce:</strong> {sauce.length > 0 ? sauce.map(s => typeof s === 'object' ? s.name : s).join(', ') : 'None'}</div>
            <div><strong>Veggies:</strong> {veggies.length > 0 ? veggies.map(v => typeof v === 'object' ? v.name : v).join(', ') : 'None'}</div>
            <div><strong>Garnishes:</strong> {garnishes.length > 0 ? garnishes.map(g => typeof g === 'object' ? g.name : g).join(', ') : 'None'}</div>
            <div><strong>Dish Name:</strong> {dishName || 'None'}</div>
          </div>
        </div>
      </div>

      {/* Show progress bar if we have multiple steps */}
      {renderProgressBar()}

      {error && renderError()}

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