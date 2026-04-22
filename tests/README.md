# Database Tests

This directory contains comprehensive tests for the Amazon Project database functionality.

## Test Structure

### Core Test Files
- **`test_connection.py`** - Database connection and setup tests
- **`test_insert.py`** - Product insertion and validation tests  
- **`test_retrieve.py`** - Product retrieval and querying tests
- **`test_update.py`** - Product update and upsert tests
- **`test_search.py`** - Search functionality and advanced queries
- **`test_delete.py`** - Product deletion and cleanup tests

### Utility Files
- **`run_tests.py`** - Test runner for individual or all tests
- **`add_sample_data.py`** - Script to populate database with sample data
- **`test_db_legacy.py`** - Legacy basic connection test
- **`test_all_methods_legacy.py`** - Legacy comprehensive test suite

## Usage

### Run All Tests
```bash
cd tests
python run_tests.py
```

### Run Individual Test
```bash
cd tests
python run_tests.py test_connection
python run_tests.py test_insert.py
```

### Run Specific Test Directly
```bash
cd tests
python test_connection.py
python test_insert.py
```

## Test Categories

### 🔌 Connection Tests (`test_connection.py`)
- Database connection establishment
- MongoDB Atlas connectivity
- Authentication verification
- Index creation validation

### 📝 Insert Tests (`test_insert.py`) 
- Product insertion with all fields
- Duplicate ASIN handling
- Data validation (required fields)
- Error handling for malformed data

### 🔍 Retrieve Tests (`test_retrieve.py`)
- Single product retrieval by ASIN
- Bulk product retrieval with pagination
- Product count queries (total and filtered)
- Edge cases (non-existent products, empty results)

### ✏️ Update Tests (`test_update.py`)
- Product field updates
- Upsert operations (insert or update)
- Timestamp handling (`updated_at`)
- Invalid ASIN update handling

### 🔎 Search Tests (`test_search.py`)
- Category-based searches
- Price range filtering
- Rating-based queries  
- Brand/manufacturer searches
- Complex multi-criteria searches
- MongoDB regex operations

### 🗑️ Delete Tests (`test_delete.py`)
- Single product deletion
- Batch deletion operations
- Deletion verification
- Invalid deletion handling

## Sample Data

Use `add_sample_data.py` to populate your database with realistic Amazon product data for testing:

```bash
python add_sample_data.py
```

This adds 5 sample products across different categories and price ranges.

## Requirements

All tests require:
- MongoDB Atlas connection (MONGO_URI in .env)
- Python dependencies: `pymongo`, `python-dotenv`
- Active virtual environment

## Test Results

Tests provide detailed output with:
- ✅ Success indicators  
- ❌ Failure notifications
- 📊 Performance metrics
- 🧹 Automatic cleanup

Each test is isolated and cleans up after itself to avoid data pollution.