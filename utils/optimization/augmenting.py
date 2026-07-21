
from collections import deque

def augmenting_sequence(base_partition_set, r_id, adj, graph_context, measurement_context, line_df):
    """
    Implements Nucera & Gilles' augmenting sequence strategy adapted for PGM objects.
    Enforces strict isolation so lines with flow sensors cannot be double-assigned.
    """
    
    # Identify lines that permanently own a flow measurement right now
    lines_with_flows = set()

    # Step 1: Safely grab the inner map
    inner_map = measurement_context.get('measurement_map', {})
    line_map = measurement_context.get('line_map', {})
    if inner_map:
        for m_id, m_info in inner_map.items():
            if m_info.get('type') == 'flow':
                nodes = m_info.get('nodes', [])
                if nodes:
                    # Map the node pair to a line ID using the line_map
                    line_id = line_map.get(tuple(sorted((int(nodes[0]), int(nodes[1])))))
                    if line_id is not None:
                        lines_with_flows.add(int(line_id))  # Use int() to ensure standard Python integers

    parent_set = graph_context['parent_set']
    parents = graph_context['parents']
    depths = graph_context['depths']
    edge_to_parent = graph_context['edge_to_parent']

    # --- Standardize inputs and track physical assignments safely ---
    line_to_sensor_registry = {}
    if isinstance(base_partition_set, dict):
        for s_id, l_id in base_partition_set.items():
            if l_id is not None:
                line_to_sensor_registry[int(l_id)] = int(s_id)
    else:
        for sensor_id, line_id in base_partition_set.items():
            if line_id is not None:
                line_to_sensor_registry[int(line_id)] = int(sensor_id)

    sensor_id = int(r_id[0] if isinstance(r_id, tuple) else r_id)
    measurement_map = measurement_context['measurement_map']
    
    measurement_info = measurement_map.get(sensor_id)
    if not measurement_info:
        return base_partition_set
    
        
    candidate_edges = []
    
    # CASE A: Injection measurement
    if measurement_info['type'] == 'injection':
        bus = int(measurement_info['bus'])
        if line_df is not None:
            incident_lines = line_df[(line_df['from_node'] == bus) | (line_df['to_node'] == bus)]['id'].values
            # CRITICAL FIX: Incident line must NOT be already owned by a flow measurement
            candidate_edges = [
                int(line_id) for line_id in incident_lines 
                if line_id not in base_partition_set and int(line_id) not in lines_with_flows
            ]
            
    # CASE B: Flow measurement (Fixed mapping)
    elif measurement_info['type'] == 'flow':
        # 1. Safely get line_id, or fall back to looking up the node tuple in line_map
        line_id = measurement_info.get('line_id')
        
        if line_id is None:
            nodes = measurement_info.get('nodes')
            if nodes and len(nodes) == 2:
                u, v = int(nodes[0]), int(nodes[1])
                # Query your line_map using the endpoint coordinates
                line_id = measurement_context['line_map'].get((u, v)) or \
                        measurement_context['line_map'].get((v, u))

        # 2. Proceed with the normal loop allocation logic
        if line_id is not None:
            line_id = int(line_id)
            if line_id not in base_partition_set:
                candidate_edges = [line_id]

    assigned_sensors = {int(e) for e in base_partition_set}
    queue = deque()
    visited_edges = set()

    if sensor_id in assigned_sensors:
        current_active_edges = [int(e) for e in base_partition_set if e == sensor_id]
        for active_edge in current_active_edges:
            queue.append((active_edge, [active_edge]))
            visited_edges.add(active_edge)
    else:
        if not candidate_edges:            
            return base_partition_set
            
        for edge in candidate_edges:
            queue.append((edge, [edge]))
            visited_edges.add(edge)

    while queue:
        current_edge, path = queue.popleft()
        level = len(path)

        if level % 2 == 1:  # Odd level: Insertion evaluation
            current_edge = int(current_edge)
            info_edge = measurement_map.get(current_edge)

            if info_edge is not None:
                if info_edge['type'] == 'flow':
                    u, v = int(info_edge['nodes'][0]), int(info_edge['nodes'][1])
                else:
                    bus_id = int(info_edge['bus'])
                    line_row = line_df[(line_df['from_node'] == bus_id) | (line_df['to_node'] == bus_id)]
                    if line_row.empty:
                        u, v = None, None
                    else:
                        u, v = int(line_row['from_node'].values[0]), int(line_row['to_node'].values[0])
            else:
                line_row = line_df[line_df['id'] == current_edge]
                if line_row.empty:
                    u, v = None, None
                else:
                    u, v = int(line_row['from_node'].values[0]), int(line_row['to_node'].values[0])
            
            if u is None or v is None or u not in depths or v not in depths:
                loop = None
            else:
                path_edges = []
                curr_u, curr_v = u, v
                while curr_u is not None and depths[curr_u] > depths[curr_v]:
                    path_edges.append(edge_to_parent[curr_u])
                    curr_u = parents[curr_u]
                    
                while curr_v is not None and depths[curr_v] > depths[curr_u]:
                    path_edges.append(edge_to_parent[curr_v])
                    curr_v = parents[curr_v]
                    
                while curr_u is not None and curr_v is not None and curr_u != curr_v:
                    m_u, m_v = edge_to_parent[curr_u], edge_to_parent[curr_v]
                    if m_u is not None: path_edges.append(m_u)
                    if m_v is not None: path_edges.append(m_v)
                    curr_u, curr_v = parents[curr_u], parents[curr_v]
                
                if curr_u is not None and curr_v is not None and curr_u == curr_v:
                    loop = path_edges + [current_edge] if path_edges else None
                else:
                    loop = None

            # --- PATH RECONSTRUCTION (No Loop Found) ---
            if loop is None:
                new_partition_set = base_partition_set.copy()
                sensor_to_line = {}
                for s_id, l_id in base_partition_set.items():
                    if l_id is not None:
                        sensor_to_line[int(s_id)] = int(l_id)

                currently_freed_sensor = int(r_id[0] if isinstance(r_id, tuple) else r_id)

                valid_path_swap = True
                for idx, seq_edge in enumerate(path):
                    line_id = int(seq_edge)

                    if idx % 2 == 0:
                        sensor_id = currently_freed_sensor
                        # CRITICAL FIX: If this target line is locked by a flow sensor, 
                        # an injection cannot take it. Abort this specific path modification.
                        s_type = measurement_map.get(sensor_id, {}).get('type')
                        if s_type == 'injection' and line_id in lines_with_flows:
                            valid_path_swap = False
                            break
                        
                        new_partition_set[sensor_id] = line_id
                    else:
                        for s, l in list(sensor_to_line.items()):
                            if l == line_id:
                                new_partition_set.pop(s, None)
                                del sensor_to_line[s]
                                currently_freed_sensor = s
                                break
                
                if valid_path_swap:
                    # Clean up backward mapping references cleanly before returning
                    final_sensor_to_line = {int(k): int(v) for k, v in new_partition_set.items() if v is not None}
                    return base_partition_set

            # --- LOOP DETECTED ---
            else:
                valid_forest_sensors = []
                for e in loop:
                    if e in base_partition_set and e not in visited_edges:
                        m_info = measurement_map.get(e)
                        # Flow sensors are hard locked. Only injections can shift.
                        if m_info and m_info.get('type') == 'injection':
                            valid_forest_sensors.append(e)
                            
                if valid_forest_sensors:
                    import random
                    random_sensor = random.choice(valid_forest_sensors)
                    measurement_info = measurement_map.get(random_sensor)
                    
                    if measurement_info['type'] == 'injection':
                        bus = int(measurement_info['bus'])
                        if line_df is not None:
                            incident_lines = line_df[(line_df['from_node'] == bus) | (line_df['to_node'] == bus)]['id'].values

                            corresponding_line = None
                            for sensor, line_id in base_partition_set.items():
                                if int(sensor) == int(random_sensor):
                                    corresponding_line = line_id
                                    break
                            
                            if corresponding_line is not None:
                                visited_edges.add(random_sensor)
                                queue.append((corresponding_line, path + [corresponding_line]))
        
        else:  # Even level: Evaluating removal of edge
            line_row = line_df[line_df['id'] == current_edge]
            if not line_row.empty:
                u_node = int(line_row['from_node'].values[0])
                v_node = int(line_row['to_node'].values[0])
                
                freed_injection = None
                for active_sensor in base_partition_set:
                    s_info = measurement_map.get(active_sensor)
                    if s_info and s_info['type'] == 'injection' and int(s_info['bus']) in (u_node, v_node):
                        for sensor_id, line_id in base_partition_set.items():
                            if int(sensor_id) == int(active_sensor):
                                if line_id == current_edge:
                                    freed_injection = active_sensor
                                    break
                        if freed_injection is not None:
                            break
            
                if freed_injection is not None:
                    inj_info = measurement_map.get(freed_injection)
                    if inj_info:
                        bus_id = int(inj_info['bus'])
                        incident_lines = line_df[(line_df['from_node'] == bus_id) | (line_df['to_node'] == bus_id)]['id'].values
                        for next_line in incident_lines:
                            if next_line == current_edge:
                                continue
                            if next_line is not None:
                                # CRITICAL FIX: The alternative branch must not be registered as an active flow asset
                                if (next_line not in base_partition_set and 
                                    next_line not in visited_edges and
                                    int(next_line) not in lines_with_flows):
                                    
                                    visited_edges.add(next_line)
                                    queue.append((next_line, path + [next_line]))

    return {
        base_partition_set
    }