import React, { useCallback, memo } from 'react';
import PropTypes from 'prop-types';

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
    // If the same item is selected, deselect it to allow changing
    if (selectedBaseType === type && selectedBaseOption === option) {
      onSelect('', ''); // Clear selection
    } else {
      onSelect(type, option);
    }
  }, [selectedBaseType, selectedBaseOption, onSelect]);

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

          return (
            <div
              key={`${baseType}-${option.name}`}
              onClick={() => handleBaseSelection(baseType, option.name)}
              className={`
                relative p-4 rounded-lg border-2 cursor-pointer transition-all
                ${isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}
                ${recommendations.includes(baseType) ? 'border-green-500 shadow-sm' : ''}
                ${isSelected && recommendations.includes(baseType) ? 'border-blue-500 shadow-md border-dashed' : ''}
                hover:border-blue-300
              `}
            >
              <div className="flex justify-between items-center">
                <span className="font-medium">{option.name}</span>
                <span className="text-sm text-gray-600">${option.price.toFixed(2)}</span>
              </div>

              <div className="text-xs text-gray-500 mt-1 truncate" title={option.description}>
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
      {Object.entries(baseTypes).map(renderBaseType)}
    </div>
  );
});

BaseSelectionGrid.propTypes = {
  title: PropTypes.string.isRequired,
  baseTypes: PropTypes.object.isRequired,
  recommendations: PropTypes.array,
  selectedBaseType: PropTypes.string,
  selectedBaseOption: PropTypes.string,
  onSelect: PropTypes.func.isRequired
};

BaseSelectionGrid.displayName = 'BaseSelectionGrid';

export default BaseSelectionGrid;