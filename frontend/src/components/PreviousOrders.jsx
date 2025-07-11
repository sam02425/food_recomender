import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const PreviousOrders = ({
  customerPhone,
  onSkip,
  onAddItem,
  onCheckout,
  onLoadDietaryPreferences
}) => {
  const [customerData, setCustomerData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedOrder, setSelectedOrder] = useState(null);

  useEffect(() => {
    if (customerPhone) {
      fetchCustomerData();
    }
  }, [customerPhone]);

  const fetchCustomerData = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/customer-orders?phone=${customerPhone}`);

      if (!response.ok) {
        throw new Error('Failed to fetch customer data');
      }

      const data = await response.json();
      setCustomerData(data);

      // Auto-load dietary preferences if available
      if (data.dietary_profile && (data.dietary_profile.restrictions?.length > 0 || data.dietary_profile.allergies?.length > 0)) {
        onLoadDietaryPreferences(data.dietary_profile);
      }

    } catch (err) {
      setError(err.message);
      console.error('Error fetching customer data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReorder = (order) => {
    setSelectedOrder(order);
    // Extract items from the order and pass to add item
    const orderItems = {
      protein: order.items.protein || [],
      sauce: order.items.sauce || [],
      base_type: order.items.base_type || '',
      base_option: order.items.base_option || '',
      veggies: order.items.veggies || [],
      garnishes: order.items.garnishes || [],
      dish_name: order.items.dish_name || ''
    };
    onAddItem(orderItems);
  };

  const formatOrderDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getOrderSummary = (order) => {
    const items = order.items;
    const summary = [];

    if (items.protein?.length > 0) {
      const proteinNames = items.protein.map(p => typeof p === 'object' ? p.name : p);
      summary.push(proteinNames.join(', '));
    }
    if (items.sauce?.length > 0) {
      const sauceNames = items.sauce.map(s => typeof s === 'object' ? s.name : s);
      summary.push(sauceNames.join(', '));
    }
    if (items.base_option) {
      summary.push(items.base_option);
    }

    return summary.join(' + ');
  };

  if (isLoading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading your order history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
        <p className="text-red-600">Error loading order history: {error}</p>
        <button
          onClick={onSkip}
          className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Continue to New Order
        </button>
      </div>
    );
  }

  if (!customerData?.has_previous_orders) {
    return (
      <div className="text-center py-8">
        <div className="text-4xl mb-4">👋</div>
        <h2 className="text-xl font-semibold mb-2">Welcome!</h2>
        <p className="text-gray-600 mb-6">This is your first order with us.</p>
        <button
          onClick={onSkip}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Start Your First Order
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome Back! 👋
        </h2>
        <p className="text-gray-600">
          You have {customerData.total_orders} previous order{customerData.total_orders !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Favorite Items */}
      {customerData.favorite_items?.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-blue-900 mb-3">⭐ Your Favorites</h3>
          <div className="flex flex-wrap gap-2">
            {customerData.favorite_items.map((item, index) => (
              <span
                key={index}
                className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
              >
                {item.name} ({item.count}x)
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recent Orders */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          📋 Your Recent Orders
        </h3>
        <div className="grid gap-4">
          {customerData.recent_orders.map((order, index) => (
            <div
              key={order.order_id}
              className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                selectedOrder?.order_id === order.order_id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedOrder(order)}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="font-medium text-gray-900">
                    {getOrderSummary(order)}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    {formatOrderDate(order.timestamp)}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    ${order.total_price} • {order.total_calories} calories
                  </div>
                </div>
                <div className="ml-4">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleReorder(order);
                    }}
                    className="px-3 py-1 bg-green-600 text-white text-sm rounded-md hover:bg-green-700"
                  >
                    Reorder
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={onSkip}
          className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
        >
          🆕 Start New Order
        </button>

        <button
          onClick={onAddItem}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          ➕ Add Another Item
        </button>

        <button
          onClick={onCheckout}
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          🛒 Go to Checkout
        </button>
      </div>

      {/* Selected Order Details */}
      {selectedOrder && (
        <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h4 className="font-semibold text-gray-900 mb-3">
            📋 Selected Order Details
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <strong>Protein:</strong> {selectedOrder.items.protein?.map(p => typeof p === 'object' ? p.name : p).join(', ') || 'None'}
            </div>
            <div>
              <strong>Sauce:</strong> {selectedOrder.items.sauce?.map(s => typeof s === 'object' ? s.name : s).join(', ') || 'None'}
            </div>
            <div>
              <strong>Base:</strong> {selectedOrder.items.base_option || 'None'}
            </div>
            <div>
              <strong>Veggies:</strong> {selectedOrder.items.veggies?.map(v => typeof v === 'object' ? v.name : v).join(', ') || 'None'}
            </div>
            <div>
              <strong>Garnishes:</strong> {selectedOrder.items.garnishes?.map(g => typeof g === 'object' ? g.name : g).join(', ') || 'None'}
            </div>
            <div>
              <strong>Dish Name:</strong> {selectedOrder.items.dish_name || 'Custom'}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

PreviousOrders.propTypes = {
  customerPhone: PropTypes.string.isRequired,
  onSkip: PropTypes.func.isRequired,
  onAddItem: PropTypes.func.isRequired,
  onCheckout: PropTypes.func.isRequired,
  onLoadDietaryPreferences: PropTypes.func.isRequired
};

export default PreviousOrders;