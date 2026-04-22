#!/usr/bin/env python3
"""
Comprehensive test script for the Amazon Competitor Analysis API
Tests the complete workflow including database persistence
"""
import asyncio
import requests
import json
import time
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_ASIN = "B08N5WRWNW"  # Echo Dot - good for testing
TEST_ZIP = "10001"
TEST_DOMAIN = "com"

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_health_check(self) -> bool:
        """Test API health check"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log(f"Health check passed: {data['message']}")
                return True
            else:
                self.log(f"Health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Health check error: {e}", "ERROR")
            return False
    
    def test_product_scraping(self) -> Dict[str, Any]:
        """Test product scraping and database storage"""
        self.log("Testing product scraping...")
        
        payload = {
            "identifier": TEST_ASIN,
            "identifier_type": "asin",
            "zip_code": TEST_ZIP,
            "domain": TEST_DOMAIN
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/products/scrape",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                product_data = data["data"]["product"]
                self.log(f"Product scraped successfully: {product_data['title']}")
                self.log(f"Price: {product_data.get('currency', '$')}{product_data.get('price', 'N/A')}")
                self.log(f"Rating: {product_data.get('rating', 'N/A')}")
                return product_data
            else:
                self.log(f"Product scraping failed: {response.status_code} - {response.text}", "ERROR")
                return {}
                
        except Exception as e:
            self.log(f"Product scraping error: {e}", "ERROR")
            return {}
    
    def test_product_retrieval(self, asin: str) -> bool:
        """Test product retrieval from database"""
        self.log(f"Testing product retrieval from database...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/products/{asin}")
            
            if response.status_code == 200:
                data = response.json()
                product = data["data"]["product"]
                self.log(f"Product retrieved from DB: {product['title']}")
                return True
            elif response.status_code == 404:
                self.log(f"Product {asin} not found in database", "WARN")
                return False
            else:
                self.log(f"Product retrieval failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Product retrieval error: {e}", "ERROR")
            return False
    
    def test_competitor_analysis(self, asin: str) -> Dict[str, Any]:
        """Test competitor analysis"""
        self.log("Testing competitor analysis...")
        
        payload = {
            "asin": asin,
            "search_pages": 2,
            "max_competitors": 10
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/competitors/analyze",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                competitor_count = data["data"]["competitor_count"]
                self.log(f"Competitor analysis completed: {competitor_count} competitors found")
                return data["data"]
            else:
                self.log(f"Competitor analysis failed: {response.status_code} - {response.text}", "ERROR")
                return {}
                
        except Exception as e:
            self.log(f"Competitor analysis error: {e}", "ERROR")
            return {}
    
    def test_competitor_retrieval(self, asin: str) -> bool:
        """Test competitor retrieval from database"""
        self.log("Testing competitor retrieval from database...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/competitors/{asin}")
            
            if response.status_code == 200:
                data = response.json()
                competitor_count = data["data"]["competitor_count"]
                self.log(f"Retrieved {competitor_count} competitors from database")
                
                if competitor_count > 0:
                    # Show a few competitors
                    competitors = data["data"]["competitors"][:3]
                    for i, comp in enumerate(competitors, 1):
                        title = comp.get("title", "Unknown")[:50]
                        price = comp.get("price", "N/A")
                        self.log(f"  {i}. {title}... - ${price}")
                
                return competitor_count > 0
            else:
                self.log(f"Competitor retrieval failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Competitor retrieval error: {e}", "ERROR")
            return False
    
    def test_pricing_analysis(self, asin: str) -> bool:
        """Test pricing analysis"""
        self.log("Testing pricing analysis...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/competitors/{asin}/pricing")
            
            if response.status_code == 200:
                data = response.json()
                analysis = data["data"]["pricing_analysis"]
                
                main_product = analysis["main_product"]
                price_analysis = analysis["price_analysis"]
                position = analysis["position"]
                
                self.log(f"Main product price: {main_product['currency']}{main_product['price']}")
                self.log(f"Competitor price range: ${price_analysis['min_price']:.2f} - ${price_analysis['max_price']:.2f}")
                self.log(f"Position: {position['cheaper_count']} cheaper, {position['more_expensive_count']} more expensive")
                
                return True
            elif response.status_code == 404:
                self.log("No pricing data available for analysis", "WARN")
                return False
            else:
                self.log(f"Pricing analysis failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Pricing analysis error: {e}", "ERROR")
            return False
    
    def test_llm_analysis(self, asin: str) -> bool:
        """Test LLM analysis"""
        self.log("Testing LLM analysis...")
        
        payload = {
            "main_asin": asin,
            "include_competitors": True,
            "analysis_focus": ["pricing", "positioning", "recommendations"]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/llm/analyze",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis = data["data"]["analysis"]
                
                self.log("LLM Analysis completed:")
                self.log(f"  Summary: {analysis['summary'][:100]}...")
                self.log(f"  Top competitors analyzed: {len(analysis['top_competitors'])}")
                self.log(f"  Recommendations provided: {len(analysis['recommendations'])}")
                
                return True
            else:
                self.log(f"LLM analysis failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"LLM analysis error: {e}", "ERROR")
            return False
    
    def test_database_persistence(self) -> bool:
        """Test database persistence by checking data across requests"""
        self.log("Testing database persistence...")
        
        try:
            # Get product stats
            response = self.session.get(f"{self.base_url}/api/products/stats")
            
            if response.status_code == 200:
                data = response.json()
                stats = data["data"]["statistics"]
                
                self.log(f"Database contains {stats['total_products']} products")
                self.log(f"Domain distribution: {stats['domain_distribution']}")
                self.log(f"Recent ASINs: {stats['recent_asins']}")
                
                return stats['total_products'] > 0
            else:
                self.log(f"Database stats failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Database persistence test error: {e}", "ERROR")
            return False
    
    def test_product_search(self) -> bool:
        """Test product search functionality"""
        self.log("Testing product search...")
        
        try:
            # Search for Echo products
            params = {
                "query": "Echo",
                "limit": 5
            }
            
            response = self.session.get(
                f"{self.base_url}/api/products/search",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                products = data["data"]["products"]
                
                self.log(f"Search found {len(products)} products")
                for product in products:
                    title = product.get("title", "Unknown")[:40]
                    self.log(f"  - {title}...")
                
                return len(products) > 0
            else:
                self.log(f"Product search failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Product search error: {e}", "ERROR")
            return False
    
    def run_comprehensive_test(self):
        """Run complete workflow test"""
        self.log("=" * 60)
        self.log("STARTING COMPREHENSIVE API WORKFLOW TEST")
        self.log("=" * 60)
        
        results = {}
        
        # Test 1: Health Check
        results["health_check"] = self.test_health_check()
        
        # Test 2: Product Scraping
        product_data = self.test_product_scraping()
        results["product_scraping"] = bool(product_data)
        
        if product_data:
            asin = product_data.get("asin", TEST_ASIN)
            
            # Test 3: Product Retrieval from DB
            results["product_retrieval"] = self.test_product_retrieval(asin)
            
            # Test 4: Competitor Analysis
            competitor_data = self.test_competitor_analysis(asin)
            results["competitor_analysis"] = bool(competitor_data)
            
            # Test 5: Competitor Retrieval from DB
            results["competitor_retrieval"] = self.test_competitor_retrieval(asin)
            
            # Test 6: Pricing Analysis
            results["pricing_analysis"] = self.test_pricing_analysis(asin)
            
            # Test 7: LLM Analysis
            results["llm_analysis"] = self.test_llm_analysis(asin)
        
        # Test 8: Database Persistence
        results["database_persistence"] = self.test_database_persistence()
        
        # Test 9: Product Search
        results["product_search"] = self.test_product_search()
        
        # Summary
        self.log("=" * 60)
        self.log("TEST RESULTS SUMMARY")
        self.log("=" * 60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            self.log(f"{test_name:.<30} {status}")
        
        self.log(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            self.log("All tests passed! System is working correctly.", "SUCCESS")
        else:
            self.log(f"{total - passed} test(s) failed. Check logs above.", "ERROR")
        
        return results


def main():
    """Main test function"""
    print("Amazon Competitor Analysis API - Comprehensive Test Suite")
    print("Make sure the API server is running on http://localhost:8000")
    print()
    
    # Wait for user confirmation
    input("Press Enter to start testing...")
    
    # Run tests
    tester = APITester()
    results = tester.run_comprehensive_test()
    
    return results


if __name__ == "__main__":
    main()