
from power_grid_model import ComponentType

# def calculate_partition_score(edges, admittance_map):
#     """
#     edges: list of (u, v, m_id) tuples. 
#            m_id is the unique Line ID (e.g., 15636).
#     admittance_map: dict keyed by Line ID.
#     """
#     total_score = 0.0
#     for u, v, m_id in edges:
#         # We use m_id directly. This is the only way to distinguish 
#         # between lines that might share the same nodes.
#         total_score += admittance_map.get(m_id, 0.0)
            
#     return total_score


def calculate_partition_score(partition_dict, admittance_map):
    """
    Calculates the total numerical score of the active topological basis 
    using the dictionary-style representation.
    
    Parameters:
    -----------
    partition_dict : dict
        A dictionary mapping {measurement_id: line_id} representing the active basis.
    admittance_map : dict
        A lookup dictionary mapping unique physical Line IDs (ints) to their admittances.
    """
    total_score = 0.0
    
    # We iterate directly over the values (the line_ids) in the dictionary
    for line_id in partition_dict.values():
        if line_id is None:
            continue
            
        # Safely force native integer casting to prevent NumPy type-mismatch misses
        line_id_native = int(line_id)
        
        # Accumulate the admittance score
        total_score += admittance_map.get(line_id_native, 0.0)
            
    return total_score