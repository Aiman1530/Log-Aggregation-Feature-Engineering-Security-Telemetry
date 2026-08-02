import pandas as pd
import numpy as np
import json
import csv
import hashlib
import argparse
from scipy.stats import entropy
from collections import Counter

print ("Libraries imported successfully")

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input",
    default="sample_raw_events.jsonl"
)

parser.add_argument(
    "--output",
    default="sample_features.csv"
)

parser.add_argument(
    "--window",
    choices=["user-hour", "host-hour"],
    default="user-hour"
)

parser.add_argument(
    "--rolling",
    choices=["1h", "4h", "24h"],
    default="1h"
)

args = parser.parse_args()

# Read JSONL File
df = pd.read_json(args.input, lines=True)

print (" Dataset Load Successfully\n")
print (df.head())

print ("\nColumns:")
print (df.columns)

# Dataset Info
print ("\nDataset Information")
print (df.info())

# Missing values
print ("\nMissing Values")
print (df.isnull().sum())

# Fill missing values
# Replace missing values

df["user"] = df["user"].fillna ("Unknown")

df["host"] = df["host"].fillna ("Unknown")

df["status"] = df["status"].fillna ("Unknown")

df["bytes"] = df["bytes"].fillna (0)

df["port"] = df["port"].fillna (0)

# Convert Timestamp
df["timestamp"] = pd.to_datetime (df["timestamp"])

# Sorting according to timestamp
df = df.sort_values ("timestamp")

print(df.head())

# Hour of Day
df["hour"] = df["timestamp"].dt.hour

# Business hours
df["is_business_hours"] = df["hour"].between(9,18)

# Date
df["date"] = df["timestamp"].dt.date

# Window ID
df["window_id"] = (
    df["date"].astype(str)
    + "_"
    + df["hour"].astype(str)
)

# Showing Output
print(df[[
    "timestamp",
    "hour",
    "is_business_hours",
    "date",
    "window_id"
]
         ]
      )

# User Hour Aggregation
user_hour = df.groupby (["user", "date", "hour"])

# count total events
event_count = (
    user_hour
    .size()
    .reset_index (name="event_count")
)
print(event_count)

# Success Count
success = df[df["status"] == "SUCCESS"]

success = success.groupby(
    ["user", "date", "hour"]
).size()

success = success.reset_index(
    name="login_success_count"
)
print(success)

# Failure Count
failure = df[df["status"] == "FAILURE"]

failure = failure.groupby(
    ["user", "date", "hour"]
).size()

failure = failure.reset_index(
    name="login_failure_count"
)

# unique_source_ips
ip_count = (
    df.groupby(["user", "date", "hour"])["source_ip"]
    .nunique()
    .reset_index (name="unique_source_ips")
)

# Merging the tables
features = event_count.merge(
    success,
    on=["user", "date", "hour"],
    how="left"
)
features = features.merge(
    failure,
    on=["user", "date", "hour"],
    how="left"
)
features = features.merge(
    ip_count,
    on=["user", "date", "hour"],
    how="left"
)

features.fillna(0, inplace=True)

# Ratio Features
features ["failure_ratio"] = np.where(
    features ["event_count"] > 0,
    features ["login_failure_count"] /
    features ["event_count"],
    0
)

features ["success_rate"] = np.where(
    features ["event_count"] > 0,
    features ["login_success_count"] /
    features ["event_count"],
    0
)

print(features)

# time since last login
auth_data = df [df["event_type"] == "AUTH"].copy()
auth_data = auth_data.sort_values (["user","timestamp"])
auth_data ["previous login"] = auth_data.groupby("user") ["timestamp"].shift(1)

auth_data ["time_since_last_login"] = (
    auth_data ["timestamp"] -
    auth_data ["previous login"]
).dt.total_seconds() / 60

auth_data["time_since_last_login"] = auth_data["time_since_last_login"].fillna(0)

# Bytes Transfer
network_df = df[df["event_type"] == "NETWORK"]

bytes_data = (
    network_df
    .groupby(["source_ip","date","hour"])["bytes"]
    .sum()
    .reset_index(name="bytes_transferred")
)

# Unique Destination Ports
ports_data = (
    network_df
    .groupby(["source_ip","date","hour"])["port"]
    .nunique()
    .reset_index(name="unique dest ports")
)

# Domain Length
dns_df = df[df["event_type"]=="DNS"].copy()
dns_df["domain_length"] = dns_df["query_domain"].str.len()

# DNS Query Entropy
from collections import Counter

def calculate_entropy(domain):

    if pd.isna(domain):
        return 0

    counts = Counter(domain)

    probabilities = np.array(list(counts.values()))

    probabilities = probabilities / probabilities.sum()

    return entropy (probabilities, base=2)

dns_df ["dns_query_entropy"] = dns_df ["query_domain"]. apply(calculate_entropy)

# peer_deviation
mean = bytes_data ["bytes_transferred"].mean()
std = bytes_data ["bytes_transferred"].std()

if std == 0 or pd.isna(std):
    bytes_data ["peer_deviation"] = 0
else:
    bytes_data["peer_deviation"] = (
        bytes_data["bytes_transferred"] - mean
    ) / std

   
features.fillna(0, inplace=True)

# hashlib
def hash_user(user):
    return hashlib.sha256(
        str(user).encode()
    ).hexdigest()[:12]


features["user_hash"] = features["user"].apply(hash_user)
  
# privacy Risk
  
def privacy_risk(ip_count):

     if ip_count >= 10:
        return "HIGH"

     elif ip_count >= 5:
        return "MEDIUM"

     else:
        return "LOW"
    
features["privacy_risk"] = (
    features["unique_source_ips"]
    .apply(privacy_risk)
)
  
# CSV Export
features.to_csv(
    args.output,
    index=False
)
    
 #  JSoN Export
features.to_json(
    "sample_features.json",
    orient="records",
    indent=4
)
    
# Statistics
print("\n==== Summary =====")

print ( "Total Feature Rows :",
      len(features))

print ( "Total Columns :",
      len(features.columns))

print ("\nMissing Values")

print (features.isnull().sum())

