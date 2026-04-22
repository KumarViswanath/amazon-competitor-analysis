"""
Product service for handling Amazon product operations
"""
import logging
from typing import Dict, Any, List, Optional, Union
from src.oxylabs_service import OxylabsClient
from src.db import Database
from src.models import ProductDetails, ProductInput
from src.geo_utils import GeoLocationHandler

logger = logging.getLogger(__name__)


class ProductService:
    """Service for product-related operations"""
    
    def __init__(self):
        self.oxylabs_client = OxylabsClient()
    
    def parse_product_input(self, product_input: ProductInput) -> Dict[str, str]:
        """Parse and validate product input"""
        identifier = product_input.identifier.strip()
        identifier_type = product_input.identifier_type.lower()
        
        result = {
            "asin": None,
            "search_query": None,
            "original_input": identifier,
            "input_type": identifier_type
        }
        
        if identifier_type == "asin":
            if self.oxylabs_client.validate_asin(identifier):
                result["asin"] = identifier.upper()
            else:
                raise ValueError(f"Invalid ASIN format: {identifier}")
        
        elif identifier_type == "url":
            asin = self.oxylabs_client.extract_asin_from_url(identifier)
            if asin:
                result["asin"] = asin
            else:
                raise ValueError(f"Could not extract ASIN from URL: {identifier}")
        
        elif identifier_type == "name":
            result["search_query"] = identifier
        
        else:
            raise ValueError(f"Invalid identifier_type: {identifier_type}. Must be 'asin', 'url', or 'name'")
        
        return result
    
    def scrape_product_by_input(self, product_input: ProductInput) -> ProductDetails:
        """Scrape product based on input type"""
        parsed_input = self.parse_product_input(product_input)
        
        if parsed_input["asin"]:
            # Direct ASIN scraping
            return self.scrape_product_by_asin(
                asin=parsed_input["asin"],
                geo_location=product_input.zip_code,
                domain=product_input.domain
            )
        
        elif parsed_input["search_query"]:
            # Search and get first result
            return self.scrape_product_by_search(
                query=parsed_input["search_query"],
                geo_location=product_input.zip_code,
                domain=product_input.domain
            )
        
        else:
            raise ValueError("Unable to determine scraping method from input")
    
    def scrape_product_by_asin(
        self, 
        asin: str, 
        geo_location: Optional[str] = None, 
        domain: str = "com"
    ) -> ProductDetails:
        """Scrape product details by ASIN"""
        
        logger.info(f"Scraping product by ASIN: {asin} for domain: {domain}")
        
        # Validate and normalize geo-location
        if geo_location:
            geo_location = GeoLocationHandler.normalize_postal_code(geo_location, domain)
            logger.info(f"Using geo-location: {geo_location}")
        
        try:
            # Get product data from Oxylabs
            product_data = self.oxylabs_client.scrape_product_details(
                asin=asin,
                geo_location=geo_location,
                domain=domain
            )
            
            # Convert to ProductDetails model
            product_details = ProductDetails(**product_data)
            
            # Store in database
            with Database() as db:
                db.upsert_product(product_data)
            
            logger.info(f"Successfully scraped product: {product_details.title}")
            return product_details
            
        except Exception as e:
            logger.error(f"Failed to scrape product {asin}: {e}")
            raise Exception(f"Failed to scrape product: {str(e)}")
    
    def scrape_product_by_search(
        self, 
        query: str, 
        geo_location: Optional[str] = None, 
        domain: str = "com"
    ) -> ProductDetails:
        """Scrape product by searching and taking first result"""
        
        logger.info(f"Searching for product: {query} in domain: {domain}")
        
        # Validate and normalize geo-location  
        if geo_location:
            geo_location = GeoLocationHandler.normalize_postal_code(geo_location, domain)
            logger.info(f"Using geo-location: {geo_location}")
        
        try:
            # Search for products
            search_results = self.oxylabs_client.search_products(
                query=query,
                domain=domain,
                geo_location=geo_location,
                page=1
            )
            
            if not search_results:
                raise Exception(f"No products found for query: {query}")
            
            # Get the first result with an ASIN
            target_product = None
            for result in search_results:
                if result.get("asin"):
                    target_product = result
                    break
            
            if not target_product:
                raise Exception("No products found with valid ASIN")
            
            # Scrape detailed information
            return self.scrape_product_by_asin(
                asin=target_product["asin"],
                geo_location=geo_location,
                domain=domain
            )
            
        except Exception as e:
            logger.error(f"Failed to scrape product by search '{query}': {e}")
            raise Exception(f"Failed to find and scrape product: {str(e)}")
    
    def get_product_from_db(self, asin: str) -> Optional[ProductDetails]:
        """Get product from database"""
        try:
            with Database() as db:
                product_data = db.get_product(asin)
                if product_data:
                    # Remove MongoDB _id field for Pydantic model
                    product_data.pop('_id', None)
                    return ProductDetails(**product_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get product from DB: {e}")
            return None
    
    def list_products(self, limit: int = 100, skip: int = 0) -> List[ProductDetails]:
        """List all products from database"""
        try:
            with Database() as db:
                products_data = db.get_all_products(limit=limit, skip=skip)
                products = []
                for product_data in products_data:
                    # Remove MongoDB _id field
                    product_data.pop('_id', None)
                    try:
                        products.append(ProductDetails(**product_data))
                    except Exception as e:
                        logger.warning(f"Failed to parse product data: {e}")
                        continue
                return products
        except Exception as e:
            logger.error(f"Failed to list products: {e}")
            return []
    
    def search_products_in_db(
        self, 
        search_criteria: Dict[str, Any], 
        limit: int = 100
    ) -> List[ProductDetails]:
        """Search products in database"""
        try:
            with Database() as db:
                products_data = db.search_products(search_criteria, limit=limit)
                products = []
                for product_data in products_data:
                    # Remove MongoDB _id field
                    product_data.pop('_id', None)
                    try:
                        products.append(ProductDetails(**product_data))
                    except Exception as e:
                        logger.warning(f"Failed to parse product data: {e}")
                        continue
                return products
        except Exception as e:
            logger.error(f"Failed to search products: {e}")
            return []
    
    def update_product_in_db(self, asin: str, update_data: Dict[str, Any]) -> bool:
        """Update product in database"""
        try:
            with Database() as db:
                return db.update_product(asin, update_data)
        except Exception as e:
            logger.error(f"Failed to update product {asin}: {e}")
            return False
    
    def delete_product_from_db(self, asin: str) -> bool:
        """Delete product from database"""
        try:
            with Database() as db:
                return db.delete_product(asin)
        except Exception as e:
            logger.error(f"Failed to delete product {asin}: {e}")
            return False
    
    def get_product_stats(self) -> Dict[str, Any]:
        """Get product statistics"""
        try:
            with Database() as db:
                total_count = db.get_product_count()
                
                # Get counts by domain
                domain_stats = {}
                for domain in ["com", "in", "co.uk", "de", "fr", "it"]:
                    count = db.get_product_count({"amazon_domain": domain})
                    if count > 0:
                        domain_stats[domain] = count
                
                # Get recent products
                recent_products = db.get_all_products(limit=5)
                recent_asins = [p.get("asin") for p in recent_products if p.get("asin")]
                
                return {
                    "total_products": total_count,
                    "domain_distribution": domain_stats,
                    "recent_asins": recent_asins
                }
        except Exception as e:
            logger.error(f"Failed to get product stats: {e}")
            return {
                "total_products": 0,
                "domain_distribution": {},
                "recent_asins": []
            }