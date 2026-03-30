# mil-multi-modal-pilot
A sandbox pilot demonstrating Multiple Instance Learning (MIL) to detect root causes of system failures using combined APM telemetry and SBOM dependency data.
Markdown
# Multi-Modal MIL Pilot: Root Cause Diagnostics

This repository contains a sandbox pilot demonstrating how to use Multiple Instance Learning (MIL) to detect the exact root cause of system failures. It bridges DevOps telemetry with AppSec data, designed specifically to solve complex diagnostic challenges—such as isolating the exact Sonatype policy violations triggered after installing the New Relic Python agent.

By using an instance-space Random Forest classifier, this tool analyzes a single "failed release" and pinpoints whether the root cause was a slow runtime span or a deeply nested vulnerable dependency.

## 🚀 Getting Started (Sandbox Phase)

This initial phase uses synthetic, publicly available data to prove the MIL architecture without requiring firewall access to sensitive organizational telemetry.

### Prerequisites
* Python 3.9+
* `pandas`
* `scikit-learn`

### Running the Pilot

1. **Generate the Synthetic Multi-Modal Data:**
   Run the data generator to create a mix of healthy and failed "Release Bags." This mimics a scenario where a release contains both fast API spans (instances) and secure dependencies (instances), but occasionally fails due to a latency spike or a critical CVSS vulnerability.
   ```bash
   python generate_release_bags.py
Output: multi_modal_bags.csv

Train the MIL Classifier and Run Diagnostics:
Execute the instance-space machine learning model. It will train on the weakly supervised bag labels, and then output a probability score for every individual instance inside a failed release to find the anomaly.

Bash
python train_mil_model.py
🗺️ Phase 3: Production Integration Roadmap
To transition this pilot from the synthetic sandbox to real organizational data behind the firewall, the generate_release_bags.py script must be replaced with direct API integrations. The underlying ML classifier (train_mil_model.py) will remain identical.

1. The Runtime Pipeline (New Relic)
Instead of generating synthetic spans, fetch distributed traces directly using the New Relic NerdGraph GraphQL API.

Endpoint: https://api.newrelic.com/graphql (or https://api.eu.newrelic.com/graphql for EU accounts)

Authentication: Requires a API-Key header with your User API key.

Data Extraction Strategy: Use a GraphQL query targeting actor.account.nrql to pull the raw Span data associated with specific trace.id values.

Target Features: Map the span duration and error.message presence directly to the duration_ms and error_flag columns in the X feature matrix.

2. The Build-Time Pipeline (Sonatype Lifecycle)
Instead of generating synthetic dependencies, extract the evaluated Bill of Materials (SBOM) using the Sonatype Lifecycle REST API.

Endpoint: GET /api/v2/evaluations/applications/{applicationId} (to get the overall bag label/policy status) and GET /api/v2/applications/{applicationPublicId}/reports (to fetch the granular component report).

Authentication: Standard Basic Auth using Lifecycle credentials or an API token.

Data Extraction Strategy: Parse the JSON response to extract the deeply nested, transitive dependencies.

Target Features: Map the securityData.securityIssues.severity and tree depth directly to the cvss_score and depth columns in the X feature matrix.

The MIL Assumption
This tool relies on the Standard MIL Assumption:

Negative bags (healthy releases) contain no critical anomalies. Positive bags (failed releases) contain at least one anomaly. By mapping both the NerdGraph spans and the Lifecycle dependencies into the same mathematical space, the classifier automatically ignores the high-frequency background noise shared across both tools to highlight the specific failing instance.