import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# 1. Load the generated multi-modal data
df = pd.read_csv("multi_modal_bags.csv")

# 2. Prepare the Features (X) and Labels (y)
# We map the bag label to the instances to train our baseline instance-space model
feature_columns = ['is_span', 'is_dependency', 'duration_ms', 'error_flag', 'cvss_score', 'depth']
X = df[feature_columns]
y = df['bag_label']

# 3. Train the Model
print("Training the instance-level diagnostic model...")
# Random Forest is excellent at handling our mixed data types without requiring extensive scaling
model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
model.fit(X, y)
print("Model trained successfully!\n")

# 4. Inference: Diagnosing a System Failure
# Let's isolate v1.0.9, which we know is a "Positive Bag" (a failed release)
failed_release_id = "v1.0.9" 
failed_bag = df[df['bag_id'] == failed_release_id].copy()

# The model calculates the probability that each individual instance is the root cause
failed_bag['root_cause_probability'] = model.predict_proba(failed_bag[feature_columns])[:, 1]

# Sort the instances to bubble the actual anomalies to the top
suspects = failed_bag.sort_values(by='root_cause_probability', ascending=False)

# 5. The Developer UI Output
print(f"--- Root Cause Diagnostics for {failed_release_id} ---")
print("Total instances scanned in this release:", len(failed_bag))
print("\nTop 3 Suspects Identified by the Model:")

# Format the output for readability
for index, row in suspects.head(3).iterrows():
    prob = round(row['root_cause_probability'] * 100, 1)
    
    if row['is_span'] == 1:
        print(f"[Run-time Anomaly] {prob}% Probability | Span Latency: {row['duration_ms']}ms, Error Flag: {row['error_flag']}")
    elif row['is_dependency'] == 1:
        print(f"[Build-time Anomaly] {prob}% Probability | CVSS Score: {row['cvss_score']}, Tree Depth: {row['depth']}")