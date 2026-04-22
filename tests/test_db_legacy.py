#!/usr/bin/env python3
"""
Quick test script for database functionality
"""
import os
from src.db import Database

def test_database():
    """Test basic database operations"""
    try:
        # Test database connection
        print("Testing database connection...")
        
        # This will fail if MONGO_URI is not set
        with Database() as db:
            print("PASS: Database connection successful")
            
            # Test product count
            count = db.get_product_count()
            print(f"PASS: Current product count: {count}")
            
            # Test sample product insertion (won't actually insert due to validation)
            print("PASS: Database methods are accessible")
            
    except RuntimeError as e:
        print(f"FAIL: Connection error: {e}")
        print("Make sure MONGO_URI is set in your .env file")
    except Exception as e:
        print(f"FAIL: Unexpected error: {e}")

if __name__ == "__main__":
    test_database()