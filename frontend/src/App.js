import React, { useState, useEffect } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { 
  Target, 
  Brain, 
  BarChart3, 
  RefreshCw,
  ExternalLink,
  AlertTriangle
} from 'lucide-react';

// Import components
import ProductInputForm from './components/ProductInputForm';
import ProductCard from './components/ProductCard';
import CompetitorAnalysis from './components/CompetitorAnalysis';
import EnhancedLLMAnalysis from './components/EnhancedLLMAnalysis';
import WorkflowSteps from './components/WorkflowSteps';

// Import API
import { amazonAPI } from './api';

function App() {
  // State management
  const [currentStep, setCurrentStep] = useState('input');
  const [completedSteps, setCompletedSteps] = useState([]);
  const [loading, setLoading] = useState({
    scrape: false,
    competitors: false,
    llm: false
  });

  // Data state
  const [productData, setProductData] = useState(null);
  const [competitorData, setCompetitorData] = useState(null);
  const [pricingAnalysis, setPricingAnalysis] = useState(null);
  const [llmAnalysis, setLLMAnalysis] = useState(null);

  // Form data
  // const [lastFormData, setLastFormData] = useState(null);

  // API health check on component mount
  useEffect(() => {
    checkAPIHealth();
  }, []);

  const checkAPIHealth = async () => {
    try {
      await amazonAPI.healthCheck();
      toast.success('Connected to Amazon Analysis API', {
        icon: '✅',
        duration: 2000
      });
    } catch (error) {
      toast.error('API connection failed. Please check if the backend is running.', {
        icon: '❌',
        duration: 5000
      });
    }
  };

  // Helper functions
  const updateLoading = (key, value) => {
    setLoading(prev => ({ ...prev, [key]: value }));
  };

  const markStepCompleted = (stepId) => {
    if (!completedSteps.includes(stepId)) {
      setCompletedSteps(prev => [...prev, stepId]);
    }
  };

  const resetAnalysis = () => {
    setCurrentStep('input');
    setCompletedSteps([]);
    setProductData(null);
    setCompetitorData(null);
    setPricingAnalysis(null);
    setLLMAnalysis(null);
    // setLastFormData(null);
    setLoading({ scrape: false, competitors: false, llm: false });
  };

  // Step handlers
  const handleProductScrape = async (formData) => {
    updateLoading('scrape', true);
    setCurrentStep('scrape');
    // setLastFormData(formData);

    try {
      const response = await amazonAPI.scrapeProduct(formData);
      
      if (response.data.success) {
        const product = response.data.data.product;
        setProductData(product);
        markStepCompleted('scrape');
        setCurrentStep('competitors');
        
        toast.success(`Product scraped: ${product.title?.slice(0, 50)}...`, {
          icon: '🔍',
          duration: 4000
        });
      } else {
        throw new Error(response.data.error || 'Failed to scrape product');
      }
    } catch (error) {
      console.error('Scraping error:', error);
      toast.error(error.response?.data?.detail || 'Failed to scrape product. Please try again.');
      setCurrentStep('input');
    } finally {
      updateLoading('scrape', false);
    }
  };

  const handleCompetitorAnalysis = async () => {
    if (!productData?.asin) {
      toast.error('No product data available for competitor analysis');
      return;
    }

    updateLoading('competitors', true);
    setCurrentStep('competitors');

    try {
      const analysisData = {
        asin: productData.asin,
        search_pages: 2,
        max_competitors: 10
      };

      const response = await amazonAPI.analyzeCompetitors(analysisData);
      
      if (response.data.success) {
        const competitors = response.data.data.competitors;
        setCompetitorData(competitors);
        markStepCompleted('competitors');
        
        // Also get pricing analysis
        try {
          const pricingResponse = await amazonAPI.getPricingAnalysis(productData.asin);
          if (pricingResponse.data.success) {
            setPricingAnalysis(pricingResponse.data.data.pricing_analysis);
          }
        } catch (pricingError) {
          console.warn('Pricing analysis failed:', pricingError);
        }
        
        setCurrentStep('analyze');
        
        toast.success(`Found ${competitors.length} competitors`, {
          icon: '🎯',
          duration: 4000
        });
      } else {
        throw new Error(response.data.error || 'Failed to analyze competitors');
      }
    } catch (error) {
      console.error('Competitor analysis error:', error);
      let errorMessage = 'Failed to analyze competitors. Please try again.';
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. Competitor analysis is taking longer than expected.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error occurred. Please check the backend logs.';
      } else if (error.message.includes('Network Error')) {
        errorMessage = 'Network error. Please check if the backend is running.';
      }
      
      toast.error(errorMessage);
    } finally {
      updateLoading('competitors', false);
    }
  };

  const handleLLMAnalysis = async () => {
    if (!productData?.asin) {
      toast.error('No product data available for LLM analysis');
      return;
    }

    updateLoading('llm', true);
    setCurrentStep('analyze');

    try {
      const analysisData = {
        main_asin: productData.asin,
        include_competitors: true,
        analysis_focus: ['pricing', 'positioning', 'recommendations']
      };

      const response = await amazonAPI.analyzeLLM(analysisData);
      
      if (response.data.success) {
        const analysis = response.data.data.analysis;
        setLLMAnalysis(analysis);
        markStepCompleted('analyze');
        
        toast.success('AI analysis completed!', {
          icon: '🧠',
          duration: 4000
        });
      } else {
        throw new Error(response.data.error || 'Failed to complete LLM analysis');
      }
    } catch (error) {
      console.error('LLM analysis error:', error);
      toast.error(error.response?.data?.detail || 'AI analysis failed. Please check your OpenAI configuration.');
    } finally {
      updateLoading('llm', false);
    }
  };

  const handleStepClick = (stepId) => {
    // Allow navigation to completed steps
    if (completedSteps.includes(stepId)) {
      setCurrentStep(stepId);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
      
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="gradient-amazon w-12 h-12 rounded-lg flex items-center justify-center mr-4">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Amazon Competitor Analysis
                </h1>
                <p className="text-gray-600 mt-1">
                  AI-powered competitive intelligence for Amazon products
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={resetAnalysis}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Reset
              </button>
              
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-4 py-2 border border-amazon-300 rounded-md shadow-sm text-sm font-medium text-amazon-700 bg-amazon-50 hover:bg-amazon-100 transition-colors"
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                API Docs
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Workflow Steps */}
        <WorkflowSteps
          currentStep={currentStep}
          completedSteps={completedSteps}
          onStepClick={handleStepClick}
        />

        {/* Step 1: Product Input */}
        {(currentStep === 'input' || !productData) && (
          <ProductInputForm
            onSubmit={handleProductScrape}
            loading={loading.scrape}
          />
        )}

        {/* Step 2: Product Display */}
        {productData && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Product Details</h2>
              <div className="flex items-center space-x-3">
                {!completedSteps.includes('competitors') && (
                  <button
                    onClick={handleCompetitorAnalysis}
                    disabled={loading.competitors}
                    className={`inline-flex items-center px-6 py-3 border border-transparent rounded-lg text-base font-medium text-white transition-all duration-200 ${
                      loading.competitors
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'gradient-info hover:shadow-lg transform hover:scale-105'
                    }`}
                  >
                    {loading.competitors ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Finding Competitors... (This may take 1-2 minutes)
                      </>
                    ) : (
                      <>
                        <Target className="w-5 h-5 mr-2" />
                        Analyze Competitors
                      </>
                    )}
                  </button>
                )}
                
                {completedSteps.includes('competitors') && !completedSteps.includes('analyze') && (
                  <button
                    onClick={handleLLMAnalysis}
                    disabled={loading.llm}
                    className={`inline-flex items-center px-6 py-3 border border-transparent rounded-lg text-base font-medium text-white transition-all duration-200 ${
                      loading.llm
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:shadow-lg transform hover:scale-105'
                    }`}
                  >
                    {loading.llm ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Analyzing with AI...
                      </>
                    ) : (
                      <>
                        <Brain className="w-5 h-5 mr-2" />
                        Analyze with AI
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
            
            <ProductCard product={productData} isMainProduct={true} />
          </div>
        )}

        {/* Step 3: Competitor Analysis */}
        {competitorData && completedSteps.includes('competitors') && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Competitor Analysis</h2>
            <CompetitorAnalysis
              competitors={competitorData}
              mainProduct={productData}
              pricingAnalysis={pricingAnalysis}
            />
          </div>
        )}

        {/* Step 4: Enhanced LLM Analysis */}
        {llmAnalysis && (
          <EnhancedLLMAnalysis 
            analysis={llmAnalysis} 
            mainProduct={productData}
            onClose={() => setLLMAnalysis(null)}
          />
        )}

        {/* API Status Warning */}
        {!productData && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-8">
            <div className="flex">
              <AlertTriangle className="w-5 h-5 text-yellow-400 mr-3 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-yellow-800">
                  Getting Started
                </h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <p>
                    Make sure the Amazon Analysis API is running on localhost:8000. 
                    Enter a product ASIN, URL, or name above to begin your competitive analysis.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            Amazon Competitor Analysis Tool • Powered by Oxylabs Web Scraper API & OpenAI • 
            Built with React & FastAPI
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;