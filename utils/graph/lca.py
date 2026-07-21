def get_path_using_LCA(u, v, parent, depth, edge_to_parent):
    """
    Finds the path between two nodes in a forest using Lowest Common Ancestor.
    """
    if u not in depth or v not in depth:
        return []
    
    path_edges = []
    
    # Bring both nodes to the same depth
    while depth[u] > depth[v]:
        path_edges.append(edge_to_parent[u])
        u = parent[u]
    while depth[v] > depth[u]:
        path_edges.append(edge_to_parent[v])
        v = parent[v]
        
    # Climb together until the LCA is reached
    while u != v:
        m_u, m_v = edge_to_parent[u], edge_to_parent[v]
        if m_u is not None: path_edges.append(m_u)
        if m_v is not None: path_edges.append(m_v)
        u, v = parent[u], parent[v]
        
    return path_edges

def find_weakest_link(edge_ids, admittance_map):
    """Identifies the edge with the minimum admittance."""
    if not edge_ids:
        return None
    return min(edge_ids, key=lambda eid: admittance_map.get(eid, float('inf')))