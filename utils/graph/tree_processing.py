def preprocess_tree(tree_adj, root=0):
    """
    Performs a Depth-First Search (DFS) traversal to compile structural tree metadata.

    This function maps the hierarchical relationships of a connected grid island starting from a 
    specified root node. It calculates parent-child links, node depths, and the telemetry 
    sensors (edge IDs) associated with each branch.

    Parameters:
    -----------
    tree_adj : dict
        An adjacency list representation of the network tree where keys are node IDs and values 
        are lists of (neighbor_node, m_id) tuples.
    root : int, default 0
        The starting node ID (typically the island root) for the traversal.

    Returns:
    --------
    tuple (parent, depth, edge_to_parent)
        - parent : dict
            Maps each node to its direct ancestral node.
        - depth  : dict
            Maps each node to its distance from the root.
        - edge_to_parent : dict
            Maps each node to the unique measurement ID linking it to its parent.
    """
    parent = {root: None}
    depth = {root: 0}
    edge_to_parent = {root: None}
    stack = [root]
    
    while stack:
        u = stack.pop()
        for v, m_id in tree_adj.get(u, []):
            if v not in parent:
                parent[v] = u
                depth[v] = depth[u] + 1
                edge_to_parent[v] = m_id
                stack.append(v)
    return parent, depth, edge_to_parent

def get_path_in_tree(u, v, tree_adj):
    """
    Extracts the unique path between two nodes in the current Spanning Forest.

    Since the spanning forest is acyclic, a single unique path exists between any two 
    connected nodes. This function uses Breadth-First Search (BFS) to traverse the tree 
    and identify the sequence of node-to-edge transitions connecting u and v.

    Parameters:
    -----------
    u : int
        The starting node identifier.
    v : int
        The target node identifier.
    tree_adj : dict
        An adjacency list representation of the network tree.

    Returns:
    --------
    list or None
        A list of alternating node IDs and edge (measurement) IDs representing the path, 
        or None if no path exists (i.e., u and v are in different islands).
    """
    queue = [(u, [u])]
    visited = {u}
    while queue:
        curr, path = queue.pop(0)
        if curr == v:
            return path
        for neighbor, edge_id in tree_adj.get(curr, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [edge_id]))
    return None