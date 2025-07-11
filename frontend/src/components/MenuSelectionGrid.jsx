import React, { useState } from 'react';
import PropTypes from 'prop-types';
import './MenuSelectionGrid.css';

const MenuSelectionGrid = ({
  items = [],
  title,
  onSelect,
  selectedItems = [],
  multiSelect = false,
  showCalories = true,
  showPortionSizes = false
}) => {
  const [selectedPortions, setSelectedPortions] = useState({});

  if (!items || items.length === 0) {
    return (
      <div className="menu-selection-grid">
        <h3>{title}</h3>
        <p className="no-items">No items available</p>
      </div>
    );
  }

  const handleItemClick = (item) => {
    if (multiSelect) {
      const isSelected = selectedItems.some(selected => selected.name === item.name);
      if (isSelected) {
        // Remove item from selection
        onSelect(selectedItems.filter(selected => selected.name !== item.name));
      } else {
        // Add item to selection
        onSelect([...selectedItems, item]);
      }
    } else {
      // Single selection - replace current selection
      onSelect([item]);
    }
  };

  const handlePortionSelect = (itemName, portionSize, event) => {
    // Prevent the item click when clicking on portion buttons
    event.stopPropagation();

    setSelectedPortions(prev => ({
      ...prev,
      [itemName]: portionSize
    }));
  };

  const isItemSelected = (item) => {
    return selectedItems.some(selected => selected.name === item.name);
  };

  const getSelectedPortion = (itemName) => {
    return selectedPortions[itemName] || 'medium';
  };

  const getStatusBadge = (item) => {
    if (!item.status || item.status === 'available') return null;

    const statusConfig = {
      'low_stock': { text: 'Low Stock', className: 'status-low-stock' },
      'preparing': { text: `Preparing (${item.wait_time}m)`, className: 'status-preparing' },
      'out_of_stock': { text: 'Out of Stock', className: 'status-out-of-stock' }
    };

    const config = statusConfig[item.status];
    if (!config) return null;

    return (
      <div className={`status-badge ${config.className}`}>
        {config.text}
      </div>
    );
  };

  const getStockIndicator = (item) => {
    if (!item.stock_level && item.stock_level !== 0) return null;

    let stockClass = 'stock-high';
    if (item.stock_level <= 5) {
      stockClass = 'stock-critical';
    } else if (item.stock_level <= 10) {
      stockClass = 'stock-low';
    } else if (item.stock_level <= 20) {
      stockClass = 'stock-medium';
    }

    return (
      <div className={`stock-indicator ${stockClass}`}>
        Stock: {item.stock_level}
      </div>
    );
  };

  const renderPortionSizes = (item) => {
    if (!showPortionSizes || !item.portion_sizes) return null;

    const currentPortion = getSelectedPortion(item.name);
    const portionData = item.portion_sizes[currentPortion];

    return (
      <div className="portion-sizes">
        <div className="portion-selector">
          {Object.entries(item.portion_sizes).map(([size, data]) => (
            <button
              key={size}
              onClick={(e) => handlePortionSelect(item.name, size, e)}
              className={`portion-btn ${currentPortion === size ? 'selected' : ''}`}
            >
              <div className="portion-name">{data.name}</div>
              <div className="portion-price">${data.price}</div>
              <div className="portion-calories">{data.calories} cal</div>
            </button>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="menu-selection-grid">
      <h3>{title}</h3>
      <div className="grid-container">
        {items.map((item, index) => {
          const selected = isItemSelected(item);
          const isDisabled = item.status === 'out_of_stock';

          return (
            <div
              key={index}
              className={`grid-item ${selected ? 'selected' : ''} ${isDisabled ? 'disabled' : ''}`}
              onClick={() => !isDisabled && handleItemClick(item)}
            >
              <div className="item-header">
                <h4>{item.name}</h4>
                {getStatusBadge(item)}
              </div>

              {showPortionSizes && item.portion_sizes ? (
                renderPortionSizes(item)
              ) : (
                <div className="item-details">
                  {item.price !== undefined && (
                    <span className="price">${item.price.toFixed(2)}</span>
                  )}
                  {showCalories && item.calories && (
                    <span className="calories">{item.calories} cal</span>
                  )}
                </div>
              )}

              {getStockIndicator(item)}

              {item.status === 'preparing' && item.wait_time && (
                <div className="wait-time">
                  ⏱️ Ready in {item.wait_time} minutes
                </div>
              )}

              {/* Selected indicator is now handled by CSS pseudo-element */}
            </div>
          );
        })}
      </div>
    </div>
  );
};

MenuSelectionGrid.propTypes = {
  items: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string.isRequired,
    price: PropTypes.number,
    calories: PropTypes.number,
    status: PropTypes.string,
    wait_time: PropTypes.number,
    stock_level: PropTypes.number,
    portion_sizes: PropTypes.object
  })),
  title: PropTypes.string.isRequired,
  onSelect: PropTypes.func.isRequired,
  selectedItems: PropTypes.array,
  multiSelect: PropTypes.bool,
  showCalories: PropTypes.bool,
  showPortionSizes: PropTypes.bool
};

export default MenuSelectionGrid;