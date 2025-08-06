# ✅ Testing Strategy

The project includes unit tests to ensure reliability and correctness of each pipeline layer. All tests are written
using `pytest` and make use of the `unittest.mock` library to simulate external dependencies like Spark sessions, file
systems, and logger calls.

## 🧪 What is Tested?

Tests are written for each layer of the medallion architecture and cover:
## 🥉 Bronze Layer

- Data Ingestion Validations
  - Verifies correct HTTP request handling and response parsing from the public API.
  - Ensures data is saved with proper partitioning by random date.
- Error Handling
  - Confirms that network or serialization errors are logged and do not crash the pipeline.

## 🥈 Silver Layer

- Schema Enforcement & Cleaning
  - Verifies that the raw JSON data is parsed using the expected schema.
  - Confirms that duplicates are correctly dropped.
- Error Handling
  - Tests raise and log a `ParseException` when JSON parsing fails.
  - Ensures Spark session is always stopped in error scenarios.

## 🥇 Gold Layer

- Aggregation Logic
  - Checks that grouping by `country`, `state_province`, `city`, and `brewery_type` is performed correctly.
  - Confirms the result is written in Parquet format to the correct path.
- Error Handling
  - Simulates errors while reading or writing Parquet files and verifies they are logged appropriately.
  - Ensures Spark session is stopped even when exceptions occur.

## 🧪 How to Run the Tests

To execute all tests, you can run the following command in the root folder:
```bash
pytest
```

You can also see a summary of test results with:
```bash
pytest -v
```
