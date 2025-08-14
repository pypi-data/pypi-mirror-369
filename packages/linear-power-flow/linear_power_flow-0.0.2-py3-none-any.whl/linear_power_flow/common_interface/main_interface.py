import numpy as np
import scipy.sparse as sp
from linear_power_flow.rect_model.lpf_computation import compute_lpf_mat, solve_voltage


def lpf_run(y_bus, bus_power, s_idx, v_idx, o_idx, vs, u_v, lpf_option):

    Yss, Ysv, Yso, Yvs, Yvv, Yvo, Yos, Yov, Yoo = partition_matrix_pv(y_bus, s_idx, v_idx)

    lmatrix, bvector = compute_lpf_mat(
        bus_power, Yvs, Yvv, Yvo, Yos, Yov, Yoo, s_idx, v_idx, vs, u_v, lpf_option
    )

    v_sp = solve_voltage(lmatrix, bvector)

    v_l = post_reorder(v_sp, u_v, s_idx, v_idx, o_idx, vs)

    return v_l


def compute_simple_branch_currents(Ybus, V, output_branches=None):
    """
    Compute simplified branch currents using Ybus and voltage vector.

    For each branch from bus i to bus j:
    Current = Ybus[i,j] * (V[i] - V[j])

    Parameters:
    Ybus (np.ndarray or scipy.sparse): Bus admittance matrix (n x n)
    V (np.ndarray): Complex voltage vector (n x 1 or n,)
    output_branches (np.ndarray, optional): Array of shape (m, 2) where each row
                                           contains [from_bus, to_bus] indices (0-based).
                                           If None, outputs all non-zero currents.

    Returns:
    np.ndarray: Array of shape (m, 3) where each row contains:
                [from_bus, to_bus, current_complex]
                from_bus and to_bus are 0-based indices
    """
    # Convert to dense if sparse
    if sp.issparse(Ybus):
        Ybus_dense = Ybus.toarray()
    else:
        Ybus_dense = Ybus.copy()

    # Ensure V is 1D array
    V = np.array(V).flatten()
    n_bus = len(V)

    results = []

    if output_branches is not None:
        # Use specified branches
        output_branches = np.array(output_branches)

        for branch in output_branches:
            from_bus = int(branch[0])
            to_bus = int(branch[1])

            # Check bounds
            if from_bus < 0 or from_bus >= n_bus or to_bus < 0 or to_bus >= n_bus:
                raise ValueError(f"Bus indices out of range: {from_bus}, {to_bus}")

            # Get admittance (could be zero)
            y_branch = Ybus_dense[from_bus, to_bus]

            # Calculate current: I = Y * (V_from - V_to)
            current = y_branch * (V[from_bus] - V[to_bus])

            results.append([from_bus, to_bus, current])

    else:
        # Find all non-zero off-diagonal elements
        for i in range(n_bus):
            for j in range(n_bus):
                if i != j and abs(Ybus_dense[i, j]) > 1e-12:  # Non-zero admittance
                    # Calculate current: I = Y * (V_from - V_to)
                    current = Ybus_dense[i, j] * (V[i] - V[j])

                    results.append([i, j, current])

    # Convert results to numpy array
    if results:
        results_array = np.array(results, dtype=object)
        # Convert first two columns to int, keep third as complex
        results_array[:, 0] = results_array[:, 0].astype(int)
        results_array[:, 1] = results_array[:, 1].astype(int)
        return results_array
    else:
        # Return empty array with correct shape
        return np.empty((0, 3), dtype=object)


def post_reorder(v_vo, ur, s_idx, v_idx, o_idx, vs, m_flag=True):
    if m_flag:
        v_vo[: len(v_idx)] = ur
        v_l = np.insert(v_vo, 0, np.abs(vs))
    else:
        v_l = np.insert(v_vo, 0, np.angle(vs))
    bus_order = np.concatenate((np.atleast_1d(s_idx), v_idx, o_idx))

    # To reorder v_l_r back to v_true order, you need the inverse mapping
    inverse_order = np.empty_like(bus_order)
    inverse_order[bus_order] = np.arange(len(bus_order))

    # Now reorder v_l_r to match v_true order
    v_l_r = v_l[inverse_order]
    return v_l_r


def partition_matrix(matrix, indices):
    """
    Partition an n×n matrix into four submatrices based on given indices.
    Works with both numpy arrays and scipy sparse matrices.

    Parameters:
    matrix (np.ndarray or scipy.sparse matrix): n×n input matrix
    indices (np.ndarray): 1D array of indices to define the partitioning

    Returns:
    tuple: (Yss, Yso, Yos, Yoo) where:
        - Yss: submatrix with rows and columns from indices
        - Yso: submatrix with rows from indices, columns not from indices
        - Yos: submatrix with rows not from indices, columns from indices
        - Yoo: submatrix with rows and columns not from indices
    """
    n = matrix.shape[0]

    # Convert indices to numpy array if not already
    s_indices = np.array(indices)

    # Get the complement indices (all other indices)
    all_indices = np.arange(n)
    o_indices = np.setdiff1d(all_indices, s_indices)

    # Sort indices to maintain order
    s_indices = np.sort(s_indices)
    o_indices = np.sort(o_indices)

    # Check if input is sparse matrix
    if sp.issparse(matrix):
        # For sparse matrices, use slicing operations that preserve sparsity
        # Convert to CSR format for efficient row slicing
        if not sp.isspmatrix_csr(matrix):
            matrix_csr = matrix.tocsr()
        else:
            matrix_csr = matrix

        # Extract submatrices using sparse slicing
        # Yss: rows from s_indices, columns from s_indices
        Yss = matrix_csr[s_indices, :][:, s_indices]

        # Yso: rows from s_indices, columns from o_indices
        Yso = matrix_csr[s_indices, :][:, o_indices]

        # Yos: rows from o_indices, columns from s_indices
        Yos = matrix_csr[o_indices, :][:, s_indices]

        # Yoo: rows from o_indices, columns from o_indices
        Yoo = matrix_csr[o_indices, :][:, o_indices]

    else:
        # For dense numpy arrays, use advanced indexing
        # Yss: rows from s_indices, columns from s_indices
        Yss = matrix[np.ix_(s_indices, s_indices)]

        # Yso: rows from s_indices, columns from o_indices
        Yso = matrix[np.ix_(s_indices, o_indices)]

        # Yos: rows from o_indices, columns from s_indices
        Yos = matrix[np.ix_(o_indices, s_indices)]

        # Yoo: rows from o_indices, columns from o_indices
        Yoo = matrix[np.ix_(o_indices, o_indices)]

    return Yss, Yso, Yos, Yoo


def partition_matrix_pv_dict(matrix, s_indices, v_indices):
    """
    Partition an n×n matrix into nine submatrices based on two given index arrays.
    Works with both numpy arrays and scipy sparse matrices.

    Parameters:
    matrix (np.ndarray or scipy.sparse matrix): n×n input matrix
    s_indices (array-like): 1D array of indices for the 's' partition
    v_indices (array-like): 1D array of indices for the 'v' partition

    Returns:
    dict: Dictionary containing the nine submatrices:
        - Yss: rows from s_indices, columns from s_indices
        - Ysv: rows from s_indices, columns from v_indices
        - Yso: rows from s_indices, columns from other indices
        - Yvs: rows from v_indices, columns from s_indices
        - Yvv: rows from v_indices, columns from v_indices
        - Yvo: rows from v_indices, columns from other indices
        - Yos: rows from other indices, columns from s_indices
        - Yov: rows from other indices, columns from v_indices
        - Yoo: rows from other indices, columns from other indices
    """
    n = matrix.shape[0]

    # Convert indices to numpy arrays if not already
    s_indices = np.array(s_indices)
    v_indices = np.array(v_indices)

    # Get all indices
    all_indices = np.arange(n)

    # Get the "other" indices (complement of s_indices and v_indices)
    sv_combined = np.union1d(s_indices, v_indices)
    o_indices = np.setdiff1d(all_indices, sv_combined)

    # Sort all index arrays to maintain order
    s_indices = np.sort(s_indices)
    v_indices = np.sort(v_indices)
    o_indices = np.sort(o_indices)

    # Check if input is sparse matrix
    if sp.issparse(matrix):
        # For sparse matrices, use slicing operations that preserve sparsity
        # Convert to CSR format for efficient row slicing
        if not sp.isspmatrix_csr(matrix):
            matrix_csr = matrix.tocsr()
        else:
            matrix_csr = matrix

        # Extract all nine submatrices using sparse slicing
        result = {
            "Yss": matrix_csr[s_indices, :][:, s_indices],
            "Ysv": matrix_csr[s_indices, :][:, v_indices],
            "Yso": matrix_csr[s_indices, :][:, o_indices],
            "Yvs": matrix_csr[v_indices, :][:, s_indices],
            "Yvv": matrix_csr[v_indices, :][:, v_indices],
            "Yvo": matrix_csr[v_indices, :][:, o_indices],
            "Yos": matrix_csr[o_indices, :][:, s_indices],
            "Yov": matrix_csr[o_indices, :][:, v_indices],
            "Yoo": matrix_csr[o_indices, :][:, o_indices],
        }

    else:
        # For dense numpy arrays, use advanced indexing
        result = {
            "Yss": matrix[np.ix_(s_indices, s_indices)],
            "Ysv": matrix[np.ix_(s_indices, v_indices)],
            "Yso": matrix[np.ix_(s_indices, o_indices)],
            "Yvs": matrix[np.ix_(v_indices, s_indices)],
            "Yvv": matrix[np.ix_(v_indices, v_indices)],
            "Yvo": matrix[np.ix_(v_indices, o_indices)],
            "Yos": matrix[np.ix_(o_indices, s_indices)],
            "Yov": matrix[np.ix_(o_indices, v_indices)],
            "Yoo": matrix[np.ix_(o_indices, o_indices)],
        }

    return result


def partition_matrix_pv(matrix, s_indices, v_indices):
    """
    Alternative version that returns results as a tuple instead of dictionary.

    Returns:
    tuple: (Yss, Ysv, Yso, Yvs, Yvv, Yvo, Yos, Yov, Yoo)
    """
    result_dict = partition_matrix_pv_dict(matrix, s_indices, v_indices)
    return (
        result_dict["Yss"],
        result_dict["Ysv"],
        result_dict["Yso"],
        result_dict["Yvs"],
        result_dict["Yvv"],
        result_dict["Yvo"],
        result_dict["Yos"],
        result_dict["Yov"],
        result_dict["Yoo"],
    )
