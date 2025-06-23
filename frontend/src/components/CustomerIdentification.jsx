import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * Enhanced customer identification component with improved camera capture.
 * Added name field and ensures both phone and name are validated and stored.
 */
const CustomerIdentification = ({ onCustomerIdentified, onIdentified, isLoading = false }) => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [imageData, setImageData] = useState(null);
  const [errors, setErrors] = useState({});
  const [isCameraAvailable, setIsCameraAvailable] = useState(true);
  const [localIsLoading, setLocalIsLoading] = useState(isLoading); // Local loading state
  const [showCamera, setShowCamera] = useState(false);
  const [stream, setStream] = useState(null);
  const fileInputRef = useRef(null);
  const phoneInputRef = useRef(null);
  const nameInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // Format phone number with appropriate separators
  const formatPhoneNumber = (value) => {
    if (!value) return value;

    // Remove all non-digit characters
    const phoneNumber = value.replace(/\D/g, '');

    // Format the phone number as needed (US format example)
    if (phoneNumber.length <= 3) {
      return phoneNumber;
    } else if (phoneNumber.length <= 6) {
      return `(${phoneNumber.slice(0, 3)}) ${phoneNumber.slice(3)}`;
    } else {
      return `(${phoneNumber.slice(0, 3)}) ${phoneNumber.slice(3, 6)}-${phoneNumber.slice(6, 10)}`;
    }
  };

  // Handle phone number input with formatting
  const handlePhoneChange = (e) => {
    const formattedNumber = formatPhoneNumber(e.target.value);
    setPhoneNumber(formattedNumber);

    // Clear error when user is typing
    if (errors.phoneNumber) {
      setErrors({...errors, phoneNumber: null});
    }
  };

  // Handle name input
  const handleNameChange = (e) => {
    setCustomerName(e.target.value);

    // Clear error when user is typing
    if (errors.customerName) {
      setErrors({...errors, customerName: null});
    }
  };

  // Check if camera is available when component mounts
  useEffect(() => {
    // Check if navigator.mediaDevices is supported
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then(() => setIsCameraAvailable(true))
        .catch(() => setIsCameraAvailable(false));
    } else {
      setIsCameraAvailable(false);
    }

    // Focus on phone input when component mounts
    if (phoneInputRef.current) {
      phoneInputRef.current.focus();
    }
  }, []);

  // Start camera stream
  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'user', // Use front camera
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });
      setStream(mediaStream);
      setShowCamera(true);

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      setIsCameraAvailable(false);
      setErrors({...errors, image: 'Unable to access camera. Please use file upload instead.'});
    }
  };

  // Stop camera stream
  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setShowCamera(false);
  };

  // Capture photo from camera
  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      // Wait for video to be ready
      if (video.readyState < 2) {
        console.log('Video not ready, waiting...');
        setTimeout(capturePhoto, 100);
        return;
      }

      // Set canvas size to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      console.log('Capturing photo:', canvas.width, 'x', canvas.height);

      // Draw video frame to canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert to data URL
      const imageDataUrl = canvas.toDataURL('image/jpeg', 0.8);
      console.log('Image captured, data URL length:', imageDataUrl.length);

      setImageData(imageDataUrl);

      // Stop camera
      stopCamera();
    } else {
      console.error('Video or canvas ref not available');
    }
  };

  // Handle file input photo capture (fallback)
  const handlePhotoCapture = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type and size
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
      // Clear any image errors
      setErrors({...errors, image: null});
    };
    reader.onerror = () => {
      setErrors({...errors, image: 'Failed to read image file'});
    };
  };

  // Take a new photo - try camera first, fallback to file input
  const handleTakePhoto = () => {
    if (isCameraAvailable) {
      startCamera();
    } else {
      // Fallback to file input
      if (fileInputRef.current) {
        fileInputRef.current.click();
      }
    }
  };

  // Clear the current photo
  const handleClearPhoto = () => {
    setImageData(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    // Clear image errors
    setErrors({...errors, image: null});
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};

    // Check if phone number is provided
    if (!phoneNumber) {
      newErrors.phoneNumber = 'Please enter your phone number';
    } else {
      // Validate phone number format
      const digitsOnly = phoneNumber.replace(/\D/g, '');
      if (digitsOnly.length !== 10) {
        newErrors.phoneNumber = 'Please enter a valid 10-digit phone number';
      }
    }

    // Check if name is provided
    if (!customerName.trim()) {
      newErrors.customerName = 'Please enter your name';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLocalIsLoading(true);

    try {
      // Process the phone number to strip formatting
      const processedPhoneNumber = phoneNumber ? phoneNumber.replace(/\D/g, '') : null;

      // If we have an image, store it for future recognition
      if (imageData) {
        const customerData = {
          name: customerName.trim(),
          phone_number: processedPhoneNumber,
          image_data: imageData
        };

        const response = await fetch('http://localhost:8000/api/store-customer-face', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(customerData)
        });

        const result = await response.json();
        if (result.success) {
          console.log('Face stored for future recognition');
        }
      }

      // Submit to parent component with debugging
      console.log('Debug - onCustomerIdentified type:', typeof onCustomerIdentified);
      console.log('Debug - onIdentified type:', typeof onIdentified);

      const callback = typeof onCustomerIdentified === 'function' ? onCustomerIdentified : (typeof onIdentified === 'function' ? onIdentified : null);
      console.log('Debug - callback type:', typeof callback);

      if (callback) {
        console.log('Debug - calling callback with:', {
          phoneNumber: processedPhoneNumber,
          name: customerName.trim(),
          imageData
        });
        callback({
          phoneNumber: processedPhoneNumber,
          name: customerName.trim(),
          imageData
        });
      } else {
        console.error('No valid customer identification callback provided.');
        console.error('onCustomerIdentified:', onCustomerIdentified);
        console.error('onIdentified:', onIdentified);
      }

    } catch (error) {
      console.error('Error storing customer face:', error);
      // Still proceed with order even if face storage fails
      const processedPhoneNumber = phoneNumber ? phoneNumber.replace(/\D/g, '') : null;

      // Use the same safe callback logic
      const callback = typeof onCustomerIdentified === 'function' ? onCustomerIdentified : (typeof onIdentified === 'function' ? onIdentified : null);
      if (callback) {
        callback({
          phoneNumber: processedPhoneNumber,
          name: customerName.trim(),
          imageData
        });
      } else {
        console.error('No valid customer identification callback provided in catch block.');
      }
    } finally {
      setLocalIsLoading(false);
    }
  };

  // Check if a returning customer based on phone number
  const checkReturningCustomer = async () => {
    // This would typically be an API call to check if this phone number exists in the system
    const digitsOnly = phoneNumber.replace(/\D/g, '');

    if (digitsOnly.length === 10) {
      setLocalIsLoading(true);
      try {
        // API call would go here
        // For now, we'll simulate with a timeout
        setTimeout(() => {
          setLocalIsLoading(false);
          // If customer found, would populate name automatically
          // This is just placeholder logic
          if (Math.random() > 0.7) {
            setCustomerName("John Doe"); // Example returning customer
            nameInputRef.current.focus();
            alert("Welcome back! We've filled in some of your information.");
          }
        }, 1000);
      } catch (err) {
        setLocalIsLoading(false);
        console.error("Error checking customer status:", err);
      }
    }
  };

  // Cleanup camera on unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream]);

  return (
    <div className="max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4 text-center" id="identification-heading">Welcome!</h2>
      <p className="text-gray-600 mb-6 text-center">
        Please identify yourself for a personalized experience
      </p>

      {errors.form && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md" role="alert">
          {errors.form}
        </div>
      )}

      <form onSubmit={handleSubmit} aria-labelledby="identification-heading">
        <div className="mb-4">
          <label htmlFor="phoneNumber" className="block text-gray-700 mb-2">
            Phone Number <span className="text-red-500">*</span>
          </label>
          <div className="flex">
            <input
              type="tel"
              id="phoneNumber"
              ref={phoneInputRef}
              value={phoneNumber}
              onChange={handlePhoneChange}
              onBlur={checkReturningCustomer}
              className={`flex-1 px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.phoneNumber ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="(555) 555-5555"
              aria-invalid={errors.phoneNumber ? 'true' : 'false'}
              aria-describedby={errors.phoneNumber ? 'phone-error' : undefined}
            />
          </div>
          {errors.phoneNumber && (
            <p id="phone-error" className="mt-1 text-red-500 text-sm">
              {errors.phoneNumber}
            </p>
          )}
        </div>

        <div className="mb-4">
          <label htmlFor="customerName" className="block text-gray-700 mb-2">
            Your Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="customerName"
            ref={nameInputRef}
            value={customerName}
            onChange={handleNameChange}
            className={`w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.customerName ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Your name"
            aria-invalid={errors.customerName ? 'true' : 'false'}
            aria-describedby={errors.customerName ? 'name-error' : undefined}
          />
          {errors.customerName && (
            <p id="name-error" className="mt-1 text-red-500 text-sm">
              {errors.customerName}
            </p>
          )}
        </div>

        <div className="mb-6">
          <p className="block text-gray-700 mb-2">Take a Photo (optional)</p>

          {!isCameraAvailable && (
            <p className="mb-2 text-amber-600 text-sm">
              Camera access is not available on your device or browser.
            </p>
          )}

          {/* Hidden file input for fallback */}
          <input
            type="file"
            accept="image/*"
            ref={fileInputRef}
            onChange={handlePhotoCapture}
            className="hidden"
            aria-label="Take photo for identification"
            disabled={!isCameraAvailable}
          />

          {/* Camera interface */}
          {showCamera && (
            <div className="mb-4 p-4 bg-gray-100 rounded-lg">
              <div className="relative">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  className="w-full h-64 object-cover rounded-md"
                />
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2">
                  <button
                    type="button"
                    onClick={capturePhoto}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                  >
                    📸 Capture
                  </button>
                  <button
                    type="button"
                    onClick={stopCamera}
                    className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                  >
                    ❌ Cancel
                  </button>
                </div>
              </div>
              <canvas ref={canvasRef} className="hidden" />
            </div>
          )}

          {errors.image && (
            <p className="mb-2 text-red-500 text-sm" role="alert">
              {errors.image}
            </p>
          )}

          {imageData ? (
            <div className="mb-3">
              <div className="relative">
                <img
                  src={imageData}
                  alt="Captured photo"
                  className="w-full h-40 object-cover rounded-md mb-2 border border-gray-300"
                  onLoad={() => console.log('Image loaded successfully')}
                  onError={(e) => console.error('Image failed to load:', e)}
                />
                <button
                  type="button"
                  onClick={handleClearPhoto}
                  className="absolute top-2 right-2 bg-red-600 text-white p-1 rounded-full hover:bg-red-700"
                  aria-label="Clear photo"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
              <p className="text-sm text-gray-600 mb-2">Photo captured successfully!</p>
              <button
                type="button"
                onClick={handleTakePhoto}
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                Take Another Photo
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={handleTakePhoto}
              className="w-full py-3 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors flex items-center justify-center disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed"
              disabled={!isCameraAvailable}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4 5a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V7a2 2 0 00-2-2h-1.586a1 1 0 01-.707-.293l-1.121-1.121A2 2 0 0011.172 3H8.828a2 2 0 00-1.414.586L6.293 4.707A1 1 0 015.586 5H4zm6 9a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
              </svg>
              Take Photo
            </button>
          )}
        </div>

        <button
          type="submit"
          disabled={localIsLoading || !phoneNumber || !customerName.trim()}
          className={`
            w-full py-2 rounded-md text-white transition-colors flex items-center justify-center
            ${localIsLoading || !phoneNumber || !customerName.trim()
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'}
          `}
          aria-busy={localIsLoading ? 'true' : 'false'}
        >
          {localIsLoading ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </>
          ) : 'Continue'}
        </button>
      </form>
    </div>
  );
};

CustomerIdentification.propTypes = {
  onCustomerIdentified: PropTypes.func,
  onIdentified: PropTypes.func,
  isLoading: PropTypes.bool
};

export default CustomerIdentification;