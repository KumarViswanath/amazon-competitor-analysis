import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging

from pymongo import MongoClient, IndexModel
from pymongo.errors import ServerSelectionTimeoutError, DuplicateKeyError, OperationFailure

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    def __init__(
        self,
        db_name: str = "amazon_scraper",
        collection_name: str = "products",
    ):
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise RuntimeError("MONGO_URI environment variable not set")

        # Connect to Atlas
        self.client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=8000
        )

        # Force connection check
        try:
            self.client.admin.command("ping")
        except ServerSelectionTimeoutError:
            raise RuntimeError(
                "MongoDB connection failed. Check:\n"
                "- IP Whitelist\n"
                "- Username / Password\n"
                "- Internet access"
            )

        self.db = self.client[db_name]
        self.products = self.db[collection_name]

        # Create indexes safely (only if they don't exist)
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create indexes if they don't exist"""
        try:
            existing_indexes = self.products.list_indexes()
            index_names = [idx.get("name") for idx in existing_indexes]
            
            if "asin_1" not in index_names:
                self.products.create_index("asin", unique=True)
                logger.info("Created unique index on 'asin'")
            
            if "created_at_1" not in index_names:
                self.products.create_index("created_at")
                logger.info("Created index on 'created_at'")
                
        except OperationFailure as e:
            logger.error(f"Failed to create indexes: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def insert_product(self, product_data: Dict[str, Any]) -> str:
        """
        Insert new product with created_at timestamp
        Returns the document ID as string
        """
        if not product_data.get("asin"):
            raise ValueError("Product data must include 'asin' field")
            
        doc = dict(product_data)
        doc["created_at"] = datetime.now(timezone.utc)

        try:
            result = self.products.insert_one(doc)
            logger.info(f"Inserted product with ASIN: {doc.get('asin')}")
            return str(result.inserted_id)
        except DuplicateKeyError:
            logger.warning(f"Product with ASIN {doc.get('asin')} already exists")
            existing = self.get_product(doc.get("asin"))
            return str(existing["_id"]) if existing else ""
        except Exception as e:
            logger.error(f"Failed to insert product: {e}")
            raise

    def get_product(self, asin: str) -> Optional[Dict[str, Any]]:
        """Get product by ASIN"""
        if not asin:
            return None
        try:
            return self.products.find_one({"asin": asin})
        except Exception as e:
            logger.error(f"Failed to get product {asin}: {e}")
            return None

    def update_product(self, asin: str, update_data: Dict[str, Any]) -> bool:
        """Update existing product by ASIN"""
        if not asin or not update_data:
            return False
            
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        try:
            result = self.products.update_one(
                {"asin": asin}, 
                {"$set": update_data}
            )
            logger.info(f"Updated product {asin}: {result.modified_count} document(s)")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update product {asin}: {e}")
            return False

    def upsert_product(self, product_data: Dict[str, Any]) -> str:
        """Insert or update product based on ASIN"""
        asin = product_data.get("asin")
        if not asin:
            raise ValueError("Product data must include 'asin' field")
            
        existing = self.get_product(asin)
        if existing:
            # Update existing product
            update_data = {k: v for k, v in product_data.items() if k != "asin"}
            self.update_product(asin, update_data)
            return str(existing["_id"])
        else:
            # Insert new product
            return self.insert_product(product_data)

    def get_all_products(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Get all products with pagination"""
        try:
            return list(
                self.products
                .find({})
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )
        except Exception as e:
            logger.error(f"Failed to get products: {e}")
            return []

    def search_products(self, search_criteria: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search products by criteria with limit
        """
        try:
            return list(
                self.products
                .find(search_criteria)
                .sort("created_at", -1)
                .limit(limit)
            )
        except Exception as e:
            logger.error(f"Failed to search products: {e}")
            return []

    def delete_product(self, asin: str) -> bool:
        """Delete product by ASIN"""
        if not asin:
            return False
            
        try:
            result = self.products.delete_one({"asin": asin})
            logger.info(f"Deleted product {asin}: {result.deleted_count} document(s)")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete product {asin}: {e}")
            return False

    def get_product_count(self, filter_criteria: Optional[Dict[str, Any]] = None) -> int:
        """Get total count of products"""
        try:
            return self.products.count_documents(filter_criteria or {})
        except Exception as e:
            logger.error(f"Failed to count products: {e}")
            return 0

    def close(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("Database connection closed")
