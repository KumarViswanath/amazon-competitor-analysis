import React, { useState } from 'react';
import { Search, Package, Zap } from 'lucide-react';
import toast from 'react-hot-toast';

const ProductInputForm = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    identifier: '',
    identifier_type: 'asin',
    zip_code: '10001',
    domain: 'com'
  });

  const [errors, setErrors] = useState({});

  // Domain-specific postal code examples and validation
  const postalCodeConfig = {
    'com': { example: '10001', label: 'ZIP Code', pattern: /^\d{5}(-\d{4})?$/, errorMsg: 'Please enter a valid US ZIP code (e.g., 10001)' },
    'in': { example: '110001', label: 'PIN Code', pattern: /^\d{6}$/, errorMsg: 'Please enter a valid 6-digit Indian PIN code (e.g., 110001)' },
    'co.uk': { example: 'SW1A 1AA', label: 'Postcode', pattern: /^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$/i, errorMsg: 'Please enter a valid UK postcode (e.g., SW1A 1AA)' },
    'de': { example: '10115', label: 'Postleitzahl', pattern: /^\d{5}$/, errorMsg: 'Please enter a valid 5-digit German postal code (e.g., 10115)' },
    'fr': { example: '75001', label: 'Code Postal', pattern: /^\d{5}$/, errorMsg: 'Please enter a valid 5-digit French postal code (e.g., 75001)' },
    'it': { example: '00118', label: 'Codice Postale', pattern: /^\d{5}$/, errorMsg: 'Please enter a valid 5-digit Italian postal code (e.g., 00118)' },
    'es': { example: '28001', label: 'Código Postal', pattern: /^\d{5}$/, errorMsg: 'Please enter a valid 5-digit Spanish postal code (e.g., 28001)' }
  };

  const getCurrentPostalConfig = () => postalCodeConfig[formData.domain] || postalCodeConfig['com'];

  const validateForm = () => {
    const newErrors = {};
    const postalConfig = getCurrentPostalConfig();
    
    if (!formData.identifier.trim()) {
      newErrors.identifier = 'Please enter a product identifier';
    }
    
    if (!formData.zip_code.trim()) {
      newErrors.zip_code = `Please enter a ${postalConfig.label.toLowerCase()}`;
    } else if (!postalConfig.pattern.test(formData.zip_code.trim())) {
      newErrors.zip_code = postalConfig.errorMsg;
    }

    // ASIN validation
    if (formData.identifier_type === 'asin' && formData.identifier.trim()) {
      const asinRegex = /^[A-Z0-9]{10}$/;
      if (!asinRegex.test(formData.identifier.trim().toUpperCase())) {
        newErrors.identifier = 'ASIN must be 10 characters (letters and numbers)';
      }
    }

    // URL validation
    if (formData.identifier_type === 'url' && formData.identifier.trim()) {
      try {
        const url = new URL(formData.identifier);
        if (!url.hostname.includes('amazon')) {
          newErrors.identifier = 'Please enter a valid Amazon URL';
        }
      } catch {
        newErrors.identifier = 'Please enter a valid URL';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      const submitData = {
        ...formData,
        identifier: formData.identifier.trim()
      };
      onSubmit(submitData);
    } else {
      toast.error('Please fix the form errors');
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => {
      const newData = { ...prev, [field]: value };
      
      // Auto-update postal code when domain changes
      if (field === 'domain') {
        const newPostalConfig = postalCodeConfig[value] || postalCodeConfig['com'];
        newData.zip_code = newPostalConfig.example;
      }
      
      return newData;
    });
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const getPlaceholder = () => {
    switch (formData.identifier_type) {
      case 'asin':
        return 'e.g., B08N5WRWNW';
      case 'url':
        return 'e.g., https://amazon.com/dp/B08N5WRWNW';
      case 'name':
        return 'e.g., Echo Dot Smart Speaker';
      default:
        return 'Enter product identifier';
    }
  };

  const getInputIcon = () => {
    switch (formData.identifier_type) {
      case 'asin':
        return <Package className="w-5 h-5 text-gray-400" />;
      case 'url':
        return <Search className="w-5 h-5 text-gray-400" />;
      case 'name':
        return <Zap className="w-5 h-5 text-gray-400" />;
      default:
        return <Search className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Product Information</h2>
        <p className="text-gray-600">Enter product details to start your competitive analysis</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Identifier Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Product Identifier Type
          </label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {[
              { value: 'asin', label: 'ASIN', desc: '10-character Amazon ID' },
              { value: 'url', label: 'Product URL', desc: 'Full Amazon product link' },
              { value: 'name', label: 'Product Name', desc: 'Search by product title' }
            ].map((option) => (
              <label
                key={option.value}
                className={`relative flex cursor-pointer rounded-lg border p-4 transition-all duration-200 ${
                  formData.identifier_type === option.value
                    ? 'border-amazon-500 bg-amazon-50 ring-2 ring-amazon-500'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <input
                  type="radio"
                  name="identifier_type"
                  value={option.value}
                  checked={formData.identifier_type === option.value}
                  onChange={(e) => handleInputChange('identifier_type', e.target.value)}
                  className="sr-only"
                />
                <div className="flex flex-col">
                  <span className="block text-sm font-medium text-gray-900">
                    {option.label}
                  </span>
                  <span className="mt-1 text-xs text-gray-500">
                    {option.desc}
                  </span>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Product Identifier Input */}
        <div>
          <label htmlFor="identifier" className="block text-sm font-medium text-gray-700 mb-2">
            Product {formData.identifier_type.toUpperCase()}
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              {getInputIcon()}
            </div>
            <input
              id="identifier"
              type="text"
              value={formData.identifier}
              onChange={(e) => handleInputChange('identifier', e.target.value)}
              placeholder={getPlaceholder()}
              className={`block w-full pl-10 pr-4 py-3 border rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amazon-500 focus:border-amazon-500 transition-colors ${
                errors.identifier ? 'border-red-300 bg-red-50' : 'border-gray-300'
              }`}
            />
          </div>
          {errors.identifier && (
            <p className="mt-2 text-sm text-red-600">{errors.identifier}</p>
          )}
        </div>

        {/* Location and Domain Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Postal Code */}
          <div>
            <label htmlFor="zip_code" className="block text-sm font-medium text-gray-700 mb-2">
              {getCurrentPostalConfig().label}
            </label>
            <input
              id="zip_code"
              type="text"
              value={formData.zip_code}
              onChange={(e) => handleInputChange('zip_code', e.target.value)}
              placeholder={getCurrentPostalConfig().example}
              className={`block w-full px-4 py-3 border rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amazon-500 focus:border-amazon-500 transition-colors ${
                errors.zip_code ? 'border-red-300 bg-red-50' : 'border-gray-300'
              }`}
            />
            {errors.zip_code && (
              <p className="mt-2 text-sm text-red-600">{errors.zip_code}</p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              Example for {formData.domain === 'com' ? 'US' : 
                         formData.domain === 'in' ? 'India' : 
                         formData.domain === 'co.uk' ? 'UK' : 
                         formData.domain === 'de' ? 'Germany' : 
                         formData.domain === 'fr' ? 'France' : 
                         formData.domain === 'it' ? 'Italy' : 'Spain'}: {getCurrentPostalConfig().example}
            </p>
          </div>

          {/* Amazon Domain */}
          <div>
            <label htmlFor="domain" className="block text-sm font-medium text-gray-700 mb-2">
              Amazon Domain
            </label>
            <select
              id="domain"
              value={formData.domain}
              onChange={(e) => handleInputChange('domain', e.target.value)}
              className="block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-amazon-500 focus:border-amazon-500 transition-colors"
            >
              <option value="com">amazon.com (US)</option>
              <option value="in">amazon.in (India)</option>
              <option value="co.uk">amazon.co.uk (UK)</option>
              <option value="de">amazon.de (Germany)</option>
              <option value="fr">amazon.fr (France)</option>
              <option value="it">amazon.it (Italy)</option>
              <option value="es">amazon.es (Spain)</option>
            </select>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className={`w-full flex justify-center items-center px-6 py-4 border border-transparent rounded-lg text-base font-medium text-white transition-all duration-200 ${
            loading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'gradient-amazon hover:shadow-lg transform hover:scale-105 active:scale-95'
          }`}
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Scraping Product...
            </>
          ) : (
            <>
              <Search className="w-5 h-5 mr-2" />
              Scrape Product Details
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default ProductInputForm;