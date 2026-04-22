import React, { useState } from 'react';
import { Star, ExternalLink, DollarSign, Users, Package, Image as ImageIcon } from 'lucide-react';

const ProductCard = ({ product, isMainProduct = false }) => {
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);

  const handleImageLoad = () => {
    setImageLoading(false);
  };

  const handleImageError = () => {
    setImageError(true);
    setImageLoading(false);
  };

  const formatPrice = (price, currency = 'USD') => {
    if (!price) return 'N/A';
    const symbol = currency === 'USD' ? '$' : currency;
    return `${symbol}${price.toFixed(2)}`;
  };

  const formatRating = (rating) => {
    if (!rating) return 'No rating';
    return rating.toFixed(1);
  };

  const formatReviewCount = (count) => {
    if (!count) return 'No reviews';
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K reviews`;
    }
    return `${count} reviews`;
  };

  const mainImage = product.images && product.images.length > 0 ? product.images[0] : null;

  return (
    <div className={`bg-white rounded-lg shadow-lg overflow-hidden transition-all duration-300 hover:shadow-xl ${
      isMainProduct ? 'ring-2 ring-amazon-500 ring-opacity-50' : ''
    }`}>
      {/* Product Badge */}
      {isMainProduct && (
        <div className="bg-amazon-500 text-white px-4 py-2 text-sm font-medium">
          Main Product
        </div>
      )}

      <div className="p-6">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Product Image */}
          <div className="flex-shrink-0">
            <div className="w-full lg:w-48 h-48 bg-gray-100 rounded-lg overflow-hidden relative">
              {imageLoading && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amazon-500"></div>
                </div>
              )}
              
              {mainImage && !imageError ? (
                <img
                  src={mainImage}
                  alt={product.title || 'Product image'}
                  className={`w-full h-full object-contain transition-opacity duration-300 ${
                    imageLoading ? 'opacity-0' : 'opacity-100'
                  }`}
                  onLoad={handleImageLoad}
                  onError={handleImageError}
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-50">
                  <ImageIcon className="w-12 h-12 text-gray-400" />
                </div>
              )}
            </div>
            
            {/* Additional Images Indicator */}
            {product.images && product.images.length > 1 && (
              <p className="text-xs text-gray-500 mt-2 text-center">
                +{product.images.length - 1} more images
              </p>
            )}
          </div>

          {/* Product Details */}
          <div className="flex-1 min-w-0">
            {/* Title */}
            <h3 className="text-lg font-semibold text-gray-900 mb-3 line-clamp-3 leading-tight">
              {product.title || 'Product title not available'}
            </h3>

            {/* Brand */}
            {product.brand && (
              <div className="flex items-center mb-3">
                <Package className="w-4 h-4 text-gray-400 mr-2" />
                <span className="text-sm text-gray-600">Brand: {product.brand}</span>
              </div>
            )}

            {/* Price and Rating Row */}
            <div className="flex flex-wrap items-center gap-4 mb-4">
              {/* Price */}
              <div className="flex items-center">
                <DollarSign className="w-5 h-5 text-green-600 mr-1" />
                <span className="text-xl font-bold text-green-600">
                  {formatPrice(product.price, product.currency)}
                </span>
              </div>

              {/* Rating */}
              {product.rating && (
                <div className="flex items-center">
                  <div className="flex items-center mr-2">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-4 h-4 ${
                          i < Math.floor(product.rating)
                            ? 'text-yellow-400 fill-current'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-sm text-gray-600">
                    {formatRating(product.rating)}
                  </span>
                </div>
              )}

              {/* Review Count */}
              {product.review_count && (
                <div className="flex items-center">
                  <Users className="w-4 h-4 text-gray-400 mr-1" />
                  <span className="text-sm text-gray-600">
                    {formatReviewCount(product.review_count)}
                  </span>
                </div>
              )}
            </div>

            {/* Stock Status */}
            {product.stock && (
              <div className="mb-4">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  product.stock.toLowerCase().includes('in stock')
                    ? 'bg-green-100 text-green-800'
                    : product.stock.toLowerCase().includes('out')
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {product.stock}
                </span>
              </div>
            )}

            {/* Description */}
            {product.description && (
              <div className="mb-4">
                <p className="text-sm text-gray-600 line-clamp-2">
                  {product.description}
                </p>
              </div>
            )}

            {/* Categories */}
            {product.categories && product.categories.length > 0 && (
              <div className="mb-4">
                <div className="flex flex-wrap gap-1">
                  {product.categories.slice(0, 3).map((category, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800"
                    >
                      {category}
                    </span>
                  ))}
                  {product.categories.length > 3 && (
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
                      +{product.categories.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Features */}
            {product.features && product.features.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Key Features:</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  {product.features.slice(0, 3).map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <span className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                      <span className="line-clamp-1">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
              <div className="flex items-center text-xs text-gray-500">
                <span>ASIN: {product.asin || 'N/A'}</span>
              </div>
              
              {product.url && (
                <a
                  href={product.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-3 py-1.5 border border-amazon-300 text-sm font-medium rounded text-amazon-700 bg-amazon-50 hover:bg-amazon-100 transition-colors"
                >
                  <ExternalLink className="w-3 h-3 mr-1" />
                  View on Amazon
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;