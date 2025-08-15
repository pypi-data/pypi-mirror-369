from ..numba_utils import maybe_jit

@maybe_jit(nopython=False, cache=True)
def _best(F, w, i, j_lo, j_hi):
    best_j = j_lo
    best_val = F[j_lo] + w(j_lo, i)
    for j in range(j_lo+1, j_hi+1):
        val = F[j] + w(j, i)
        if val < best_val:
            best_val = val
            best_j = j
    return best_val, best_j


@maybe_jit(nopython=False, cache=True)
def _dc(F, w, i_lo, i_hi, j_lo, j_hi, out_F, out_arg):
    if i_lo > i_hi:
        return
    i_mid = (i_lo + i_hi) // 2
    val, arg = _best(F, w, i_mid, j_lo, j_hi)
    out_F[i_mid] = val
    out_arg[i_mid] = arg
    _dc(F, w, i_lo, i_mid-1, j_lo, arg, out_F, out_arg)
    _dc(F, w, i_mid+1, i_hi, arg, j_hi, out_F, out_arg)

def solve_dc_opt(F, w, i_lo, i_hi, j_lo, j_hi, out_F, out_arg):
    """Classic divide-and-conquer optimization assuming monotone argmins.
    This function is exact if the monotone-argmin property holds; otherwise it's a heuristic.
    In CAMELEON-DP, we call this only when certified, else we fall back to baseline.
    """
    _dc(F, w, i_lo, i_hi, j_lo, j_hi, out_F, out_arg)