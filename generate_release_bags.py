import pandas as pd
import random
import uuid

def generate_release_bag(release_version, is_failed_release):
    instances = []
    
    # --- 1. Generate Runtime Instances (Spans) ---
    # Baseline normal traces
    for _ in range(5):
        instances.append({
            "bag_id": release_version,
            "bag_label": 1 if is_failed_release else 0,
            "is_span": 1,
            "is_dependency": 0,
            "duration_ms": random.randint(10, 100),
            "error_flag": 0,
            "cvss_score": 0.0, # Not applicable to spans
            "depth": 0         # Not applicable to spans
        })
        
    # If the release failed, inject a massive latency spike
    if is_failed_release:
        instances.append({
            "bag_id": release_version,
            "bag_label": 1,
            "is_span": 1,
            "is_dependency": 0,
            "duration_ms": random.randint(5000, 9000), 
            "error_flag": 1,
            "cvss_score": 0.0,
            "depth": 0
        })

    # --- 2. Generate Build-Time Instances (Dependencies) ---
    # Baseline safe dependencies
    for _ in range(10):
        instances.append({
            "bag_id": release_version,
            "bag_label": 1 if is_failed_release else 0,
            "is_span": 0,
            "is_dependency": 1,
            "duration_ms": 0,    # Not applicable to dependencies
            "error_flag": 0,     # Not applicable to dependencies
            "cvss_score": round(random.uniform(0.0, 3.0), 1), # Low risk
            "depth": random.randint(1, 3)
        })
        
    # If the release failed, inject a critical vulnerability
    if is_failed_release:
        instances.append({
            "bag_id": release_version,
            "bag_label": 1,
            "is_span": 0,
            "is_dependency": 1,
            "duration_ms": 0,
            "error_flag": 0,
            "cvss_score": 9.8, # Critical CVSS!
            "depth": 4         # Hidden deep in the tree
        })
        
    return instances

# Generate 10 Releases: 8 Healthy, 2 Failed
all_instances = []
for i in range(1, 9):
    all_instances.extend(generate_release_bag(f"v1.0.{i}", is_failed_release=False))
for i in range(9, 11):
    all_instances.extend(generate_release_bag(f"v1.0.{i}", is_failed_release=True))

df = pd.DataFrame(all_instances)

# Save to CSV so we can inspect it
df.to_csv("multi_modal_bags.csv", index=False)
print("Data generated! Check multi_modal_bags.csv")
print(df.head())