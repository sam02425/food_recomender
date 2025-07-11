import React, { useCallback, memo } from 'react';
import PropTypes from 'prop-types';
import './BaseSelectionGrid.css';

/**
 * Specialized component for base options that handles the hierarchical structure.
 * Groups options by base type (e.g., Biryani, Sandwich, Wrap) and manages selection.
 */
const BaseSelectionGrid = memo(({
  title,
  baseTypes,
  recommendations = [],
  selectedBaseType = '',
  selectedBaseOption = '',
  onSelect
}) => {
  // Handle base selection (updates both type and option)
  const handleBaseSelection = useCallback((type, option) => {
    // Don't allow selection if item is out of stock
    if (option.status === 'out_of_stock') {
      return;
    }

    // If the same item is selected, deselect it to allow changing
    if (selectedBaseType === type && selectedBaseOption === option.name) {
      onSelect('', ''); // Clear selection
    } else {
      onSelect(type, option.name);
    }
  }, [selectedBaseType, selectedBaseOption, onSelect]);

  const getStatusBadge = (option) => {
    if (!option.status || option.status === 'available') return null;

    const statusConfig = {
      'low_stock': { text: 'Low Stock', className: 'status-low-stock' },
      'preparing': { text: `Preparing (${option.wait_time}m)`, className: 'status-preparing' },
      'out_of_stock': { text: 'Out of Stock', className: 'status-out-of-stock' }
    };

    const config = statusConfig[option.status];
    if (!config) return null;

    return (
      <div className={`status-badge ${config.className}`}>
        {config.text}
      </div>
    );
  };

  const getStockIndicator = (option) => {
    if (!option.stock_level && option.stock_level !== 0) return null;

    let stockClass = 'stock-high';
    if (option.stock_level <= 5) {
      stockClass = 'stock-critical';
    } else if (option.stock_level <= 10) {
      stockClass = 'stock-low';
    } else if (option.stock_level <= 20) {
      stockClass = 'stock-medium';
    }

    return (
      <div className={`stock-indicator ${stockClass}`}>
        Stock: {option.stock_level}
      </div>
    );
  };

  // Memoize the base type rendering to prevent unnecessary re-renders
  const renderBaseType = useCallback(([baseType, options]) => (
    <div key={baseType} className="mb-6">
      <h3 className={`text-lg font-medium mb-2 pb-2 border-b ${recommendations.includes(baseType) ? 'text-green-600' : ''}`}>
        {baseType}
        {recommendations.includes(baseType) && <span className="text-green-500 ml-2">✓</span>}
      </h3>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {options.map((option) => {
          const isSelected = selectedBaseType === baseType && selectedBaseOption === option.name;
          const isDisabled = option.status === 'out_of_stock';

          return (
            <div
              key={`${baseType}-${option.name}`}
              onClick={() => handleBaseSelection(baseType, option)}
              className={`
                relative p-4 rounded-lg border-2 cursor-pointer transition-all
                ${isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}
                ${recommendations.includes(baseType) ? 'border-green-500 shadow-sm' : ''}
                ${isSelected && recommendations.includes(baseType) ? 'border-blue-500 shadow-md border-dashed' : ''}
                ${isDisabled ? 'opacity-50 cursor-not-allowed bg-gray-50' : 'hover:border-blue-300'}
              `}
              title={option.description}
            >
              <div className="flex justify-between items-start">
                <span className="font-medium">{option.name}</span>
                {getStatusBadge(option)}
              </div>

              <div className="flex justify-between items-center mt-1">
                <div className="text-sm text-gray-600">${option.price.toFixed(2)}</div>
                {option.calories && (
                  <div className="text-xs text-gray-500">{option.calories} cal</div>
                )}
              </div>

              {getStockIndicator(option)}

              {option.status === 'preparing' && option.wait_time && (
                <div className="wait-time">
                  ⏱️ Ready in {option.wait_time} minutes
                </div>
              )}

              <div className="text-xs text-gray-500 mt-1 truncate">
                {option.description}
              </div>

              {isSelected && (
                <div className="absolute top-0 right-0 bg-blue-500 w-6 h-6 flex items-center justify-center rounded-bl-md">
                  <span className="text-white text-xs">✓</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  ), [selectedBaseType, selectedBaseOption, recommendations, handleBaseSelection]);

  return (
    <div className="w-full mb-6">
      <h2 className="text-xl font-bold mb-3">{title}</h2>
      {!baseTypes ? (
        <div className="text-center py-8">
          <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading base options...</p>
        </div>
      ) : (
        Object.entries(baseTypes).map(renderBaseType)
      )}
    </div>
  );
});

BaseSelectionGrid.propTypes = {
  title: PropTypes.string.isRequired,
  baseTypes: PropTypes.object,
  recommendations: PropTypes.array,
  selectedBaseType: PropTypes.string,
  selectedBaseOption: PropTypes.string,
  onSelect: PropTypes.func.isRequired
};

BaseSelectionGrid.displayName = 'BaseSelectionGrid';

export default BaseSelectionGrid;