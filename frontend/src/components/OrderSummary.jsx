// frontend/src/components/OrderSummary.jsx
import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';

/**
 * Production-level component for displaying the order summary with
 * calculations, responsive design, and clear data presentation.
 * Supports both single-item orders (individual props) and multi-item orders (orderItems array).
 */
const OrderSummary = ({
  // Multi-item order props
  orderItems,
  totalPrice,
  onAddAnother,
  onComplete,
  isLoading = false,

  // Single-item order props (for backward compatibility)
  protein,
  baseType,
  baseOption,
  sauce,
  veggies = [],
  garnishes = [],
  dishName,
  onEdit,
  customerData
}) => {
  const [animateTotal, setAnimateTotal] = useState(false);

  // Determine if this is a single-item or multi-item order
  const isSingleItemOrder = !orderItems && (protein || baseType || sauce);

  // For single-item orders, create a mock orderItems array
  const currentOrderItems = isSingleItemOrder ? [{
    dish_name: dishName || `${protein?.map(p => typeof p === 'object' ? p.name : p).join(', ') || 'Custom'} ${baseType || 'Dish'}`,
    protein: protein || [],
    sauce: sauce || [],
    base_type: baseType || 'Custom',
    base_option: baseOption || 'Custom',
    veggies: veggies || [],
    garnishes: garnishes || [],
    price: 0 // Will be calculated
  }] : (orderItems || []);

    // Calculate total price for single-item orders
  const calculatedTotalPrice = isSingleItemOrder ?
    (protein?.length > 0 ? 4.50 : 0) +
    (veggies?.length > 0 ? veggies.length * 0.50 : 0) +
    (garnishes?.length > 0 ? garnishes.length * 0.25 : 0) :
    totalPrice;

  // Calculate total calories for single-item orders
  const calculateTotalCalories = () => {
    if (!isSingleItemOrder) return 0;

    let totalCalories = 0;

    // Protein calories (approximate based on menu data)
    if (protein?.length > 0) {
      const proteinCalories = {
        'Chicken': 250,
        'Egg': 180,
        'Paneer': 220,
        'Soya': 150,
        'Potato': 200
      };
      protein.forEach(p => {
        totalCalories += proteinCalories[p] || 200;
      });
    }

    // Veggie calories (approximate)
    if (veggies?.length > 0) {
      const veggieCalories = {
        'Onion': 40,
        'Tomato': 25,
        'Cucumber': 15,
        'Lettuce': 5,
        'Carrot': 30
      };
      veggies.forEach(v => {
        totalCalories += veggieCalories[v] || 20;
      });
    }

    // Garnish calories (approximate)
    if (garnishes?.length > 0) {
      const garnishCalories = {
        'Cilantro': 5,
        'Mint': 5,
        'Lemon': 5,
        'Chili': 5
      };
      garnishes.forEach(g => {
        totalCalories += garnishCalories[g] || 5;
      });
    }

    // Base calories (approximate)
    if (baseType && baseOption) {
      const baseCalories = {
        'Rice': 300,
        'Sourdough': 220,
        'Ciabatta': 240,
        'White Bread': 200,
        'Naan': 280,
        'Pitta': 200
      };
      totalCalories += baseCalories[baseOption] || 250;
    }

    // Sauce calories (approximate)
    if (sauce?.length > 0) {
      const sauceCalories = {
        'Curry Special': 120,
        'Malai Masala': 150,
        'Curry Masala': 130,
        'Marinara': 80,
        'Yogurt/Raita': 60
      };
      sauce.forEach(s => {
        totalCalories += sauceCalories[s] || 100;
      });
    }

    return totalCalories;
  };

  // Animate total when it changes
  useEffect(() => {
    setAnimateTotal(true);
    const timer = setTimeout(() => setAnimateTotal(false), 300);
    return () => clearTimeout(timer);
  }, [calculatedTotalPrice]);

  // Calculate total veggies
  const getTotalVeggies = () => {
    return currentOrderItems.reduce((sum, item) => sum + (item.veggies?.length || 0), 0);
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  // Get time estimate
  const getTimeEstimate = () => {
    // Basic estimation: 5 minutes base + 2 minutes per item
    const minutes = 5 + (currentOrderItems.length * 2);
    const now = new Date();
    const readyTime = new Date(now.getTime() + minutes * 60000);
    return readyTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="w-full" aria-live="polite">
      <h2 className="text-2xl font-bold mb-4" id="order-summary-heading">Order Summary</h2>

      {currentOrderItems.length === 0 ? (
        <div className="p-8 text-center bg-gray-50 rounded-lg border border-gray-200">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <p className="text-gray-600 mb-4">Your order is empty</p>
          <button
            onClick={onAddAnother || onEdit}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors inline-flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
            </svg>
            Start Adding Items
          </button>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden mb-6 shadow-sm">
            {/* Order items section */}
            <div className="divide-y divide-gray-200">
              {currentOrderItems.map((item, index) => (
                <div key={index} className="animate-fadeIn">
                  <div className="p-4 bg-orange-50 border-b border-gray-200 flex justify-between items-center">
                    <h3 className="font-bold text-orange-700">
                      {item.dish_name || `${Array.isArray(item.protein)
                        ? item.protein.map(p => typeof p === 'object' ? p.name : p).join(', ')
                        : (typeof item.protein === 'object' ? item.protein.name : item.protein)
                      } ${item.base_type}`}
                    </h3>
                    <span className="font-medium text-gray-900">
                      {formatCurrency(item.price || calculatedTotalPrice)}
                    </span>
                  </div>

                  <div className="p-4">
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                      <div>
                        <p className="text-sm text-gray-500">Protein</p>
                        <p className="font-medium">
                          {Array.isArray(item.protein)
                            ? item.protein.map(p => typeof p === 'object' ? p.name : p).join(', ')
                            : (typeof item.protein === 'object' ? item.protein.name : item.protein)
                          }
                        </p>
                      </div>

                      <div>
                        <p className="text-sm text-gray-500">Sauce</p>
                        <p className="font-medium">
                          {Array.isArray(item.sauce)
                            ? item.sauce.map(s => typeof s === 'object' ? s.name : s).join(', ')
                            : (typeof item.sauce === 'object' ? item.sauce.name : item.sauce)
                          }
                        </p>
                      </div>

                      <div>
                        <p className="text-sm text-gray-500">Base</p>
                        <p className="font-medium">{`${item.base_type} - ${item.base_option}`}</p>
                      </div>

                      <div>
                        <p className="text-sm text-gray-500">Veggies</p>
                        <p className="font-medium">{item.veggies?.length || 0}</p>
                      </div>

                      <div>
                        <p className="text-sm text-gray-500">Calories</p>
                        <p className="font-medium">{calculateTotalCalories()} cal</p>
                      </div>
                    </div>

                    {/* Show veggies if any */}
                    {item.veggies && item.veggies.length > 0 && (
                      <div className="mt-3">
                        <p className="text-sm text-gray-500">Veggies</p>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {item.veggies.map((veggie, i) => (
                            <span key={i} className="px-2 py-1 bg-gray-100 rounded-md text-sm">
                              {typeof veggie === 'object' ? veggie.name : veggie}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Show garnishes if any */}
                    {item.garnishes && item.garnishes.length > 0 && (
                      <div className="mt-3">
                        <p className="text-sm text-gray-500">Garnishes</p>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {item.garnishes.map((garnish, i) => (
                            <span key={i} className="px-2 py-1 bg-green-100 rounded-md text-sm">
                              {typeof garnish === 'object' ? garnish.name : garnish}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Order summary section */}
            <div className="p-4 bg-gray-50">
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Items</span>
                <span className="text-gray-800">{currentOrderItems.length}</span>
              </div>

              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Total Veggies</span>
                <span className="text-gray-800">{getTotalVeggies()}</span>
              </div>

              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Total Calories</span>
                <span className="text-gray-800">{calculateTotalCalories()} cal</span>
              </div>

              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Estimated Ready Time</span>
                <span className="text-gray-800">{getTimeEstimate()}</span>
              </div>

              <div className="h-px bg-gray-200 my-3"></div>

              <div className="flex justify-between items-center mb-2">
                <span className="text-lg font-bold">Total</span>
                <span className={`text-lg font-bold ${animateTotal ? 'text-green-600 scale-110 transition-all' : 'text-gray-900'}`}>
                  {formatCurrency(calculatedTotalPrice)}
                </span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-lg font-bold text-orange-600">Total Calories</span>
                <span className="text-lg font-bold text-orange-600">
                  {calculateTotalCalories()} cal
                </span>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={onAddAnother || onEdit}
              className="flex-1 py-2 px-4 bg-gray-200 hover:bg-gray-300 rounded-md text-gray-800 transition-colors flex items-center justify-center"
              disabled={isLoading}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
              </svg>
              {isSingleItemOrder ? 'Edit Order' : 'Add Another Item'}
            </button>

            <button
              onClick={onComplete}
              disabled={isLoading}
              className={`
                flex-1 py-2 px-4 rounded-md text-white transition-colors flex items-center justify-center
                ${isLoading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'}
              `}
              aria-busy={isLoading ? 'true' : 'false'}
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing Order...
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Complete Order
                </>
              )}
            </button>
          </div>
        </>
      )}
    </div>
  );
};

OrderSummary.propTypes = {
  // Multi-item order props
  orderItems: PropTypes.arrayOf(
    PropTypes.shape({
      dish_name: PropTypes.string,
      protein: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.arrayOf(PropTypes.oneOfType([PropTypes.string, PropTypes.object]))
      ]).isRequired,
      sauce: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.arrayOf(PropTypes.oneOfType([PropTypes.string, PropTypes.object]))
      ]).isRequired,
      base_type: PropTypes.string.isRequired,
      base_option: PropTypes.string.isRequired,
      veggies: PropTypes.arrayOf(PropTypes.oneOfType([PropTypes.string, PropTypes.object])),
      garnishes: PropTypes.arrayOf(PropTypes.oneOfType([PropTypes.string, PropTypes.object])),
      price: PropTypes.number.isRequired
    })
  ),
  totalPrice: PropTypes.number,
  onAddAnother: PropTypes.func,
  onComplete: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,

  // Single-item order props
  protein: PropTypes.arrayOf(PropTypes.oneOfType([PropTypes.string, PropTypes.object])),
  baseType: PropTypes.string,
  baseOption: PropTypes.string,
  sauce: PropTypes.arrayOf(PropTypes.oneOfType([PropTypes.string, PropTypes.object])),
  veggies: PropTypes.arrayOf(PropTypes.oneOfType([PropTypes.string, PropTypes.object])),
  garnishes: PropTypes.arrayOf(PropTypes.oneOfType([PropTypes.string, PropTypes.object])),
  dishName: PropTypes.string,
  onEdit: PropTypes.func,
  customerData: PropTypes.object
};

export default OrderSummary;