# Multi-Modal MIL Pilot: Root Cause Diagnostics

This repository contains a sandbox pilot demonstrating how to use **Multiple Instance Learning (MIL)** to detect the exact root cause of system failures. It bridges DevOps telemetry (New Relic) with AppSec data (Sonatype), designed specifically to solve complex diagnostic challenges—such as isolating the exact policy violations or latency spikes triggered after a deployment.

By using an **instance-space Random Forest classifier**, this tool analyzes a single "failed release" (Bag) and pinpoints whether the root cause was a slow runtime span or a deeply nested vulnerable dependency (Instances).

---

## 🚀 Getting Started (Sandbox Phase)

This initial phase uses synthetic data to prove the MIL architecture without requiring firewall access to sensitive organizational telemetry.

### Prerequisites
* **Python 3.12+**
* **Libraries:** `pandas`, `scikit-learn`, `streamlit`

### Running the Pilot

1. **Generate the Synthetic Multi-Modal Data**
   Run the data generator to create a mix of healthy and failed "Release Bags." This mimics a scenario where a release contains both fast API spans and secure dependencies, but occasionally fails due to a latency spike or a critical CVSS vulnerability.
   ```powershell
   python generate_release_bags.py
   ```
   * **Output:** `multi_modal_bags.csv`

2. **Train the MIL Classifier**
   Execute the instance-space machine learning model. It trains on weakly supervised bag labels and outputs a probability score for every individual instance.
   ```powershell
   python train_mil_model.py
   ```

3. **Launch the Aggregation UI (Phase 4)**
   Visualize the diagnostics through a professional Streamlit dashboard.
   ```powershell
   streamlit run app.py
   ```

---

## 📊 Phase 4: The Aggregation UI
The pilot features a functional diagnostic hub that maps abstract model probabilities to actionable telemetry.

* **Telemetry Mapping:** Converts model outputs into identifiable IDs (e.g., `nr-trace-ID` or `sonatype-hash-ID`).
* **Threat Distribution:** Visualizes the statistical "gap" between primary suspects and background noise using bar charts.
* **Root Cause Probability:** Provides a confidence metric (e.g., 91.11%) to prioritize engineering investigation.

---

## 🗺️ Production Integration Roadmap

To transition this pilot from the synthetic sandbox to real organizational data, the data generation script is replaced with direct API integrations.

### 1. The Runtime Pipeline (New Relic)
Fetch distributed traces directly using the **New Relic NerdGraph GraphQL API**.
* **Endpoint:** `https://api.newrelic.com`
* **Strategy:** Use GraphQL queries targeting `actor.account.nrql` to pull raw Span data associated with specific `trace.id` values.
* **Mapping:** Map span `duration` and `error.message` to the `duration_ms` and `error_flag` features.

### 2. The Build-Time Pipeline (Sonatype Lifecycle)
Extract the evaluated Bill of Materials (SBOM) using the **Sonatype Lifecycle REST API**.
* **Endpoint:** `GET /api/v2/applications/{appId}/reports`
* **Strategy:** Parse the JSON response to extract deeply nested, transitive dependencies.
* **Mapping:** Map `securityIssues.severity` and tree depth to the `cvss_score` and `depth` features.

---

## 🔬 The MIL Assumption
This tool relies on the **Standard MIL Assumption**:
* **Negative Bags (Healthy):** Contain no critical anomalies.
* **Positive Bags (Failed):** Contain **at least one** anomaly (the "witness").

By mapping both NerdGraph spans and Lifecycle dependencies into the same mathematical space, the classifier automatically ignores high-frequency background noise shared across both tools to highlight the specific failing instance.
