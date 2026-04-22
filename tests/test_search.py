#!/usr/bin/env python3
"""
Test database search methods
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import Database

def test_search_products():
    """Test search_products method"""
    print("INFO: Testing search_products()...")
    
    test_products = [
        {
            "asin": "TEST_SEARCH_001",
            "title": "Gaming Laptop",
            "price": 1299.99,
            "category": "Electronics",
            "rating": 4.5,
            "brand": "TestBrand"
        },
        {
            "asin": "TEST_SEARCH_002",
            "title": "Wireless Mouse",
            "price": 29.99,
            "category": "Electronics",
            "rating": 4.2,
            "brand": "TestBrand"
        },
        {
            "asin": "TEST_SEARCH_003",
            "title": "Cookbook",
            "price": 19.99,
            "category": "Books",
            "rating": 4.8,
            "brand": "Publisher"
        }
    ]
    
    try:
        with Database() as db:
            # Insert test products
            for product in test_products:
                db.insert_product(product)
            print("PASS: Test products inserted")
            
            # Search by category
            electronics = db.search_products({"category": "Electronics"})
            print(f"PASS: Electronics found: {len(electronics)}")
            
            # Search by price range
            affordable = db.search_products({"price": {"$lt": 100}})
            print(f"PASS: Products under $100: {len(affordable)}")
            
            # Search by rating
            high_rated = db.search_products({"rating": {"$gte": 4.5}})
            print(f"PASS: High rated products (4.5+): {len(high_rated)}")
            
            # Search by brand
            brand_products = db.search_products({"brand": "TestBrand"})
            print(f"PASS: TestBrand products: {len(brand_products)}")
            
            # Complex search
            complex_search = db.search_products({
                "category": "Electronics",
                "price": {"$lt": 50}
            })
            print(f"PASS: Cheap electronics: {len(complex_search)}")
            
            # Search with limit
            limited_search = db.search_products({}, limit=2)
            print(f"PASS: Limited search results: {len(limited_search)}")
            
            # Cleanup
            for product in test_products:
                db.delete_product(product["asin"])
            print("PASS: Test cleanup completed")
            
            return True
            
    except Exception as e:
        print(f"FAIL: Search test failed: {e}")
        return False

def test_advanced_queries():
    """Test advanced MongoDB queries"""
    print(" Testing advanced queries...")
    
    try:
        with Database() as db:
            # Test text search (if you have existing data)
            current_count = db.get_product_count()
            print(f"PASS: Current database has {current_count} products")
            
            if current_count > 0:
                # Test regex search on existing data
                echo_products = db.search_products({
                    "title": {"$regex": "Echo", "$options": "i"}
                })
                print(f"PASS: Products with 'Echo' in title: {len(echo_products)}")
                
                # Test price range on existing data
                mid_range = db.search_products({
                    "price": {"$gte": 50, "$lte": 200}
                })
                print(f"PASS: Products $50-$200: {len(mid_range)}")
            
            return True
            
    except Exception as e:
        print(f"FAIL: Advanced query test failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_search_products()
    success2 = test_advanced_queries()
    sys.exit(0 if (success1 and success2) else 1)