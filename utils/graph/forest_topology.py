class ForestTopology:
    def __init__(self, initial_parent_set):
        self.parent_set = initial_parent_set.copy()
        self.parents = {}
        self.depths = {}
        self.edge_to_parent = {}

    def clear(self):
        """Wipes the slate clean for a fresh calculation pass."""
        self.parents.clear()
        self.depths.clear()
        self.edge_to_parent.clear()

    def update_from_subgraph(self, p_sub, d_sub, e_sub):
        """Updates the internal maps safely via memory pointers."""
        self.parents.update(p_sub)
        self.depths.update(d_sub)
        self.edge_to_parent.update(e_sub)
        
    def to_dict(self):
        """Legacy compatibility helper if your older functions strictly expect the old dict."""
        return {
            'parent_set': self.parent_set,
            'parents': self.parents,
            'depths': self.depths,
            'edge_to_parent': self.edge_to_parent
        }