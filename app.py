"""
FastAPI application for Amazon Product Competitor Analysis
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from src.models import (
    ProductInput, ProductDetails, CompetitorAnalysisRequest,
    LLMAnalysisRequest, LLMAnalysisResponse, APIResponse, ErrorResponse
)
from src.product_service import ProductService
from src.competitor_service import CompetitorService
from src.llm_service import LLMService, LLMAnalysisResult
from src.db import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Amazon Product Competitor Analysis API",
    description="Comprehensive API for Amazon product scraping, competitor analysis, and LLM-powered insights using Oxylabs Web Scraper",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
product_service = ProductService()
competitor_service = CompetitorService()
llm_service = LLMService()


# Dependency injection
async def get_product_service() -> ProductService:
    return product_service

async def get_competitor_service() -> CompetitorService:
    return competitor_service

async def get_llm_service() -> LLMService:
    return llm_service


# Health check endpoint
@app.get("/health", response_model=APIResponse)
async def health_check():
    """Health check endpoint"""
    return APIResponse(
        success=True,
        message="Amazon Competitor Analysis API is running",
        data={
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "status": "healthy"
        }
    )


# Product endpoints
@app.post("/api/products/scrape", response_model=APIResponse)
async def scrape_product(
    product_input: ProductInput,
    service: ProductService = Depends(get_product_service)
):
    """
    Scrape Amazon product by ASIN, URL, or product name
    
    - **identifier**: ASIN (B0ABCD1234), Amazon URL, or product name
    - **identifier_type**: 'asin', 'url', or 'name'
    - **zip_code**: ZIP/postal code for geo-location
    - **domain**: Amazon domain (com, in, co.uk, etc.)
    """
    try:
        logger.info(f"Scraping product: {product_input.identifier}")
        
        product_details = service.scrape_product_by_input(product_input)
        
        return APIResponse(
            success=True,
            message="Product scraped successfully",
            data={
                "product": product_details.model_dump(),
                "scraped_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Product scraping failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/products/{asin}", response_model=APIResponse)
async def get_product(
    asin: str,
    service: ProductService = Depends(get_product_service)
):
    """Get product details by ASIN from database"""
    try:
        product = service.get_product_from_db(asin.upper())
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {asin} not found")
        
        return APIResponse(
            success=True,
            message="Product retrieved successfully",
            data={"product": product.model_dump()}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get product {asin}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/products", response_model=APIResponse)
async def list_products(
    limit: int = Query(50, ge=1, le=200, description="Number of products to return"),
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    service: ProductService = Depends(get_product_service)
):
    """List all products with pagination"""
    try:
        products = service.list_products(limit=limit, skip=skip)
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(products)} products",
            data={
                "products": [p.model_dump() for p in products],
                "pagination": {
                    "limit": limit,
                    "skip": skip,
                    "returned": len(products)
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to list products: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/products/search", response_model=APIResponse)
async def search_products(
    query: str = Query(..., description="Search query (title, brand, etc.)"),
    category: Optional[str] = Query(None, description="Product category filter"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating filter"),
    limit: int = Query(50, ge=1, le=200, description="Number of results to return"),
    service: ProductService = Depends(get_product_service)
):
    """Search products in database with filters"""
    try:
        # Build search criteria
        search_criteria = {}
        
        # Text search
        if query:
            search_criteria["$text"] = {"$search": query}
        
        # Category filter
        if category:
            search_criteria["categories"] = {"$regex": category, "$options": "i"}
        
        # Price range filter
        if min_price is not None or max_price is not None:
            price_filter = {}
            if min_price is not None:
                price_filter["$gte"] = min_price
            if max_price is not None:
                price_filter["$lte"] = max_price
            search_criteria["price"] = price_filter
        
        # Rating filter
        if min_rating is not None:
            search_criteria["rating"] = {"$gte": min_rating}
        
        products = service.search_products_in_db(search_criteria, limit=limit)
        
        return APIResponse(
            success=True,
            message=f"Found {len(products)} products matching criteria",
            data={
                "products": [p.model_dump() for p in products],
                "search_criteria": search_criteria,
                "result_count": len(products)
            }
        )
        
    except Exception as e:
        logger.error(f"Product search failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/products/stats", response_model=APIResponse)
async def get_product_stats(service: ProductService = Depends(get_product_service)):
    """Get product database statistics"""
    try:
        stats = service.get_product_stats()
        
        return APIResponse(
            success=True,
            message="Product statistics retrieved",
            data={"statistics": stats}
        )
        
    except Exception as e:
        logger.error(f"Failed to get product stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Competitor analysis endpoints
@app.post("/api/competitors/analyze", response_model=APIResponse)
async def analyze_competitors(
    analysis_request: CompetitorAnalysisRequest,
    background_tasks: BackgroundTasks,
    service: CompetitorService = Depends(get_competitor_service)
):
    """
    Analyze competitors for a given product
    
    - **asin**: Main product ASIN to analyze
    - **search_pages**: Number of search pages to analyze (1-5)
    - **max_competitors**: Maximum competitors to find (5-50)
    """
    try:
        logger.info(f"Starting competitor analysis for {analysis_request.asin}")
        
        # Check if main product exists in database
        with Database() as db:
            main_product = db.get_product(analysis_request.asin)
            if not main_product:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Product {analysis_request.asin} not found. Please scrape it first."
                )
        
        # Start competitor analysis
        competitors = service.find_competitors(analysis_request)
        
        return APIResponse(
            success=True,
            message=f"Found {len(competitors)} competitors",
            data={
                "main_asin": analysis_request.asin,
                "competitor_count": len(competitors),
                "competitors": competitors[:10],  # Return first 10 for response size
                "analysis_completed_at": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Competitor analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/competitors/{asin}", response_model=APIResponse)
async def get_competitors(
    asin: str,
    service: CompetitorService = Depends(get_competitor_service)
):
    """Get existing competitors for a product"""
    try:
        competitors = service.get_existing_competitors(asin.upper())
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(competitors)} competitors",
            data={
                "main_asin": asin.upper(),
                "competitor_count": len(competitors),
                "competitors": competitors
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get competitors for {asin}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/competitors/{asin}/refresh", response_model=APIResponse)
async def refresh_competitors(
    asin: str,
    search_pages: int = Query(2, ge=1, le=5, description="Number of search pages"),
    max_competitors: int = Query(20, ge=5, le=50, description="Maximum competitors"),
    service: CompetitorService = Depends(get_competitor_service)
):
    """Refresh competitor analysis by finding new competitors"""
    try:
        analysis_request = CompetitorAnalysisRequest(
            asin=asin.upper(),
            search_pages=search_pages,
            max_competitors=max_competitors
        )
        
        competitors = service.refresh_competitors(analysis_request)
        
        return APIResponse(
            success=True,
            message=f"Refreshed competitors: found {len(competitors)} new competitors",
            data={
                "main_asin": asin.upper(),
                "competitor_count": len(competitors),
                "competitors": competitors[:10]
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to refresh competitors for {asin}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/competitors/{asin}/pricing", response_model=APIResponse)
async def analyze_pricing(
    asin: str,
    service: CompetitorService = Depends(get_competitor_service)
):
    """Analyze pricing among competitors"""
    try:
        pricing_analysis = service.analyze_competitor_pricing(asin.upper())
        
        if "error" in pricing_analysis:
            raise HTTPException(status_code=404, detail=pricing_analysis["error"])
        
        return APIResponse(
            success=True,
            message="Pricing analysis completed",
            data={"pricing_analysis": pricing_analysis}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pricing analysis failed for {asin}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/competitors/{asin}/summary", response_model=APIResponse)
async def get_competitor_summary(
    asin: str,
    service: CompetitorService = Depends(get_competitor_service)
):
    """Get competitor analysis summary"""
    try:
        summary = service.get_competitor_summary(asin.upper())
        
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        
        return APIResponse(
            success=True,
            message="Competitor summary retrieved",
            data={"summary": summary}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get competitor summary for {asin}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# LLM analysis endpoints
@app.post("/api/llm/analyze", response_model=APIResponse)
async def llm_analysis(
    analysis_request: LLMAnalysisRequest,
    service: LLMService = Depends(get_llm_service)
):
    """
    Perform LLM analysis on product and competitors
    
    - **main_asin**: Product ASIN to analyze
    - **include_competitors**: Whether to include competitor analysis
    - **analysis_focus**: Focus areas (pricing, features, positioning, recommendations)
    """
    try:
        logger.info(f"Starting LLM analysis for {analysis_request.main_asin}")
        
        # Get main product and competitors from database
        with Database() as db:
            main_product = db.get_product(analysis_request.main_asin)
            if not main_product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product {analysis_request.main_asin} not found"
                )
            
            competitors = []
            if analysis_request.include_competitors:
                competitors = db.search_products({"parent_asin": analysis_request.main_asin})
        
        # Remove MongoDB _id fields
        main_product.pop('_id', None)
        for comp in competitors:
            comp.pop('_id', None)
        
        # Perform LLM analysis
        analysis_result = service.analyze_product_with_competitors(
            main_product=main_product,
            competitors=competitors,
            analysis_focus=analysis_request.analysis_focus
        )
        
        return APIResponse(
            success=True,
            message="LLM analysis completed successfully",
            data={
                "analysis": analysis_result.model_dump(),
                "main_product": {
                    "asin": main_product.get("asin"),
                    "title": main_product.get("title")
                },
                "competitor_count": len(competitors),
                "analysis_completed_at": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LLM analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/llm/analyze-single", response_model=APIResponse)
async def llm_analyze_single_product(
    asin: str,
    service: LLMService = Depends(get_llm_service)
):
    """Analyze single product without competitors using LLM"""
    try:
        with Database() as db:
            product = db.get_product(asin.upper())
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {asin} not found")
        
        product.pop('_id', None)
        analysis = service.analyze_single_product(product)
        
        return APIResponse(
            success=True,
            message="Single product analysis completed",
            data={
                "product": {
                    "asin": product.get("asin"),
                    "title": product.get("title")
                },
                "analysis": analysis
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Single product analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/llm/market-insights", response_model=APIResponse)
async def get_market_insights(
    limit: int = Query(20, ge=5, le=100, description="Number of products to analyze"),
    service: LLMService = Depends(get_llm_service)
):
    """Generate market insights from stored products"""
    try:
        # Get products from database
        with Database() as db:
            products_data = db.get_all_products(limit=limit)
        
        # Remove MongoDB _id fields
        for product in products_data:
            product.pop('_id', None)
        
        insights = service.generate_market_insights(products_data)
        
        return APIResponse(
            success=True,
            message="Market insights generated successfully",
            data={
                "insights": insights,
                "analyzed_product_count": len(products_data),
                "generated_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Market insights generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return HTTPException(status_code=422, detail=str(exc))


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return HTTPException(status_code=400, detail=str(exc))


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Amazon Product Competitor Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)