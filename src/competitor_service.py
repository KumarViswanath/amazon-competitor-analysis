"""
Competitor analysis service for finding and analyzing product competitors
"""
import logging
import re
from typing import List, Dict, Any, Optional, Set
from src.oxylabs_service import OxylabsClient
from src.db import Database
from src.models import ProductDetails, CompetitorAnalysisRequest
from src.geo_utils import GeoLocationHandler

logger = logging.getLogger(__name__)


class CompetitorService:
    """Service for competitor analysis operations"""
    
    def __init__(self):
        self.oxylabs_client = OxylabsClient()
    
    def clean_product_name(self, title: str) -> str:
        """Clean product name for better search results"""
        if not title:
            return ""
        
        # Remove brand names and common suffixes
        title = title.strip()
        
        # Remove everything after common separators
        separators = [" - ", " | ", " (", " ["]
        for sep in separators:
            if sep in title:
                title = title.split(sep)[0]
        
        # Remove common words that don't help in search
        remove_words = [
            "Amazon", "Brand", "Bestseller", "Choice", "Renewed",
            "Refurbished", "Used", "New", "Pack of", "Set of"
        ]
        
        words = title.split()
        filtered_words = []
        for word in words:
            if word not in remove_words:
                filtered_words.append(word)
        
        return " ".join(filtered_words).strip()
    
    def find_competitors(self, analysis_request: CompetitorAnalysisRequest) -> List[Dict[str, Any]]:
        """Find competitors for a given product"""
        
        logger.info(f"Finding competitors for ASIN: {analysis_request.asin}")
        
        # Get the main product from database
        with Database() as db:
            main_product = db.get_product(analysis_request.asin)
        
        if not main_product:
            raise Exception(f"Product with ASIN {analysis_request.asin} not found in database")
        
        # Extract search parameters from main product
        search_title = self.clean_product_name(main_product.get("title", ""))
        categories = main_product.get("categories", []) or main_product.get("category_path", [])
        domain = main_product.get("amazon_domain", "com")
        geo_location = main_product.get("geo_location")
        
        # If no geo_location in product, use default for domain
        if not geo_location:
            geo_location = GeoLocationHandler.get_default_postal_code(domain)
        else:
            # Normalize the existing geo_location
            geo_location = GeoLocationHandler.normalize_postal_code(geo_location, domain)
        
        logger.info(f"Searching with title: {search_title}")
        logger.info(f"Categories: {categories}")
        
        # Collect competitor ASINs from multiple search strategies
        competitor_asins = self._search_competitors_multi_strategy(
            search_title=search_title,
            categories=categories,
            domain=domain,
            geo_location=geo_location,
            pages=analysis_request.search_pages,
            main_asin=analysis_request.asin
        )
        
        # Limit to max competitors
        competitor_asins = list(competitor_asins)[:analysis_request.max_competitors]
        
        if not competitor_asins:
            logger.warning("No competitors found")
            return []
        
        logger.info(f"Found {len(competitor_asins)} unique competitor ASINs")
        
        # Scrape detailed competitor information
        competitors = self._scrape_competitor_details(
            competitor_asins, geo_location, domain
        )
        
        # Store competitors in database with parent_asin reference
        self._store_competitors(competitors, analysis_request.asin)
        
        return competitors
    
    def _search_competitors_multi_strategy(
        self,
        search_title: str,
        categories: List[str],
        domain: str,
        geo_location: str,
        pages: int,
        main_asin: str
    ) -> Set[str]:
        """Use multiple search strategies to find competitors"""
        
        competitor_asins = set()
        
        # Strategy 1: Basic title search
        competitors = self._search_by_title(
            title=search_title,
            domain=domain,
            geo_location=geo_location,
            pages=pages
        )
        competitor_asins.update(comp.get("asin") for comp in competitors if comp.get("asin"))
        
        # Strategy 2: Category-based searches
        for category in categories[:3]:  # Limit to top 3 categories
            if category and isinstance(category, str):
                competitors = self._search_by_category(
                    title=search_title,
                    category=category.strip(),
                    domain=domain,
                    geo_location=geo_location,
                    pages=min(2, pages)
                )
                competitor_asins.update(comp.get("asin") for comp in competitors if comp.get("asin"))
        
        # Strategy 3: Different sorting methods
        sort_methods = ["price_low_to_high", "price_high_to_low", "avg_customer_review"]
        for sort_method in sort_methods:
            competitors = self._search_with_sorting(
                title=search_title,
                sort_by=sort_method,
                domain=domain,
                geo_location=geo_location,
                pages=1  # Only first page for sorted results
            )
            competitor_asins.update(comp.get("asin") for comp in competitors if comp.get("asin"))
        
        # Remove the main product ASIN and any invalid ASINs
        competitor_asins.discard(main_asin)
        competitor_asins = {asin for asin in competitor_asins if asin and self.oxylabs_client.validate_asin(asin)}
        
        return competitor_asins
    
    def _search_by_title(
        self, title: str, domain: str, geo_location: str, pages: int
    ) -> List[Dict[str, Any]]:
        """Search competitors by product title"""
        
        results = []
        for page in range(1, pages + 1):
            try:
                search_results = self.oxylabs_client.search_products(
                    query=title,
                    domain=domain,
                    geo_location=geo_location,
                    page=page,
                    sort_by="featured"
                )
                results.extend(search_results)
            except Exception as e:
                logger.error(f"Failed to search page {page} for title '{title}': {e}")
                continue
        
        return results
    
    def _search_by_category(
        self, title: str, category: str, domain: str, geo_location: str, pages: int
    ) -> List[Dict[str, Any]]:
        """Search competitors within specific category"""
        
        results = []
        for page in range(1, pages + 1):
            try:
                search_results = self.oxylabs_client.search_products(
                    query=title,
                    domain=domain,
                    geo_location=geo_location,
                    page=page,
                    category=category
                )
                results.extend(search_results)
            except Exception as e:
                logger.error(f"Failed to search category '{category}' page {page}: {e}")
                continue
        
        return results
    
    def _search_with_sorting(
        self, title: str, sort_by: str, domain: str, geo_location: str, pages: int
    ) -> List[Dict[str, Any]]:
        """Search competitors with specific sorting"""
        
        results = []
        for page in range(1, pages + 1):
            try:
                search_results = self.oxylabs_client.search_products(
                    query=title,
                    domain=domain,
                    geo_location=geo_location,
                    page=page,
                    sort_by=sort_by
                )
                results.extend(search_results)
            except Exception as e:
                logger.error(f"Failed to search with sorting '{sort_by}' page {page}: {e}")
                continue
        
        return results
    
    def _scrape_competitor_details(
        self, competitor_asins: List[str], geo_location: str, domain: str
    ) -> List[Dict[str, Any]]:
        """Scrape detailed information for competitor ASINs"""
        
        logger.info(f"Scraping details for {len(competitor_asins)} competitors")
        
        competitors = []
        for i, asin in enumerate(competitor_asins, 1):
            try:
                logger.info(f"Scraping competitor {i}/{len(competitor_asins)}: {asin}")
                
                product_data = self.oxylabs_client.scrape_product_details(
                    asin=asin,
                    geo_location=geo_location,
                    domain=domain
                )
                
                competitors.append(product_data)
                
            except Exception as e:
                logger.error(f"Failed to scrape competitor {asin}: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(competitors)} out of {len(competitor_asins)} competitors")
        return competitors
    
    def _store_competitors(self, competitors: List[Dict[str, Any]], parent_asin: str):
        """Store competitors in database with parent product reference"""
        
        with Database() as db:
            for competitor in competitors:
                try:
                    # Add parent reference
                    competitor["parent_asin"] = parent_asin
                    competitor["is_competitor"] = True
                    
                    # Store/update in database
                    db.upsert_product(competitor)
                    
                except Exception as e:
                    logger.error(f"Failed to store competitor {competitor.get('asin')}: {e}")
                    continue
    
    def get_existing_competitors(self, main_asin: str) -> List[Dict[str, Any]]:
        """Get existing competitors from database"""
        
        try:
            with Database() as db:
                competitors = db.search_products({"parent_asin": main_asin})
                
                # Remove MongoDB _id fields
                for comp in competitors:
                    comp.pop('_id', None)
                
                return competitors
                
        except Exception as e:
            logger.error(f"Failed to get existing competitors for {main_asin}: {e}")
            return []
    
    def refresh_competitors(self, analysis_request: CompetitorAnalysisRequest) -> List[Dict[str, Any]]:
        """Refresh competitor analysis by finding new competitors"""
        
        logger.info(f"Refreshing competitors for ASIN: {analysis_request.asin}")
        
        # Delete existing competitors
        try:
            with Database() as db:
                # Get existing competitor ASINs
                existing_competitors = db.search_products({"parent_asin": analysis_request.asin})
                
                # Delete existing competitors
                for comp in existing_competitors:
                    if comp.get("asin"):
                        db.delete_product(comp["asin"])
                
                logger.info(f"Deleted {len(existing_competitors)} existing competitors")
        
        except Exception as e:
            logger.error(f"Failed to delete existing competitors: {e}")
        
        # Find new competitors
        return self.find_competitors(analysis_request)
    
    def analyze_competitor_pricing(self, main_asin: str) -> Dict[str, Any]:
        """Analyze pricing among competitors"""
        
        try:
            with Database() as db:
                # Get main product
                main_product = db.get_product(main_asin)
                if not main_product:
                    return {"error": "Main product not found"}
                
                # Get competitors
                competitors = db.search_products({"parent_asin": main_asin})
                
                main_price = main_product.get("price")
                if not main_price or not isinstance(main_price, (int, float)):
                    return {"error": "Main product price not available"}
                
                # Analyze competitor prices
                competitor_prices = []
                for comp in competitors:
                    price = comp.get("price")
                    if price and isinstance(price, (int, float)):
                        competitor_prices.append({
                            "asin": comp.get("asin"),
                            "title": comp.get("title"),
                            "price": price,
                            "currency": comp.get("currency"),
                            "price_difference": price - main_price,
                            "price_difference_pct": ((price - main_price) / main_price) * 100
                        })
                
                # Calculate statistics
                if competitor_prices:
                    prices = [cp["price"] for cp in competitor_prices]
                    analysis = {
                        "main_product": {
                            "asin": main_asin,
                            "title": main_product.get("title"),
                            "price": main_price,
                            "currency": main_product.get("currency")
                        },
                        "competitor_count": len(competitor_prices),
                        "price_analysis": {
                            "min_price": min(prices),
                            "max_price": max(prices),
                            "avg_price": sum(prices) / len(prices),
                            "median_price": sorted(prices)[len(prices) // 2]
                        },
                        "position": {
                            "cheaper_count": len([p for p in prices if p < main_price]),
                            "more_expensive_count": len([p for p in prices if p > main_price]),
                            "same_price_count": len([p for p in prices if p == main_price])
                        },
                        "competitors": sorted(competitor_prices, key=lambda x: x["price"])
                    }
                    return analysis
                
                else:
                    return {"error": "No competitors with valid pricing found"}
        
        except Exception as e:
            logger.error(f"Failed to analyze competitor pricing: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def get_competitor_summary(self, main_asin: str) -> Dict[str, Any]:
        """Get summary of competitor analysis"""
        
        try:
            with Database() as db:
                main_product = db.get_product(main_asin)
                competitors = db.search_products({"parent_asin": main_asin})
                
                if not main_product:
                    return {"error": "Main product not found"}
                
                summary = {
                    "main_product": {
                        "asin": main_asin,
                        "title": main_product.get("title"),
                        "price": main_product.get("price"),
                        "rating": main_product.get("rating"),
                        "currency": main_product.get("currency")
                    },
                    "competitor_count": len(competitors),
                    "analysis_available": len(competitors) > 0
                }
                
                if competitors:
                    # Quick stats
                    prices = [c.get("price") for c in competitors if c.get("price")]
                    ratings = [c.get("rating") for c in competitors if c.get("rating")]
                    
                    if prices:
                        summary["price_range"] = {"min": min(prices), "max": max(prices)}
                    
                    if ratings:
                        summary["rating_range"] = {"min": min(ratings), "max": max(ratings)}
                    
                    # Recent competitors
                    summary["recent_competitors"] = [
                        {
                            "asin": c.get("asin"),
                            "title": c.get("title", "")[:100] + "..." if len(c.get("title", "")) > 100 else c.get("title", ""),
                            "price": c.get("price"),
                            "rating": c.get("rating")
                        }
                        for c in competitors[:5]  # First 5 competitors
                    ]
                
                return summary
        
        except Exception as e:
            logger.error(f"Failed to get competitor summary: {e}")
            return {"error": f"Failed to get summary: {str(e)}"}