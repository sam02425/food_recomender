// frontend/src/context/OrderContext.js
import React, { createContext, useContext, useReducer, useCallback } from 'react';

// Initial state
const initialState = {
  orderItems: [],
  currentItem: {
    protein: '',
    sauce: '',
    baseType: '',
    baseOption: '',
    veggies: [],
    dishName: ''
  },
  customer: null,
  totalPrice: 0,
  currentStep: 'start'
};

// Actions
const ADD_ITEM = 'ADD_ITEM';
const UPDATE_CURRENT_ITEM = 'UPDATE_CURRENT_ITEM';
const RESET_CURRENT_ITEM = 'RESET_CURRENT_ITEM';
const SET_CUSTOMER = 'SET_CUSTOMER';
const SET_STEP = 'SET_STEP';
const RESET_ORDER = 'RESET_ORDER';

// Reducer
function orderReducer(state, action) {
  switch (action.type) {
    case ADD_ITEM:
      return {
        ...state,
        orderItems: [...state.orderItems, action.payload],
        totalPrice: state.totalPrice + action.payload.price
      };

    case UPDATE_CURRENT_ITEM:
      return {
        ...state,
        currentItem: {
          ...state.currentItem,
          ...action.payload
        }
      };

    case RESET_CURRENT_ITEM:
      return {
        ...state,
        currentItem: initialState.currentItem
      };

    case SET_CUSTOMER:
      return {
        ...state,
        customer: action.payload
      };

    case SET_STEP:
      return {
        ...state,
        currentStep: action.payload
      };

    case RESET_ORDER:
      return initialState;

    default:
      return state;
  }
}

// Create context
const OrderContext = createContext();

// Provider component
export function OrderProvider({ children }) {
  const [state, dispatch] = useReducer(orderReducer, initialState);

  // Action creators
  const addItem = useCallback((item) => {
    dispatch({ type: ADD_ITEM, payload: item });
  }, []);

  const updateCurrentItem = useCallback((itemData) => {
    dispatch({ type: UPDATE_CURRENT_ITEM, payload: itemData });
  }, []);

  const resetCurrentItem = useCallback(() => {
    dispatch({ type: RESET_CURRENT_ITEM });
  }, []);

  const setCustomer = useCallback((customer) => {
    dispatch({ type: SET_CUSTOMER, payload: customer });
  }, []);

  const setStep = useCallback((step) => {
    dispatch({ type: SET_STEP, payload: step });
  }, []);

  const resetOrder = useCallback(() => {
    dispatch({ type: RESET_ORDER });
  }, []);

  const value = {
    ...state,
    addItem,
    updateCurrentItem,
    resetCurrentItem,
    setCustomer,
    setStep,
    resetOrder
  };

  return <OrderContext.Provider value={value}>{children}</OrderContext.Provider>;
}

// Custom hook to use the context
export function useOrder() {
  const context = useContext(OrderContext);
  if (!context) {
    throw new Error('useOrder must be used within an OrderProvider');
  }
  return context;
}