import pandas as pd
import numpy as np
import networkx as nx
import json

def generate_pgm_json(n_nodes=14, mesh_ratio=0.2, sensor_density=0.4):
    # 1. Create Topology - Guaranteed Connectivity via Spanning Tree Backbone
    G = nx.random_labeled_tree(n_nodes)
    mapping = {old: int(old + 1) for old in G.nodes()} 
    G = nx.relabel_nodes(G, mapping)
    
    # Inject meshing loops without altering the spanning tree backbone
    num_extra_lines = int(n_nodes * mesh_ratio)
    nodes_list = list(G.nodes())
    for _ in range(num_extra_lines):
        u, v = np.random.choice(nodes_list, 2, replace=False)
        u_int, v_int = u.item(), v.item()
        if not G.has_edge(u_int, v_int):
            G.add_edge(u_int, v_int)

    current_id = n_nodes + 1

    # 2. Populate Nodes
    pgm_nodes = [{"id": int(n), "u_rated": 10000.0} for n in G.nodes()]

    # 3. Setup Slack Reference Source (At Node 1)
    source_id = 100
    pgm_sources = [{"id": source_id, "node": 1, "status": 1, "u_ref": 1.0}]

    # 4. Generate Lines
    pgm_lines = []
    for u, v in G.edges():
        base_r = 0.1
        jitter = np.random.uniform(0.8, 1.2)
        pgm_lines.append({
            "id": int(current_id),
            "from_node": int(u),
            "to_node": int(v),
            "from_status": 1,
            "to_status": 1,
            "r1": float(base_r * jitter),
            "x1": float(base_r * jitter),
            "c1": 0.0,
            "tan1": 0.0,
            "i_n": 500.0
        })
        current_id += 1

    # 5. Generate Loads
    pgm_loads = []
    potential_load_nodes = [n for n in G.nodes() if n != 1]
    for n in potential_load_nodes:
        if np.random.rand() < 0.8: 
            pgm_loads.append({"id": int(current_id), "node": int(n), "status": 1, "type": 0})
            current_id += 1

    # 6. Populate Sensor Network
    pgm_v_sensors = []
    pgm_p_sensors = []
    pgm_i_sensors = []

    # Voltage Sensors (Schema Corrected for PGM Validation)
    for node in G.nodes():
        if np.random.rand() < sensor_density:
            pgm_v_sensors.append({
                "id": int(current_id),
                "measured_object": int(node),
                "measured_terminal_type": 10,  # Node terminal type constant
                "u_sigma": 10.0,
                "u_measured": 10000.0,
                "u_angle_sigma": 0.01,
                "u_angle_measured": 0.0,
                "voltage_sigma": 10.0
            })
            current_id += 1

    # Power Injection Sensors (Corrected to map directly to Node IDs via type 9)
    for node in G.nodes():
        if np.random.rand() < sensor_density:
            pgm_p_sensors.append({
                "id": int(current_id),
                "measured_object": int(node),
                "measured_terminal_type": 9,  # Internal Nodal Injection Terminal Constant
                "p_sigma": 1000.0, 
                "q_sigma": 1000.0, 
                "p_measured": 0.0, 
                "q_measured": 0.0
            })
            current_id += 1

    # Current Flow Sensors (On Lines)
    for line in pgm_lines:
        if np.random.rand() < (sensor_density / 2):
            pgm_i_sensors.append({
                "id": int(current_id),
                "measured_object": int(line["id"]),
                "measured_terminal_type": 0,
                "angle_measurement_type": 0,
                "i_sigma": 0.1, 
                "i_measured": 1.0, 
                "i_angle_sigma": 0.01, 
                "i_angle_measured": 0.0
            })
            current_id += 1

    # 7. Construct Output Dictionary
    output = {
        "version": "1.0",
        "type": "input",
        "is_batch": False,
        "attributes": {},
        "data": {
            "source": pgm_sources,
            "node": pgm_nodes,
            "line": pgm_lines,
            "sym_power_sensor": pgm_p_sensors,    
            "sym_current_sensor": pgm_i_sensors,  
            "sym_voltage_sensor": pgm_v_sensors,  
            "sym_load": pgm_loads                
        }
    }
    return output