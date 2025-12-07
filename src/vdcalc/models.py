# Voltage Drop Project - Models

from dataclasses import dataclass

@dataclass
class Node:
    node_id: int
    type: str
    distance_m: float
    kva: float
    pf: float = 0.8  # Default power factor
    conductor_size_mm2: int = None
    note: str = ""

@dataclass
class Segment:
    from_node: int
    to_node: int
    length_m: float
    conductor_size_mm2: int
    R_ohm_per_km: float
    X_ohm_per_km: float

@dataclass
class Result:
    node_id: int
    V_actual_V: float
    V_drop_V: float
    V_drop_pct: float
    recommended_size_mm2: int = None
