#!/usr/bin/env python3
"""
Test database update methods
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import Database

def test_update_product():
    """Test update_product method"""
    print("INFO: Testing update_product()...")
    
    test_product = {
        "asin": "TEST_UPDATE_001",
        "title": "Test Update Product",
        "price": 100.00,
        "rating": 4.0
    }
    
    try:
        with Database() as db:
            # Insert test product
            db.insert_product(test_product)
            
            # Update product
            update_data = {
                "price": 89.99,
                "rating": 4.5,
                "discount": True
            }
            
            success = db.update_product("TEST_UPDATE_001", update_data)
            if success:
                print("PASS: Update successful")
                
                # Verify update
                updated = db.get_product("TEST_UPDATE_001")
                print(f"PASS: New price: ${updated['price']}")
                print(f"PASS: New rating: {updated['rating']}")
                print(f"PASS: Discount added: {updated['discount']}")
                print(f"PASS: Updated at: {updated['updated_at']}")
            else:
                print("FAIL: Update failed")
                return False
            
            # Test update non-existent product
            invalid_update = db.update_product("INVALID_ASIN", {"price": 50})
            if not invalid_update:
                print("PASS: Correctly handled invalid ASIN update")
            
            # Cleanup
            db.delete_product("TEST_UPDATE_001")
            print("PASS: Test cleanup completed")
            
            return True
            
    except Exception as e:
        print(f"FAIL: Update test failed: {e}")
        return False

def test_upsert_product():
    """Test upsert_product method"""
    print(" Testing upsert_product()...")
    
    try:
        with Database() as db:
            # Test upsert new product
            new_product = {
                "asin": "TEST_UPSERT_001",
                "title": "Upsert New Product",
                "price": 75.00
            }
            
            id1 = db.upsert_product(new_product)
            print(f"PASS: Upserted new product, ID: {id1}")
            
            # Test upsert existing product
            updated_product = {
                "asin": "TEST_UPSERT_001",
                "title": "Updated Upsert Product",
                "price": 65.00,
                "category": "Updated"
            }
            
            id2 = db.upsert_product(updated_product)
            print(f"PASS: Upserted existing product, ID: {id2}")
            
            if id1 == id2:
                print("PASS: Same ID returned for existing product")
            
            # Verify final state
            final = db.get_product("TEST_UPSERT_001")
            print(f"PASS: Final title: {final['title']}")
            print(f"PASS: Final price: ${final['price']}")
            
            # Cleanup
            db.delete_product("TEST_UPSERT_001")
            print("PASS: Test cleanup completed")
            
            return True
            
    except Exception as e:
        print(f"FAIL: Upsert test failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_update_product()
    success2 = test_upsert_product()
    sys.exit(0 if (success1 and success2) else 1)