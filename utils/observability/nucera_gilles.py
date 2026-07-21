def apply_nucera_pruning(forest_measurement_ids, physical_adj, measurement_map, partition):
    """
    forest_measurement_ids: Set of measurement IDs currently in the spanning forest (basis)
    physical_adj: Adjacency list of the physical grid (bus to neighboring buses)
    measurement_map: Dict mapping measurement IDs to their type ('flow' or 'injection') and associated nodes/bus
    partition: Dict mapping each bus to its partition (used for optimized neighbor checks)
    Implements the Nucera-Gilles pruning algorithm to identify and remove "leaky" injection measurements.
    A "leaky" injection is one that has at least one incident branch that is NOT covered by any flow measurement in the current forest.
    This is a pre-processing step to reduce the candidate set for basis exchange, improving computational efficiency

    Note: In many modern MV/LV grids, injection measurements are often sparse and mostly consist of zero-injection sensors.
          Therefore, this pruning step does not per se prune the search space by a large amount.
    ###
    """
    # 1. Build the span adjacency once (Flows only)
    span_adj = {}
    injections_to_check = []
    final_forest = set()
    toberemoved = set()

    for m_id in forest_measurement_ids:
        info = measurement_map.get(m_id)
        if not info:
            continue
            
        if info['type'] == 'flow':
            u, v = info['nodes']
            final_forest.add(m_id)
            # Build a bidirectional span map for fast O(1) neighbor checking
            span_adj.setdefault(u, set()).add(v)
            span_adj.setdefault(v, set()).add(u)
        else:
            injections_to_check.append(m_id)

    # 2. Single-pass check for injections
    # An injection is valid ONLY if its physical neighbors are a subset of the span
    for m_id in injections_to_check:
        info = measurement_map[m_id]
        bus = info['bus']
        
        physical_neighbors = physical_adj.get(bus, set())
        for item in physical_neighbors:
            if item not in partition[bus]:  
                # This neighbour is considered leaky so we remove it
                toberemoved.add(m_id)
            
    return final_forest

def apply_nucera_pruning_better(forest_measurement_ids, physical_adj, measurement_map):
    """
    Prunes leaky injection measurements by checking if all neighboring 
    physical nodes are members of the current forest boundary.
    """
    final_forest = set(forest_measurement_ids)
    toberemoved = set()
    injections_to_check = []

    # 1. Map out every single node that is currently covered by the forest
    nodes_in_forest = set()
    for m_id in final_forest:
        actual_id = m_id[0] if isinstance(m_id, tuple) else m_id
        info = measurement_map.get(actual_id)
        if not info:
            continue
            
        if info['type'] == 'flow':
            u, v = info['nodes']
            nodes_in_forest.add(u)
            nodes_in_forest.add(v)
        elif info['type'] == 'injection':
            nodes_in_forest.add(info['bus'])
            neighbors = info.get('neighbors')
            if neighbors:
                if isinstance(neighbors, (list, set, tuple)):
                    nodes_in_forest.update(neighbors)
                else:
                    nodes_in_forest.add(neighbors)
            
            

    # 2. Check each injection: Are ALL of its physical neighbors in the forest?
    for m_id in injections_to_check:
        info = measurement_map[m_id]
        bus = info['bus']
        
        physical_neighbors = physical_adj.get(bus, set())
        for neighbor in physical_neighbors:
            # If a neighbor node is entirely missing from the forest boundary
            if neighbor not in nodes_in_forest:  
                toberemoved.add(m_id)
                break # Move to the next injection immediately

    # 3. Strip out the leaky elements from your final basis set
    final_forest.difference_update(toberemoved)
            
    return final_forest, toberemoved