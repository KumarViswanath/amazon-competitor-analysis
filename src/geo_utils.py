"""
Geo-location utilities for handling international postal codes and domains
"""
import re
from typing import Dict, Optional, Tuple

class GeoLocationHandler:
    """Handle geo-location for different Amazon domains"""
    
    # Default postal codes for different Amazon domains
    DEFAULT_POSTAL_CODES = {
        "com": "10001",      # US - New York
        "in": "110001",      # India - New Delhi
        "co.uk": "SW1A 1AA", # UK - London
        "de": "10115",       # Germany - Berlin
        "fr": "75001",       # France - Paris
        "ca": "M5V 3A8",     # Canada - Toronto
        "co.jp": "100-0001", # Japan - Tokyo
        "it": "00118",       # Italy - Rome
        "es": "28001",       # Spain - Madrid
        "com.au": "2000",    # Australia - Sydney
        "com.br": "01310-100", # Brazil - São Paulo
        "com.mx": "06600",   # Mexico - Mexico City
        "nl": "1012",        # Netherlands - Amsterdam
        "se": "11148",       # Sweden - Stockholm
        "com.tr": "34110"    # Turkey - Istanbul
    }
    
    # Popular city postal codes for major markets
    POPULAR_POSTAL_CODES = {
        "in": {
            "mumbai": "400001",
            "delhi": "110001", 
            "bangalore": "560001",
            "hyderabad": "500001",
            "chennai": "600001",
            "kolkata": "700001",
            "pune": "411001",
            "ahmedabad": "380001",
            "jaipur": "302001",
            "surat": "395001"
        },
        "com": {
            "new_york": "10001",
            "los_angeles": "90210", 
            "chicago": "60601",
            "houston": "77001",
            "phoenix": "85001",
            "philadelphia": "19101",
            "san_antonio": "78201",
            "san_diego": "92101",
            "dallas": "75201",
            "san_jose": "95101"
        },
        "co.uk": {
            "london": "SW1A 1AA",
            "manchester": "M1 1AA",
            "birmingham": "B1 1AA",
            "glasgow": "G1 1AA",
            "liverpool": "L1 1AA",
            "leeds": "LS1 1AA",
            "sheffield": "S1 1AA",
            "bristol": "BS1 1AA",
            "edinburgh": "EH1 1AA",
            "leicester": "LE1 1AA"
        }
    }
    
    @classmethod
    def validate_postal_code(cls, postal_code: str, domain: str = "com") -> bool:
        """Validate postal code format for the given domain"""
        if not postal_code:
            return False
            
        postal_code = postal_code.strip()
        
        # Validation patterns for different domains
        patterns = {
            "com": r"^\d{5}(-\d{4})?$",  # US ZIP codes
            "in": r"^\d{6}$",            # Indian PIN codes
            "co.uk": r"^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$",  # UK postcodes
            "de": r"^\d{5}$",            # German postal codes
            "fr": r"^\d{5}$",            # French postal codes
            "ca": r"^[A-Z]\d[A-Z]\s?\d[A-Z]\d$",  # Canadian postal codes
            "co.jp": r"^\d{3}-?\d{4}$",  # Japanese postal codes
            "it": r"^\d{5}$",            # Italian postal codes
            "es": r"^\d{5}$",            # Spanish postal codes
            "com.au": r"^\d{4}$",        # Australian postcodes
            "com.br": r"^\d{5}-?\d{3}$", # Brazilian postal codes
            "com.mx": r"^\d{5}$",        # Mexican postal codes
            "nl": r"^\d{4}\s?[A-Z]{2}$", # Netherlands postal codes
            "se": r"^\d{3}\s?\d{2}$",    # Swedish postal codes
            "com.tr": r"^\d{5}$"         # Turkish postal codes
        }
        
        pattern = patterns.get(domain, patterns["com"])
        return bool(re.match(pattern, postal_code, re.IGNORECASE))
    
    @classmethod
    def normalize_postal_code(cls, postal_code: str, domain: str = "com") -> str:
        """Normalize postal code format for the given domain"""
        if not postal_code:
            return cls.get_default_postal_code(domain)
            
        postal_code = postal_code.strip().upper()
        
        # Domain-specific normalization
        if domain == "in":
            # Indian PIN codes - remove any non-digits
            postal_code = re.sub(r'[^\d]', '', postal_code)
            if len(postal_code) == 6 and postal_code.isdigit():
                return postal_code
        
        elif domain == "com":
            # US ZIP codes - handle ZIP+4 format
            postal_code = re.sub(r'[^\d-]', '', postal_code)
            if len(postal_code) >= 5:
                return postal_code[:5]  # Return just the 5-digit ZIP
        
        elif domain == "co.uk":
            # UK postcodes - normalize spacing
            postal_code = re.sub(r'\s+', ' ', postal_code)
            if len(postal_code) >= 5:
                return postal_code
        
        elif domain == "ca":
            # Canadian postal codes - normalize format A1A 1A1
            postal_code = re.sub(r'[^A-Z0-9]', '', postal_code)
            if len(postal_code) == 6:
                return f"{postal_code[:3]} {postal_code[3:]}"
        
        elif domain == "co.jp":
            # Japanese postal codes - add hyphen if missing
            postal_code = re.sub(r'[^\d-]', '', postal_code)
            if len(postal_code) == 7 and '-' not in postal_code:
                return f"{postal_code[:3]}-{postal_code[3:]}"
        
        # Validate the normalized postal code
        if cls.validate_postal_code(postal_code, domain):
            return postal_code
        
        # Return default if validation fails
        return cls.get_default_postal_code(domain)
    
    @classmethod
    def get_default_postal_code(cls, domain: str = "com") -> str:
        """Get default postal code for the given domain"""
        return cls.DEFAULT_POSTAL_CODES.get(domain, "10001")
    
    @classmethod
    def detect_domain_from_postal_code(cls, postal_code: str) -> str:
        """Detect likely Amazon domain from postal code format"""
        if not postal_code:
            return "com"
            
        postal_code = postal_code.strip()
        
        # Try to match against different domain patterns
        for domain in cls.DEFAULT_POSTAL_CODES.keys():
            if cls.validate_postal_code(postal_code, domain):
                return domain
        
        # Default fallback
        return "com"
    
    @classmethod
    def get_geo_location_info(cls, postal_code: str, domain: str = "com") -> Dict[str, str]:
        """Get comprehensive geo-location information"""
        normalized_code = cls.normalize_postal_code(postal_code, domain)
        
        return {
            "postal_code": normalized_code,
            "domain": domain,
            "is_valid": cls.validate_postal_code(normalized_code, domain),
            "country_code": cls._get_country_code(domain),
            "currency": cls._get_currency(domain),
            "default_code": cls.get_default_postal_code(domain)
        }
    
    @classmethod
    def _get_country_code(cls, domain: str) -> str:
        """Get country code for domain"""
        country_mapping = {
            "com": "US",
            "in": "IN", 
            "co.uk": "GB",
            "de": "DE",
            "fr": "FR",
            "ca": "CA",
            "co.jp": "JP",
            "it": "IT",
            "es": "ES",
            "com.au": "AU",
            "com.br": "BR",
            "com.mx": "MX",
            "nl": "NL",
            "se": "SE",
            "com.tr": "TR"
        }
        return country_mapping.get(domain, "US")
    
    @classmethod
    def _get_currency(cls, domain: str) -> str:
        """Get default currency for domain"""
        currency_mapping = {
            "com": "USD",
            "in": "INR",
            "co.uk": "GBP", 
            "de": "EUR",
            "fr": "EUR",
            "ca": "CAD",
            "co.jp": "JPY",
            "it": "EUR",
            "es": "EUR",
            "com.au": "AUD",
            "com.br": "BRL",
            "com.mx": "MXN",
            "nl": "EUR",
            "se": "SEK",
            "com.tr": "TRY"
        }
        return currency_mapping.get(domain, "USD")

    @classmethod
    def suggest_postal_codes(cls, domain: str, city: Optional[str] = None) -> Dict[str, str]:
        """Suggest postal codes for popular cities in the domain"""
        suggestions = {}
        
        if domain in cls.POPULAR_POSTAL_CODES:
            city_codes = cls.POPULAR_POSTAL_CODES[domain]
            
            if city and city.lower() in city_codes:
                # Return specific city code
                suggestions[city.lower()] = city_codes[city.lower()]
            else:
                # Return all popular cities for the domain
                suggestions = city_codes.copy()
        
        # Always include the default
        suggestions["default"] = cls.get_default_postal_code(domain)
        
        return suggestions