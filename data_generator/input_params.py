from dataclasses import dataclass
from typing import Optional

"""
Input parameters for Power Grid Model State Estimation data generator.
"""



@dataclass
class GridParameters:
    """Parameters defining the power grid structure."""
    
    num_nodes: int
    num_lines: int
    num_transformers: int
    num_loads: int
    num_generators: int
    base_voltage: float  # kV
    base_power: float  # MVA


@dataclass
class MeasurementParameters:
    """Parameters for measurement generation."""
    
    voltage_std: float  # Standard deviation for voltage measurements
    current_std: float  # Standard deviation for current measurements
    power_std: float  # Standard deviation for power measurements
    missing_data_ratio: float  # Fraction of missing measurements (0.0-1.0)
    measurement_frequency: int  # Measurements per time step


@dataclass
class StateEstimationParameters:
    """Parameters for state estimation configuration."""
    
    estimation_method: str  # e.g., "weighted_least_squares", "kalman_filter"
    convergence_threshold: float
    max_iterations: int
    bad_data_detection: bool


class InputParams:
    """Main configuration class for data generator."""
    
    def __init__(
        self,
        grid: GridParameters,
        measurements: MeasurementParameters,
        state_estimation: StateEstimationParameters,
        time_steps: int = 100,
        random_seed: Optional[int] = None,
    ):
        self.grid = grid
        self.measurements = measurements
        self.state_estimation = state_estimation
        self.time_steps = time_steps
        self.random_seed = random_seed