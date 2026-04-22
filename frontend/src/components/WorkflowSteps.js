import React from 'react';
import { CheckCircle, Clock, AlertCircle, Play } from 'lucide-react';

const WorkflowSteps = ({ currentStep, completedSteps, onStepClick }) => {
  const steps = [
    {
      id: 'input',
      title: 'Product Input',
      description: 'Enter product details',
      icon: '📝'
    },
    {
      id: 'scrape',
      title: 'Scrape Product',
      description: 'Get product information',
      icon: '🔍'
    },
    {
      id: 'competitors',
      title: 'Find Competitors',
      description: 'Discover competing products',
      icon: '🎯'
    },
    {
      id: 'analyze',
      title: 'AI Analysis',
      description: 'Generate market insights',
      icon: '🧠'
    }
  ];

  const getStepStatus = (stepId) => {
    if (completedSteps.includes(stepId)) return 'completed';
    if (currentStep === stepId) return 'current';
    return 'pending';
  };

  // const getStepColor = (status) => {
  //   switch (status) {
  //     case 'completed':
  //       return 'bg-green-100 border-green-500 text-green-700';
  //     case 'current':
  //       return 'bg-amazon-100 border-amazon-500 text-amazon-700';
  //     default:
  //       return 'bg-gray-100 border-gray-300 text-gray-500';
  //   }
  // };

  const getIconColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500 text-white';
      case 'current':
        return 'bg-amazon-500 text-white';
      default:
        return 'bg-gray-300 text-gray-600';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Analysis Workflow</h2>
      
      <div className="relative">
        {/* Progress Line */}
        <div className="absolute top-8 left-8 right-8 h-0.5 bg-gray-300 -z-10"></div>
        <div 
          className="absolute top-8 left-8 h-0.5 bg-amazon-500 transition-all duration-500 -z-10"
          style={{ 
            width: `${(completedSteps.length / (steps.length - 1)) * 100}%` 
          }}
        ></div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {steps.map((step, index) => {
            const status = getStepStatus(step.id);
            const isClickable = completedSteps.includes(step.id) || currentStep === step.id;
            
            return (
              <div
                key={step.id}
                className={`relative flex flex-col items-center cursor-pointer transition-all duration-200 ${
                  isClickable ? 'hover:scale-105' : 'cursor-not-allowed opacity-60'
                }`}
                onClick={() => isClickable && onStepClick && onStepClick(step.id)}
              >
                {/* Step Circle */}
                <div
                  className={`w-16 h-16 rounded-full border-2 flex items-center justify-center transition-all duration-200 ${getIconColor(status)} ${
                    status === 'current' ? 'animate-pulse' : ''
                  }`}
                >
                  {status === 'completed' ? (
                    <CheckCircle className="w-8 h-8" />
                  ) : status === 'current' ? (
                    <Play className="w-6 h-6" />
                  ) : (
                    <span className="text-2xl">{step.icon}</span>
                  )}
                </div>

                {/* Step Content */}
                <div className="mt-4 text-center">
                  <h3 className={`font-semibold ${
                    status === 'completed' ? 'text-green-700' :
                    status === 'current' ? 'text-amazon-700' : 'text-gray-500'
                  }`}>
                    {step.title}
                  </h3>
                  <p className="text-xs text-gray-600 mt-1">
                    {step.description}
                  </p>
                  
                  {/* Status Indicator */}
                  <div className="mt-2">
                    {status === 'completed' && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Complete
                      </span>
                    )}
                    {status === 'current' && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-amazon-100 text-amazon-800">
                        <Clock className="w-3 h-3 mr-1" />
                        In Progress
                      </span>
                    )}
                    {status === 'pending' && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                        <AlertCircle className="w-3 h-3 mr-1" />
                        Pending
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default WorkflowSteps;