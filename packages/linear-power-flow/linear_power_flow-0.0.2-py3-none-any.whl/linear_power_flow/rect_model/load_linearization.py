import numpy as np
import scipy as sp


def setup_regression_matrices(v_data):
    """
    Set up the regression matrices for least squares solution
    For complex function g(v) = A*v + B*v* + C
    """
    n = len(v_data)
    M = np.zeros((2 * n, 6))  # 2n equations (real and imaginary parts), 6 unknowns

    for i in range(n):
        v = v_data[i]
        v_conj = np.conj(v)

        # Real part equation
        M[2 * i, 0] = np.real(v)  # Re(A) coefficient
        M[2 * i, 1] = -np.imag(v)  # Im(A) coefficient
        M[2 * i, 2] = np.real(v_conj)  # Re(B) coefficient
        M[2 * i, 3] = -np.imag(v_conj)  # Im(B) coefficient
        M[2 * i, 4] = 1  # Re(C) coefficient
        M[2 * i, 5] = 0  # Im(C) coefficient

        # Imaginary part equation
        M[2 * i + 1, 0] = np.imag(v)  # Re(A) coefficient
        M[2 * i + 1, 1] = np.real(v)  # Im(A) coefficient
        M[2 * i + 1, 2] = np.imag(v_conj)  # Re(B) coefficient
        M[2 * i + 1, 3] = np.real(v_conj)  # Im(B) coefficient
        M[2 * i + 1, 4] = 0  # Re(C) coefficient
        M[2 * i + 1, 5] = 1  # Im(C) coefficient

    return M


def fit_linear_regression(v_data, f_data):
    """
    Fit linear regression to approximate f(v)
    """
    n = len(v_data)

    # Set up design matrix
    M = setup_regression_matrices(v_data)

    # Set up target vector b
    b = np.zeros(2 * n)
    for i in range(n):
        b[2 * i] = np.real(f_data[i])  # Real part
        b[2 * i + 1] = np.imag(f_data[i])  # Imaginary part

    # Solve least squares: M * x = b
    x, residuals, rank, s = np.linalg.lstsq(M, b, rcond=None)

    # Extract coefficients
    A = x[0] + 1j * x[1]  # Complex coefficient for v
    B = x[2] + 1j * x[3]  # Complex coefficient for v*
    C = x[4] + 1j * x[5]  # Complex constant term

    return A, B, C, residuals


def generate_training_data(delta_v_m, delta_v_a, vr=1.0 + 1j * 0.0, n_samples=1000, load_model=0):
    """
    Generate training data for differnt load model
    load_model = 0: const PQ model - 1/(v*)
    load_model = 1: const PV model - (|v|-|vr|)/(v*)
    load_model = 2: const |I| model - |v|/(v*)
    where v = v_real + j*v_imag, and v* is the complex conjugate
    """

    # Sample around the reference point with given deltas
    v_m_min = max(0.1, abs(vr) - delta_v_m)  # Ensure positive magnitude
    v_m_max = abs(vr) + delta_v_m
    v_a_min = np.angle(vr) - delta_v_a
    v_a_max = np.angle(vr) + delta_v_a

    v_m_samples = np.random.uniform(v_m_min, v_m_max, n_samples)
    v_a_samples = np.random.uniform(v_a_min, v_a_max, n_samples)

    # Convert to complex values
    v_data = v_m_samples * np.exp(1j * v_a_samples)

    if load_model == 0:
        # Compute f(v) = 1/conj(v)
        f_data = 1 / np.conj(v_data)
    elif load_model == 1:
        # Compute f(v) = (|v| - Ur)/conj(v)
        f_data = (np.abs(v_data) - abs(vr)) / np.conj(v_data)
    elif load_model == 2:
        # Compute f(v) = |v|/conj(v)
        f_data = np.abs(v_data) / np.conj(v_data)
    else:
        f_data = 1 / np.conj(v_data)
        print("wrong load model, convert to const PQ load")

    return v_data, f_data


def fit_multi_reference_approximation(
    v_m_ref, v_a_ref, delta_v_m=0.01, delta_v_a=0.05, n_samples_per_point=500, load_model=0
):
    """
    Fit linear approximation parameters for multiple reference points.

    Parameters:
    -----------
    v_m_ref : float or array-like
        Reference voltage magnitude(s) in per unit
    v_a_ref : float or array-like
        Reference voltage angle(s) in radians
    delta_v_m : float or array-like, default=0.01
        Voltage magnitude variation range(s) around reference (±delta_v_m)
    delta_v_a : float or array-like, default=0.05
        Voltage angle variation range(s) around reference (±delta_v_a)
    n_samples_per_point : int, default=500
        Number of training samples per reference point
    load_model : int, default=0

    Returns:
    --------
    M1, M2, M3 : np.array
        Arrays of complex coefficients A, B, C for each reference point
    metrics : dict
        Dictionary containing fitting metrics for each point
    """

    # Convert inputs to numpy arrays
    v_m_ref = np.atleast_1d(v_m_ref)
    v_a_ref = np.atleast_1d(v_a_ref)

    # Check that v_m_ref and v_a_ref have the same length
    if len(v_m_ref) != len(v_a_ref):
        raise ValueError("v_m_ref and v_a_ref must have the same length")

    n_points = len(v_m_ref)

    # Handle delta parameters - can be scalars or arrays
    if np.isscalar(delta_v_m):
        delta_v_m = np.full(n_points, delta_v_m)
    else:
        delta_v_m = np.atleast_1d(delta_v_m)
        if len(delta_v_m) != n_points:
            raise ValueError("delta_v_m must be scalar or have same length as v_m_ref")

    if np.isscalar(delta_v_a):
        delta_v_a = np.full(n_points, delta_v_a)
    else:
        delta_v_a = np.atleast_1d(delta_v_a)
        if len(delta_v_a) != n_points:
            raise ValueError("delta_v_a must be scalar or have same length as v_a_ref")

    # Handle Ur parameter
    Vr_array = v_m_ref * np.exp(1j * v_a_ref)

    # Initialize output arrays
    M1 = np.zeros(n_points, dtype=complex)  # Coefficient A
    M2 = np.zeros(n_points, dtype=complex)  # Coefficient B
    M3 = np.zeros(n_points, dtype=complex)  # Coefficient C

    # Initialize metrics storage
    metrics = {
        "mse": np.zeros(n_points),
        "max_error": np.zeros(n_points),
        "rmse": np.zeros(n_points),
        "residuals": [],
        "v_m_ref": v_m_ref.copy(),
        "v_a_ref": v_a_ref.copy(),
        "delta_v_m": delta_v_m.copy(),
        "delta_v_a": delta_v_a.copy(),
        "Vr": Vr_array.copy(),
        "n_samples_per_point": n_samples_per_point,
    }

    print(f"Fitting approximation for {n_points} reference point(s)...")

    # Fit approximation for each reference point
    for i in range(n_points):
        print(
            f"  Point {i + 1}/{n_points}: v_m={v_m_ref[i]:.4f}, v_a={v_a_ref[i]:.4f} rad ({np.degrees(v_a_ref[i]):.2f}°)"
        )

        # Generate samples in polar coordinates around this reference
        np.random.seed(42 + i)  # Reproducible results

        v_data, f_data = generate_training_data(
            delta_v_m[i], delta_v_a[i], Vr_array[i], n_samples=500, load_model=load_model
        )

        # Fit linear regression for this point
        A, B, C, residuals = fit_linear_regression(v_data, f_data)

        # Store coefficients
        M1[i] = A
        M2[i] = B
        M3[i] = C

        # Evaluate approximation quality
        g_data = A * v_data + B * np.conj(v_data) + C
        mse = np.mean(np.abs(f_data - g_data) ** 2)
        max_error = np.max(np.abs(f_data - g_data))
        rmse = np.sqrt(mse)

        # Store metrics
        metrics["mse"][i] = mse
        metrics["max_error"][i] = max_error
        metrics["rmse"][i] = rmse
        metrics["residuals"].append(residuals)

        print(f"    MSE: {mse:.6e}, RMSE: {rmse:.6e}, Max Error: {max_error:.6e}")

    print("Fitting completed!")
    return M1, M2, M3, metrics


def linear_factor_update(s_idx, v_idx, lpf_opt):
    pv_model = lpf_opt["pv_model"]
    l_type = lpf_opt["l_type"]
    pq_ltype = l_type[0]
    pv_ltype = l_type[1]
    du_range = lpf_opt["du_range"]
    da_range = lpf_opt["da_range"]
    num_node = lpf_opt["num_node"]
    u_0 = lpf_opt.get("u_0", np.ones(num_node))
    a_0 = lpf_opt.get("a_0", np.zeros(num_node))
    M1, M2, M3 = 0, 0, 0
    if pv_model == 0:
        if pq_ltype == 0 and pv_ltype == 0:
            print("under development")
            pass

        elif pq_ltype == 0 and pv_ltype == 1:
            u_v = u_0[v_idx]
            a_v = a_0[v_idx]
            print("Constant I model, PQ: Taylor, PV: Linear Regression")
            M1, M2, M3, _ = fit_multi_reference_approximation(
                u_v,
                a_v,
                delta_v_m=du_range,
                delta_v_a=da_range,
                n_samples_per_point=500,
                load_model=2,
            )
        elif pq_ltype == 1 and pv_ltype == 0:
            print("under development")
            pass
        else:  # pq_ltype == 1 and pv_ltype == 1
            print("under development")
            pass
    else:
        if pq_ltype == 0 and pv_ltype == 0:
            print("under development")
            pass

        elif pq_ltype == 0 and pv_ltype == 1:
            u_v = u_0[v_idx]
            a_v = a_0[v_idx]
            print("PV model, PQ: Taylor, PV: Linear Regression")
            M1, M2, M3, _ = fit_multi_reference_approximation(
                u_v,
                a_v,
                delta_v_m=du_range,
                delta_v_a=da_range,
                n_samples_per_point=500,
                load_model=1,
            )

        elif pq_ltype == 1 and pv_ltype == 0:
            print("under development")
            pass

        else:  # pq_ltype == 1 and pv_ltype == 1
            o_idx = np.ones(num_node, dtype=bool)
            o_idx[s_idx] = False
            o_idx[v_idx] = False
            # PQ load model
            u_o = u_0[o_idx]
            a_o = a_0[o_idx]
            print("PV model, PQ: Linear Regression, PV: Linear Regression")
            M1_o, M2_o, M3_o, _ = fit_multi_reference_approximation(
                u_o, a_o, delta_v_m=0.1, delta_v_a=0.05, n_samples_per_point=500, load_model=0
            )

            # PV load model
            u_v = u_0[v_idx]
            a_v = a_0[v_idx]
            # PQ part
            M1_vo, M2_vo, M3_vo, _ = fit_multi_reference_approximation(
                u_v, a_v, delta_v_m=0.01, delta_v_a=0.05, n_samples_per_point=500, load_model=0
            )

            # PV part
            M1_vv, M2_vv, M3_vv, _ = fit_multi_reference_approximation(
                u_v, a_v, delta_v_m=0.01, delta_v_a=0.05, n_samples_per_point=500, load_model=1
            )

            M1 = {"M1_o": M1_o, "M1_vo": M1_vo, "M1_vv": M1_vv}
            M2 = {"M2_o": M2_o, "M2_vo": M2_vo, "M3_vv": M2_vv}
            M3 = {"M3_o": M3_o, "M3_vo": M3_vo, "M3_vv": M3_vv}

    return M1, M2, M3
