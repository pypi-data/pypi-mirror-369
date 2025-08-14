import numpy as np
import scipy.sparse as sp
from typing import Union, Tuple
from linear_power_flow.rect_model import load_linearization as ll


LPF_OPTION_DEFAULT = {
    "M1": 0.494255 + 0.001510j,
    "M2": -0.492387 + 0.005016j,
    "M3": 0.991921 - 0.006323j,
    "k_pv": -10000,
    "new_M": True,  # flag of compute M1 - M3
    "pv_model": 0,  # "0" is constant current model, "1" is constant voltage magnitude model
    "l_type": [0, 1],  # [PQ_type, PV_type]; "0" is Taylor expansion, "1" is linear regression
    "du_range": 0.1,
    "da_range": np.pi / 16,
}


def compute_lpf_mat(
    sbus: np.ndarray,
    Yvs: Union[np.ndarray, sp.spmatrix],
    Yvv: Union[np.ndarray, sp.spmatrix],
    Yvo: Union[np.ndarray, sp.spmatrix],
    Yos: Union[np.ndarray, sp.spmatrix],
    Yov: Union[np.ndarray, sp.spmatrix],
    Yoo: Union[np.ndarray, sp.spmatrix],
    s_idx: np.ndarray,
    v_idx: np.ndarray,
    vs: np.ndarray,
    u_r: np.ndarray,
    lpf_opt: dict,
) -> Tuple[Union[np.ndarray, sp.spmatrix], np.ndarray]:
    """
    Compute power flow matrices.
    Preserves input matrix type - if sparse input, returns sparse l_mat; if dense input, returns dense l_mat.

    Parameters:
    Sbus (np.ndarray): Complex power injection vector
    Yvs, Yvv, Yvo, Yos, Yov, Yoo (Union[np.ndarray, sp.spmatrix]): Admittance matrix partitions
    s_idx (np.ndarray): Slack bus indices
    v_idx (np.ndarray): PV bus indices
    vs (np.ndarray): Slack bus voltages
    u_r (np.ndarray): Real part of voltage at PV buses
    lpf_opt (dict): Linear power flow options containing k_pv, M1, M2, M3, et al.

    Returns:
    tuple: (l_mat, b_vec) where l_mat has same type as input matrices, b_vec is always dense
    """
    if lpf_opt is None:
        lpf_opt = LPF_OPTION_DEFAULT

    lpv_flag = lpf_opt.get("pv_model", 0)
    k_pv = lpf_opt["k_pv"]
    n_bus = len(sbus)
    lpf_opt["num_node"] = n_bus
    if lpf_opt["new_M"]:
        M1, M2, M3 = ll.linear_factor_update(s_idx, v_idx, lpf_opt)
        lpf_opt["M1"] = M1
        lpf_opt["M2"] = M2
        lpf_opt["M3"] = M3
    else:
        M1 = lpf_opt["M1"]
        M2 = lpf_opt["M2"]
        M3 = lpf_opt["M3"]
    # Extract power injections
    # sg_v = sbus[v_idx]
    # sg_o = np.delete(sbus, np.concatenate((s_idx, v_idx)))

    o_idx = np.ones(n_bus, dtype=bool)
    o_idx[s_idx] = False
    o_idx[v_idx] = False
    sg_v = sbus[v_idx]
    sg_o = sbus[o_idx]  # Much faster than np.delete
    # Determine if inputs are sparse or dense
    is_sparse = sp.issparse(Yvv)  # Use Yvv as reference since it's typically the largest

    l_type = lpf_opt["l_type"]
    pq_ltype = l_type[0]
    pv_ltype = l_type[1]

    if pq_ltype == 0 and pv_ltype == 0:  # PQ Taylor, PV Taylor
        print("solver under development")
        l_mat, b_vec = pq_taylor_pv_data(
            Yvs, Yvv, Yvo, Yos, Yov, Yoo, M1, M2, M3, vs, u_r, sg_v, sg_o, k_pv, is_sparse, lpv_flag
        )

    elif pq_ltype == 0 and pv_ltype == 1:  # PQ Taylor, PV data
        l_mat, b_vec = pq_taylor_pv_data(
            Yvs, Yvv, Yvo, Yos, Yov, Yoo, M1, M2, M3, vs, u_r, sg_v, sg_o, k_pv, is_sparse, lpv_flag
        )
    elif pq_ltype == 1 and pv_ltype == 0:  # PQ data, PV Taylor
        print("solver under development")
        l_mat, b_vec = pq_taylor_pv_data(
            Yvs, Yvv, Yvo, Yos, Yov, Yoo, M1, M2, M3, vs, u_r, sg_v, sg_o, k_pv, is_sparse, lpv_flag
        )
    else:  # pq_ltype == 1 and pv_ltype == 1  # PQ data, PV data
        print("solver under development")
        l_mat, b_vec = pq_taylor_pv_data(
            Yvs, Yvv, Yvo, Yos, Yov, Yoo, M1, M2, M3, vs, u_r, sg_v, sg_o, k_pv, is_sparse, lpv_flag
        )

    return l_mat, b_vec


def pq_taylor_pv_data(
    Yvs: Union[np.ndarray, sp.spmatrix],
    Yvv: Union[np.ndarray, sp.spmatrix],
    Yvo: Union[np.ndarray, sp.spmatrix],
    Yos: Union[np.ndarray, sp.spmatrix],
    Yov: Union[np.ndarray, sp.spmatrix],
    Yoo: Union[np.ndarray, sp.spmatrix],
    M1,
    M2,
    M3,
    vs,
    u_r,
    sg_v,
    sg_o,
    k_pv,
    is_sparse,
    lpv_flag,
):

    n = len(u_r)  # assuming u_r defines the size
    M1_vec = np.full(n, M1) if np.isscalar(M1) else M1
    M2_vec = np.full(n, M2) if np.isscalar(M2) else M2

    if lpv_flag == 0:  ## M1, M2, M3, Const current model
        if is_sparse:
            # Sparse coefficient matrices
            sparse_type = "csr"  # Yoo.format if sp.issparse(Yoo) else 'csr'
            A_mat = (0 - 1j * k_pv) * sp.diags(M1_vec, format=sparse_type)
            B_mat = (0 - 1j * k_pv) * (
                sp.diags(M2_vec, format=sparse_type) + sp.diags(u_r, format=sparse_type)
            ) - sp.diags(sg_v.conj(), format=sparse_type)
            C_mat = 2 * sg_v.conj() - 2 * (0 - 1j * k_pv) * u_r + (0 - 1j * k_pv) * M3
            E_mat = 2 * sg_o.conj()
        else:
            # Dense coefficient matrices
            A_mat = (0 - 1j * k_pv) * np.diag(M1_vec)
            B_mat = (0 - 1j * k_pv) * (np.diag(M2_vec) + np.diag(u_r)) - np.diag(sg_v.conj())
            C_mat = 2 * sg_v.conj() - 2 * (0 - 1j * k_pv) * u_r + (0 - 1j * k_pv) * M3
            E_mat = 2 * sg_o.conj()

    else:  # PV model
        if is_sparse:
            # Sparse coefficient matrices
            sparse_type = "csr"  # Yoo.format if sp.issparse(Yoo) else 'csr'
            A_mat = (0 - 1j * k_pv) * sp.diags(M1_vec, format=sparse_type)
            B_mat = (0 - 1j * k_pv) * sp.diags(M2_vec, format=sparse_type) - sp.diags(
                sg_v.conj(), format=sparse_type
            )
            C_mat = 2 * sg_v.conj() + (0 - 1j * k_pv) * M3
            E_mat = 2 * sg_o.conj()
        else:
            # Dense coefficient matrices
            A_mat = (0 - 1j * k_pv) * np.diag(M1_vec)
            B_mat = (0 - 1j * k_pv) * np.diag(M2_vec) - np.diag(sg_v.conj())
            C_mat = 2 * sg_v.conj() + (0 - 1j * k_pv) * M3
            E_mat = 2 * sg_o.conj()

    # Extract real and imaginary parts of slack bus voltages
    es = vs.real
    fs = vs.imag

    # Pre-extract real/imaginary parts once
    if is_sparse:
        A_real, A_imag = A_mat.real, A_mat.imag
        B_real, B_imag = B_mat.real, B_mat.imag
        Yvv_real, Yvv_imag = Yvv.real, Yvv.imag
        Yvo_real, Yvo_imag = Yvo.real, Yvo.imag
        Yov_real, Yov_imag = Yov.real, Yov.imag
        Yoo_real, Yoo_imag = Yoo.real, Yoo.imag
        Yvs_real, Yvs_imag = Yvs.real, Yvs.imag
        Yos_real, Yos_imag = Yos.real, Yos.imag

        # Diagonal matrix for sg_o (keep as vector for efficiency)
        D_mat = -sp.diags(sg_o.conj(), format=sparse_type)
        D_real, D_imag = D_mat.real, D_mat.imag

        # Build sparse system matrix blocks (avoid unnecessary conversions)
        p11 = A_real + B_real - Yvv_real
        p12 = -Yvo_real
        p13 = B_imag - A_imag + Yvv_imag
        p14 = Yvo_imag

        p21 = A_imag + B_imag - Yvv_imag
        p22 = -Yvo_imag
        p23 = A_real - B_real - Yvv_real
        p24 = -Yvo_real

        p31 = -Yov_real
        p32 = D_real - Yoo_real
        p33 = Yov_imag
        p34 = D_imag + Yoo_imag

        p41 = -Yov_imag
        p42 = D_imag - Yoo_imag
        p43 = -Yov_real
        p44 = -D_real - Yoo_real

        # RHS vector computation
        b1 = Yvs_real @ es - Yvs_imag @ fs - C_mat.real
        b2 = Yvs_real @ fs + Yvs_imag @ es - C_mat.imag
        b3 = Yos_real @ es - Yos_imag @ fs - E_mat.real
        b4 = Yos_real @ fs + Yos_imag @ es - E_mat.imag

        # Assemble sparse system matrix
        l_mat = sp.bmat(
            [
                [p11, p12, p13, p14],
                [p21, p22, p23, p24],
                [p31, p32, p33, p34],
                [p41, p42, p43, p44],
            ],
            format=sparse_type,
        )

    else:
        # Similar optimization for dense case
        A_real, A_imag = A_mat.real, A_mat.imag
        B_real, B_imag = B_mat.real, B_mat.imag

        # Pre-compute diagonal matrix
        D_mat = -np.diag(sg_o.conj())
        D_real, D_imag = D_mat.real, D_mat.imag

        # Extract real/imaginary parts once
        Yvv_real, Yvv_imag = Yvv.real, Yvv.imag
        Yvo_real, Yvo_imag = Yvo.real, Yvo.imag
        Yov_real, Yov_imag = Yov.real, Yov.imag
        Yoo_real, Yoo_imag = Yoo.real, Yoo.imag

        # Build blocks
        p11 = A_real + B_real - Yvv_real
        p12 = -Yvo_real
        p13 = B_imag - A_imag + Yvv_imag
        p14 = Yvo_imag

        p21 = A_imag + B_imag - Yvv_imag
        p22 = -Yvo_imag
        p23 = A_real - B_real - Yvv_real
        p24 = -Yvo_real

        p31 = -Yov_real
        p32 = D_real - Yoo_real
        p33 = Yov_imag
        p34 = D_imag + Yoo_imag

        p41 = -Yov_imag
        p42 = D_imag - Yoo_imag
        p43 = -Yov_real
        p44 = -D_real - Yoo_real

        # Optimized RHS computation
        Yvs_real, Yvs_imag = Yvs.real, Yvs.imag
        Yos_real, Yos_imag = Yos.real, Yos.imag

        b1 = Yvs_real @ es - Yvs_imag @ fs - C_mat.real
        b2 = Yvs_real @ fs + Yvs_imag @ es - C_mat.imag
        b3 = Yos_real @ es - Yos_imag @ fs - E_mat.real
        b4 = Yos_real @ fs + Yos_imag @ es - E_mat.imag

        # Assemble dense system matrix
        l_mat = np.block(
            [
                [p11, p12, p13, p14],
                [p21, p22, p23, p24],
                [p31, p32, p33, p34],
                [p41, p42, p43, p44],
            ]
        )

    # Assemble RHS vector
    b_vec = np.concatenate([b1, b2, b3, b4])

    return l_mat, b_vec


def pq_data_pv_data(
    Yvs: Union[np.ndarray, sp.spmatrix],
    Yvv: Union[np.ndarray, sp.spmatrix],
    Yvo: Union[np.ndarray, sp.spmatrix],
    Yos: Union[np.ndarray, sp.spmatrix],
    Yov: Union[np.ndarray, sp.spmatrix],
    Yoo: Union[np.ndarray, sp.spmatrix],
    M1,
    M2,
    M3,
    vs,
    u_r,
    sg_v,
    sg_o,
    k_pv,
    is_sparse,
    lpv_flag,
):
    # Extract M components
    M1_o = M1["M1_o"]
    M2_o = M2["M2_o"]
    M3_o = M3["M3_o"]
    M1_vo = M1["M1_vo"]
    M2_vo = M2["M2_vo"]
    M3_vo = M3["M3_vo"]
    M1_vv = M1["M1_vv"]
    M2_vv = M2["M2_vv"]
    M3_vv = M3["M3_vv"]

    # Compute modified M values
    M1_o_f = sg_o.conj() * M1_o
    M2_o_f = sg_o.conj() * M2_o
    M3_o_f = sg_o.conj() * M3_o
    M1_vo_f = sg_v.real * M1_vo
    M2_vo_f = sg_v.real * M2_vo
    M3_vo_f = sg_v.real * M3_vo
    M1_vv_f = (0 - 1j) * k_pv * M1_vv
    M2_vv_f = (0 - 1j) * k_pv * M2_vv
    M3_vv_f = (0 - 1j) * k_pv * M3_vv

    M1_v_f = M1_vo_f + M1_vv_f
    M2_v_f = M2_vo_f + M2_vv_f
    M3_v_f = M3_vo_f + M3_vv_f

    # Create diagonal vectors for H, J matrices and K vector
    # Pre-allocate arrays
    n_v = len(M1_v_f)
    n_o = len(M1_o_f)
    n_total = n_v + n_o

    H_diag = np.empty(n_total, dtype=M1_v_f.dtype)
    J_diag = np.empty(n_total, dtype=M2_v_f.dtype)
    K_vec = np.empty(n_total, dtype=M3_v_f.dtype)

    # Fill in-place (no copying)
    H_diag[:n_v] = M1_v_f
    H_diag[n_v:] = M1_o_f
    J_diag[:n_v] = M2_v_f
    J_diag[n_v:] = M2_o_f
    K_vec[:n_v] = M3_v_f
    K_vec[n_v:] = M3_o_f

    # Extract real/imaginary parts once
    es = vs.real
    fs = vs.imag
    Rh = H_diag.real
    Lh = H_diag.imag
    Rj = J_diag.real
    Lj = J_diag.imag
    Rk = K_vec.real
    Lk = K_vec.imag

    if is_sparse:
        # Sparse matrix operations - avoid conversions
        # Build Ynn and Yns without converting to dense
        Ynn_real = sp.bmat([[Yvv.real, Yvo.real], [Yov.real, Yoo.real]], format="csr")
        Ynn_imag = sp.bmat([[Yvv.imag, Yvo.imag], [Yov.imag, Yoo.imag]], format="csr")

        Yns_real = sp.vstack([Yvs.real, Yos.real], format="csr")
        Yns_imag = sp.vstack([Yvs.imag, Yos.imag], format="csr")

        # Build coefficient matrices using sparse operations
        H_real_diag = sp.diags(Rh, format="csr")
        H_imag_diag = sp.diags(Lh, format="csr")
        J_real_diag = sp.diags(Rj, format="csr")
        J_imag_diag = sp.diags(Lj, format="csr")

        p11 = -Ynn_real + H_real_diag + J_real_diag
        p12 = Ynn_imag - H_imag_diag + J_imag_diag
        p21 = -Ynn_imag + H_imag_diag + J_imag_diag
        p22 = -Ynn_real + H_real_diag - J_real_diag

        # RHS vector computation
        b1 = Yns_real @ es - Yns_imag @ fs - Rk
        b2 = Yns_real @ fs + Yns_imag @ es - Lk

        # Assemble sparse system matrix
        l_mat = sp.bmat([[p11, p12], [p21, p22]], format="csr")

    else:
        # Dense matrix operations
        Ynn_real = np.block([[Yvv.real, Yvo.real], [Yov.real, Yoo.real]])
        Ynn_imag = np.block([[Yvv.imag, Yvo.imag], [Yov.imag, Yoo.imag]])

        Yns_real = np.vstack([Yvs.real, Yos.real])
        Yns_imag = np.vstack([Yvs.imag, Yos.imag])

        # Build coefficient matrices using broadcasting
        p11 = -Ynn_real + np.diag(Rh + Rj)
        p12 = Ynn_imag + np.diag(-Lh + Lj)
        p21 = -Ynn_imag + np.diag(Lh + Lj)
        p22 = -Ynn_real + np.diag(Rh - Rj)

        # RHS vector computation
        b1 = Yns_real @ es - Yns_imag @ fs - Rk
        b2 = Yns_real @ fs + Yns_imag @ es - Lk

        # Assemble dense system matrix
        l_mat = np.block([[p11, p12], [p21, p22]])

    # Assemble RHS vector (always dense)
    b_vec = np.concatenate([b1, b2])

    return l_mat, b_vec


def solve_voltage(lmatrix, bvector, out_option=0):
    """
    Solve the linear system and return only voltage magnitudes (more memory efficient).

    Parameters:
    lmatrix (np.ndarray or scipy.sparse matrix): 2n×2n coefficient matrix
    bvector (np.ndarray): 2n×1 right-hand side vector
    out_option (int): type of the output, 0: voltage magnitudes, 1: voltage angle, 2: complex voltage

    Returns:
    np.ndarray: Voltage magnitude vector (n×1)
    """

    # Solve the linear system
    if sp.issparse(lmatrix):
        x = sp.linalg.spsolve(lmatrix, bvector)
    else:
        x = np.linalg.solve(lmatrix, bvector)

    # Calculate number of buses
    num_bus = x.shape[0] // 2

    # Extract real and imaginary parts and compute magnitudes directly
    v_real = x[:num_bus]
    v_imag = x[num_bus:]

    if out_option == 0:
        v_out = np.sqrt(v_real**2 + v_imag**2)
    elif out_option == 1:
        v_out = np.arctan2(v_imag, v_real)
    else:
        v_out = v_real + 1j * v_imag

    return v_out
