# Beyond Binary Observability

This repository contains the implementation accompanying the master's thesis:

**Beyond Binary Observability: Admittance-Aware Topological Observability Analysis for Power System State Estimation**

The project investigates power system observability from a graph-theoretic perspective, reformulating observability analysis as a combinatorial basis-selection problem. The framework combines topological observability assessment, observable island identification, and admittance-aware basis optimization to improve numerical robustness in state estimation.

## Repository Layout

- `pipeline.ipynb`: Main end-to-end thesis pipeline.
- `utils/`: Core algorithms split by concern:
	- `graph/`: Tree processing, LCA, DSU helpers.
	- `measurements/`: Sensor parsing, endpoint mapping, line lookup helpers.
	- `observability/`: Pruning, island checks, redundancy logic.
	- `optimization/`: Augmenting and targeted basis exchange loops.
	- `io/`: Logging and result export helpers.
- `data_generator/`: Synthetic grid generation.
- `json_input/`: Example/manual input datasets.
- `synthetic_data/`: Generated synthetic benchmark networks.
- `results/`: Logged benchmark and experiment outputs.

## Main Entry Point

The primary implementation is located in:

`pipeline.ipynb`

This notebook contains the complete workflow, including:

- Topological observability analysis
- Observable island detection
- Admittance-aware basis optimization
- Validation and benchmarking experiments
- Numerical state estimation evaluation

## Quickstart

### 1) Environment setup

Use Python 3.12+.

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Alternative with project metadata:

```bash
pip install .
```

### 2) Launch the notebook

```bash
jupyter notebook
```

Open `pipeline.ipynb` and run cells top-to-bottom.

### 3) Input data behavior

The notebook now resolves input data via relative paths in this order:

1. `synthetic_data/<generated-name>.json`
2. `<generated-name>.json` in the repository root
3. `json_input/input.json`

If none exist, a clear `FileNotFoundError` is raised listing checked paths.

## Dependencies

Core dependencies are listed in `requirements.txt` and duplicated in `pyproject.toml` for packaging.

Optional groups in `pyproject.toml`:

- `visualization`: extra visualization tooling.
- `rdf`: RDF/SPARQL and related data tooling.
- `doc`: documentation-related extras for power-grid-model.

Install optional extras with:

```bash
pip install .[visualization]
pip install .[rdf]
pip install .[doc]
```

## Handover Notes

### What is stable

- Main thesis pipeline execution path in `pipeline.ipynb`.
- Refactored utility package structure under `utils/`.
- Core dependency baseline for notebook execution.

### What is still exploratory

- Sections marked as "Work In Progress" in the notebook (postprocessing/state-estimation partition export).
- Commented experimental blocks (for example, optional plotting and Monte Carlo checks).

### Recommended first checks for a new maintainer

1. Run `pipeline.ipynb` top-to-bottom once with a known dataset.
2. Verify `results/thesis_scaling_results.csv` updates as expected.
3. Validate whether WIP postprocessing sections should be promoted, rewritten, or isolated into a separate notebook.

### Code style and module API notes

- Utility imports should use explicit module paths (for example, `utils.optimization.*`).
- The `utils.measurements` package now has explicit exports (no wildcard re-export), so public functions are discoverable from one place.

### Quick test command

Run the Phase 1 helper tests with:

```powershell
& '.\.venv\Scripts\python.exe' -m unittest discover -s '.\tests' -p 'test_*.py'
```

## License

This project is licensed under the **Mozilla Public License 2.0 (MPL-2.0)**.

See the [LICENSE](LICENSE) file for details.

## Author

**Lars de Graaf**  
Msc Artificial Intelligence  
Radboud University  
Research conducted at Alliander N.V.
