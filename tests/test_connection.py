#!/usr/bin/env python3
"""
Test database connection functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import Database

def test_connection():
    """Test basic database connection"""
    print("Testing Database Connection...")
    
    try:
        with Database() as db:
            print("PASS: Database connection established")
            print(f"INFO: Database name: {db.db.name}")
            print(f"INFO: Collection name: {db.products.name}")
            
            # Test ping
            db.client.admin.command("ping")
            print("PASS: Database ping successful")
            
            return True
            
    except Exception as e:
        print(f"FAIL: Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)