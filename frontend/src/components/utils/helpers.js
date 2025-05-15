// frontend/src/utils/helpers.js

/**
 * Format currency with specified locale and options
 * @param {number} amount - Amount to format
 * @param {string} locale - Locale to use for formatting
 * @return {string} Formatted currency string
 */
export function formatCurrency(amount, locale = 'en-US') {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  }

  /**
   * Format phone number to (XXX) XXX-XXXX
   * @param {string} phoneNumber - Phone number to format
   * @return {string} Formatted phone number
   */
  export function formatPhoneNumber(phoneNumber) {
    if (!phoneNumber) return '';

    // Remove all non-digit characters
    const cleaned = phoneNumber.replace(/\D/g, '');

    // Check if the input is of correct length
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);

    if (match) {
      return '(' + match[1] + ') ' + match[2] + '-' + match[3];
    }

    return phoneNumber;
  }

  /**
   * Validate email address
   * @param {string} email - Email to validate
   * @return {boolean} Whether email is valid
   */
  export function isValidEmail(email) {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
  }

  /**
   * Debounce function to limit function calls
   * @param {Function} func - Function to debounce
   * @param {number} wait - Milliseconds to wait
   * @return {Function} Debounced function
   */
  export function debounce(func, wait) {
    let timeout;
    return function(...args) {
      const context = this;
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(context, args), wait);
    };
  }