#!/usr/bin/env python3
"""
Query the live data in MongoDB Atlas
"""
from src.db import Database

def query_live_data():
    """Query and display live data from Atlas"""
    
    with Database() as db:
        print("🌐 Live data from MongoDB Atlas:\n")
        
        # Show all products
        products = db.get_all_products()
        for i, product in enumerate(products, 1):
            status = "✅ In Stock" if product.get('in_stock') else "❌ Out of Stock"
            print(f"{i}. {product['title']}")
            print(f"   ASIN: {product['asin']} | ${product['price']} | ⭐{product['rating']} | {status}")
            print(f"   Brand: {product['brand']} | Reviews: {product.get('review_count', 0):,}")
            print()

if __name__ == "__main__":
    query_live_data()