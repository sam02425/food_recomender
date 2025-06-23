import React from 'react';

const TrialHeader = ({ experimentConfig }) => {
  if (!experimentConfig) return null;

  const { trialType, trialNumber, orderType, specificOrder, participantId } = experimentConfig;

  const renderOrderInstructions = () => {
    if (orderType === 'custom') {
      return (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">Order Instructions</h3>
          <p className="text-blue-700">
            <strong>Place order as you like</strong> - Choose any items you prefer
          </p>
        </div>
      );
    } else if (orderType === 'specific' && specificOrder) {
      return (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-4">
          <h3 className="text-lg font-semibold text-orange-800 mb-2">Order Instructions</h3>
          <p className="text-orange-700">
            <strong>Place order for:</strong> {specificOrder}
          </p>
          {trialType === 'B' && (
            <p className="text-sm text-orange-600 mt-2">
              Note: You can change this order if you like, but please indicate your choice.
            </p>
          )}
        </div>
      );
    } else if (orderType === 'specific_flexible' && specificOrder) {
      return (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
          <h3 className="text-lg font-semibold text-green-800 mb-2">Order Instructions</h3>
          <p className="text-green-700">
            <strong>Place order as you like OR:</strong> {specificOrder}
          </p>
          <p className="text-sm text-green-600 mt-2">
            You have the choice to either follow the suggested order or create your own.
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="mb-6">
      {/* Trial Information */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 mb-4">
        <div className="flex justify-between items-center">
          <div>
            <span className="text-sm font-medium text-gray-600">
              Participant: {participantId} | Trial {trialNumber} | Type: {trialType}
            </span>
          </div>
          <div>
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              trialType === 'A'
                ? 'bg-red-100 text-red-800'
                : 'bg-blue-100 text-blue-800'
            }`}>
              {trialType === 'A' ? 'Baseline (No Suggestions)' : 'With Suggestions'}
            </span>
          </div>
        </div>
      </div>

      {/* Order Instructions */}
      {renderOrderInstructions()}
    </div>
  );
};

export default TrialHeader;