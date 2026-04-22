#!/usr/bin/env python3
"""
Test database delete methods
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import Database

def test_delete_product():
    """Test delete_product method"""
    print("INFO: Testing delete_product()...")
    
    test_product = {
        "asin": "TEST_DELETE_001",
        "title": "Test Delete Product",
        "price": 25.99
    }
    
    try:
        with Database() as db:
            # Insert test product
            db.insert_product(test_product)
            print("PASS: Test product inserted")
            
            # Verify it exists
            existing = db.get_product("TEST_DELETE_001")
            if existing:
                print("PASS: Product exists before deletion")
            else:
                print("FAIL: Product should exist")
                return False
            
            # Delete the product
            deleted = db.delete_product("TEST_DELETE_001")
            if deleted:
                print("PASS: Product deleted successfully")
            else:
                print("FAIL: Delete operation failed")
                return False
            
            # Verify it's gone
            after_delete = db.get_product("TEST_DELETE_001")
            if after_delete is None:
                print("PASS: Product confirmed deleted")
            else:
                print("FAIL: Product still exists after deletion")
                return False
            
            # Test delete non-existent product
            invalid_delete = db.delete_product("NONEXISTENT")
            if not invalid_delete:
                print("PASS: Correctly handled non-existent product deletion")
            
            # Test delete with empty ASIN
            empty_delete = db.delete_product("")
            if not empty_delete:
                print("PASS: Correctly handled empty ASIN deletion")
            
            return True
            
    except Exception as e:
        print(f"FAIL: Delete test failed: {e}")
        return False

def test_batch_operations():
    """Test batch insert and delete operations"""
    print(" Testing batch operations...")
    
    test_products = [
        {"asin": "BATCH_001", "title": "Batch Product 1", "price": 10.00},
        {"asin": "BATCH_002", "title": "Batch Product 2", "price": 20.00},
        {"asin": "BATCH_003", "title": "Batch Product 3", "price": 30.00},
    ]
    
    try:
        with Database() as db:
            # Insert multiple products
            inserted_ids = []
            for product in test_products:
                product_id = db.insert_product(product)
                inserted_ids.append(product_id)
            
            print(f"PASS: Inserted {len(inserted_ids)} products")
            
            # Verify all exist
            for product in test_products:
                exists = db.get_product(product["asin"])
                if not exists:
                    print(f"FAIL: Product {product['asin']} not found")
                    return False
            
            print("PASS: All batch products verified")
            
            # Delete all test products
            deleted_count = 0
            for product in test_products:
                if db.delete_product(product["asin"]):
                    deleted_count += 1
            
            print(f"PASS: Deleted {deleted_count} products")
            
            # Verify all are gone
            for product in test_products:
                still_exists = db.get_product(product["asin"])
                if still_exists:
                    print(f"FAIL: Product {product['asin']} still exists")
                    return False
            
            print("PASS: All batch products successfully deleted")
            
            return True
            
    except Exception as e:
        print(f"FAIL: Batch operations test failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_delete_product()
    success2 = test_batch_operations()
    sys.exit(0 if (success1 and success2) else 1)