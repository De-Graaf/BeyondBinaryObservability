def preprocess_tree(tree_adj, root=0):
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
    Finds the unique path between u and v in the current Spanning Forest.
    Uses a simple BFS/DFS since the forest has no cycles.
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