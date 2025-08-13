import numpy as np

def apply_weights(D: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """
    If `weights` is empty, return D unchanged.
    If `weights` has length n_s, assume 1D grid and tile automatically.
    If `weights` has length 2*n_s, assume 2D grid and use directly.
    Returns D_star = D * sqrt(w) applied column-wise.
    """
    n_s, n_t = D.shape
    if weights.size == 0:
        return D
    w = np.asarray(weights, dtype=D.dtype)
    if w.size == n_s:
        # 1D grid: automatically broadcast each weight to full time series
        w_full = np.repeat(w, n_t//n_s)  # or tile as needed for time dims
    elif w.size == 2*n_s:
        w_full = w
    else:
        raise ValueError(f"weights must be length {n_s} or {2*n_s}, got {w.size}")
    # apply weights: scale each row i by sqrt(w_full[i])
    return (D.T * np.sqrt(w_full)).T