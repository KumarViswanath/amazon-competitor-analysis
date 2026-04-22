#!/usr/bin/env python3
"""
Test database insert methods
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import Database

def test_insert_product():
    """Test product insertion"""
    print("Testing insert_product()...")
    
    test_product = {
        "asin": "TEST_INSERT_001",
        "title": "Test Insert Product",
        "price": 99.99,
        "rating": 4.2,
        "brand": "TestBrand"
    }
    
    try:
        with Database() as db:
            # Insert product
            product_id = db.insert_product(test_product)
            print(f"PASS: Product inserted with ID: {product_id}")
            
            # Verify insertion
            retrieved = db.get_product("TEST_INSERT_001")
            if retrieved:
                print(f"PASS: Product verified: {retrieved['title']}")
                print(f"PASS: Created at: {retrieved['created_at']}")
            
            # Test duplicate handling
            duplicate_id = db.insert_product(test_product)
            print(f"PASS: Duplicate handled, ID: {duplicate_id}")
            
            # Cleanup
            db.delete_product("TEST_INSERT_001")
            print("PASS: Test cleanup completed")
            
            return True
            
    except Exception as e:
        print(f"FAIL: Insert test failed: {e}")
        return False

def test_insert_validation():
    """Test insert validation"""
    print("INFO: Testing insert validation...")
    
    try:
        with Database() as db:
            # Test missing ASIN
            try:
                db.insert_product({"title": "No ASIN Product"})
                print("FAIL: Should have failed for missing ASIN")
                return False
            except ValueError:
                print("PASS: Correctly rejected product without ASIN")
            
            return True
            
    except Exception as e:
        print(f"FAIL: Validation test failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_insert_product()
    success2 = test_insert_validation()
    sys.exit(0 if (success1 and success2) else 1)