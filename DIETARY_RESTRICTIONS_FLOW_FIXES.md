# Dietary Restrictions Flow & Participant Memory Fixes

## ✅ Issues Fixed

### 1. **Dietary Restrictions Step Placement for Trial B**

**Problem**: Dietary restrictions weren't showing right after "Order Now" for Trial B
**Solution**:
- **New Flow for Trial B**: `Order Now` → `Customer Identification` → **`Dietary Restrictions`** → `Activity Selection` → `Protein` → `Base` → etc.
- **Flow for Trial A**: `Order Now` → `Customer Identification` → `Activity Selection` → `Protein` → `Base` → etc.

### 2. **Participant Memory System**

**Problem**: Dietary preferences weren't remembered for returning participants
**Solution**: Implemented comprehensive participant identification and memory system:

#### **Multiple Identification Methods**:
- **Phone Number**: Primary identifier for returning customers
- **Customer ID**: Unique database identifier
- **Face Detection**: Automatic recognition via camera (with simulated detection)
- **Name Matching**: Secondary identification method

#### **Automatic Data Loading**:
- When participant is identified, dietary preferences are automatically loaded
- Preferences populate immediately in the dietary restrictions step
- No need to re-enter dietary information for returning participants

#### **Backend Integration**:
- Uses existing `/api/dietary/profile/{user_id}` endpoint to load preferences
- Uses `/api/dietary/restrictions/set` and `/api/dietary/allergens/set` to save preferences
- Persistent storage in database linked to customer identifier

### 3. **Real-time Preference Saving**

**Features Implemented**:
- **Immediate Save**: Preferences saved to backend as soon as user clicks any dietary option
- **Session Persistence**: Preferences remain active throughout experiment session
- **Cross-trial Memory**: Dietary preferences carry over between Trial A and Trial B
- **Visual Confirmation**: Users see "✅ These preferences will be remembered for future trials" message

### 4. **Enhanced Navigation Flow**

**Updated Navigation**:
- **Trial B Path**: Customer → Dietary → Activity → Protein → Base → Dish Name → etc.
- **Back Button Logic**: Correctly handles the new step sequence
- **Skip Logic**: Trial A bypasses dietary restrictions step entirely

### 5. **Smart Loading System**

**Implementation Details**:
```javascript
// Auto-load when customer identified
const handleCustomerIdentified = async (customerInfo) => {
  // Load dietary preferences for this customer
  if (customerInfo.customerId || customerInfo.phoneNumber) {
    const identifier = customerInfo.customerId || customerInfo.phoneNumber;
    // Fetch from backend and populate UI
    const response = await fetch(`/api/dietary/profile/${identifier}`);
    // Auto-populate dietary restrictions and allergens
  }

  // Route based on trial type
  if (isTrialB) {
    setCurrentStep('dietary'); // Show dietary first for Trial B
  } else {
    setCurrentStep('activity'); // Skip dietary for Trial A
  }
};
```

### 6. **User Experience Improvements**

**Enhanced Features**:
- **Smart Memory Notice**: Clear messaging about preference persistence
- **Visual Feedback**: Green for restrictions, red for allergies
- **Selection Summary**: Shows all selected preferences with colored tags
- **Instant Save**: No "Save" button needed - preferences save automatically
- **Loading State**: Shows when preferences are being loaded for returning customers

## 🔄 **Complete Flow for Trial B (AI-Powered)**

1. **Order Now** button clicked
2. **Customer Identification** (phone, name, face recognition)
3. **Auto-load Dietary Preferences** (if returning customer)
4. **Dietary Restrictions Step** (with mood detection camera)
   - Dietary restrictions: Vegan, Vegetarian, Halal, No Beef, No Pork
   - Food allergies: Dairy, Eggs, Nuts, Gluten, etc.
   - Real-time saving to backend
   - AI mood detection via camera
5. **Activity Selection** (with dietary-aware recommendations)
6. **Protein Selection** (filtered by dietary restrictions)
7. **Base Selection** (filtered by dietary restrictions)
8. **Continue with rest of flow...**

## 🧠 **Memory Persistence**

### **Session Memory** (ExperimentContext):
- Dietary preferences stored in React context
- Persists across component re-renders
- Available throughout experiment session

### **Database Memory** (Backend):
- Linked to customer phone number or ID
- Survives browser refresh and app restarts
- Available for future visits

### **Automatic Recognition**:
- Face detection attempts to identify returning customers
- Phone number lookup for manual identification
- Instant preference loading upon recognition

## 🚀 **Ready for Testing**

The application is now running on Docker with all fixes applied:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Database**: PostgreSQL with persistent dietary profile storage

### **Test Scenarios**:
1. **New Trial B Participant**: Should see dietary restrictions right after customer ID
2. **Returning Participant**: Should auto-load previous dietary preferences
3. **Trial A vs Trial B**: Trial A should skip dietary restrictions completely
4. **Preference Persistence**: Changes should save immediately and persist across trials