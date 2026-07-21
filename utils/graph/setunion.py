def make_parent(vertices):
    return {v: v for v in vertices}

def find(parent, v):
    if parent[v] != v:
        parent[v] = find(parent, parent[v])  # path compression
    return parent[v]

def union(parent, a, b):
    ra, rb = find(parent, a), find(parent, b)
    if ra == rb:
        return False
    parent[rb] = ra
    return True
