import numpy as np
from pypower.api import runpf, ppoption, loadcase, ext2int, makeYbus, makeSbus
from pandapower.converter import to_ppc
from pandapower.networks.power_system_test_cases import case9, case2848rte, case9241pegase
from numpy import c_, zeros
from pypower.idx_brch import QT
from linear_power_flow.common_interface.main_interface import (
    partition_matrix,
    partition_matrix_pv,
    post_reorder,
)
from linear_power_flow.rect_model.lpf_computation import compute_lpf_mat, solve_voltage

# import matplotlib.pyplot as plt
import plotly.graph_objects as go


def get_bus_orders_by_type(bus_array, bus_type=3):
    """
    Extract the row indices in bus_array where the bus type matches the specified value.

    Parameters:
    bus_array (np.ndarray): 2D array where column 0 is bus index, column 1 is bus type
    bus_type (int): The bus type to filter by (default: 3)

    Returns:
    np.ndarray: Array of row indices where bus_type matches
    """
    # Find rows where bus type (column 1) equals the specified type
    mask = bus_array[:, 1] == bus_type

    # Return the row indices where mask is True
    return np.where(mask)[0]


np.random.seed(42)  # Fix the seed for reproducibility

n_sim = 50  # number of simulation

net = case9241pegase()  # case9241pegase() # case2848rte() # case9()
ppc = to_ppc(net, init="flat")
ppopt = ppoption(VERBOSE=0, OUT_ALL=0)
## read data
ppci = loadcase(ppc)

## add zero columns to branch for flows if needed
if ppci["branch"].shape[1] < QT:
    ppci["branch"] = c_[
        ppc["branch"], zeros((ppc["branch"].shape[0], QT - ppc["branch"].shape[1] + 1))
    ]

## convert to internal indexing
ppci = ext2int(ppci)
r_t0 = runpf(ppci, ppopt)
v_true_0 = r_t0[0]["bus"][:, 7]

baseMVA, bus, gen, branch = ppci["baseMVA"], ppci["bus"], ppci["gen"], ppci["branch"]

load_ratio = 1
gen[:, 1] = gen[:, 1] * load_ratio

num_load = bus.shape[0]
num_node = bus.shape[0]

base_p_load = bus[:, 2].copy() / baseMVA * load_ratio
base_q_load = bus[:, 3].copy() / baseMVA * load_ratio

s_idx = get_bus_orders_by_type(bus, bus_type=3)
v_idx = get_bus_orders_by_type(bus, bus_type=2)
o_idx = get_bus_orders_by_type(bus, bus_type=1)

vs_m = bus[s_idx, 7]
vs_a = bus[s_idx, 8]
vs = vs_m * np.exp(1j * vs_a)

u_r = bus[v_idx, 7]

# new_p_ratio = np.random.uniform(0.8, 1)
# new_p_load = new_p_ratio * base_p_load
# new_q_ratio = np.random.uniform(0.8, 1)
# new_q_load = new_q_ratio * base_q_load
# for i in range(num_load):
#     bus[i, 2] = new_p_load[i] * baseMVA
#     bus[i, 3] = new_q_load[i] * baseMVA

Y_bus, Yf, Yt = makeYbus(baseMVA, bus, branch)
# Y_bus = Y_bus.toarray()
Sbus = makeSbus(baseMVA, bus, gen)
# Nonlinear Power Flow
r_t = runpf(ppci, ppopt)
v_true = r_t[0]["bus"][:, 7]
v_true_a = r_t[0]["bus"][:, 8] / 180 * np.pi

# Linear Power Flow
lpf_option = {
    "M1": 0.494255 + 0.001510j,
    "M2": -0.492387 + 0.005016j,
    "M3": 0.991921 - 0.006323j,
    "k_pv": -10000,
    "new_M": True,  # flag of compute M1 - M3
    "pv_model": 0,  # "0" is constant current model, "1" is constant voltage magnitude model
    "l_type": [0, 1],  # [PQ_type, PV_type]; "0" is Taylor expansion, "1" is linear regression
    "du_range": 0.01,
    "da_range": np.pi / 8,
    "u_0": v_true,
    "a_0": v_true_a,
}

Yss, Ysv, Yso, Yvs, Yvv, Yvo, Yos, Yov, Yoo = partition_matrix_pv(Y_bus, s_idx, v_idx)

lmatrix_s, bvector_s = compute_lpf_mat(
    Sbus, Yvs, Yvv, Yvo, Yos, Yov, Yoo, s_idx, v_idx, vs, u_r, lpf_option
)

v_amp_only_sp = solve_voltage(lmatrix_s, bvector_s)
v_l_sp = post_reorder(v_amp_only_sp, u_r, s_idx, v_idx, o_idx, vs)
# v_l_sp = np.insert(v_amp_only_sp, s_idx, bus[s_idx, 7])

# Y_bus = Y_bus.toarray()
# Yss, Ysv, Yso, Yvs, Yvv, Yvo, Yos, Yov, Yoo = partition_matrix_pv(Y_bus, s_idx, v_idx)
# lmatrix_d, bvector_d = compute_lpf_mat(Sbus, Yvs, Yvv, Yvo, Yos, Yov, Yoo, s_idx, v_idx, vs, u_r, lpf_option)
#
# v_amp_only_ds = solve_voltage(lmatrix_d, bvector_d)
# v_l_ds = np.insert(v_amp_only_ds, s_idx, bus[s_idx, 7])
#
# d_l = np.max(np.max(lmatrix_s.toarray() - lmatrix_d))
# d_b = np.max(bvector_s - bvector_d)
#
# print(f"l_matrix difference: {d_l}")
# print(f"b_vector difference: {d_b}")

# plt.figure()
# plt.xlabel('Bus index')
# plt.ylabel('Voltage magnitude (p.u.)')
# # plt.ylim(0.8, 1.2)
# plt.grid(True)
# plt.plot(np.array(v_true), label='true_v', marker='o', linestyle='-')  # Circle markers, solid line
# plt.plot(np.array(abs(v_l_sp)), label='linear_v_s', marker='^', linestyle='-.')  # Triangle markers, dash-dot line
# # plt.plot(np.array(abs(v_l_ds)), label='line_v_d', marker='s', linestyle='--')  # Square markers, dashed line
# plt.legend()
# plt.tight_layout()
# plt.show()

x = np.arange(len(v_true))

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=x,
        y=v_true,
        mode="lines+markers",
        name="True",
        marker=dict(symbol="circle"),
        line=dict(dash="solid"),
    )
)
fig.add_trace(
    go.Scatter(
        x=x,
        y=v_l_sp,
        mode="lines+markers",
        name="Lpf_r",
        marker=dict(symbol="square"),
        line=dict(dash="dash"),
    )
)
# fig.add_trace(go.Scatter(
#     x=x,
#     y=v_l,
#     mode='lines+markers',
#     name='Lpf',
#     marker=dict(symbol='square'),
#     line=dict(dash='dash')
# ))
fig.update_layout(
    title="Comparison of v_true, v_l",
    xaxis_title="bus",
    yaxis_title="V in p.u.",
    legend=dict(x=0.01, y=0.99),
    template="simple_white",
)
fig.show()
