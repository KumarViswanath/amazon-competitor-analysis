"""
Oxylabs Web Scraper API client for Amazon product scraping
"""
import os
import re
import time
import requests
import logging
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse, parse_qs
from .geo_utils import GeoLocationHandler

logger = logging.getLogger(__name__)

class OxylabsClient:
    """Client for Oxylabs Web Scraper API"""
    
    def __init__(self):
        self.base_url = "https://realtime.oxylabs.io/v1/queries"
        self.username = os.getenv("OXYLABS_USERNAME")
        self.password = os.getenv("OXYLABS_PASSWORD")
        
        if not self.username or not self.password:
            raise ValueError("OXYLABS_USERNAME and OXYLABS_PASSWORD environment variables must be set")
    
    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to Oxylabs API"""
        try:
            response = requests.post(
                self.base_url,
                auth=(self.username, self.password),
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Oxylabs request successful for source: {payload.get('source')}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Oxylabs API request failed: {e}")
            raise Exception(f"Failed to scrape data: {str(e)}")
    
    def _extract_content(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract content from Oxylabs response"""
        if isinstance(response_data, dict):
            # Check for results array first
            if "results" in response_data and isinstance(response_data["results"], list) and response_data["results"]:
                first_result = response_data["results"][0]
                if isinstance(first_result, dict) and "content" in first_result:
                    return first_result.get("content", {}) or {}
            
            # Fallback to direct content
            if "content" in response_data:
                return response_data.get("content", {})
        
        return response_data if isinstance(response_data, dict) else {}
    
    def extract_asin_from_url(self, url: str) -> Optional[str]:
        """Extract ASIN from Amazon URL"""
        if not url or not isinstance(url, str):
            return None
            
        # Common ASIN patterns in Amazon URLs
        asin_patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'/product/([A-Z0-9]{10})',
            r'asin=([A-Z0-9]{10})',
            r'/([A-Z0-9]{10})(?:/|$)'
        ]
        
        for pattern in asin_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def validate_asin(self, asin: str) -> bool:
        """Validate ASIN format"""
        if not asin or not isinstance(asin, str):
            return False
        return bool(re.match(r'^[A-Z0-9]{10}$', asin.strip().upper()))
    
    def scrape_product_details(
        self, 
        asin: str, 
        geo_location: Optional[str] = None, 
        domain: str = "com"
    ) -> Dict[str, Any]:
        """Scrape detailed product information by ASIN"""
        
        if not self.validate_asin(asin):
            raise ValueError(f"Invalid ASIN format: {asin}")
        
        # Handle geo-location intelligently
        if geo_location:
            geo_location = GeoLocationHandler.normalize_postal_code(geo_location, domain)
        else:
            geo_location = GeoLocationHandler.get_default_postal_code(domain)
            
        payload = {
            "source": "amazon_product",
            "query": asin.strip().upper(),
            "geo_location": geo_location,
            "domain": domain,
            "parse": True,
            "context": [
                {"key": "autoselect_variant", "value": False}
            ]
        }
        
        logger.info(f"Scraping product details for ASIN: {asin}")
        raw_response = self._make_request(payload)
        content = self._extract_content(raw_response)
        
        # Normalize the product data
        normalized = self._normalize_product_data(content)
        
        # Ensure ASIN is set
        if not normalized.get("asin"):
            normalized["asin"] = asin.upper()
        
        # Add metadata
        normalized["amazon_domain"] = domain
        normalized["geo_location"] = geo_location
        
        return normalized
    
    def _normalize_product_data(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize product data from Oxylabs response"""
        
        # Extract category path
        category_path = []
        if content.get("category_path"):
            category_path = [cat.strip() for cat in content["category_path"] if cat and isinstance(cat, str)]
        
        # Extract images
        images = []
        if content.get("images"):
            if isinstance(content["images"], list):
                images = [img for img in content["images"] if img and isinstance(img, str)]
            elif isinstance(content["images"], str):
                images = [content["images"]]
        
        # Extract features/bullets
        features = []
        if content.get("feature_bullets"):
            if isinstance(content["feature_bullets"], list):
                features = [f.strip() for f in content["feature_bullets"] if f and isinstance(f, str)]
        
        # Extract specifications
        specifications = {}
        if content.get("specifications"):
            if isinstance(content["specifications"], dict):
                specifications = content["specifications"]
            elif isinstance(content["specifications"], list):
                for spec in content["specifications"]:
                    if isinstance(spec, dict) and "name" in spec and "value" in spec:
                        specifications[spec["name"]] = spec["value"]
        
        return {
            "asin": content.get("asin"),
            "title": content.get("title") or content.get("product_title"),
            "brand": content.get("brand") or content.get("manufacturer"),
            "price": self._extract_price(content.get("price")),
            "currency": content.get("currency"),
            "rating": self._extract_rating(content.get("rating")),
            "review_count": self._extract_review_count(content.get("reviews_count") or content.get("review_count")),
            "stock": content.get("stock") or content.get("availability"),
            "images": images,
            "categories": content.get("category", []) or content.get("categories", []),
            "category_path": category_path,
            "description": content.get("description") or content.get("product_description"),
            "features": features,
            "specifications": specifications,
            "url": content.get("url") or content.get("product_url"),
        }
    
    def _extract_price(self, price_data: Any) -> Optional[float]:
        """Extract price as float from various formats"""
        if price_data is None:
            return None
        
        if isinstance(price_data, (int, float)):
            return float(price_data)
        
        if isinstance(price_data, str):
            # Remove currency symbols and extract numbers
            price_str = re.sub(r'[^\d.,]', '', price_data)
            if price_str:
                try:
                    # Handle comma as decimal separator
                    if ',' in price_str and '.' in price_str:
                        # Format: 1,234.56
                        price_str = price_str.replace(',', '')
                    elif ',' in price_str and price_str.count(',') == 1 and len(price_str.split(',')[1]) <= 2:
                        # Format: 1234,56 (European format)
                        price_str = price_str.replace(',', '.')
                    return float(price_str)
                except ValueError:
                    pass
        
        return None
    
    def _extract_rating(self, rating_data: Any) -> Optional[float]:
        """Extract rating as float"""
        if rating_data is None:
            return None
        
        if isinstance(rating_data, (int, float)):
            return float(rating_data)
        
        if isinstance(rating_data, str):
            # Extract number from string like "4.5 out of 5 stars"
            match = re.search(r'(\d+\.?\d*)', rating_data)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
        
        return None
    
    def _extract_review_count(self, review_data: Any) -> Optional[int]:
        """Extract review count as integer"""
        if review_data is None:
            return None
        
        if isinstance(review_data, int):
            return review_data
        
        if isinstance(review_data, str):
            # Extract number from strings like "1,234 reviews" or "1.2K reviews"
            review_str = review_data.upper().replace(',', '')
            
            # Handle K, M notations
            if 'K' in review_str:
                match = re.search(r'(\d+\.?\d*)K', review_str)
                if match:
                    return int(float(match.group(1)) * 1000)
            elif 'M' in review_str:
                match = re.search(r'(\d+\.?\d*)M', review_str)
                if match:
                    return int(float(match.group(1)) * 1000000)
            else:
                match = re.search(r'(\d+)', review_str)
                if match:
                    return int(match.group(1))
        
        return None
    
    def search_products(
        self,
        query: str,
        domain: str = "com",
        geo_location: Optional[str] = None,
        page: int = 1,
        sort_by: str = "featured",
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for products on Amazon"""
        
        # Handle geo-location intelligently
        if geo_location:
            geo_location = GeoLocationHandler.normalize_postal_code(geo_location, domain)
        else:
            geo_location = GeoLocationHandler.get_default_postal_code(domain)
            
        payload = {
            "source": "amazon_search",
            "query": query.strip(),
            "domain": domain,
            "geo_location": geo_location,
            "page": page,
            "sort_by": sort_by,
            "parse": True
        }
        
        # Add category filter if specified
        if category:
            payload["refinements"] = {"category": category}
        
        logger.info(f"Searching products with query: {query}")
        raw_response = self._make_request(payload)
        content = self._extract_content(raw_response)
        
        # Extract search results
        items = self._extract_search_results(content)
        
        # Normalize search results
        normalized_results = []
        for item in items:
            normalized = self._normalize_search_result(item)
            if normalized:
                normalized_results.append(normalized)
        
        return normalized_results
    
    def _extract_search_results(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract search result items from content"""
        items = []
        
        if not isinstance(content, dict):
            return items
        
        # Check different result structures
        if "results" in content:
            results = content["results"]
            if isinstance(results, dict):
                # Extract organic and paid results
                if "organic" in results and isinstance(results["organic"], list):
                    items.extend(results["organic"])
                if "paid" in results and isinstance(results["paid"], list):
                    items.extend(results["paid"])
            elif isinstance(results, list):
                items.extend(results)
        elif "products" in content and isinstance(content["products"], list):
            items.extend(content["products"])
        
        return items
    
    def _normalize_search_result(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize individual search result"""
        if not isinstance(item, dict):
            return None
        
        asin = item.get("asin") or item.get("product_asin")
        title = item.get("title") or item.get("product_title")
        
        # Skip items without ASIN or title
        if not (asin or title):
            return None
        
        return {
            "asin": asin,
            "title": title,
            "price": self._extract_price(item.get("price")),
            "currency": item.get("currency"),
            "rating": self._extract_rating(item.get("rating")),
            "review_count": self._extract_review_count(item.get("reviews_count") or item.get("review_count")),
            "category": item.get("category"),
            "brand": item.get("brand"),
            "url": item.get("url") or item.get("product_url"),
            "image": item.get("image") or item.get("product_image")
        }
    
    def scrape_multiple_products(
        self,
        asins: List[str],
        geo_location: Optional[str] = None,
        domain: str = "com",
        delay: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Scrape multiple products with rate limiting"""
        
        # Handle geo-location intelligently
        if geo_location:
            geo_location = GeoLocationHandler.normalize_postal_code(geo_location, domain)
        else:
            geo_location = GeoLocationHandler.get_default_postal_code(domain)
            
        results = []
        valid_asins = [asin for asin in asins if self.validate_asin(asin)]
        
        logger.info(f"Scraping {len(valid_asins)} products with geo-location: {geo_location}")
        
        for i, asin in enumerate(valid_asins, 1):
            try:
                logger.info(f"Scraping product {i}/{len(valid_asins)}: {asin}")
                product_data = self.scrape_product_details(asin, geo_location, domain)
                results.append(product_data)
                
                # Rate limiting
                if i < len(valid_asins):
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Failed to scrape product {asin}: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(results)} out of {len(valid_asins)} products")
        return results