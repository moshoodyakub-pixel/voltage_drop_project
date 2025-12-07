# Voltage Drop Calculator using Streamlit
import streamlit as st
import pandas as pd
from src.vdcalc.calc_core import recommend_conductor_sizes
from src.vdcalc.models import Node, Segment

# Load IEC table function (reusing from calc_core)
def load_iec_table(file_path):
    return pd.read_csv(file_path)

# Streamlit App
st.title("Voltage Drop Calculator")
st.markdown("Calculate voltage drops and recommend conductor sizes.")

# Upload IEC table CSV
iec_file = st.file_uploader("Upload IEC Aluminum Conductor CSV", type=["csv"])
if iec_file:
    iec_table = load_iec_table(iec_file)

# Input for voltage source
voltage_source = st.number_input("Enter Source Voltage (V)", value=400)
max_vdrop_pct = st.number_input("Enter Max Voltage Drop (%)", value=6.5)

# Input Nodes
st.header("Nodes")
nodes_data = st.text_area(
    "Enter Nodes Data (node_id, type, distance_m, kva, pf)",
    "1,source,0,0,0.8\n2,load,100,10,0.85\n3,load,250,15,0.9"
)
nodes = []
if nodes_data:
    for line in nodes_data.strip().split("\n"):
        node_id, type_, distance_m, kva, pf = line.split(",")
        nodes.append(Node(int(node_id), type_, float(distance_m), float(kva), float(pf)))

# Input Segments
st.header("Segments")
segments_data = st.text_area(
    "Enter Segments Data (from_node, to_node, length_m, conductor_size_mm2, R_ohm_per_km, X_ohm_per_km)",
    "1,2,100,50,0.268,0.073\n2,3,150,50,0.268,0.073"
)
segments = []
if segments_data:
    for line in segments_data.strip().split("\n"):
        from_node, to_node, length_m, size, R, X = line.split(",")
        segments.append(Segment(int(from_node), int(to_node), float(length_m), int(size), float(R), float(X)))

# Calculate Results
if st.button("Calculate"):
    if iec_file:
        results = recommend_conductor_sizes(nodes, segments, iec_table, voltage_source, max_vdrop_pct)
        st.header("Results")
        results_df = pd.DataFrame(results)
        st.dataframe(results_df)

        # Download Button
        st.download_button(
            label="Download Results as CSV",
            data=results_df.to_csv(index=False).encode("utf-8"),
            file_name="voltage_drop_results.csv",
            mime="text/csv",
        )
    else:
        st.error("Please upload an IEC Table CSV.")