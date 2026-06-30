from utils.setunion import find
from utils.measurements import get_measurement_endpoints
from power_grid_model import (
    ComponentType,
)

def check_island_observability(parent, input_data, all_nodes, admittance_map, base_partition_edges, measurement_map):
    islands = {}
    
    # 1. Pre-calculate Island Grouping and Root Mapping
    # O(V) - Do this once so we don't call find() repeatedly in loops
    node_to_root = {node: find(parent, node) for node in all_nodes}
    
    # Initialize the results dict for all unique roots
    # O(Islands)
    for root in set(node_to_root.values()):
        islands[root] = {
            "nodes": [],
            "is_observable": False,
            "ref_type": "NONE",
            "stability_score": 0.0,
            "anchors": [],
            "y_sum": 0.0  # Temporary accumulator
        }

    # Group nodes into islands (O(V))
    for node, root in node_to_root.items():
        islands[root]["nodes"].append(node)

    # 2. Vectorized Anchor Processing
    # Instead of checking nodes inside islands, check anchors directly (O(Anchors))
    for v in input_data.get(ComponentType.sym_voltage_sensor, []):
        node = int(v["measured_object"])
        root = node_to_root.get(node)
        if root is not None:
            islands[root]["is_observable"] = True
            islands[root]["ref_type"] = "Voltage Sensor"
            islands[root]["anchors"].append(node)

    for s in input_data.get(ComponentType.source, []):
        node = int(s["node"])
        root = node_to_root.get(node)
        if root is not None and islands[root]["ref_type"] != "Voltage Sensor":
            islands[root]["is_observable"] = True
            islands[root]["ref_type"] = "Source (Slack Bus)"
            islands[root]["anchors"].append(node)

    # 3. SINGLE-PASS Stability Score Calculation (CRITICAL FIX)
    # Instead of looping through edges PER island, loop through edges ONCE.
    # O(Edges) instead of O(Islands * Edges)
    for m_id in base_partition_edges.keys():
        u, v = get_measurement_endpoints(m_id, measurement_map)
        # Use u to find the root (since u and v must be in the same island in a tree)
        root = node_to_root.get(u)
        if root is not None:
            islands[root]["y_sum"] += admittance_map.get(m_id, 0.0)

    # 4. Final Normalization (O(Islands))
    for root, info in islands.items():
        num_branches = len(info["nodes"]) - 1
        if num_branches > 0:
            info["stability_score"] = info["y_sum"] / num_branches
        del info["y_sum"] # Clean up temporary variable

    return islands