from utils.graph_lca import get_path_using_LCA, find_weakest_link
from utils.mapping_utils import find_line
from utils.measurements import get_measurement_endpoints
from utils.setunion import find
import numpy as np

def get_measurement_priority(m_id, measurement_map):
    """
    Returns the symbolic priority of a basis element for tie-breaking.
    """
    # If it's a tuple (sensor_id, neighbor), extract the raw sensor ID
    actual_id = m_id[0] if isinstance(m_id, tuple) else m_id
    
    info = measurement_map.get(actual_id)
    if not info:
        return 0  # It's an unmetered background line from line_df (Lowest priority)
        
    if info.get('type') == 'flow':
        return 2  # Flow sensor (Highest priority)
    elif info.get('type') == 'injection':
        return 1  # Injection sensor (Medium priority)
        
    return 0


def swap_basis_dict(base_partition_dict, edge_to_remove_id, new_measurement_id, new_line_id):
    """
    base_partition_dict: Dictionary mapping {measurement_id: physical_line_id}
    edge_to_remove_id: The ID of the measurement being kicked out of the basis
    new_measurement_id: The ID of the redundant sensor coming in
    new_line_id: The physical line ID that the new sensor is assigned to monitor
    """
    new_partition = base_partition_dict.copy()
    
    # 1. Remove the weakest link measurement
    if edge_to_remove_id in new_partition:
        del new_partition[edge_to_remove_id]
        
    # 2. Assign the incoming measurement to its physical line
    
    if isinstance(new_measurement_id, tuple):
        sensor_id = new_measurement_id[0]  # The actual sensor ID is the first element of the tuple
    else:
        sensor_id = new_measurement_id  # For non-tuple cases, the edge itself is the sensor ID
    new_partition[sensor_id] = new_line_id

    return new_partition

def targeted_basis_exchange_dict(
    base_partition_dict, 
    r_id, 
    report, 
    admittance_map, 
    graph_context, # Dictionary containing parents, depths, edge_to_parent
    measurement_context, # Dictionary containing line_map, measurement_map, etc.
    adj
):
    # 1. Unpack context for readability
    parents = graph_context['parents']
    depths = graph_context['depths']
    edge_to_parent = graph_context['edge_to_parent']
    counter = 0

    u, v = get_measurement_endpoints(r_id, measurement_context['measurement_map'])

    sensor_id = int(r_id[0] if isinstance(r_id, tuple) else r_id)


    if sensor_id in base_partition_dict:
        current_line = int(base_partition_dict[sensor_id])
        # 1. Cleanly find the (u, v) tuple matching your current_line ID
        endpoints = next((nodes for nodes, lid in measurement_context['line_map'].items() if int(lid) == int(current_line)), None)

        # 2. Print them safely out to your log console
   
        if endpoints:
            u = int(endpoints[0])
            v = int(endpoints[1])
            # If either endpoint has a physical degree of 1, it's a dead end. LOCK IT!
            if len(adj.get(u, set())) == 1 or len(adj.get(v, set())) == 1:
                return None, 0.0, counter


    # Identify the Fundamental Cycle in O(log N)
    cycle_edges = get_path_using_LCA(u, v, parents, depths, edge_to_parent)
    # 1. Intersect the keys to find which cycle measurements are active in the basis
    active_keys = base_partition_dict.keys() & set(cycle_edges)

    # 2. Extract the corresponding values (physical line IDs) into a list
    active_cycle_lines = [base_partition_dict[k] for k in active_keys]

    if sensor_id in base_partition_dict:
        current_line = int(base_partition_dict[sensor_id])
        candidate_line = int(find_line(u, v, measurement_context['line_map']))
        if candidate_line == current_line:
            return None, 0.0, counter


    if not active_cycle_lines or len(active_cycle_lines) == 1:
        return None, 0.0, counter
    
    # Identify the weakest link 
    edge_to_remove = min(active_cycle_lines, key=lambda eid: admittance_map.get(eid, float('inf')))
 
    # PRIORITY 3: DYNAMICAL RANKING (The "Weakest Link")
    current_edge = find_line(u, v, measurement_context['line_map']) # This should return the line ID if it exists, or None if it's an injection measurement
    
    priority, degree_score, new_admittance = get_edge_score(r_id, measurement_context['measurement_map'], adj, admittance_map, u, v, current_edge)
    
    # old_line = base_partition_dict[edge_to_remove]
    older_score = admittance_map.get(edge_to_remove, 0.0)
    new_score = admittance_map.get(current_edge, 0.0)
    swap_score = new_score - older_score
    # Accept the swap if either condition is met
    if swap_score <= 0:
        # print(f"Swap score is non-positive ({swap_score:.4f}). Skipping targeted exchange for candidate {r_id}.")
        counter = 1
        return None, 0.0, counter
    else:
        new_partition = swap_basis_dict(base_partition_dict, edge_to_remove, r_id, current_edge)
    return new_partition, swap_score, counter



def get_edge_score(r_id, measurement_map, adj, admittance_map, u, v, current_edge):
    """
    Generates a 3-part hybrid score for any candidate or existing edge.
    Returns: (Sensor_Priority, Nodal_Degree, Admittance_Value)
    """
    # 1. Sensor Priority (e.g., Flow=2, Inj=1, Background=0)
    priority = get_measurement_priority(r_id, measurement_map)
    
    # 2. Topological Hub Score (Degree centrality of its endpoints)
    degree_score = len(adj.get(u, set())) + len(adj.get(v, set()))
    
    # 3. Numerical Admittance Score
    admittance = admittance_map.get(current_edge, 0.0)
    
    return (priority, degree_score, admittance)