"""
Measurement Topology Processing Suite
--------------------------------------
This module handles the transformation of raw PGM (Power Grid Model) components 
into a topology-aware measurement map. 

Core logic:
1. Translates physical assets (Loads, Sources, Lines) into unified measurement types.
2. Resolves 'Type 9' injection measurements into their graph-based neighbor dependencies.
3. Implements virtual Z-in mapping for unmonitored bus observability.
4. Provides universal endpoint resolution for branch-based flows and node-based injections.
"""

from power_grid_model import (
    ComponentType,
    MeasuredTerminalType
)

from utils.measurements.get_component import get_component

def get_neighbors(adj, node_id):
    return list(adj.get(node_id, []))

def get_line_by_id(line_id, line_lookup):
    # This returns a Series: [from_node, to_node]
    return line_lookup.loc[line_id]

def get_load_by_id(load_id, load_df):
    return load_df.loc[load_id]

def get_node_from_sensor(obj_id, term_type, source_map):
    if term_type  == 2:
        return source_map.get(obj_id)

def get_flow_measurements(input_data, line_lookup):
    """
    Parses power and current sensors to extract branch-based flow measurements.
    
    Identifies sensors connected to branch terminals (0 or 1). It cross-references 
    the PGM line registry to map each flow sensor to its physical (from, to) nodes.
    
    Returns: List of (sensor_id, u, v) tuples.
    """
    M_flow = []

    for sensor in get_component(input_data, ComponentType.sym_power_sensor):
        obj_id = sensor["measured_object"]
        term_type = sensor["measured_terminal_type"]
        is_branch_terminal = (term_type == 0 or term_type == 1)
        lines = get_component(input_data, ComponentType.line)
        if obj_id in lines["id"] and is_branch_terminal:
            line_data = get_line_by_id(obj_id, line_lookup)
            u, v = line_data["from_node"], line_data["to_node"]
            M_flow.append((sensor["id"], u, v))

    for sensor in get_component(input_data, ComponentType.sym_current_sensor):
        obj_id = sensor["measured_object"]
        term_type = sensor["measured_terminal_type"]
        is_branch_terminal = (term_type == 0 or term_type == 1)
        lines = get_component(input_data, ComponentType.line)
        if obj_id in lines["id"] and is_branch_terminal:
            line_data = get_line_by_id(obj_id, line_lookup)
            u, v = line_data["from_node"], line_data["to_node"]
            M_flow.append((sensor["id"], u, v))

    return M_flow

def get_injection_measurements(input_data, adj, load_df, source_map):
    """
    Parses node-specific power sensors and maps them to bus-based injections.
    
    Handles three categories:
    - Node sensors: Direct bus mapping.
    - Load sensors: Translates Load ID to parent Bus ID.
    - Source sensors: Resolves connectivity using the source_map lookup.
    
    Returns: List of (sensor_id, target_node, neighbor_list) tuples.
    """
    M_inj = []

    for sensor in get_component(input_data, ComponentType.sym_power_sensor):
        obj_id = sensor["measured_object"]
        term_type = sensor["measured_terminal_type"]
        
        target_node = None
        
        # Case A: Explicit Node Sensor
        if term_type == MeasuredTerminalType.node:
            target_node = obj_id # The object ID is the Node ID
            
        # Case B: Load Sensor (Implicit Nodal Injection)
        elif term_type == MeasuredTerminalType.load:
            # Map Load ID -> Node ID
            load_data = get_load_by_id(obj_id, load_df)
            target_node = load_data["node"]
        # Case C: Source Sensor (Implicit Nodal Injection)    
        elif term_type == MeasuredTerminalType.source:
            # Look up which node the source is connected to
            target_node = get_node_from_sensor(obj_id, term_type, source_map)

        if target_node:
            # Neighbors must be from the 'Grounded' adjacency list
            neighbors = get_neighbors(adj, target_node) 
            M_inj.append((sensor["id"], target_node, neighbors))
    return M_inj

def get_zin_measurments(input_data, adj):
    """
    Generates virtual 'Zero-Injection' measurements for unmonitored buses.
    
    To ensure observability in sparse grids, buses without physical sensors are 
    assigned a 'Virtual Sensor ID' (90000+). This allows the DSU logic to treat 
    unmonitored nodes as constraints, preventing islands from being marked 
    as strictly unobservable.
    """
    M_zin = []
    nodes_with = set()
    for sensor in input_data.get(ComponentType.source, []):
       nodes_with.add(sensor["node"])
    for sensor in input_data.get(ComponentType.sym_load, []):
        nodes_with.add(sensor["node"])
    for node in input_data.get(ComponentType.node, []):
        node_id = node["id"]
        if node_id not in nodes_with:
            # We need the neighbors to treat this as a link in the DSU
            neighbors = get_neighbors(adj, node_id) # Using your existing neighbor function
            
            # Create a 'Virtual Sensor ID' so it doesn't clash with physical ones
            # 90000 + ID is a common trick for virtual mapping
            virtual_id = 90000 + node_id 
            
            # Format: (id, target_node, neighbors)
            M_zin.append((virtual_id, node_id, neighbors))
    return M_zin

def create_measurement_map(M_flow, M_inj_zin):
    """
    Consolidates flow and injection/zin measurement lists into a unified 
    dictionary lookup table.
    
    The resulting structure separates measurement logic by 'type', enabling
    O(1) retrieval of graph-theoretic properties (u, v) for any sensor ID.
    """
    measurement_map = {}

    # Flow measurements cover a physical branch (u, v)
    for m_id, u, v in M_flow:
        measurement_map[m_id] = {'type': 'flow', 'nodes': (u, v)}

    # Injection measurements (and ZINs) are associated with a single bus
    # but depend on ALL incident neighbors
    for m_id, u, neighbors in M_inj_zin:
        measurement_map[m_id] = {'type': 'injection', 'bus': u, 'neighbors': neighbors}

    return measurement_map

def get_measurement_endpoints(m_id, measurement_map):
    """
    Resolves the graph-theoretic endpoints (u, v) for a given measurement ID.
    
    This function handles the polymorphic nature of measurements:
    - For flow: Returns the static branch endpoints.
    - For injection/ZIN: Returns the bus and its primary electrical neighbor. 
      Supports tuple-based input (id, neighbor) for use in cycle-swapping 
      or pathfinding algorithms.
    """
    # CASE A: Handle the Contextual Tuple (m_id = (actual_id, target_neighbor))
    # This is used for swaps or DSU results where an injection is 'linked' to a specific node
    if isinstance(m_id, tuple):
        actual_id = m_id[0]
        target_neighbor = m_id[1]
        
        info = measurement_map.get(actual_id)
        if not info: 
            return None, None
            
        if info['type'] == 'flow':
            # Flows are fixed, target_neighbor is ignored
            return info['nodes']
        else:
            # Injection: return the source bus and the specific neighbor provided in the tuple
            return info['bus'], target_neighbor
    
    # CASE B: Handle the Scalar ID (m_id = actual_id)
    # Used in loops through R or general lookups
    else:
        info = measurement_map.get(m_id)
        if not info: 
            return None, None

        if info['type'] == 'flow':
            return info['nodes']  # Returns the (u, v) tuple directly
        else:
            # Injection/ZIN: If no specific neighbor is provided, we default to the first neighbor.
            # In the Aguirre/LCA logic, an injection effectively "links" its bus to its primary neighbor.
            bus = info['bus']
            neighbors = info.get('neighbors', [])
            v = neighbors[0] if neighbors else None
            return bus, v