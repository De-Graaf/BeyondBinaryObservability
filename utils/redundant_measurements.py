from utils.setunion import make_parent, union
from utils.mapping_utils import find_line
from power_grid_model import (
    PowerGridModel,
    CalculationType,
    CalculationMethod,
    ComponentType,
    DatasetType,
    initialize_array
)

def find_redundants_measurements(input_data, M_flow, M_inj_zin, line_map):
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

    print(f"Total Redundant Measurements Identified: {len(R)}")
    return V, parent, R, base_partition_dict