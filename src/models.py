"""
Pydantic models for request/response schemas
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from src.geo_utils import GeoLocationHandler


class ProductInput(BaseModel):
    """Input for product scraping request"""
    identifier: str = Field(..., description="ASIN, product URL, or product name")
    identifier_type: str = Field(..., description="Type: 'asin', 'url', or 'name'")
    zip_code: str = Field(..., description="ZIP/postal code for geo-location")
    domain: str = Field(default="com", description="Amazon domain (com, in, co.uk, etc.)")
    
    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v):
        """Validate Amazon domain"""
        allowed_domains = ['com', 'in', 'co.uk', 'de', 'fr', 'it', 'es', 'ca', 'com.au', 'co.jp']
        if v not in allowed_domains:
            raise ValueError(f"Unsupported domain: {v}. Allowed: {', '.join(allowed_domains)}")
        return v
    
    @model_validator(mode='after')
    def validate_postal_code_for_domain(self):
        """Validate postal code format matches the selected domain"""
        if not self.zip_code or not self.zip_code.strip():
            raise ValueError("Postal code cannot be empty")
        
        # Validate using our geo utils
        if not GeoLocationHandler.validate_postal_code(self.zip_code, self.domain):
            domain_examples = {
                'com': '10001 (US ZIP)',
                'in': '110001 (6-digit PIN)',
                'co.uk': 'SW1A 1AA (UK postcode)',
                'de': '10115 (5-digit)',
                'fr': '75001 (5-digit)',
                'it': '00118 (5-digit)',
                'es': '28001 (5-digit)'
            }
            example = domain_examples.get(self.domain, '10001')
            raise ValueError(f"Invalid postal code format for {self.domain} domain. Expected format: {example}")
        
        # Normalize the postal code
        self.zip_code = GeoLocationHandler.normalize_postal_code(self.zip_code, self.domain)
        return self


class ProductDetails(BaseModel):
    """Product details response model"""
    asin: Optional[str] = None
    title: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    stock: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    categories: Union[List[str], List[Dict], Dict, Any] = Field(default_factory=list)
    category_path: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    specifications: Dict[str, str] = Field(default_factory=dict)
    url: Optional[str] = None
    amazon_domain: Optional[str] = None
    geo_location: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @field_validator('categories')
    @classmethod
    def normalize_categories(cls, v):
        """Normalize categories from various formats to list of strings"""
        if not v:
            return []
        
        if isinstance(v, list):
            # Handle list of strings or dicts
            result = []
            for item in v:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, dict):
                    # Extract category names from dict structure
                    if 'name' in item:
                        result.append(item['name'])
                    elif 'category' in item:
                        result.append(item['category'])
            return result
        
        elif isinstance(v, dict):
            # Handle nested dict structure like {'ladder': [{'name': 'Category'}]}
            result = []
            for key, value in v.items():
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) and 'name' in item:
                            result.append(item['name'])
                        elif isinstance(item, str):
                            result.append(item)
                elif isinstance(value, str):
                    result.append(value)
                else:
                    result.append(str(key))
            return result
        
        elif isinstance(v, str):
            return [v]
        
        return []


class CompetitorAnalysisRequest(BaseModel):
    """Request for competitor analysis"""
    asin: str = Field(..., description="Main product ASIN")
    search_pages: int = Field(default=2, ge=1, le=5, description="Number of search pages to analyze")
    max_competitors: int = Field(default=20, ge=5, le=50, description="Maximum competitors to find")


class CompetitorInsights(BaseModel):
    """Individual competitor analysis"""
    asin: str
    title: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    rating: Optional[float] = None
    key_points: List[str] = Field(default_factory=list)
    price_difference_pct: Optional[float] = None
    rating_difference: Optional[float] = None


class LLMAnalysisRequest(BaseModel):
    """Request for LLM analysis"""
    main_asin: str = Field(..., description="Main product ASIN to analyze")
    include_competitors: bool = Field(default=True, description="Include competitor analysis")
    analysis_focus: List[str] = Field(
        default=["pricing", "features", "positioning", "recommendations"],
        description="Analysis focus areas"
    )


class LLMAnalysisResponse(BaseModel):
    """LLM analysis response"""
    summary: str = Field(..., description="Executive summary of the analysis")
    positioning: str = Field(..., description="Market positioning analysis")
    top_competitors: List[CompetitorInsights] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    pricing_analysis: Optional[str] = None
    feature_comparison: Optional[str] = None
    market_insights: Optional[str] = None


class APIResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str
    error: str
    error_code: Optional[str] = None