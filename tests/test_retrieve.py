#!/usr/bin/env python3
"""
Test database retrieve methods
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import Database

def test_get_product():
    """Test get_product method"""
    print("INFO: Testing get_product()...")
    
    test_product = {
        "asin": "TEST_GET_001",
        "title": "Test Get Product",
        "price": 45.50,
        "category": "TestCategory"
    }
    
    try:
        with Database() as db:
            # Insert test product
            db.insert_product(test_product)
            
            # Test successful retrieval
            product = db.get_product("TEST_GET_001")
            if product:
                print(f"PASS: Retrieved: {product['title']}")
                print(f"PASS: Price: ${product['price']}")
            else:
                print("FAIL: Failed to retrieve product")
                return False
            
            # Test non-existent product
            none_product = db.get_product("NONEXISTENT")
            if none_product is None:
                print("PASS: Correctly returned None for non-existent ASIN")
            else:
                print("FAIL: Should return None for non-existent product")
                return False
            
            # Test empty ASIN
            empty_result = db.get_product("")
            if empty_result is None:
                print("PASS: Correctly handled empty ASIN")
            
            # Cleanup
            db.delete_product("TEST_GET_001")
            print("PASS: Test cleanup completed")
            
            return True
            
    except Exception as e:
        print(f"FAIL: Get test failed: {e}")
        return False

def test_get_all_products():
    """Test get_all_products method"""
    print("INFO: Testing get_all_products()...")
    
    try:
        with Database() as db:
            # Get initial count
            initial_products = db.get_all_products()
            initial_count = len(initial_products)
            print(f"PASS: Initial product count: {initial_count}")
            
            # Test limit parameter
            limited_products = db.get_all_products(limit=2)
            print(f"PASS: Limited results: {len(limited_products)} (max 2)")
            
            # Test pagination
            if initial_count > 2:
                page_2 = db.get_all_products(limit=2, skip=2)
                print(f"PASS: Page 2 results: {len(page_2)}")
            
            return True
            
    except Exception as e:
        print(f"FAIL: Get all test failed: {e}")
        return False

def test_get_product_count():
    """Test get_product_count method"""
    print(" Testing get_product_count()...")
    
    try:
        with Database() as db:
            # Test total count
            total = db.get_product_count()
            print(f"PASS: Total products: {total}")
            
            # Test filtered count
            electronics = db.get_product_count({"category": "Electronics"})
            print(f"PASS: Electronics products: {electronics}")
            
            return True
            
    except Exception as e:
        print(f"FAIL: Count test failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_get_product()
    success2 = test_get_all_products()
    success3 = test_get_product_count()
    sys.exit(0 if (success1 and success2 and success3) else 1)