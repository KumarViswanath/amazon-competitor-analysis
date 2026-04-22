import React from 'react';
import { TrendingUp, Target, Users2, DollarSign, BarChart3, Trophy } from 'lucide-react';

const CompetitorAnalysis = ({ competitors, mainProduct, pricingAnalysis }) => {
  if (!competitors || competitors.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Competitor Data</h3>
        <p className="text-gray-600">Run competitor analysis to see competing products</p>
      </div>
    );
  }

  const formatPrice = (price, currency = 'USD') => {
    if (!price) return 'N/A';
    const symbol = currency === 'USD' ? '$' : currency;
    return `${symbol}${price.toFixed(2)}`;
  };

  const getPriceColor = (competitorPrice, mainPrice) => {
    if (!competitorPrice || !mainPrice) return 'text-gray-600';
    if (competitorPrice < mainPrice) return 'text-green-600';
    if (competitorPrice > mainPrice) return 'text-red-600';
    return 'text-gray-600';
  };

  const getRatingColor = (rating) => {
    if (!rating) return 'text-gray-600';
    if (rating >= 4.5) return 'text-green-600';
    if (rating >= 4.0) return 'text-yellow-600';
    if (rating >= 3.5) return 'text-orange-600';
    return 'text-red-600';
  };

  // Sort competitors by price for better insights
  const sortedCompetitors = [...competitors].sort((a, b) => {
    if (!a.price) return 1;
    if (!b.price) return -1;
    return a.price - b.price;
  });

  const mainProductPrice = mainProduct?.price || 0;
  const cheaperCompetitors = competitors.filter(c => c.price && c.price < mainProductPrice);
  const expensiveCompetitors = competitors.filter(c => c.price && c.price > mainProductPrice);

  return (
    <div className="space-y-6">
      {/* Analysis Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Users2 className="w-8 h-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">{competitors.length}</p>
              <p className="text-sm text-gray-600">Competitors Found</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <TrendingUp className="w-8 h-8 text-green-600" />
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">{cheaperCompetitors.length}</p>
              <p className="text-sm text-gray-600">Cheaper Options</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <DollarSign className="w-8 h-8 text-red-600" />
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">{expensiveCompetitors.length}</p>
              <p className="text-sm text-gray-600">Premium Options</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <BarChart3 className="w-8 h-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">
                {pricingAnalysis?.price_analysis ? 
                  `$${pricingAnalysis.price_analysis.avg_price?.toFixed(2) || 'N/A'}` : 
                  'N/A'
                }
              </p>
              <p className="text-sm text-gray-600">Avg. Price</p>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Analysis Summary */}
      {pricingAnalysis && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2 text-purple-600" />
            Price Analysis Summary
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Price Range</p>
              <p className="text-lg font-semibold text-gray-900">
                {formatPrice(pricingAnalysis.price_analysis?.min_price)} - {formatPrice(pricingAnalysis.price_analysis?.max_price)}
              </p>
            </div>
            
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Your Position</p>
              <p className="text-lg font-semibold text-blue-600">
                {pricingAnalysis.position?.percentile ? 
                  `${pricingAnalysis.position.percentile.toFixed(0)}th percentile` : 
                  'N/A'
                }
              </p>
            </div>
            
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Market Position</p>
              <div className="flex items-center justify-center space-x-2">
                {mainProductPrice <= (pricingAnalysis.price_analysis?.avg_price || 0) ? (
                  <>
                    <Trophy className="w-4 h-4 text-green-600" />
                    <span className="text-sm font-medium text-green-600">Competitive</span>
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-4 h-4 text-orange-600" />
                    <span className="text-sm font-medium text-orange-600">Premium</span>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Competitors Table */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Target className="w-5 h-5 mr-2 text-blue-600" />
            Competitor Analysis ({competitors.length} products)
          </h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Brand
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rating
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Reviews
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  vs. Main Product
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedCompetitors.map((competitor, index) => (
                <tr key={competitor.asin || index} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-12 w-12">
                        {competitor.images && competitor.images.length > 0 ? (
                          <img
                            className="h-12 w-12 rounded object-cover"
                            src={competitor.images[0]}
                            alt={competitor.title}
                            onError={(e) => {
                              e.target.style.display = 'none';
                            }}
                          />
                        ) : (
                          <div className="h-12 w-12 bg-gray-200 rounded flex items-center justify-center">
                            <Target className="w-6 h-6 text-gray-400" />
                          </div>
                        )}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900 line-clamp-2 max-w-xs">
                          {competitor.title || 'Untitled Product'}
                        </div>
                        <div className="text-xs text-gray-500">
                          ASIN: {competitor.asin}
                        </div>
                      </div>
                    </div>
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900">
                      {competitor.brand || 'Unknown'}
                    </span>
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-sm font-medium ${getPriceColor(competitor.price, mainProductPrice)}`}>
                      {formatPrice(competitor.price, competitor.currency)}
                    </span>
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className={`text-sm font-medium ${getRatingColor(competitor.rating)}`}>
                        {competitor.rating ? competitor.rating.toFixed(1) : 'N/A'}
                      </span>
                      {competitor.rating && (
                        <div className="ml-2 flex">
                          {[...Array(5)].map((_, i) => (
                            <svg
                              key={i}
                              className={`w-3 h-3 ${
                                i < Math.floor(competitor.rating)
                                  ? 'text-yellow-400'
                                  : 'text-gray-300'
                              }`}
                              fill="currentColor"
                              viewBox="0 0 20 20"
                            >
                              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                            </svg>
                          ))}
                        </div>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {competitor.review_count ? 
                      (competitor.review_count >= 1000 ? 
                        `${(competitor.review_count / 1000).toFixed(1)}K` : 
                        competitor.review_count
                      ) : 'No reviews'}
                  </td>
                  
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex flex-col space-y-1">
                      {competitor.price && mainProductPrice ? (
                        <span className={`text-xs font-medium ${
                          competitor.price < mainProductPrice ? 'text-green-600' : 
                          competitor.price > mainProductPrice ? 'text-red-600' : 'text-gray-600'
                        }`}>
                          {competitor.price < mainProductPrice ? 
                            `$${(mainProductPrice - competitor.price).toFixed(2)} cheaper` :
                            competitor.price > mainProductPrice ?
                            `$${(competitor.price - mainProductPrice).toFixed(2)} more` :
                            'Same price'
                          }
                        </span>
                      ) : null}
                      
                      {competitor.rating && mainProduct?.rating ? (
                        <span className={`text-xs ${
                          competitor.rating > mainProduct.rating ? 'text-green-600' : 
                          competitor.rating < mainProduct.rating ? 'text-red-600' : 'text-gray-600'
                        }`}>
                          {competitor.rating > mainProduct.rating ? 
                            `+${(competitor.rating - mainProduct.rating).toFixed(1)} rating` :
                            competitor.rating < mainProduct.rating ?
                            `${(competitor.rating - mainProduct.rating).toFixed(1)} rating` :
                            'Same rating'
                          }
                        </span>
                      ) : null}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default CompetitorAnalysis;