# ⚡ Power Grid Observability & Partitioning Pipeline

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MPL-2.0](https://img.shields.io/badge/License-MPL--2.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![power-grid-model](https://img.shields.io/badge/power--grid--model-≥1.12.0-orange)](https://github.com/PowerGridModel/power-grid-model)

---

## 📖 Project Overview

This pipeline is designed to handle **power system state estimation** by preprocessing grid data to ensure observability. It searches all possible observability configurations and ranks them. It utilizes a **Disjoint Set Union (DSU)** approach to efficiently manage network topology and identify redundant measurements that can be swapped to create various *Candidate Partitions* of the grid.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔗 **Topological Analysis** | Uses DSU with path compression to stitch nodes into "islands" or "superbuses" |
| 🔍 **Redundancy Identification** | Automatically detects redundant flow and injection measurements |
| 🔄 **Basis Exchange Algorithm** | Generates multiple unique candidate partitions by swapping redundant measurements with base partition edges |
| ✅ **Observability Validation** | Checks each partition for a valid voltage reference (Voltage Sensors or Slack Buses) to ensure numerical convergence |
| ⚙️ **PGM Integration** | Prepares and validates data for the `power-grid-model` State Estimation engine |

---

## 🔄 Pipeline Workflow

### 1. Stage Preparation & Data Loading
The notebook initializes the environment with `power-grid-model` components and loads grid data from a JSON source (e.g., `input.json`).

### 2. Network Pruning
A pruning step is included to reduce combinatorial explosion. It filters lines based on impedance (*Z* magnitude) to keep the partitioning process computationally viable.

### 3. Measurement Mapping
The system categorizes measurements into three types:

- 📏 **Flow Measurements** — Power/current sensors on lines
- 💉 **Injection Measurements** — Nodal injections from loads or sources
- 🔮 **Virtual Zero Injection Nodes (ZIN)** — Nodes without loads/sources, treated as virtual measurements

### 4. Partition Exploration
The core logic identifies a **Base Partition** (a spanning forest). It then identifies *Fundamental Cycles* created by redundant measurements and performs a **Basis Exchange** to find alternative observable sets.

### 5. State Estimation & Validation
Each candidate partition is converted back into a PGM-compatible format. The pipeline then attempts to run State Estimation:

| Outcome | Meaning |
|---|---|
| ✅ **Success** | The partition is numerically stable and fully observable |
| ❌ **Failure** | Captures errors such as *"Not enough measurements"* or *"Floating islands"* |

---

## 🚀 Getting Started

### Prerequisites

Requires **Python 3.12+** and the following packages:

```txt
numpy
pandas
power-grid-model >= 1.12.0
```


### Running the Pipeline

1. Prepare your grid data as a JSON file (see `json_input/` for examples).
2. Open `pipeline.ipynb` in Jupyter:
   ```bash
   jupyter notebook pipeline.ipynb
   ```
3. Update the data-loading cell to point to your input file.
4. Run all cells to execute the full observability analysis.

---

## 💡 Technical Insights

> **Note on Scaling:** The number of ways to partition a set grows faster than exponentially ([Bell numbers](https://en.wikipedia.org/wiki/Bell_number)). This pipeline uses **pruning** and **DSU** to maintain efficiency even as the number of nodes increases.

---

## 📄 License

This project is licensed under the **Mozilla Public License 2.0 (MPL-2.0)**.  
See the [LICENSE](https://opensource.org/licenses/MPL-2.0) for details.
