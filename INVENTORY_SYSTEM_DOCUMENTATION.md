# Inventory Management System Documentation

## Overview

The Food Recommender system now includes a comprehensive inventory management system that dynamically affects menu availability, preparation times, and user experience. This system creates realistic scenarios where ingredients are unavailable, low in stock, or need preparation time.

## Key Features

### 1. Dynamic Inventory Levels
- **Random Initialization**: Each experiment trial starts with random inventory levels for all ingredients
- **Realistic Stock Levels**: Items have maximum stock limits based on typical restaurant operations
- **Status Categories**:
  - `available`: Normal stock levels
  - `low_stock`: Less than 20% of max stock
  - `preparing`: Items being prepared (with wait times)
  - `out_of_stock`: Zero stock

### 2. Preparation Time Management
- **Item-Specific Prep Times**: Each ingredient has realistic preparation requirements
- **Cutting Requirements**: Some items need cutting (adds complexity)
- **Cooking Requirements**: Some items need cooking (adds time)
- **Dynamic Wait Times**: Real-time calculation of remaining preparation time

### 3. Menu Filtering
- **Out-of-Stock Filtering**: Items with zero stock are automatically hidden from menus
- **Status Indicators**: Visual badges show stock status and wait times
- **Stock Level Display**: Shows current stock levels for transparency

### 4. Queue and Complexity Management
- **Queue Position**: Random queue position (1-50) affects preparation time
- **Complexity Multipliers**: Based on ingredient requirements and stock status
- **Additional Wait Times**: For items currently being prepared

## System Architecture

### Backend Components

#### InventoryItem Class
```python
class InventoryItem:
    def __init__(self, name, max_stock, prep_time_minutes=0,
                 needs_cutting=False, needs_cooking=False):
        self.name = name
        self.max_stock = max_stock
        self.prep_time_minutes = prep_time_minutes
        self.needs_cutting = needs_cutting
        self.needs_cooking = needs_cooking
        self.current_stock = 0
        self.status = "available"
        self.prep_start_time = None
        self.estimated_ready_time = None
```

#### Key Functions

1. **`initialize_inventory()`**: Sets random stock levels and determines status
2. **`get_available_menu_items()`**: Filters menu based on inventory status
3. **`get_wait_time()`**: Calculates remaining preparation time
4. **`calculate_preparation_time()`**: Computes total order preparation time

### Frontend Components

#### MenuSelectionGrid
- Displays inventory status badges
- Shows stock levels and wait times
- Disables out-of-stock items
- Visual feedback for different statuses

#### BaseSelectionGrid
- Handles hierarchical base selection
- Inventory-aware filtering
- Status indicators for each option

#### AgentRecommendations
- Shows inventory-related insights
- Displays unavailable/preparing items
- Additional wait time calculations

## API Endpoints

### Inventory Management
- `POST /api/inventory/initialize` - Initialize inventory for new trial
- `GET /api/inventory/status` - Get current inventory status

### Menu Data
- `GET /api/menu-data` - Get menu filtered by inventory availability

### Agent Recommendations
- `POST /api/agent-recommendations` - Get recommendations with inventory awareness

## Inventory Items Configuration

### Proteins
- **Chicken**: 50 max, 15min prep, needs cutting & cooking
- **Egg**: 100 max, 5min prep, needs cooking
- **Paneer**: 30 max, 0min prep, needs cutting
- **Soya**: 25 max, 10min prep, needs cooking
- **Potato**: 40 max, 8min prep, needs cutting & cooking

### Sauces
- **Curry Special**: 20 max, 12min prep, needs cooking
- **Malai Masala**: 15 max, 8min prep, needs cooking
- **Curry Masala**: 18 max, 10min prep, needs cooking
- **Marinara**: 12 max, 5min prep, needs cooking
- **Yogurt/Raita**: 25 max, 0min prep

### Bases
- **Rice**: 200 max, 20min prep, needs cooking
- **Sourdough**: 30 max, 0min prep
- **Ciabatta**: 25 max, 0min prep
- **White Bread**: 40 max, 0min prep
- **Naan**: 35 max, 8min prep, needs cooking
- **Pitta**: 30 max, 0min prep

### Vegetables
- **Onion**: 60 max, 3min prep, needs cutting
- **Tomato**: 50 max, 2min prep, needs cutting
- **Cucumber**: 40 max, 2min prep, needs cutting
- **Lettuce**: 35 max, 1min prep, needs cutting
- **Carrot**: 45 max, 4min prep, needs cutting

### Garnishes
- **Cilantro**: 30 max, 1min prep, needs cutting
- **Mint**: 25 max, 1min prep, needs cutting
- **Lemon**: 40 max, 0min prep
- **Chili**: 35 max, 0min prep

## Preparation Time Calculation

### Base Formula
```
total_preparation = (base_time * complexity_multiplier * queue_multiplier) + queue_wait + additional_wait_time
```

### Complexity Factors
- **Base time**: 8 minutes
- **Cutting items**: +0.1x multiplier
- **Cooking items**: +0.2x multiplier
- **Low stock items**: +0.2x multiplier
- **Preparing items**: +0.3x multiplier

### Queue Impact
- **Position 1-5**: 1.0x multiplier, 1.5min per position
- **Position 6-15**: 1.2x multiplier, 1.2min per position
- **Position 16-30**: 1.5x multiplier, 1.0min per position
- **Position 31-50**: 2.0x multiplier, 0.8min per position

## Visual Indicators

### Status Badges
- **Low Stock**: Yellow badge with warning icon
- **Preparing**: Blue badge with timer
- **Out of Stock**: Red badge with X icon

### Stock Indicators
- **High Stock**: Green background
- **Medium Stock**: Yellow background
- **Low Stock**: Orange background
- **Critical Stock**: Red background

### Wait Time Display
- Shows remaining preparation time for items being prepared
- Updates in real-time
- Blue background with timer icon

## Experiment Integration

### Trial B Features
- **Automatic Initialization**: Inventory resets for each new trial
- **Realistic Scenarios**: Creates varied availability situations
- **Agent Integration**: Preparation time agent uses inventory data
- **User Experience**: Realistic constraints affect decision-making

### Data Collection
- Inventory status affects user choices
- Preparation time influences satisfaction
- Queue position impacts perceived wait time
- Stock levels affect order complexity

## Benefits for Research

### Realistic Constraints
- Simulates real restaurant operations
- Creates decision-making pressure
- Tests user adaptability to constraints

### Varied Scenarios
- Different inventory states for each trial
- Unpredictable availability patterns
- Realistic preparation time variations

### Enhanced User Experience
- Transparent inventory information
- Real-time status updates
- Clear visual feedback

### Research Value
- Tests user behavior under constraints
- Measures satisfaction with realistic delays
- Evaluates agent effectiveness in dynamic environments

## Usage Examples

### Starting a New Trial
```javascript
// Frontend automatically calls this when Trial B starts
await fetch('/api/inventory/initialize', { method: 'POST' });
```

### Getting Menu Data
```javascript
// Returns only available items with status information
const menuData = await fetch('/api/menu-data').then(r => r.json());
```

### Agent Recommendations
```javascript
// Includes inventory-aware preparation time
const recommendations = await fetch('/api/agent-recommendations', {
  method: 'POST',
  body: JSON.stringify({ order_details: selections })
}).then(r => r.json());
```

## Testing

Use the provided test script to verify system functionality:
```bash
python test_inventory.py
```

This will test:
1. Inventory initialization
2. Status retrieval
3. Menu filtering
4. Agent recommendations with inventory data

## Future Enhancements

### Potential Improvements
- **Real-time Updates**: WebSocket connections for live inventory updates
- **Predictive Analytics**: ML-based inventory forecasting
- **Supplier Integration**: Real supplier data integration
- **Seasonal Variations**: Dynamic inventory based on seasons/events
- **Waste Management**: Track and minimize food waste

### Advanced Features
- **Substitution Suggestions**: Recommend alternatives for out-of-stock items
- **Batch Preparation**: Optimize preparation schedules
- **Inventory Alerts**: Notify when items are running low
- **Historical Analysis**: Track inventory patterns over time

## Conclusion

The inventory management system significantly enhances the realism and research value of the Food Recommender experiment. By introducing dynamic constraints and realistic preparation times, it creates a more authentic restaurant ordering experience while providing valuable data for understanding user behavior under various operational conditions.