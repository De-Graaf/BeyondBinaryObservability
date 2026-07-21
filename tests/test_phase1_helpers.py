import unittest

from power_grid_model import ComponentType

from utils.graph.setunion import find, make_parent, union
from utils.measurements.get_component import get_component
from utils.measurements.mapping import create_line_map, find_line
from utils.measurements.measurements import (
    create_measurement_map,
    get_measurement_endpoints,
)
from utils.observability.check_island_obs import check_island_observability


class TestPhase1Helpers(unittest.TestCase):
    def test_get_component_supports_enum_and_string_keys(self):
        input_data = {
            ComponentType.line: [{"id": 1, "from_node": 10, "to_node": 11}],
            "sym_power_sensor": [{"id": 99, "measured_object": 1}],
        }

        self.assertEqual(
            get_component(input_data, ComponentType.line),
            [{"id": 1, "from_node": 10, "to_node": 11}],
        )
        self.assertEqual(
            get_component(input_data, ComponentType.sym_power_sensor),
            [{"id": 99, "measured_object": 1}],
        )
        self.assertEqual(get_component({}, ComponentType.line), [])

    def test_create_line_map_and_find_line_handle_reversed_nodes(self):
        input_data = {
            ComponentType.line: [{"id": 7, "from_node": 10, "to_node": 11}],
        }

        line_map = create_line_map(input_data, ComponentType.line)

        self.assertEqual(line_map, {(10, 11): 7})
        self.assertEqual(find_line(10, 11, line_map), 7)
        self.assertEqual(find_line(11, 10, line_map), 7)

    def test_measurement_endpoints_cover_flow_and_injection_cases(self):
        measurement_map = create_measurement_map(
            M_flow=[(1, 10, 11)],
            M_inj_zin=[(2, 5, [8, 9])],
        )

        self.assertEqual(get_measurement_endpoints(1, measurement_map), (10, 11))
        self.assertEqual(get_measurement_endpoints(2, measurement_map), (5, 8))
        self.assertEqual(get_measurement_endpoints((2, 9), measurement_map), (5, 9))
        self.assertEqual(get_measurement_endpoints((999, 1), measurement_map), (None, None))

    def test_check_island_observability_reports_reference_sources_and_stability(self):
        parent = {1: 1, 2: 1, 3: 3}
        all_nodes = [1, 2, 3]
        input_data = {
            ComponentType.node: [{"id": 1}, {"id": 2}, {"id": 3}],
            ComponentType.sym_voltage_sensor: [{"measured_object": 1}],
            ComponentType.source: [{"node": 3}],
        }
        measurement_map = create_measurement_map(
            M_flow=[(100, 1, 2)],
            M_inj_zin=[],
        )
        admittance_map = {100: 2.5}
        base_partition_edges = {100: 100}

        report = check_island_observability(
            parent,
            input_data,
            all_nodes,
            admittance_map,
            base_partition_edges,
            measurement_map,
        )

        self.assertTrue(report[1]["is_observable"])
        self.assertEqual(report[1]["ref_type"], "Voltage Sensor")
        self.assertEqual(report[1]["anchors"], [1])
        self.assertEqual(report[1]["stability_score"], 2.5)

        self.assertTrue(report[3]["is_observable"])
        self.assertEqual(report[3]["ref_type"], "Source (Slack Bus)")
        self.assertEqual(report[3]["anchors"], [3])
        self.assertEqual(report[3]["stability_score"], 0.0)

    def test_union_find_helpers_work_for_basic_tree_merging(self):
        parent = make_parent([1, 2, 3])

        self.assertTrue(union(parent, 1, 2))
        self.assertEqual(find(parent, 1), find(parent, 2))
        self.assertFalse(union(parent, 1, 2))


if __name__ == "__main__":
    unittest.main()
