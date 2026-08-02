# Drift Analysis Methodology

Machine learning models assume that the data used during prediction has a similar distribution to the data used during training. However, data can change over time due to changes in user behavior, network traffic, system updates, or emerging cyber threats. This phenomenon is known as **drift**. If drift is not detected, model performance may gradually decrease, leading to inaccurate predictions and unreliable security decisions.

The purpose of this project is to automatically detect significant changes in feature distributions before they negatively affect the machine learning pipeline.


## Types of Drift

### 1. Data Drift

Data drift occurs when the statistical distribution of one or more input features changes over time while the model remains unchanged.
For example, if the average number of failed login attempts suddenly increases because of a brute-force attack, the feature distribution becomes different from the original training data.

**Examples include:**

* Increase in login failure count
* Higher network traffic volume
* Changes in DNS entropy values
* Increase in bytes transferred

The validator compares the current feature dataset with a reference dataset to identify these changes.

### 2. Concept Drift

Concept drift occurs when the relationship between the input features and the expected output changes over time.

For example, a login failure ratio that was previously considered suspicious may become normal after a company changes its authentication policy. Although the feature values remain similar, their meaning changes.
Detecting concept drift usually requires labeled historical data. Since this project does not include labels, concept drift is discussed conceptually but is not fully implemented.

## Drift Detection Method

This project uses the **Kolmogorov–Smirnov (KS) Test** to compare the distribution of each numerical feature in the current dataset with the reference dataset.

The KS Test measures the maximum difference between two cumulative distributions and determines whether both datasets are likely to come from the same distribution.

For every numerical feature, the validator calculates:

* KS Statistic
* p-value

The p-value is compared with the default significance threshold:

**Default Threshold:** `0.05`

**Decision Rule**

* **p-value ≥ 0.05** → No significant drift detected.
* **p-value < 0.05** → Significant drift detected.

A significant result indicates that the feature distribution has changed and should be investigated.

## Features Compared

The validator evaluates the following numerical features:

* `login_success_count`
* `login_failure_count`
* `failure_ratio`
* `bytes_transferred`
* `dns_entropy`
* `peer_deviation`

Each feature is compared independently with the corresponding feature in the reference dataset.


## Why the KS Test?

The Kolmogorov–Smirnov Test was selected because it:

* Does not assume a normal data distribution.
* Compares complete feature distributions rather than only averages.
* Is simple to implement using the SciPy library.
* Is widely used for monitoring feature drift in production machine learning systems.

These advantages make it suitable for validating cybersecurity feature datasets.


## Practical Example

Suppose the reference dataset contains users with an average of **one failed login attempt per hour**.
Later, the current dataset shows an average of **five failed login attempts per hour** because of a brute-force attack.
The KS Test compares both distributions. If the calculated **p-value is less than 0.05**, the validator reports **Significant Drift**, allowing analysts to investigate the abnormal behavior before retraining or redeploying the model.

## Recommendations

When significant drift is detected, the following actions are recommended:

1. Verify that the incoming data is valid.
2. Investigate possible security incidents or infrastructure changes.
3. Monitor whether the drift continues over multiple days.
4. Retrain the machine learning model if the drift persists.
5. Update the reference dataset after validating the new data.


## Conclusion
Drift detection is an important part of maintaining reliable machine learning systems. In this project, the Kolmogorov–Smirnov (KS) Test is used to compare the current feature dataset with a reference dataset and identify significant changes in feature distributions. Detecting drift early helps maintain model accuracy, improve security monitoring, and support better data-driven decision-making.
