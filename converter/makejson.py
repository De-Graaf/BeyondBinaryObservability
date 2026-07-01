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
node = initialize_array(DatasetType.input, ComponentType.node, 3)
node["id"] = [1, 2, 6]
node["u_rated"] = [10.5e3, 10.5e3, 10.5e3]

# line
line = initialize_array(DatasetType.input, ComponentType.line, 3)
line["id"] = [3, 5, 8]
line["from_node"] = [1, 2, 1]
line["to_node"] = [2, 6, 6]
line["from_status"] = [1, 1, 1]
line["to_status"] = [1, 1, 1]
line["r1"] = [0.25, 0.25, 0.25]
line["x1"] = [0.2, 0.2, 0.2]
line["c1"] = [10e-6, 10e-6, 10e-6]
line["tan1"] = [0.0, 0.0, 0.0]
line["i_n"] = [1000, 1000, 1000]

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

# power sensor
sym_power_sensor = initialize_array(DatasetType.input, ComponentType.sym_power_sensor, 5)
sym_power_sensor["id"] = [14, 15, 16, 17, 18]
sym_power_sensor["measured_object"] = [3, 5, 8, 4, 6]
sym_power_sensor["measured_terminal_type"] = [
    MeasuredTerminalType.branch_to,
    MeasuredTerminalType.branch_from,
    MeasuredTerminalType.branch_to,
    MeasuredTerminalType.load,
    MeasuredTerminalType.node,
]
sym_power_sensor["power_sigma"] = [1.0e3, 1.0e3, 1.0e3, 1.0e3, 1.0e3]
sym_power_sensor["p_measured"] = [-1.66e07, -3.36e06, -1.33e07, 20e6, -10e6]
sym_power_sensor["q_measured"] = [-3.82e06, -1.17e06, -2.88e06, 5e6, -2e6]

# current sensor
sym_current_sensor = initialize_array(DatasetType.input, ComponentType.sym_current_sensor, 3)
sym_current_sensor["id"] = [19, 20, 21]
sym_current_sensor["measured_object"] = [3, 5, 8]
sym_current_sensor["measured_terminal_type"] = [
    MeasuredTerminalType.branch_from,
    MeasuredTerminalType.branch_to,
    MeasuredTerminalType.branch_from,
]
sym_current_sensor["angle_measurement_type"] = [
    AngleMeasurementType.global_angle,
    AngleMeasurementType.local_angle,
    AngleMeasurementType.local_angle,
]
sym_current_sensor["i_sigma"] = [100, 100, 100]
sym_current_sensor["i_angle_sigma"] = [0.1, 0.1, 0.1]
sym_current_sensor["i_measured"] = [978.814, 806.486, 776.753]
sym_current_sensor["i_angle_measured"] = [-0.20864859135578062, 1.368, 1.349]

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
save_path = current_dir / "input.json"
json_serialize_to_file(save_path, input_data)

print(f"Success! Network data saved to: {save_path}")
