# Linear Power Flow

[![PyPI version](https://badge.fury.io/py/linear-power-flow.svg)](https://badge.fury.io/py/linear-power-flow)
[![Python Version](https://img.shields.io/pypi/pyversions/linear-power-flow.svg)](https://pypi.org/project/linear-power-flow/)
[![Tests](https://github.com/yourusername/linear_power_flow/actions/workflows/test.yml/badge.svg)](https://github.com/yourusername/linear_power_flow/actions/workflows/test.yml)
[![License: BSD 3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python package for efficient linear power flow analysis in electrical power systems. This package provides fast, linearized power flow solutions suitable for large-scale power system studies.

The rectangular model used in this tool comes from:

T. Hong, D. Zhao and Y. Zhang, "A Relaxed PV Bus Model in Linear Power Flow," in IEEE Transactions on Power Delivery, vol. 36, no. 2, pp. 1249-1252, April 2021, doi: 10.1109/TPWRD.2020.3031758.

keywords: {Load flow;Numerical models;Computational modeling;Mathematical model;Voltage control;Reactive power;Load modeling;PV bus model;linear power flow;rectangular coordinates;multiphase power system}.


## Features

- **Fast Linear Power Flow Computation**: Linearized power flow models for rapid analysis
- **Multiple Load Models**: Support for constant PQ, constant current, and constant impedance load models
- **Sparse Matrix Support**: Efficient handling of large-scale power systems using sparse matrices
- **Flexible Bus Types**: Support for slack (reference), PV (generator), and PQ (load) buses
- **Customizable Linearization**: Taylor expansion and linear regression-based linearization methods
- **Easy Integration**: Compatible with popular power system packages like PYPOWER and pandapower

## Installation

### From PyPI

```bash
pip install linear-power-flow
```

### From Source

```bash
git clone https://github.com/th1275/linear_power_flow.git
cd linear_power_flow
pip install -e .
```

### For Development

```bash
pip install -e .[dev]
```

### For Running Examples

```bash
pip install -e .[examples]
```

## Quick Start

```python
import numpy as np
from linear_power_flow import lpf_run, LPF_OPTION_DEFAULT

# Define your power system
y_bus = np.array([...])  # Bus admittance matrix
bus_power = np.array([...])  # Bus power injections
s_idx = np.array([0])  # Slack bus indices
v_idx = np.array([1, 2])  # PV bus indices
o_idx = np.array([3, 4, 5])  # PQ bus indices
vs = 1.0 + 0j  # Slack bus voltage
u_v = np.array([1.0, 1.0])  # PV bus voltage magnitudes

# Configure options
lpf_option = LPF_OPTION_DEFAULT.copy()
lpf_option["pv_model"] = 0  # Constant current model
lpf_option["new_M"] = True  # Compute linearization factors

# Run linear power flow
v_result = lpf_run(y_bus, bus_power, s_idx, v_idx, o_idx, vs, u_v, lpf_option)

print(f"Voltage magnitudes: {np.abs(v_result)}")
```

## Detailed Usage

### Matrix Partitioning

```python
from linear_power_flow import partition_matrix_pv

# Partition admittance matrix for PV buses
Yss, Ysv, Yso, Yvs, Yvv, Yvo, Yos, Yov, Yoo = partition_matrix_pv(
    y_bus, s_idx, v_idx
)
```

### Computing Branch Currents

```python
from linear_power_flow import compute_simple_branch_currents

# Compute branch currents
branches = np.array([[0, 1], [1, 2], [2, 3]])  # From-to bus pairs
currents = compute_simple_branch_currents(y_bus, voltages, branches)
```

### Custom Linearization

```python
from linear_power_flow.rect_model import fit_multi_reference_approximation

# Fit linearization around operating points
v_m_ref = np.array([1.0, 0.95, 1.05])  # Reference voltage magnitudes
v_a_ref = np.array([0.0, -0.1, 0.1])  # Reference voltage angles

M1, M2, M3, metrics = fit_multi_reference_approximation(
    v_m_ref, v_a_ref,
    delta_v_m=0.01,  # Magnitude variation range
    delta_v_a=0.05,  # Angle variation range
    load_model=0  # Constant PQ model
)
```

## Configuration Options

The `lpf_option` dictionary controls the behavior of the linear power flow:

```python
lpf_option = {
    "M1": complex,      # Linearization coefficient 1
    "M2": complex,      # Linearization coefficient 2  
    "M3": complex,      # Linearization coefficient 3
    "k_pv": float,      # PV bus penalty factor
    "new_M": bool,      # Compute new linearization factors
    "pv_model": int,    # 0: const current, 1: const voltage magnitude
    "l_type": list,     # [PQ_type, PV_type]: 0=Taylor, 1=regression
    "du_range": float,  # Voltage magnitude range for linearization
    "da_range": float,  # Voltage angle range for linearization
    "u_0": array,       # Initial voltage magnitudes
    "a_0": array,       # Initial voltage angles
}
```

## Examples

See the `linear_power_flow/examples/` directory for complete examples:

- `pypwr_examples.py`: Integration with PYPOWER test cases
- Comparison with nonlinear power flow solutions
- Visualization of results

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black linear_power_flow/
flake8 linear_power_flow/
```

### Type Checking

```bash
mypy linear_power_flow/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Citation

If you use this package in your research, please cite:

```bibtex
@software{linear_power_flow,
  title = {Linear Power Flow: A Python Package for Linear Power Flow Analysis},
  author = {Tianqi Hong},
  year = {2025},
  url = {https://github.com/th1275/linear_power_flow}
}

@article{hong2021relaxed,
  author = {Hong, T. and Zhao, D. and Zhang, Y.},
  title = {A Relaxed PV Bus Model in Linear Power Flow},
  journal = {IEEE Transactions on Power Delivery},
  volume = {36},
  number = {2},
  pages = {1249--1252},
  year = {2021},
  month = {April},
  doi = {10.1109/TPWRD.2020.3031758},
  keywords = {Load flow; Numerical models; Computational modeling; Mathematical model; Voltage control; Reactive power; Load modeling; PV bus model; linear power flow; rectangular coordinates; multiphase power system}
}
```

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This package builds upon established power flow linearization techniques
- Compatible with PYPOWER and pandapower for easy integration
- Inspired by the need for fast power flow solutions in real-time applications

## Contact

Tianqi Hong - tianqi.hong@uga.edu
