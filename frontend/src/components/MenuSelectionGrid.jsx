import React from 'react';

/**
 * Grid component for menu item selection with recommendation highlighting.
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
      onSelect(item);
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
          const isSelected = isMultiSelect
            ? selectedItems.includes(item)
            : selectedItems === item;
          const isRecommended = recommendations.includes(item);
          const pricing = getPricingInfo(item);

          return (
            <div
              key={item}
              onClick={() => handleItemClick(item)}
              className={`
                relative p-4 rounded-lg border-2 cursor-pointer transition-all
                ${isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}
                ${isRecommended ? 'border-green-500 shadow-md' : ''}
                ${isSelected && isRecommended ? 'border-blue-500 shadow-md border-dashed' : ''}
                hover:border-blue-300
              `}
            >
              <div className="flex justify-between items-center">
                <span className="font-medium">{item}</span>
                {isRecommended && (
                  <span className="text-green-500 ml-2">✓</span>
                )}
              </div>

              {pricing && (
                <div className="text-sm text-gray-600 mt-1">
                  {pricing}
                </div>
              )}

              {isSelected && (
                <div className="absolute top-0 right-0 bg-blue-500 w-6 h-6 flex items-center justify-center rounded-bl-md">
                  <span className="text-white text-xs">
                    {isMultiSelect ? (selectedItems.indexOf(item) + 1) : '✓'}
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

export default MenuSelectionGrid;