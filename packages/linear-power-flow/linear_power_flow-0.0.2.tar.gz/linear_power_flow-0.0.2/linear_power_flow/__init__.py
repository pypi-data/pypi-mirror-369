# linear_power_flow/__init__.py
"""
Linear Power Flow Analysis Package

A Python package for efficient linear power flow analysis in electrical power systems.
"""

__version__ = "0.0.1"
__author__ = "Tianqi Hong"
__email__ = "tianqi.hong@uga.edu"

from linear_power_flow.common_interface.main_interface import (
    lpf_run,
    compute_simple_branch_currents,
    partition_matrix,
    partition_matrix_pv,
    partition_matrix_pv_dict,
    post_reorder,
)

from linear_power_flow.rect_model.lpf_computation import (
    compute_lpf_mat,
    solve_voltage,
    LPF_OPTION_DEFAULT,
)

from linear_power_flow.rect_model.load_linearization import (
    fit_linear_regression,
    generate_training_data,
    fit_multi_reference_approximation,
    linear_factor_update,
)

__all__ = [
    # Main interface functions
    "lpf_run",
    "compute_simple_branch_currents",
    "partition_matrix",
    "partition_matrix_pv",
    "partition_matrix_pv_dict",
    "post_reorder",
    # LPF computation functions
    "compute_lpf_mat",
    "solve_voltage",
    "LPF_OPTION_DEFAULT",
    # Load linearization functions
    "fit_linear_regression",
    "generate_training_data",
    "fit_multi_reference_approximation",
    "linear_factor_update",
]
