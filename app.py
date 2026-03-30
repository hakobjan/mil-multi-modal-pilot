import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import uuid

# --- Page Configuration ---
st.set_page_config(page_title="MIL Diagnostics Hub", layout="wide")
st.title("🔍 Root Cause Aggregation UI")

# --- Model & Data Loading ---
@st.cache_data
def load_data_and_train_model():
    # Load your generated bags
    df = pd.read_csv("multi_modal_bags.csv")
    
    feature_columns = ['is_span', 'is_dependency', 'duration_ms', 'error_flag', 'cvss_score', 'depth']
    X = df[feature_columns]
    y = df['bag_label']
    
    # Train the exact same model from Phase 3
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X, y)
    
    # UPGRADE 2: Inject realistic identifiers to simulate real APM/Security telemetry
    if 'instance_id' not in df.columns:
        df['instance_id'] = [
            f"nr-trace-{uuid.uuid4().hex[:8]}" if row.get('is_span', 0) == 1 
            else f"sonatype-hash-{uuid.uuid4().hex[:8]}" 
            for _, row in df.iterrows()
        ]
        
    return df, model, feature_columns

df, model, feature_columns = load_data_and_train_model()

# --- User Interface Sidebar ---
st.sidebar.header("Diagnostic Controls")
releases = df['bag_id'].unique()
selected_release = st.sidebar.selectbox("Select Failed Release:", releases)

st.subheader(f"Diagnostics for: `{selected_release}`")

# --- Inference ---
failed_bag = df[df['bag_id'] == selected_release].copy()
failed_bag['root_cause_probability'] = model.predict_proba(failed_bag[feature_columns])[:, 1]

# Sort to bubble suspects to the top
suspects = failed_bag.sort_values(by='root_cause_probability', ascending=False)
top_suspects = suspects.head(5)

# --- Display High-Level Metrics ---
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Instances Scanned", len(failed_bag))
with col2:
    # Convert highest probability to a clean percentage string
    st.metric("Highest Threat Probability", f"{top_suspects['root_cause_probability'].iloc[0] * 100:.2f}%")

st.divider()

# --- UPGRADE 3: Visual Chart ---
st.markdown("### 📊 Threat Probability Distribution")
# Display a bar chart using our new instance IDs and the model's probabilities
st.bar_chart(
    data=top_suspects.set_index('instance_id')['root_cause_probability'],
    color="#ff4b4b" # Renders the bars in an alert red color
)

# --- UPGRADE 1 & 2: Formatted Dataframe with Identifiers ---
st.markdown("### 🚨 Top 5 Root Cause Suspects")

# Reorder columns so our new ID is the very first thing the engineer sees
display_cols = ['instance_id', 'is_dependency', 'error_flag', 'cvss_score', 'duration_ms', 'root_cause_probability']

# Use Streamlit's column config for percentage formatting and hiding index numbers
st.dataframe(
    top_suspects[display_cols],
    use_container_width=True,
    hide_index=True, 
    column_config={
        "instance_id": st.column_config.TextColumn("Telemetry ID"),
        "root_cause_probability": st.column_config.NumberColumn(
            "Root Cause Probability",
            format="%.2f", # Multiplies by 100 and adds the % sign automatically in newer versions, or formats decimals beautifully
            help="Model confidence that this instance caused the release failure."
        ),
        "cvss_score": st.column_config.NumberColumn("CVSS Score", format="%.1f"),
        "duration_ms": st.column_config.NumberColumn("Duration (ms)")
    }
)