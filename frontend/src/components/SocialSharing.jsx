// frontend/src/components/SocialSharing.jsx
import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * Production-level component for social media sharing with
 * photo capture, platform selection, and caption editing.
 */
const SocialSharing = ({
  dishName,
  customerName,
  onShare,
  onSkip,
  isLoading = false
}) => {
  const [imageData, setImageData] = useState(null);
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [caption, setCaption] = useState('');
  const [captionLength, setCaptionLength] = useState(0);
  const [step, setStep] = useState(1); // 1: photo, 2: platforms, 3: caption
  const [errors, setErrors] = useState({});
  const fileInputRef = useRef(null);
  const captionRef = useRef(null);

  // Platform data
  const platforms = [
    {
      id: 'facebook',
      name: 'Facebook',
      icon: 'fb',
      maxLength: 250,
      color: 'bg-blue-600',
      hoverColor: 'hover:bg-blue-700'
    },
    {
      id: 'instagram',
      name: 'Instagram',
      icon: 'ig',
      maxLength: 200,
      color: 'bg-purple-600',
      hoverColor: 'hover:bg-purple-700'
    },
    {
      id: 'tiktok',
      name: 'TikTok',
      icon: 'tt',
      maxLength: 150,
      color: 'bg-black',
      hoverColor: 'hover:bg-gray-800'
    }
  ];

  // Generate default caption
  useEffect(() => {
    if (!caption && dishName) {
      const safeCustomerName = customerName || 'Chef';
      const defaultCaption = `Just enjoyed my delicious ${dishName} at Curry Creations! 😋 #FoodLover #CurryCreations #${safeCustomerName.replace(/\s+/g, '')}sMasterpiece`;
      setCaption(defaultCaption);
      setCaptionLength(defaultCaption.length);
    }
  }, [caption, dishName, customerName]);

  // Update caption length
  useEffect(() => {
    setCaptionLength(caption.length);
  }, [caption]);

  // Focus caption textarea when step changes to 3
  useEffect(() => {
    if (step === 3 && captionRef.current) {
      captionRef.current.focus();
    }
  }, [step]);

  // Handle photo capture
  const handlePhotoCapture = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    const maxSize = 5 * 1024 * 1024; // 5MB

    if (!validTypes.includes(file.type)) {
      setErrors({...errors, image: 'Please select a JPEG or PNG image'});
      return;
    }

    if (file.size > maxSize) {
      setErrors({...errors, image: 'Image size should be less than 5MB'});
      return;
    }

    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      setImageData(reader.result);
      setErrors({...errors, image: null});
      setStep(2); // Move to platform selection
    };
    reader.onerror = () => {
      setErrors({...errors, image: 'Failed to read image file'});
    };
  };

  // Take a new photo
  const handleTakePhoto = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Toggle platform selection
  const togglePlatform = (platformId) => {
    setSelectedPlatforms(prev => {
      if (prev.includes(platformId)) {
        return prev.filter(id => id !== platformId);
      } else {
        return [...prev, platformId];
      }
    });
  };

  // Move to caption step
  const goToCaptionStep = () => {
    if (selectedPlatforms.length === 0) {
      setErrors({...errors, platforms: 'Please select at least one platform'});
      return;
    }

    setErrors({...errors, platforms: null});
    setStep(3);
  };

  // Get the maximum caption length
  const getMaxCaptionLength = () => {
    if (!selectedPlatforms.length) return 250;

    return Math.min(
      ...selectedPlatforms.map(id => {
        const platform = platforms.find(p => p.id === id);
        return platform ? platform.maxLength : 250;
      })
    );
  };

  // Handle caption change
  const handleCaptionChange = (e) => {
    const newCaption = e.target.value;
    const maxLength = getMaxCaptionLength();

    if (newCaption.length <= maxLength) {
      setCaption(newCaption);
      setErrors({...errors, caption: null});
    } else {
      setErrors({
        ...errors,
        caption: `Caption exceeds maximum length for ${selectedPlatforms.join(', ')}`
      });
    }
  };

  // Handle share submission
  const handleSubmit = () => {
    // Validate
    if (!imageData) {
      setErrors({...errors, image: 'Please take a photo'});
      setStep(1);
      return;
    }

    if (selectedPlatforms.length === 0) {
      setErrors({...errors, platforms: 'Please select at least one platform'});
      setStep(2);
      return;
    }

    if (!caption.trim()) {
      setErrors({...errors, caption: 'Please enter a caption'});
      setStep(3);
      return;
    }

    // Clear errors
    setErrors({});

    onShare({
      imageData,
      platforms: selectedPlatforms,
      caption
    });
  };

  // Render the correct step
  const renderStep = () => {
    switch (step) {
      case 1: // Photo capture
        return (
          <div className="mb-6 animate-fadeIn">
            <h3 className="text-lg font-medium mb-3">Take a Photo</h3>

            <input
              type="file"
              accept="image/*"
              capture="user"
              ref={fileInputRef}
              onChange={handlePhotoCapture}
              className="hidden"
              aria-label="Take photo of your dish"
            />

            {errors.image && (
              <div className="mb-3 p-2 bg-red-100 text-red-700 rounded-md text-sm" role="alert">
                {errors.image}
              </div>
            )}

            {imageData ? (
              <div className="mb-3">
                <div className="relative">
                  <img
                    src={imageData}
                    alt="Your dish"
                    className="w-full max-h-64 object-cover rounded-md mb-2 shadow-md"
                  />
                  <button
                    type="button"
                    onClick={handleTakePhoto}
                    className="absolute bottom-2 right-2 bg-white p-2 rounded-full shadow-md text-blue-600 hover:text-blue-800 transition-colors"
                    aria-label="Take another photo"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
                <div className="flex justify-between">
                  <button
                    type="button"
                    onClick={handleTakePhoto}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Take Another Photo
                  </button>
                  <button
                    type="button"
                    onClick={() => setStep(2)}
                    className="text-green-600 hover:text-green-800 text-sm font-medium"
                  >
                    Continue to Platforms →
                  </button>
                </div>
              </div>
            ) : (
              <button
                type="button"
                onClick={handleTakePhoto}
                className="w-full py-10 bg-gray-100 hover:bg-gray-200 rounded-md border-2 border-dashed border-gray-300 transition-colors flex flex-col items-center justify-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-gray-500 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span className="text-gray-600">Tap to take a photo</span>
                <span className="text-xs text-gray-500 mt-1">Show your delicious creation!</span>
              </button>
            )}
          </div>
        );

      case 2: // Platform selection
        return (
          <div className="mb-6 animate-fadeIn">
            <h3 className="text-lg font-medium mb-3">Select Platforms</h3>

            {errors.platforms && (
              <div className="mb-3 p-2 bg-red-100 text-red-700 rounded-md text-sm" role="alert">
                {errors.platforms}
              </div>
            )}

            <div className="flex flex-col gap-2">
              {platforms.map((platform) => (
                <button
                  key={platform.id}
                  type="button"
                  onClick={() => togglePlatform(platform.id)}
                  className={`
                    px-4 py-3 rounded-lg transition-all flex items-center justify-between
                    ${selectedPlatforms.includes(platform.id)
                      ? `${platform.color} text-white`
                      : 'bg-white text-gray-700 border border-gray-300 hover:border-gray-400'}
                  `}
                  aria-pressed={selectedPlatforms.includes(platform.id)}
                >
                  <div className="flex items-center">
                    <span className="mr-2 text-xl">
                      {platform.icon === 'fb' ? 'ⓕ' : platform.icon === 'ig' ? 'ⓘ' : 'ⓣ'}
                    </span>
                    <span className="font-medium">{platform.name}</span>
                  </div>

                  {selectedPlatforms.includes(platform.id) && (
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
              ))}
            </div>

            <div className="flex justify-between mt-4">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                ← Back to Photo
              </button>
              <button
                type="button"
                onClick={goToCaptionStep}
                disabled={selectedPlatforms.length === 0}
                className={`
                  text-sm font-medium
                  ${selectedPlatforms.length === 0
                    ? 'text-gray-400 cursor-not-allowed'
                    : 'text-green-600 hover:text-green-800'}
                `}
              >
                Continue to Caption →
              </button>
            </div>
          </div>
        );

      case 3: // Caption
        const maxCaption = getMaxCaptionLength();
        return (
          <div className="mb-6 animate-fadeIn">
            <h3 className="text-lg font-medium mb-3">Add Caption</h3>

            {errors.caption && (
              <div className="mb-3 p-2 bg-red-100 text-red-700 rounded-md text-sm" role="alert">
                {errors.caption}
              </div>
            )}

            <div className="mb-2">
              <textarea
                ref={captionRef}
                value={caption}
                onChange={handleCaptionChange}
                placeholder="Write a caption for your post..."
                className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[120px]"
                maxLength={maxCaption}
                aria-label="Social media caption"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>
                  Sharing to: {selectedPlatforms.map(id => {
                    const platform = platforms.find(p => p.id === id);
                    return platform ? platform.name : id;
                  }).join(', ')}
                </span>
                <span className={captionLength > maxCaption * 0.9 ? 'text-amber-600' : ''}>
                  {captionLength}/{maxCaption} characters
                </span>
              </div>
            </div>

            <div className="flex justify-between mt-4">
              <button
                type="button"
                onClick={() => setStep(2)}
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                ← Back to Platforms
              </button>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={!caption.trim()}
                className={`
                  text-sm font-medium
                  ${!caption.trim()
                    ? 'text-gray-400 cursor-not-allowed'
                    : 'text-green-600 hover:text-green-800'}
                `}
              >
                Ready to Share →
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="w-full">
      <h2 className="text-2xl font-bold mb-2">Share Your Masterpiece!</h2>
      <p className="text-gray-600 mb-6">
        Take a photo with your delicious creation and share it on social media
      </p>

      {/* Step indicators */}
      <div className="flex items-center mb-6">
        <div className={`flex-1 h-2 ${step >= 1 ? 'bg-blue-500' : 'bg-gray-200'} rounded-l-full`}></div>
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center ${
            step >= 1 ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-600'
          } text-sm font-medium`}
        >
          1
        </div>
        <div className={`flex-1 h-2 ${step >= 2 ? 'bg-blue-500' : 'bg-gray-200'}`}></div>
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center ${
            step >= 2 ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-600'
          } text-sm font-medium`}
        >
          2
        </div>
        <div className={`flex-1 h-2 ${step >= 3 ? 'bg-blue-500' : 'bg-gray-200'}`}></div>
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center ${
            step >= 3 ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-600'
          } text-sm font-medium`}
        >
          3
        </div>
        <div className={`flex-1 h-2 ${step > 3 ? 'bg-blue-500' : 'bg-gray-200'} rounded-r-full`}></div>
      </div>

      {/* Current step content */}
      {renderStep()}

      {/* Action buttons */}
      <div className="flex gap-3">
        <button
          type="button"
          onClick={onSkip}
          className="flex-1 py-2 px-4 bg-gray-200 hover:bg-gray-300 rounded-md text-gray-800 transition-colors"
        >
          Skip Sharing
        </button>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={!imageData || selectedPlatforms.length === 0 || !caption.trim() || isLoading}
          className={`
            flex-1 py-2 px-4 rounded-md text-white transition-colors flex items-center justify-center
            ${(!imageData || selectedPlatforms.length === 0 || !caption.trim() || isLoading)
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'}
          `}
          aria-busy={isLoading ? 'true' : 'false'}
        >
          {isLoading ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Sharing...
            </>
          ) : 'Share Now'}
        </button>
      </div>
    </div>
  );
};

SocialSharing.propTypes = {
  dishName: PropTypes.string.isRequired,
  customerName: PropTypes.string.isRequired,
  onShare: PropTypes.func.isRequired,
  onSkip: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default SocialSharing;