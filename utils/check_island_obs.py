from utils.setunion import find
from utils.measurements import get_measurement_endpoints
from power_grid_model import (
    ComponentType,
)

def check_island_observability(parent, input_data, all_nodes, admittance_map, base_partition_edges, measurement_map):
    """
    Validates structural observability, reference anchors, and numerical stability across grid partitions.
    
    This function analyzes the power grid topology to identify disconnected electrical sub-networks 
    (islands), verify if each island contains a valid reference anchor required for absolute state 
    estimation, and calculate a normalized stability score based on branch admittances.

    Parameters:
    -----------
    parent : dict or list
        The Union-Find/Disjoint Set Union (DSU) tracking data structure mapping each node to its current root.
    input_data : dict
        The raw power grid model dictionary containing network component configurations and asset definitions.
    all_nodes : iterable
        A collection of all active node identifiers (bus references) present in the targeted network.
    admittance_map : dict
        A lookup mapping measurement/branch IDs to their computed complex admittance magnitude values.
    base_partition_edges : dict
        The primary operational dictionary containing the chosen tree basis edge configurations.
    measurement_map : dict
        A lookup mapping sensor identifiers to their corresponding graph endpoint nodes (u, v).

    Returns:
    --------
    dict
        A dictionary keyed by island root node IDs, where each entry contains:
        - "nodes"          : List of all buses belonging to the subnetwork.
        - "is_observable"  : Boolean flagging whether an absolute electrical reference exists.
        - "ref_type"       : String identifying the anchor source ("Voltage Sensor", "Source (Slack Bus)", or "NONE").
        - "anchors"        : List of node IDs where absolute references are located.
        - "stability_score": The average admittance across the active branches inside that specific island.
    """
    islands = {}
    node_to_root = {node: find(parent, node) for node in all_nodes}
    
    for root in set(node_to_root.values()):
        islands[root] = {
            "nodes": [],
            "is_observable": False,
            "ref_type": "NONE",
            "stability_score": 0.0,
            "anchors": [],
            "y_sum": 0.0  # Temporary accumulator
        }

    for node, root in node_to_root.items():
        islands[root]["nodes"].append(node)

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

    for m_id in base_partition_edges.keys():
        u, v = get_measurement_endpoints(m_id, measurement_map)
        # Use u to find the root (since u and v must be in the same island in a tree)
        root = node_to_root.get(u)
        if root is not None:
            islands[root]["y_sum"] += admittance_map.get(m_id, 0.0)

    for root, info in islands.items():
        num_branches = len(info["nodes"]) - 1
        if num_branches > 0:
            info["stability_score"] = info["y_sum"] / num_branches
        del info["y_sum"] # Clean up temporary variable

    return islands