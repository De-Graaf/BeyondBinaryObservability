from utils.graph.setunion import make_parent, union
from utils.measurements.mapping import find_line
from power_grid_model import ComponentType

def find_redundants_measurements(input_data, M_flow, M_inj_zin, line_map):
    """
    Identifies redundant measurements in the grid by constructing a spanning forest via Union-Find (DSU).

    This function utilizes a Disjoint Set Union (DSU) algorithm to partition the network's buses 
    into connected trees. Measurements that would otherwise form a closed loop (a cycle) within 
    this forest structure are classified as 'redundant' because they provide redundant information 
    rather than contributing to the fundamental spanning basis of the grid.

    Parameters:
    -----------
    input_data : dict
        The raw power grid model dictionary containing network topology and components.
    M_flow : list
        A list of branch-based flow measurements formatted as tuples: (sensor_id, u, v).
    M_inj_zin : list
        A list of injection/Z-in measurements formatted as tuples: (sensor_id, target_bus, [neighbors]).
    line_map : dict
        A lookup table mapping bus-to-bus connections to their respective physical line IDs.

    Returns:
    --------
    tuple (V, parent, R, base_partition_dict)
        - V : set
            The complete set of bus/node identifiers in the grid.
        - parent : dict
            The final DSU parent-root mapping after processing all independent measurement constraints.
        - R : set
            A collection of redundant measurement identifiers (or (m, neighbor) tuples) that 
            do not contribute to the primary spanning forest.
        - base_partition_dict : dict
            A dictionary mapping fundamental measurement IDs to their corresponding physical line IDs.
    """
    V = set(input_data[ComponentType.node]["id"])

    parent = make_parent(V)

    R = set()
    base_partition_edges = []
    base_partition_dict = {}

    for m, u, v in M_flow:
        if not union(parent, u, v):
            R.add(m)
        else:
            base_partition_edges.append((u, v, m))
            physical_line_id = find_line(u, v, line_map)
            base_partition_dict[m] = physical_line_id

    for m, u, neighbors in M_inj_zin:
        found_base_link = False
        for v in neighbors:
            if not found_base_link:
                if not union(parent, u, v):
                    R.add((m, v))
                else:
                    base_partition_edges.append((u, v, m))
                    physical_line_id = find_line(u, v, line_map)
                    base_partition_dict[m] = physical_line_id
                    found_base_link = True
            else:
                R.add((m, v))
    return V, parent, R, base_partition_dict