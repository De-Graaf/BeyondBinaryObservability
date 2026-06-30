from power_grid_model import (
    ComponentType,
)

def prune_network(input_data, low_z_threshold=1e-4, high_z_threshold=1.0):
    pruned_network_indices = []
    flagged_lines_indices = []
    lines = input_data[ComponentType.line]
    for i, line_id in enumerate(lines["id"]):
        r = lines["r1"][i]
        x = lines["x1"][i]
        z_magnitude = (r**2 + x**2)**0.5
        criteria=True
        is_low = z_magnitude < low_z_threshold #See papers with also zero-impedance lines
        is_high = z_magnitude > high_z_threshold
        if not is_low and not is_high:
            pruned_network_indices.append(i)
        else:
            flagged_lines_indices.append(i)
    pruned_network = lines[pruned_network_indices]
    flagged_lines = lines[flagged_lines_indices]
    return pruned_network, flagged_lines