from power_grid_model import (
    ComponentType,
)

def prune_network(input_data, low_z_threshold=1e-4, high_z_threshold=1.0):
    """
    Filters the network line topology by identifying and excluding branches with extreme impedance values.

    Numerical instability in Power Grid Models often stems from lines with near-zero impedance 
    (causing singular matrices) or excessively high impedance (causing weak coupling that 
    renders telemetry data uninformative for state estimation). This function cleans the 
    input dataset by retaining only those lines falling within the specified impedance bounds.

    Parameters:
    -----------
    input_data : dict
        The raw power grid model dictionary containing component definitions.
    low_z_threshold : float, default 1e-4
        The lower bound for impedance magnitude. Lines below this are flagged to prevent 
        singular Jacobian matrix issues.
    high_z_threshold : float, default 1.0
        The upper bound for impedance magnitude. Lines above this are flagged due to 
        minimal electrical contribution.

    Returns:
    --------
    tuple (pruned_network, flagged_lines)
        - pruned_network : DataFrame or structured array containing valid lines within the impedance thresholds.
        - flagged_lines  : DataFrame or structured array containing the lines removed from the network backbone.
    """
    pruned_network_indices = []
    flagged_lines_indices = []
    lines = input_data[ComponentType.line]
    for i, line_id in enumerate(lines["id"]):
        r = lines["r1"][i]
        x = lines["x1"][i]
        z_magnitude = (r**2 + x**2)**0.5
        criteria=True
        is_low = z_magnitude < low_z_threshold 
        is_high = z_magnitude > high_z_threshold
        if not is_low and not is_high:
            pruned_network_indices.append(i)
        else:
            flagged_lines_indices.append(i)
    pruned_network = lines[pruned_network_indices]
    flagged_lines = lines[flagged_lines_indices]
    return pruned_network, flagged_lines