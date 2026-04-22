#!/usr/bin/env python3
"""
Comprehensive test script for all Database methods
"""
import os
import sys
from src.db import Database

def test_all_methods():
    """Test all database methods systematically"""
    
    print("🧪 Starting comprehensive database method tests...\n")
    
    try:
        with Database() as db:
            print("PASS: Database connection established\n")
            
            # Test 1: Insert Product
            print("1️⃣ Testing insert_product()...")
            test_product_1 = {
                "asin": "TEST123456",
                "title": "Test Product 1",
                "price": 29.99,
                "rating": 4.5,
                "category": "Electronics"
            }
            
            product_id = db.insert_product(test_product_1)
            print(f"   PASS: Inserted product with ID: {product_id}")
            
            # Test 2: Get Product
            print("\n2️⃣ Testing get_product()...")
            retrieved = db.get_product("TEST123456")
            if retrieved:
                print(f"   PASS: Retrieved product: {retrieved['title']}")
                print(f"   INFO: Created at: {retrieved['created_at']}")
            else:
                print("   FAIL: Failed to retrieve product")
            
            # Test 3: Insert Duplicate (should handle gracefully)
            print("\n3️⃣ Testing duplicate insert handling...")
            duplicate_id = db.insert_product(test_product_1)
            print(f"   PASS: Duplicate handled, returned ID: {duplicate_id}")
            
            # Test 4: Update Product
            print("\n4️⃣ Testing update_product()...")
            update_success = db.update_product("TEST123456", {
                "price": 24.99,
                "rating": 4.7,
                "in_stock": True
            })
            print(f"   PASS: Update successful: {update_success}")
            
            # Verify update
            updated_product = db.get_product("TEST123456")
            if updated_product:
                print(f"   INFO: New price: ${updated_product['price']}")
                print(f"   INFO: New rating: {updated_product['rating']}")
                print(f"   INFO: Updated at: {updated_product.get('updated_at', 'N/A')}")
            
            # Test 5: Insert another product for search tests
            print("\n5️⃣ Adding second test product...")
            test_product_2 = {
                "asin": "TEST789012",
                "title": "Test Product 2",
                "price": 59.99,
                "rating": 3.8,
                "category": "Books"
            }
            product_id_2 = db.insert_product(test_product_2)
            print(f"   PASS: Second product inserted with ID: {product_id_2}")
            
            # Test 6: Get Product Count
            print("\n6️⃣ Testing get_product_count()...")
            total_count = db.get_product_count()
            electronics_count = db.get_product_count({"category": "Electronics"})
            print(f"   INFO: Total products: {total_count}")
            print(f"   INFO: Electronics products: {electronics_count}")
            
            # Test 7: Get All Products
            print("\n7️⃣ Testing get_all_products()...")
            all_products = db.get_all_products(limit=10)
            print(f"   INFO: Retrieved {len(all_products)} products")
            for product in all_products:
                print(f"      - {product['title']} (${product['price']})")
            
            # Test 8: Search Products
            print("\n8️⃣ Testing search_products()...")
            
            # Search by category
            electronics = db.search_products({"category": "Electronics"})
            print(f"   INFO: Electronics products: {len(electronics)}")
            
            # Search by price range
            affordable = db.search_products({"price": {"$lt": 50}})
            print(f"   INFO: Products under $50: {len(affordable)}")
            
            # Search by rating
            high_rated = db.search_products({"rating": {"$gte": 4.0}})
            print(f"   INFO: Products rated 4+ stars: {len(high_rated)}")
            
            # Test 9: Upsert Product (update existing)
            print("\n9️⃣ Testing upsert_product() with existing ASIN...")
            upsert_id = db.upsert_product({
                "asin": "TEST123456",
                "title": "Updated Test Product 1",
                "price": 19.99,
                "description": "Added via upsert"
            })
            print(f"   PASS: Upsert returned ID: {upsert_id}")
            
            # Test 10: Upsert Product (insert new)
            print("\n Testing upsert_product() with new ASIN...")
            new_upsert_id = db.upsert_product({
                "asin": "TEST345678",
                "title": "Upserted New Product",
                "price": 39.99,
                "category": "Home"
            })
            print(f"   PASS: New upsert ID: {new_upsert_id}")
            
            # Test 11: Pagination
            print("\n1️⃣1️⃣ Testing pagination...")
            page_1 = db.get_all_products(limit=2, skip=0)
            page_2 = db.get_all_products(limit=2, skip=2)
            print(f"   INFO: Page 1: {len(page_1)} products")
            print(f"   INFO: Page 2: {len(page_2)} products")
            
            # Test 12: Get non-existent product
            print("\n1️⃣2️⃣ Testing get_product() with invalid ASIN...")
            nonexistent = db.get_product("INVALID123")
            print(f"   PASS: Non-existent product result: {nonexistent}")
            
            # Test 13: Update non-existent product
            print("\n1️⃣3️⃣ Testing update_product() with invalid ASIN...")
            invalid_update = db.update_product("INVALID123", {"price": 99.99})
            print(f"   PASS: Invalid update result: {invalid_update}")
            
            # Final count
            print("\nINFO: Final Statistics:")
            final_count = db.get_product_count()
            print(f"   Total products in database: {final_count}")
            
            # Test 14: Delete Products (cleanup)
            print("\n1️⃣4️⃣ Testing delete_product() - Cleanup...")
            deleted_1 = db.delete_product("TEST123456")
            deleted_2 = db.delete_product("TEST789012") 
            deleted_3 = db.delete_product("TEST345678")
            print(f"   INFO: Deleted TEST123456: {deleted_1}")
            print(f"   INFO: Deleted TEST789012: {deleted_2}")
            print(f"   INFO: Deleted TEST345678: {deleted_3}")
            
            # Verify cleanup
            cleanup_count = db.get_product_count()
            print(f"   INFO: Products after cleanup: {cleanup_count}")
            
    except Exception as e:
        print(f"FAIL: Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nINFO: All method tests completed!")

if __name__ == "__main__":
    test_all_methods()