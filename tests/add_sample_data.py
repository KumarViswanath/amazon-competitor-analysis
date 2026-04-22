#!/usr/bin/env python3
"""
Add sample Amazon products to database for testing
"""
from src.db import Database

def add_sample_products():
    """Add realistic Amazon product samples"""
    
    sample_products = [
        {
            "asin": "B08N5WRWNW",
            "title": "Echo Dot (4th Gen) | Smart speaker with Alexa | Charcoal",
            "price": 49.99,
            "rating": 4.7,
            "review_count": 125843,
            "category": "Electronics",
            "brand": "Amazon",
            "in_stock": True,
            "description": "Our most popular smart speaker with a fabric design",
            "image_url": "https://example.com/echo-dot.jpg"
        },
        {
            "asin": "B0BDQC2X6Z",
            "title": "Fire TV Stick 4K Max streaming device",
            "price": 54.99,
            "rating": 4.5,
            "review_count": 89234,
            "category": "Electronics",
            "brand": "Amazon", 
            "in_stock": True,
            "description": "Our most powerful streaming stick with faster app starts"
        },
        {
            "asin": "B07FZ8S74R",
            "title": "Echo Show 8 (2nd Gen) | HD smart display with Alexa",
            "price": 129.99,
            "rating": 4.6,
            "review_count": 45672,
            "category": "Electronics",
            "brand": "Amazon",
            "in_stock": True,
            "description": "Vibrant 8'' HD screen for video calls and entertainment"
        },
        {
            "asin": "B073JYC4XM", 
            "title": "Apple AirPods (3rd Generation)",
            "price": 169.99,
            "rating": 4.4,
            "review_count": 67891,
            "category": "Electronics",
            "brand": "Apple",
            "in_stock": True,
            "description": "Personalized Spatial Audio with dynamic head tracking"
        },
        {
            "asin": "B08C1W5N87",
            "title": "JBL Charge 5 - Portable Bluetooth Speaker",
            "price": 179.95,
            "rating": 4.8,
            "review_count": 34521,
            "category": "Electronics", 
            "brand": "JBL",
            "in_stock": False,
            "description": "IP67 waterproof and dustproof portable Bluetooth speaker"
        }
    ]
    
    print(" Adding sample Amazon products to database...\n")
    
    try:
        with Database() as db:
            inserted_count = 0
            
            for product in sample_products:
                try:
                    product_id = db.insert_product(product)
                    print(f"PASS: Added: {product['title'][:50]}... (ID: {product_id})")
                    inserted_count += 1
                except Exception as e:
                    print(f"⚠️  Skipped {product['asin']}: {e}")
            
            print(f"\nINFO: Summary:")
            total_count = db.get_product_count()
            print(f"   • Inserted: {inserted_count} products")
            print(f"   • Total in database: {total_count} products")
            
            # Show some stats
            electronics_count = db.get_product_count({"category": "Electronics"})
            in_stock_count = db.get_product_count({"in_stock": True})
            amazon_products = db.get_product_count({"brand": "Amazon"})
            
            print(f"   • Electronics: {electronics_count}")
            print(f"   • In Stock: {in_stock_count}")
            print(f"   • Amazon Brand: {amazon_products}")
            
            print(f"\n Check your MongoDB Atlas dashboard to see the data!")
            
    except Exception as e:
        print(f"FAIL: Error: {e}")

if __name__ == "__main__":
    add_sample_products()