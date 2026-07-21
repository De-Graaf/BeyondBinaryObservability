def create_line_map(input_data, component_type_enum):
    """
    Creates a lookup map for line IDs using frozenset for order-insensitivity.
    """
    line_map = {}
    for line in input_data[component_type_enum]:
        u, v = line['from_node'], line['to_node']
        # Using a frozenset or sorted tuple handles (u,v) vs (v,u)
        line_map[tuple(sorted((u, v)))] = line['id']
    return line_map

def find_line(u, v, line_map):
    if u is None or v is None:
        print(f"Warning: Missing node information for edge ({u}, {v}). Cannot find corresponding line ID.")
        return None
        
    u_native = int(u)
    v_native = int(v)
    
    # Create the strict, type-safe lookup key
    lookup_key = tuple(sorted((u_native, v_native)))
    return line_map.get(lookup_key)