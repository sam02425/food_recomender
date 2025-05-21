import React from 'react';
import PropTypes from 'prop-types';

/**
 * Enhanced grid component for menu item selection with recommendation highlighting.
 * Handles both single-select (protein, sauce) and multi-select (veggies) options.
 */
const MenuSelectionGrid = ({
  title,
  items,
  recommendations = [],
  category,
  selectedItems = [],
  onSelect,
  maxFreeSelections = null,
  premiumItems = [],
  premiumPrice = 0,
  extraPrice = 0
}) => {
  // Handle single vs multiple selection
  const isMultiSelect = Array.isArray(selectedItems);

  const handleItemClick = (item) => {
    if (isMultiSelect) {
      // For multi-select (like veggies)
      if (selectedItems.includes(item)) {
        onSelect(selectedItems.filter(i => i !== item));
      } else {
        onSelect([...selectedItems, item]);
      }
    } else {
      // For single select (proteins, sauces, base)
      onSelect(item === selectedItems ? '' : item); // Toggle selection if clicking the same item
    }
  };

  // Calculate pricing information for display
  const getPricingInfo = (item) => {
    if (!maxFreeSelections) return null;

    if (premiumItems.includes(item)) {
      return `$${premiumPrice.toFixed(2)}`;
    }

    // For regular items, show pricing only if it's an extra item
    if (isMultiSelect && maxFreeSelections) {
      const itemIndex = selectedItems.indexOf(item);
      if (itemIndex >= 0 && itemIndex >= maxFreeSelections) {
        return `$${extraPrice.toFixed(2)}`;
      }
    }

    return null;
  };

  return (
    <div className="w-full mb-6">
      <h2 className="text-xl font-bold mb-3">{title}</h2>

      {/* Display info about pricing for veggies */}
      {maxFreeSelections && (
        <div className="mb-4 p-3 bg-blue-50 rounded-md text-sm">
          <p>First {maxFreeSelections} {category.toLowerCase()} are included</p>
          {extraPrice > 0 && <p>Each additional: ${extraPrice.toFixed(2)}</p>}
          {premiumItems.length > 0 && <p>{premiumItems.join(', ')}: ${premiumPrice.toFixed(2)} each</p>}
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {items.map((item) => {
          // If item is an object (for proteins with prices), extract the properties
          const itemName = typeof item === 'object' ? item.name : item;
          const itemPrice = typeof item === 'object' ? item.price : null;
          const itemDescription = typeof item === 'object' ? item.description : null;

          const isSelected = isMultiSelect
            ? selectedItems.includes(itemName)
            : selectedItems === itemName;
          const isRecommended = recommendations.includes(itemName);
          const pricing = getPricingInfo(itemName);

          return (
            <div
              key={itemName}
              onClick={() => handleItemClick(itemName)}
              onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleItemClick(itemName); }}
              role="button"
              tabIndex={0}
              className={`
                relative p-4 rounded-lg border-2 cursor-pointer transition-all
                ${isSelected ? 'border-blue-500 bg-blue-600 text-white' : 'border-gray-200'}
                ${isRecommended ? 'border-green-500 shadow-md' : ''}
                ${isSelected && isRecommended ? 'border-blue-500 shadow-md border-dashed' : ''}
                hover:border-blue-300
              `}
              {...(category === 'Protein' ? { 'data-testid': `protein-${itemName.toLowerCase().replace(/[^a-z0-9]+/g, '-')}` } : {})}
            >
              <div className="flex justify-between items-center">
                <span
                  className="font-medium"
                >
                  {itemName}
                </span>
                {isRecommended && (
                  <span className="text-green-500 ml-2">✓</span>
                )}
              </div>

              {/* Display the price if protein item */}
              {itemPrice !== null && (
                <div className="text-sm text-gray-600 mt-1 font-medium">
                  ${itemPrice.toFixed(2)}
                </div>
              )}

              {/* Display the description if available */}
              {itemDescription && (
                <div className="text-xs text-gray-500 mt-1 truncate" title={itemDescription}>
                  {itemDescription}
                </div>
              )}

              {/* Show premium or extra pricing */}
              {pricing && (
                <div className="text-sm text-gray-600 mt-1">
                  {pricing}
                </div>
              )}

              {isSelected && (
                <div className="absolute top-0 right-0 bg-blue-500 w-6 h-6 flex items-center justify-center rounded-bl-md">
                  <span className="text-white text-xs">
                    {isMultiSelect ? (selectedItems.indexOf(itemName) + 1) : '✓'}
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

MenuSelectionGrid.propTypes = {
  title: PropTypes.string.isRequired,
  items: PropTypes.array.isRequired,
  recommendations: PropTypes.array,
  category: PropTypes.string,
  selectedItems: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.array
  ]),
  onSelect: PropTypes.func.isRequired,
  maxFreeSelections: PropTypes.number,
  premiumItems: PropTypes.array,
  premiumPrice: PropTypes.number,
  extraPrice: PropTypes.number
};

export default MenuSelectionGrid;