# Data Quality Report

Generated: 2026-08-02 13:39:02.126647

Input: features.csv

Reference: reference_features.csv

## Summary

- Total Records: 31
- Features: 9
- Null Values: 2
- Duplicate Rows: 2
- Drift Alerts: 2

## Schema Validation

- OK All required columns are present.
- OK No unexpected columns found.
- OK Numeric data types are correct.

## Null Checks

- OK window_id: No missing values.
- OK entity_id: No missing values.
- OK hour: No missing values.
- OK login_success_count: No missing values.
- OK login_failure_count: No missing values.
- OK failure_ratio: No missing values.
- OK bytes_transferred: No missing values.
- WARN dns_entropy: 3.23% null (Recommended Imputation: Mean)
- WARN peer_deviation: 3.23% null (Recommended Imputation: Mean)

## Range Checks

- FAIL failure_ratio: 1 invalid values.
- OK login_success_count: No negative values.
- OK login_failure_count: No negative values.
- OK bytes_transferred: No negative values.

## Outlier Detection

- OK login_success_count: No extreme outliers.
- OK login_failure_count: No extreme outliers.
- FAIL failure_ratio: 1 outliers (>5 std)
- FAIL bytes_transferred: 1 outliers (>5 std)
- OK dns_entropy: No extreme outliers.
- OK peer_deviation: No extreme outliers.

## Duplicate Detection

- FAIL 2 duplicate rows detected.

## Drift Detection

- OK login_success_count: No significant drift.
- WARN login_failure_count: KS=0.734, p=0.0000 (SIGNIFICANT DRIFT)
- WARN failure_ratio: KS=0.645, p=0.0000 (SIGNIFICANT DRIFT)
- OK bytes_transferred: No significant drift.
- OK dns_entropy: No significant drift.
- OK peer_deviation: No significant drift.

## Recommendations

1. Remove duplicate records.
2. Investigate data drift and consider retraining the model.
3. Apply an appropriate imputation strategy for missing values.
4. Validate data before every ML pipeline execution.
