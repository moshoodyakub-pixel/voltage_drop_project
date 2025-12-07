# Voltage Drop Project - Core Calculation Logic

import pandas as pd
import math

# Load IEC aluminum conductor table
def load_iec_table(file_path):
    """Loads IEC conductor data from CSV file."""
    return pd.read_csv(file_path)

# Temperature correction for resistance
def apply_temp_correction(R_20C, T_oper, alpha=0.00403):
    """Applies temperature correction to resistance."""
    return R_20C * (1 + alpha * (T_oper - 20))

# Downstream current aggregator
def calculate_downstream_current(kva, voltage, load_type):
    """Calculates downstream current based on load type and voltage."""
    if load_type == "single":
        return (kva * 1000) / voltage
    elif load_type == "three":
        return (kva * 1000) / (math.sqrt(3) * voltage)
    raise ValueError("Invalid load type. Use 'single' or 'three'.")

# Voltage drop formula per segment
def calculate_voltage_drop(I, R_seg, X_seg, pf, load_type):
    """Calculates voltage drop per segment."""
    cos_phi = pf
    sin_phi = math.sqrt(1 - pf**2)  # Using lagging power factor
    if load_type == "single":
        return I * (R_seg * cos_phi + X_seg * sin_phi)
    elif load_type == "three":
        return math.sqrt(3) * I * (R_seg * cos_phi + X_seg * sin_phi)
    raise ValueError("Invalid load type. Use 'single' or 'three'.")

# Compute impedance per segment
def calculate_segment_impedance(R_ohm_per_km, X_ohm_per_km, length_m):
    """Calculates per-segment resistance and reactance."""
    length_km = length_m / 1000
    R_seg = R_ohm_per_km * length_km
    X_seg = X_ohm_per_km * length_km
    return R_seg, X_seg

# Recommendation logic
def recommend_conductor_sizes(nodes, segments, iec_table, voltage_source, max_vdrop_pct=6.5, ambient_temp=40):
    """Recommends conductor sizes for each segment."""
    results = []
    for segment in segments:
        for size_mm2 in sorted(iec_table["NominalArea_mm2"]):
            # Load resistance and reactance per km for this conductor size
            R_ohm_km = iec_table.loc[iec_table["NominalArea_mm2"] == size_mm2, "R_ohm_per_km"].values[0]
            X_ohm_km = iec_table.loc[iec_table["NominalArea_mm2"] == size_mm2, "X_ohm_per_km"].values[0]
            R_seg, X_seg = calculate_segment_impedance(
                apply_temp_correction(R_ohm_km, ambient_temp),
                X_ohm_km,
                segment.length_m,
            )
            # Calculate downstream current and voltage drop
            I = calculate_downstream_current(segment.kva, voltage_source, segment.type)
            V_drop_seg = calculate_voltage_drop(I, R_seg, X_seg, segment.pf, segment.type)
            V_drop_pct = (V_drop_seg / voltage_source) * 100

            # Verify against voltage drop limit
            if V_drop_pct <= max_vdrop_pct:
                results.append({
                    "segment_id": segment.segment_id,
                    "recommended_size_mm2": size_mm2,
                    "V_drop_pct": V_drop_pct,
                })
                break  # Found suitable size; stop searching for this segment

    return results
