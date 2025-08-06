# ✅ Data Quality Checks

To ensure the reliability of the data being processed, the Silver Layer includes a set of data quality checks and cleaning steps:

- **Deduplication**: Duplicate records are dropped using the unique `id` field.
- **Schema Enforcement**: A strict schema is applied when reading the raw JSON from Bronze.
- **Normalization**: String fields like `city`, `country`, and `state_province` are trimmed, lowercased, and capitalized.
- **Field Derivations**:
  - `has_website`: Boolean indicating if `website_url` is present.
  - `has_phone`: Boolean indicating if `phone` is present.
  - `has_geolocation`: Boolean indicating presence of valid `latitude` and `longitude`.
- **Fallback Columns**: If `address_1` or `state_province` are missing, they are filled from `street` or `state` respectively.
- **Phone & Zip Cleaning**: Non-digit characters are stripped from phone numbers and postal codes to new cleaned columns.
- **Empty String Handling**: Empty strings are converted to `null` for consistency.
- **Critical Null Removal**: Rows missing essential fields (`id`, `name`, `country`, `state_province`) are dropped.

These steps ensure that the Silver layer contains clean, consistent, and analytics-ready data.
