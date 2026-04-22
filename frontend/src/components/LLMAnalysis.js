import React from 'react';
import { Brain, TrendingUp, Target, Lightbulb, DollarSign, Award } from 'lucide-react';

const LLMAnalysis = ({ analysis, loading }) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amazon-500 mr-3"></div>
          <span className="text-lg font-medium text-gray-900">Analyzing with AI...</span>
        </div>
        <p className="text-gray-600 text-center mt-2">
          Our AI is processing competitor data and generating insights
        </p>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <Brain className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">AI Analysis Not Available</h3>
        <p className="text-gray-600">Click "Analyze with AI" to get detailed market insights</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Analysis Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center mb-4">
          <Brain className="w-8 h-8 mr-3" />
          <h2 className="text-2xl font-bold">AI Market Analysis</h2>
        </div>
        <p className="text-purple-100">
          Advanced competitive intelligence powered by AI
        </p>
      </div>

      {/* Executive Summary */}
      {analysis.summary && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
            Executive Summary
          </h3>
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700 leading-relaxed">{analysis.summary}</p>
          </div>
        </div>
      )}

      {/* Market Positioning */}
      {analysis.positioning && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Target className="w-5 h-5 mr-2 text-green-600" />
            Market Positioning
          </h3>
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700 leading-relaxed">{analysis.positioning}</p>
          </div>
        </div>
      )}

      {/* Top Competitors Analysis */}
      {analysis.top_competitors && analysis.top_competitors.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Award className="w-5 h-5 mr-2 text-yellow-600" />
            Top Competitor Analysis
          </h3>
          <div className="grid gap-4">
            {analysis.top_competitors.slice(0, 5).map((competitor, index) => (
              <div key={competitor.asin || index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 text-sm leading-tight mb-2">
                      {competitor.title}
                    </h4>
                    <div className="flex items-center space-x-4 text-sm">
                      <span className="flex items-center text-green-600">
                        <DollarSign className="w-3 h-3 mr-1" />
                        {competitor.currency === 'USD' ? '$' : competitor.currency}
                        {competitor.price?.toFixed(2) || 'N/A'}
                      </span>
                      {competitor.rating && (
                        <span className="text-yellow-600">
                          ★ {competitor.rating.toFixed(1)}
                        </span>
                      )}
                      {competitor.price_difference_pct && (
                        <span className={`font-medium ${
                          competitor.price_difference_pct > 0 ? 'text-red-600' : 'text-green-600'
                        }`}>
                          {competitor.price_difference_pct > 0 ? '+' : ''}
                          {competitor.price_difference_pct.toFixed(1)}% vs main
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      #{index + 1} Competitor
                    </span>
                  </div>
                </div>
                
                {competitor.key_points && competitor.key_points.length > 0 && (
                  <div className="mt-3">
                    <ul className="text-sm text-gray-600 space-y-1">
                      {competitor.key_points.map((point, pointIndex) => (
                        <li key={pointIndex} className="flex items-start">
                          <span className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {analysis.recommendations && analysis.recommendations.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Lightbulb className="w-5 h-5 mr-2 text-amber-600" />
            Strategic Recommendations
          </h3>
          <div className="grid gap-3">
            {analysis.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start p-4 bg-amber-50 border border-amber-200 rounded-lg">
                <div className="flex-shrink-0 w-6 h-6 bg-amber-200 text-amber-800 rounded-full flex items-center justify-center text-sm font-bold mr-3">
                  {index + 1}
                </div>
                <p className="text-amber-900 text-sm leading-relaxed">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Additional Analysis Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pricing Analysis */}
        {analysis.pricing_analysis && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <DollarSign className="w-5 h-5 mr-2 text-green-600" />
              Pricing Analysis
            </h3>
            <div className="prose prose-sm max-w-none">
              <p className="text-gray-700 leading-relaxed">{analysis.pricing_analysis}</p>
            </div>
          </div>
        )}

        {/* Feature Comparison */}
        {analysis.feature_comparison && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Target className="w-5 h-5 mr-2 text-purple-600" />
              Feature Comparison
            </h3>
            <div className="prose prose-sm max-w-none">
              <p className="text-gray-700 leading-relaxed">{analysis.feature_comparison}</p>
            </div>
          </div>
        )}
      </div>

      {/* Market Insights */}
      {analysis.market_insights && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-indigo-600" />
            Market Insights
          </h3>
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700 leading-relaxed">{analysis.market_insights}</p>
          </div>
        </div>
      )}

      {/* Analysis Footer */}
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <p className="text-xs text-gray-600 text-center">
          Analysis completed on {new Date().toLocaleDateString()} • 
          Powered by advanced AI algorithms and real-time market data
        </p>
      </div>
    </div>
  );
};

export default LLMAnalysis;