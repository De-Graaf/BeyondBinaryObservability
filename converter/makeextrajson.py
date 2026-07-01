import numpy as np
import tempfile
from pathlib import Path

from power_grid_model.utils import json_serialize_to_file
from power_grid_model import (
    AngleMeasurementType,
    CalculationMethod,
    CalculationType,
    ComponentType,
    DatasetType,
    LoadGenType,
    MeasuredTerminalType,
    PowerGridModel,
    initialize_array,
)
# node
# Updated Nodes (now 4 total)
node = initialize_array(DatasetType.input, ComponentType.node, 4)
node["id"] = [1, 2, 6, 9]
node["u_rated"] = [10.5e3] * 4

# Updated Lines (now 6 total: 3 original + 3 to Node 9)
line = initialize_array(DatasetType.input, ComponentType.line, 6)
line["id"] = [3, 5, 8, 30, 31, 32] # Added 30, 31, 32
line["from_node"] = [1, 2, 1, 9, 9, 9] # Node 9 connects to 1, 2, and 6
line["to_node"]   = [2, 6, 6, 1, 2, 6]
line["from_status"] = [1] * 6
line["to_status"]   = [1] * 6
line["r1"] = [0.25] * 6
line["x1"] = [0.2] * 6
line["c1"] = [10e-6] * 6
line["tan1"] = [0.0] * 6
line["i_n"] = [1000] * 6

# load
sym_load = initialize_array(DatasetType.input, ComponentType.sym_load, 2)
sym_load["id"] = [4, 7]
sym_load["node"] = [2, 6]
sym_load["status"] = [1, 1]
sym_load["type"] = [LoadGenType.const_power, LoadGenType.const_power]
sym_load["p_specified"] = [20e6, 10e6]
sym_load["q_specified"] = [5e6, 2e6]

# source
source = initialize_array(DatasetType.input, ComponentType.source, 1)
source["id"] = [10]
source["node"] = [1]
source["status"] = [1]
source["u_ref"] = [1.0]

# voltage sensor
sym_voltage_sensor = initialize_array(DatasetType.input, ComponentType.sym_voltage_sensor, 3)
sym_voltage_sensor["id"] = [11, 12, 13]
sym_voltage_sensor["measured_object"] = [1, 2, 6]
sym_voltage_sensor["u_sigma"] = [1.0, 1.0, 1.0]
sym_voltage_sensor["u_measured"] = [10489.37, 9997.32, 10102.01]
sym_voltage_sensor["u_angle_measured"] = [0.0, 0.0, 0.0]

# Updated Power Sensors (Added 3 flows for new lines + 1 injection at Node 9)
# Total = 5 (original) + 4 (new) = 9
sym_power_sensor = initialize_array(DatasetType.input, ComponentType.sym_power_sensor, 9)
sym_power_sensor["id"] = [14, 15, 16, 17, 18, 33, 34, 35, 36]
sym_power_sensor["measured_object"] = [3, 5, 8, 4, 6, 30, 31, 32, 9] # 36 is injection at 9
sym_power_sensor["measured_terminal_type"] = [
    MeasuredTerminalType.branch_to,   # 14
    MeasuredTerminalType.branch_from, # 15
    MeasuredTerminalType.branch_to,   # 16
    MeasuredTerminalType.load,        # 17
    MeasuredTerminalType.node,        # 18
    MeasuredTerminalType.branch_from, # 33 (Line 9-1)
    MeasuredTerminalType.branch_from, # 34 (Line 9-2)
    MeasuredTerminalType.branch_from, # 35 (Line 9-6)
    MeasuredTerminalType.node,        # 36 (Injection at 9)
    
]
sym_power_sensor["power_sigma"] = [1.0e3] * 9
sym_power_sensor["p_measured"] = [-1.66e07, -3.36e06, -1.33e07, 20e6, -10e6, 0.0, 0.0, 0.0, 0.0]
sym_power_sensor["q_measured"] = [-3.82e06, -1.17e06, -2.88e06, 5e6, -2e6, 0.0, 0.0, 0.0, 0.0]

# Updated Current Sensors (Added 3 for the new lines)
# Total = 3 (original) + 3 (new) = 6
sym_current_sensor = initialize_array(DatasetType.input, ComponentType.sym_current_sensor, 6)
sym_current_sensor["id"] = [19, 20, 21, 37, 38, 39]
sym_current_sensor["measured_object"] = [3, 5, 8, 30, 31, 32]
sym_current_sensor["measured_terminal_type"] = [MeasuredTerminalType.branch_from] * 6
sym_current_sensor["i_sigma"] = [100] * 6
sym_current_sensor["i_angle_sigma"] = [0.1] * 6
sym_current_sensor["i_measured"] = [978.8, 806.4, 776.7, 100.0, 100.0, 100.0]
sym_current_sensor["i_angle_measured"] = [0.0] * 6
# all
input_data = {
    ComponentType.node: node,
    ComponentType.line: line,
    ComponentType.sym_load: sym_load,
    ComponentType.source: source,
    ComponentType.sym_voltage_sensor: sym_voltage_sensor,
    ComponentType.sym_power_sensor: sym_power_sensor,
    ComponentType.sym_current_sensor: sym_current_sensor,
}

# 3. Export to JSON
# This saves 'input.json' to the same directory as this script
current_dir = Path(__file__).parent.resolve()
save_path = current_dir / "inputextra.json"
json_serialize_to_file(save_path, input_data)

print(f"Success! Network data saved to: {save_path}")
