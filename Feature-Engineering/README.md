# Security Feature Extractor

## Project Overview

The purpose of this project is to convert raw security events into machine learning (ML) ready features. The program reads authentication logs, network logs, and DNS logs, then extracts useful features that can later be used for security analysis or anomaly detection.


## Libraries Used

- pandas
- numpy
- scipy
- argparse
- hashlib
- json
- csv


## Files Included

- feature_extractor.py
- sample_raw_events.jsonl
- sample_features.csv
- sample_features.json
- feature_dictionary.md
- README.md


## Features Created

The program generates features such as:

- Login success count
- Login failure count
- Unique source IPs
- Failure ratio
- Success rate
- Time since last login
- Hour of day
- Business hours
- Bytes transferred
- Unique destination ports
- Domain length
- DNS query entropy
- Peer deviation
- Privacy risk

## Privacy

User names are not stored directly.

The program converts every user ID into a SHA-256 hash before saving the output.

A privacy risk level (LOW, MEDIUM, HIGH) is also added for each record.


## Rolling Windows

This project also supports rolling windows.

Rolling windows calculate activity over a moving period of time instead of only checking the current hour.

Available rolling windows are:

- 1 hour
- 4 hours
- 24 hours

For example, if a user logs in at 2:00 PM, the 1-hour rolling window checks all events between 1:00 PM and 2:00 PM.

This helps identify user behavior over time instead of looking at only one fixed hour.


## Running the Program

Example command:

```bash
python feature_extractor.py --input sample_raw_events.jsonl --output sample_features.csv --window user-hour --rolling 1h
```

Example:

```bash
python feature_extractor.py --input sample_raw_events.jsonl --output sample_features.csv --window host-hour --rolling 24h
```

## Output Files

The program creates two output files:

- sample_features.csv
- sample_features.json

## Notes

- Missing values are replaced with 0 or "Unknown".
- Events are sorted by timestamp before processing.
- Features are grouped using user-hour or host-hour windows.
- The output is deterministic, meaning the same input produces the same results.

