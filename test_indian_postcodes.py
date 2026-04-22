#!/usr/bin/env python3
"""
Test script to verify Indian postal code functionality
"""
import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from geo_utils import GeoLocationHandler
from models import ProductInput

def test_geo_location_handler():
    """Test the GeoLocationHandler with various postal codes"""
    
    print("🔍 Testing GeoLocationHandler...")
    
    # Test Indian PIN codes
    indian_pins = ["110001", "400001", "560001", "700001", "500001"]
    print("\n📍 Testing Indian PIN codes:")
    for pin in indian_pins:
        is_valid = GeoLocationHandler.validate_postal_code(pin, "in")
        normalized = GeoLocationHandler.normalize_postal_code(pin, "in")
        print(f"  {pin} -> Valid: {is_valid}, Normalized: {normalized}")
    
    # Test US ZIP codes
    us_zips = ["10001", "90210", "94102", "33101"]
    print("\n📍 Testing US ZIP codes:")
    for zip_code in us_zips:
        is_valid = GeoLocationHandler.validate_postal_code(zip_code, "com")
        normalized = GeoLocationHandler.normalize_postal_code(zip_code, "com")
        print(f"  {zip_code} -> Valid: {is_valid}, Normalized: {normalized}")
    
    # Test UK postcodes
    uk_postcodes = ["SW1A 1AA", "M1 1AA", "B33 8TH", "W1A 0AX"]
    print("\n📍 Testing UK postcodes:")
    for postcode in uk_postcodes:
        is_valid = GeoLocationHandler.validate_postal_code(postcode, "co.uk")
        normalized = GeoLocationHandler.normalize_postal_code(postcode, "co.uk")
        print(f"  {postcode} -> Valid: {is_valid}, Normalized: {normalized}")
    
    # Test default postal codes
    print("\n📍 Testing default postal codes by domain:")
    domains = ["com", "in", "co.uk", "de", "fr", "it", "es"]
    for domain in domains:
        default = GeoLocationHandler.get_default_postal_code(domain)
        print(f"  {domain} -> Default: {default}")

def test_pydantic_validation():
    """Test Pydantic model validation with various postal codes"""
    
    print("\n🔍 Testing Pydantic model validation...")
    
    # Test valid inputs
    test_cases = [
        {"domain": "com", "zip_code": "10001", "should_pass": True, "desc": "Valid US ZIP"},
        {"domain": "in", "zip_code": "110001", "should_pass": True, "desc": "Valid Indian PIN"},
        {"domain": "co.uk", "zip_code": "SW1A 1AA", "should_pass": True, "desc": "Valid UK postcode"},
        {"domain": "in", "zip_code": "10001", "should_pass": False, "desc": "US ZIP in India domain"},
        {"domain": "com", "zip_code": "110001", "should_pass": False, "desc": "Indian PIN in US domain"},
        {"domain": "in", "zip_code": "12345", "should_pass": False, "desc": "5-digit in India (needs 6)"},
        {"domain": "co.uk", "zip_code": "12345", "should_pass": False, "desc": "Number in UK (needs postcode)"},
    ]
    
    print("\n📋 Testing validation cases:")
    for case in test_cases:
        try:
            product_input = ProductInput(
                identifier="B08N5WRWNW",
                identifier_type="asin",
                zip_code=case["zip_code"],
                domain=case["domain"]
            )
            result = "✅ PASS" if case["should_pass"] else "❌ FAIL (should have failed)"
            print(f"  {case['desc']}: {result}")
        except Exception as e:
            result = "❌ FAIL (unexpected error)" if case["should_pass"] else "✅ PASS (correctly failed)"
            print(f"  {case['desc']}: {result}")
            if case["should_pass"]:
                print(f"    Error: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing Indian Postal Code Functionality")
    print("=" * 50)
    
    try:
        test_geo_location_handler()
        test_pydantic_validation()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed! Check results above.")
        print("\nKey improvements made:")
        print("• ✅ Created GeoLocationHandler for international postal codes")
        print("• ✅ Added support for Indian 6-digit PIN codes (110001, 400001, etc.)")
        print("• ✅ Updated Oxylabs service to use flexible geo-location")
        print("• ✅ Enhanced frontend with domain-specific validation")
        print("• ✅ Added Pydantic validation for postal code formats")
        
        print("\nSupported domains and formats:")
        print("• 🇺🇸 amazon.com - 5-digit ZIP codes (10001)")
        print("• 🇮🇳 amazon.in - 6-digit PIN codes (110001)")
        print("• 🇬🇧 amazon.co.uk - UK postcodes (SW1A 1AA)")
        print("• 🇩🇪 amazon.de - 5-digit codes (10115)")
        print("• 🇫🇷 amazon.fr - 5-digit codes (75001)")
        print("• 🇮🇹 amazon.it - 5-digit codes (00118)")
        print("• 🇪🇸 amazon.es - 5-digit codes (28001)")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()