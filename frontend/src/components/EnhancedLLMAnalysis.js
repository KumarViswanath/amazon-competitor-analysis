import React, { useState } from 'react';
import { 
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer, PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, 
  PolarRadiusAxis, Area, AreaChart, Radar
} from 'recharts';
import { 
  TrendingUp, TrendingDown, Target, DollarSign, Star, 
  ChevronDown, ChevronUp, AlertTriangle, CheckCircle, 
  BarChart3, PieChart as PieChartIcon, Activity, Zap
} from 'lucide-react';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const ScoreCard = ({ title, score, maxScore = 100, color = "blue" }) => {
  const percentage = (score / maxScore) * 100;
  const getScoreColor = () => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h3 className="text-sm font-medium text-gray-600 mb-2">{title}</h3>
      <div className="flex items-center space-x-3">
        <div className={`text-2xl font-bold ${getScoreColor()}`}>
          {score?.toFixed(1) || 'N/A'}
        </div>
        <div className="flex-1">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`bg-${color}-500 h-2 rounded-full transition-all duration-500`}
              style={{ width: `${percentage}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

const CompetitorPriceChart = ({ competitors, mainProduct }) => {
  const chartData = [
    {
      name: 'Your Product',
      price: mainProduct?.price || 0,
      rating: mainProduct?.rating || 0,
      isMain: true
    },
    ...competitors.slice(0, 8).map((comp, index) => ({
      name: `Competitor ${index + 1}`,
      price: comp.price || 0,
      rating: comp.rating || 0,
      asin: comp.asin,
      title: comp.title?.substring(0, 30) + '...' || 'Unknown'
    }))
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <BarChart3 className="mr-2" size={20} />
        Price vs Rating Comparison
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
          <YAxis yAxisId="price" orientation="left" />
          <YAxis yAxisId="rating" orientation="right" domain={[0, 5]} />
          <Tooltip 
            formatter={(value, name, props) => [
              name === 'price' ? `$${value}` : `${value}/5`,
              name === 'price' ? 'Price' : 'Rating'
            ]}
          />
          <Legend />
          <Bar yAxisId="price" dataKey="price" fill="#8884d8" name="Price ($)" />
          <Bar yAxisId="rating" dataKey="rating" fill="#82ca9d" name="Rating" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

const MarketPositionRadar = ({ analysis }) => {
  const radarData = [
    {
      subject: 'Price Competitiveness',
      score: analysis.price_competitiveness_score || 50,
      fullMark: 100,
    },
    {
      subject: 'Market Position',
      score: analysis.market_position_score || 50,
      fullMark: 100,
    },
    {
      subject: 'Feature Completeness',
      score: analysis.feature_competitiveness_score || 50,
      fullMark: 100,
    },
    {
      subject: 'Brand Strength',
      score: 70, // Placeholder
      fullMark: 100,
    },
    {
      subject: 'Customer Satisfaction',
      score: 85, // Placeholder
      fullMark: 100,
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <Target className="mr-2" size={20} />
        Market Position Analysis
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <RadarChart data={radarData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="subject" />
          <PolarRadiusAxis angle={90} domain={[0, 100]} />
          <Radar
            name="Your Product"
            dataKey="score"
            stroke="#8884d8"
            fill="#8884d8"
            fillOpacity={0.6}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

const RecommendationsPanel = ({ recommendations }) => {
  const [expandedRecs, setExpandedRecs] = useState({});

  const toggleRecommendation = (index) => {
    setExpandedRecs(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const getPriorityColor = (index) => {
    if (index < 2) return 'border-l-red-500 bg-red-50';
    if (index < 5) return 'border-l-yellow-500 bg-yellow-50';
    return 'border-l-green-500 bg-green-50';
  };

  const getPriorityLabel = (index) => {
    if (index < 2) return 'High Priority';
    if (index < 5) return 'Medium Priority';
    return 'Low Priority';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <Zap className="mr-2" size={20} />
        Strategic Recommendations
      </h3>
      <div className="space-y-3">
        {recommendations.slice(0, 10).map((rec, index) => (
          <div 
            key={index}
            className={`border-l-4 p-4 rounded-r-lg ${getPriorityColor(index)}`}
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    index < 2 ? 'bg-red-200 text-red-800' :
                    index < 5 ? 'bg-yellow-200 text-yellow-800' :
                    'bg-green-200 text-green-800'
                  }`}>
                    {getPriorityLabel(index)}
                  </span>
                </div>
                <p className={`text-sm ${expandedRecs[index] ? '' : 'line-clamp-2'}`}>
                  {rec}
                </p>
              </div>
              <button
                onClick={() => toggleRecommendation(index)}
                className="ml-2 text-gray-400 hover:text-gray-600"
              >
                {expandedRecs[index] ? 
                  <ChevronUp size={16} /> : 
                  <ChevronDown size={16} />
                }
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const CompetitorTable = ({ competitors }) => {
  const [sortField, setSortField] = useState('price');
  const [sortDirection, setSortDirection] = useState('asc');

  const sortedCompetitors = [...competitors].sort((a, b) => {
    const aVal = a[sortField] || 0;
    const bVal = b[sortField] || 0;
    return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
  });

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">Detailed Competitor Comparison</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full table-auto">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-4 py-2 text-left">Product</th>
              <th 
                className="px-4 py-2 text-left cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('price')}
              >
                Price {sortField === 'price' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th 
                className="px-4 py-2 text-left cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('rating')}
              >
                Rating {sortField === 'rating' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th className="px-4 py-2 text-left">Price Diff</th>
              <th className="px-4 py-2 text-left">Rating Diff</th>
            </tr>
          </thead>
          <tbody>
            {sortedCompetitors.slice(0, 10).map((comp, index) => (
              <tr key={index} className="border-t hover:bg-gray-50">
                <td className="px-4 py-2">
                  <div>
                    <div className="font-medium text-sm">
                      {comp.title?.substring(0, 50) || 'Unknown Product'}...
                    </div>
                    <div className="text-xs text-gray-500">{comp.asin}</div>
                  </div>
                </td>
                <td className="px-4 py-2 font-medium">
                  ${comp.price?.toFixed(2) || 'N/A'}
                </td>
                <td className="px-4 py-2">
                  <div className="flex items-center">
                    <Star size={14} className="text-yellow-400 mr-1" />
                    {comp.rating?.toFixed(1) || 'N/A'}
                  </div>
                </td>
                <td className="px-4 py-2">
                  <span className={`text-sm font-medium ${
                    comp.price_difference_pct > 0 ? 'text-red-600' : 'text-green-600'
                  }`}>
                    {comp.price_difference_pct ? 
                      `${comp.price_difference_pct > 0 ? '+' : ''}${comp.price_difference_pct.toFixed(1)}%` : 
                      'N/A'
                    }
                  </span>
                </td>
                <td className="px-4 py-2">
                  <span className={`text-sm font-medium ${
                    comp.rating_difference > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {comp.rating_difference ? 
                      `${comp.rating_difference > 0 ? '+' : ''}${comp.rating_difference.toFixed(1)}` : 
                      'N/A'
                    }
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const EnhancedLLMAnalysis = ({ analysis, mainProduct, onClose }) => {
  const [activeTab, setActiveTab] = useState('overview');

  if (!analysis) {
    return (
      <div className="text-center py-8">
        <Activity className="mx-auto text-gray-400 mb-4" size={48} />
        <p className="text-gray-600">No analysis data available</p>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'insights', label: 'Strategic Insights', icon: Target },
    { id: 'categories', label: 'Category Analysis', icon: PieChartIcon },
    { id: 'reviews', label: 'Customer Reviews', icon: Star },
    { id: 'competitive', label: 'Competitive Analysis', icon: Activity },
    { id: 'recommendations', label: 'Recommendations', icon: Zap },
    { id: 'market', label: 'Market Intelligence', icon: TrendingUp }
  ];

  return (
    <div className="bg-gray-50 min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                AI-Powered Competitive Analysis
              </h2>
              <p className="text-gray-600 mt-1">
                {mainProduct?.title || 'Product Analysis'}
              </p>
            </div>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
            >
              Close Analysis
            </button>
          </div>
        </div>

        {/* Score Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <ScoreCard
            title="Market Position"
            score={analysis.market_position_score}
            color="blue"
          />
          <ScoreCard
            title="Price Competitive"
            score={analysis.price_competitiveness_score}
            color="green"
          />
          <ScoreCard
            title="Brand Strength"
            score={analysis.brand_strength_score}
            color="purple"
          />
          <ScoreCard
            title="Customer Satisfaction"
            score={analysis.customer_satisfaction_score}
            color="yellow"
          />
          <ScoreCard
            title="Feature Competitive"
            score={analysis.feature_competitiveness_score || 75}
            color="red"
          />
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="border-b">
            <nav className="flex">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <tab.icon size={18} className="mr-2" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Executive Summary */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">Executive Summary</h3>
              <p className="text-gray-700 leading-relaxed">{analysis.summary}</p>
            </div>

            {/* Market Position Radar */}
            <MarketPositionRadar analysis={analysis} />

            {/* Price Comparison Chart */}
            <div className="lg:col-span-2">
              <CompetitorPriceChart 
                competitors={analysis.top_competitors} 
                mainProduct={mainProduct}
              />
            </div>
          </div>
        )}

        {activeTab === 'competitive' && (
          <div className="space-y-6">
            {/* Positioning Analysis */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">Market Positioning</h3>
              <div className="prose max-w-none">
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {analysis.positioning}
                </p>
              </div>
            </div>

            {/* Competitor Table */}
            <CompetitorTable competitors={analysis.top_competitors} />

            {/* Pricing Analysis */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">Pricing Analysis</h3>
              <div className="prose max-w-none">
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {analysis.pricing_analysis}
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'recommendations' && (
          <div className="space-y-6">
            <RecommendationsPanel recommendations={analysis.recommendations} />
            
            {analysis.action_plan && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">90-Day Action Plan</h3>
                <div className="prose max-w-none">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {analysis.action_plan}
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'market' && (
          <div className="space-y-6">
            {/* Market Insights */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">Market Trends & Insights</h3>
              <div className="prose max-w-none">
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {analysis.market_insights}
                </p>
              </div>
            </div>

            {/* Competitive Threats */}
            {analysis.competitive_threats && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <AlertTriangle className="mr-2 text-yellow-500" size={20} />
                  Competitive Threats & Opportunities
                </h3>
                <div className="prose max-w-none">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {analysis.competitive_threats}
                  </p>
                </div>
              </div>
            )}

            {/* Feature Comparison */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">Feature Comparison</h3>
              <div className="prose max-w-none">
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {analysis.feature_comparison}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* New Tab: Strategic Insights */}
        {activeTab === 'insights' && (
          <div className="space-y-6">
            {/* Overall Strategic Insights */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">Overall Strategic Insights</h3>
              <div className="prose max-w-none">
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {analysis.overall_insights}
                </p>
              </div>
            </div>

            {/* Brand Analysis */}
            {analysis.brand_analysis && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">Brand & Competitive Advantage</h3>
                <div className="prose max-w-none">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {analysis.brand_analysis}
                  </p>
                </div>
              </div>
            )}

            {/* Risk & Opportunity Assessment */}
            {analysis.risk_assessment && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4 text-red-800 flex items-center">
                    <AlertTriangle className="mr-2" size={20} />
                    Risk Assessment
                  </h3>
                  <div className="prose max-w-none">
                    <p className="text-red-700 leading-relaxed whitespace-pre-wrap">
                      {analysis.risk_assessment}
                    </p>
                  </div>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4 text-green-800 flex items-center">
                    <CheckCircle className="mr-2" size={20} />
                    Opportunity Analysis
                  </h3>
                  <div className="prose max-w-none">
                    <p className="text-green-700 leading-relaxed whitespace-pre-wrap">
                      {analysis.opportunity_analysis}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* New Tab: Category Analysis */}
        {activeTab === 'categories' && (
          <div className="space-y-6">
            {/* Category Breakdown */}
            {analysis.category_breakdown && Object.keys(analysis.category_breakdown).length > 0 && (
              <div className="grid grid-cols-1 gap-6">
                {Object.entries(analysis.category_breakdown).map(([category, content], index) => (
                  <div key={index} className="bg-white rounded-lg shadow-md p-6">
                    <h3 className="text-lg font-semibold mb-4 capitalize">{category.replace(/([A-Z])/g, ' $1').trim()}</h3>
                    <div className="prose max-w-none">
                      <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                        {content}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Price Breakdown Details */}
            {analysis.price_breakdown && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">Detailed Price Analysis</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      ${analysis.price_breakdown.main_product_price?.toFixed(2) || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-600">Your Price</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      ${analysis.price_breakdown.avg_competitor_price?.toFixed(2) || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-600">Avg Competitor</div>
                  </div>
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-600">
                      {analysis.price_breakdown.price_percentile || 'N/A'}%
                    </div>
                    <div className="text-sm text-gray-600">Price Percentile</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {analysis.price_breakdown.cheaper_than_percent || 'N/A'}%
                    </div>
                    <div className="text-sm text-gray-600">Cheaper Than</div>
                  </div>
                </div>
              </div>
            )}

            {/* Geographic Insights */}
            {analysis.geographic_insights && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">Geographic & Market Insights</h3>
                <div className="prose max-w-none">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {analysis.geographic_insights}
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* New Tab: Customer Reviews Analysis */}
        {activeTab === 'reviews' && (
          <div className="space-y-6">
            {/* Review Analysis */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Star className="mr-2 text-yellow-500" size={20} />
                Customer Review Analysis
              </h3>
              <div className="prose max-w-none">
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {analysis.review_analysis}
                </p>
              </div>
            </div>

            {/* Customer Feedback Summary */}
            {analysis.customer_feedback_summary && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">Customer Feedback Summary</h3>
                <div className="prose max-w-none">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {analysis.customer_feedback_summary}
                  </p>
                </div>
              </div>
            )}

            {/* Optimization Suggestions */}
            {analysis.optimization_suggestions && analysis.optimization_suggestions.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">Optimization Suggestions</h3>
                <div className="space-y-3">
                  {analysis.optimization_suggestions.map((suggestion, index) => (
                    <div key={index} className="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg">
                      <div className="text-blue-600 font-bold text-lg">{index + 1}</div>
                      <p className="text-gray-700 flex-1">{suggestion}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EnhancedLLMAnalysis;