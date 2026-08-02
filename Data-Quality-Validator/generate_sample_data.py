import numpy as np
import pandas as pd

np.random.seed(42)

records = 30

reference = pd.DataFrame({
    "window_id": range(1, records + 1),
    "entity_id": [f"user_{i}" for i in range(1, records + 1)],
    "hour": np.random.randint(0, 24, records),
    "login_success_count": np.random.randint(10, 50, records),
    "login_failure_count": np.random.randint(0, 5, records),
    "failure_ratio": np.random.uniform(0, 0.3, records),
    "bytes_transferred": np.random.randint(1000, 10000, records),
    "dns_entropy": np.random.uniform(1.5, 4.0, records),
    "peer_deviation": np.random.uniform(0, 2, records)
})

features = reference.copy()

features.loc[2, "dns_entropy"] = np.nan
features.loc[8, "peer_deviation"] = np.nan

features.loc[12, "bytes_transferred"] = 150000

features.loc[15, "failure_ratio"] = 1.5

features.loc[18, "login_failure_count"] = -3

duplicate = features.iloc[[5]].copy()

features = pd.concat(
    [features, duplicate],
    ignore_index=True
)

features["login_failure_count"] += 4

features["failure_ratio"] *= 1.8

reference.to_csv(
    "reference_features.csv",
    index=False
)

features.to_csv(
    "features.csv",
    index=False
)

print("Sample datasets generated successfully.")

