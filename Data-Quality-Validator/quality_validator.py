import argparse
from datetime import datetime
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

REQUIRED_COLUMNS = [
    "window_id",
    "entity_id",
    "hour",
    "login_success_count",
    "login_failure_count",
    "failure_ratio",
    "bytes_transferred",
    "dns_entropy",
    "peer_deviation"
]

NUMERIC_COLUMNS = [
    "login_success_count",
    "login_failure_count",
    "failure_ratio",
    "bytes_transferred",
    "dns_entropy",
    "peer_deviation"
]

CATEGORICAL_COLUMNS = [
    "window_id",
    "entity_id",
    "hour"
]

# Arguments read
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Data Quality and Drift Validator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Input feature matrix CSV"
    )

    parser.add_argument(
        "--reference",
        required=True,
        help="Reference feature CSV"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output report file"
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.05,
        help="Drift significance threshold"
    )

    parser.add_argument(
        "--format",
        default="markdown",
        choices=["markdown", "html", "json"],
        help="Report format"
    )

    return parser.parse_args()

# CSV Loading Function
def load_data(input_path, reference_path):
    """
    Load input and reference datasets.
    """

    input_df = pd.read_csv(input_path)
    reference_df = pd.read_csv(reference_path)

    return input_df, reference_df

def validate_schema(df):
    """
    Validate dataset schema.
    """
    results = []
    
# Required Columns

    missing_columns = []

    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            missing_columns.append(column)

    if len(missing_columns) == 0:
        results.append("OK All required columns are present.")
    else:
        results.append(
            f"FAIL Missing columns: {', '.join(missing_columns)}"
        )
    
# Unexpected Columns
   
    unexpected = []

    for column in df.columns:
        if column not in REQUIRED_COLUMNS:
            unexpected.append(column)

    if len(unexpected) == 0:
        results.append("OK No unexpected columns found.")
    else:
        results.append(
            f"FAIL Unexpected columns: {', '.join(unexpected)}"
        )

# Data Types
    datatype_errors = []

    for column in NUMERIC_COLUMNS:

        if column in df.columns:

            if not pd.api.types.is_numeric_dtype(df[column]):
                datatype_errors.append(column)

    if len(datatype_errors) == 0:
        results.append("OK Numeric data types are correct.")
    else:
        results.append(
            f"FAIL Incorrect numeric datatype: {', '.join(datatype_errors)}"
        )

    return results

# Null value Validation
def validate_nulls(df):

    results = []

    for column in df.columns:

        null_percent = df[column].isnull().mean() * 100

        if null_percent == 0:

            results.append(
                f"OK {column}: No missing values."
            )

        elif null_percent <= 5:

            recommendation = "Mean" if column in NUMERIC_COLUMNS else "Mode"

            results.append(
                f"WARN {column}: {null_percent:.2f}% null "
                f"(Recommended Imputation: {recommendation})"
            )

        else:

            recommendation = "Investigate or Remove Feature"

            results.append(
                f"FAIL {column}: {null_percent:.2f}% null "
                f"({recommendation})"
            )

    return results

# Range Checks
def validate_ranges(df):
    results = []

    if "failure_ratio" in df.columns:

        invalid = df[
            (df["failure_ratio"] < 0)
            | (df["failure_ratio"] > 1)
        ]

        if len(invalid) == 0:

            results.append(
                "OK failure_ratio within expected range."
            )

        else:
            results.append(
                f"FAIL failure_ratio: {len(invalid)} invalid values."
            )

    count_columns = [
        "login_success_count",
        "login_failure_count",
        "bytes_transferred"
    ]

    for column in count_columns:

        if column in df.columns:

            negatives = (df[column] < 0).sum()

            if negatives == 0:

                results.append(
                    f"OK {column}: No negative values."
                )

            else:

                results.append(
                    f"FAIL {column}: {negatives} negative values."
                )

    return results

# Outlier Detection
def detect_outliers(df):
    results = []

    for column in NUMERIC_COLUMNS:

        if column not in df.columns:
            continue

        mean = df[column].mean()

        std = df[column].std()

        if std == 0:
            continue

        outliers = df[
            np.abs(df[column] - mean) > (5 * std)
        ]

        if len(outliers) == 0:

            results.append(
                f"OK {column}: No extreme outliers."
            )

        else:
            results.append(
                f"FAIL {column}: {len(outliers)} outliers (>5 std)"
            )

    return results

# Duplicate Detection
def validate_duplicates(df):
    results = []

    duplicates = df[
        df.duplicated(
            subset=["window_id", "entity_id"],
            keep=False
        )
    ]

    if duplicates.empty:

        results.append(
            "OK No duplicate window_id/entity_id pairs."
        )

    else:

        results.append(
            f"FAIL {len(duplicates)} duplicate rows detected."
        )

    return results

# Drift Detection
def detect_drift(current_df, reference_df, threshold):
    results = []

    for column in NUMERIC_COLUMNS:

        if column not in current_df.columns:
            continue

        if column not in reference_df.columns:
            continue

        current = current_df[column].dropna()

        reference = reference_df[column].dropna()

        statistic, p_value = ks_2samp(
            current,
            reference
        )

        if p_value < threshold:

            results.append(
                f"WARN {column}: "
                f"KS={statistic:.3f}, "
                f"p={p_value:.4f} "
                "(SIGNIFICANT DRIFT)"
            )

        else:

            results.append(
                f"OK {column}: No significant drift."
            )

    return results

# Report Generation Function
def generate_report(
    output_file,
    input_file,
    reference_file,
    schema_results,
    null_results,
    range_results,
    outlier_results,
    duplicate_results,
    drift_results,
    df
):

    total_records = len(df)
    total_features = len(df.columns)
    total_nulls = df.isnull().sum().sum()

    duplicate_count = len(
        df[df.duplicated(
            subset=["window_id", "entity_id"],
            keep=False
        )]
    )

    drift_alerts = sum(
        "SIGNIFICANT DRIFT" in item
        for item in drift_results
    )

    with open(output_file, "w", encoding="utf-8") as report:

        report.write("# Data Quality Report\n\n")

        report.write(
            f"Generated: {datetime.now()}\n\n"
        )

        report.write(
            f"Input: {input_file}\n\n"
        )

        report.write(
            f"Reference: {reference_file}\n\n"
        )

        report.write("## Summary\n\n")

        report.write(
            f"- Total Records: {total_records}\n"
        )

        report.write(
            f"- Features: {total_features}\n"
        )

        report.write(
            f"- Null Values: {total_nulls}\n"
        )

        report.write(
            f"- Duplicate Rows: {duplicate_count}\n"
        )

        report.write(
            f"- Drift Alerts: {drift_alerts}\n\n"
        )

        report.write("## Schema Validation\n\n")

        for item in schema_results:
            report.write(f"- {item}\n")

        report.write("\n## Null Checks\n\n")

        for item in null_results:
            report.write(f"- {item}\n")

        report.write("\n## Range Checks\n\n")

        for item in range_results:
            report.write(f"- {item}\n")

        report.write("\n## Outlier Detection\n\n")

        for item in outlier_results:
            report.write(f"- {item}\n")

        report.write("\n## Duplicate Detection\n\n")

        for item in duplicate_results:
            report.write(f"- {item}\n")

        report.write("\n## Drift Detection\n\n")

        for item in drift_results:
            report.write(f"- {item}\n")

        report.write("\n## Recommendations\n\n")

        if duplicate_count > 0:
            report.write(
                "1. Remove duplicate records.\n"
            )

        if drift_alerts > 0:
            report.write(
                "2. Investigate data drift and consider retraining the model.\n"
            )

        if total_nulls > 0:
            report.write(
                "3. Apply an appropriate imputation strategy for missing values.\n"
            )

        report.write(
            "4. Validate data before every ML pipeline execution.\n"
        )

    print(f"\nReport saved as: {output_file}")
    
# Main Function
def main():
    args = parse_arguments()

    features_df, reference_df = load_data(
        args.input,
        args.reference
    )

    print("Files load successfully.\n")

    # Calling Functions
    schema_results = validate_schema (features_df)

    null_results = validate_nulls (features_df)

    range_results = validate_ranges (features_df)

    outlier_results = detect_outliers (features_df)

    duplicate_results = validate_duplicates (features_df)

    drift_results = detect_drift(
        features_df,
        reference_df,
        args.threshold
    )

    print("Validation completed successfully.")

    generate_report(
        args.output,
        args.input,
        args.reference,
        schema_results,
        null_results,
        range_results,
        outlier_results,
        duplicate_results,
        drift_results,
        features_df
    )

    print("\nQuality validation completed successfully.")

    print("\nSCHEMA VALIDATION")
    for item in schema_results:
        print(item)

    print("\nNULL CHECKS")
    for item in null_results:
        print(item)

    print("\nRANGE CHECKS")
    for item in range_results:
        print(item)

    print("\nOUTLIER CHECKS")
    for item in outlier_results:
        print(item)

    print("\nDUPLICATE CHECKS")
    for item in duplicate_results:
        print(item)

    print("\nDRIFT DETECTION")
    for item in drift_results:
        print(item)

if __name__ == "__main__":
    main()