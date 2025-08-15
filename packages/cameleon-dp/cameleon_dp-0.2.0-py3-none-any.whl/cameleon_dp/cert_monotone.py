from .ledger import Cert
from .numeric import strictly_less, strictly_greater, Interval, interval_definitely_leq


def _early_monotone_guard_reject(w, B, eps: float, grid: int) -> bool:
    jL, jR, iL, iR = B.j_lo, B.j_hi, B.i_lo, B.i_hi
    length = iR - iL + 1
    step = max(1, length // max(2, grid))
    i_positions = list(range(iL, iR + 1, step))
    if i_positions[-1] != iR:
        i_positions.append(iR)
    prev_j = None
    for i in i_positions:
        # compute full argmin over j for guard (exact, reject-only)
        best_val = float('inf')
        best_j = jL
        for j in range(jL, min(jR, i - 1) + 1):
            val = w(j, i)
            if strictly_less(val, best_val, eps):
                best_val = val
                best_j = j
        if prev_j is not None and best_j < prev_j:
            return True
        prev_j = best_j
    return False


def _local_window_around_best(w, i: int, j_best: int, j_lo: int, j_hi: int, eps: float, slack: float = 0.0, interval_oracle=None) -> tuple[int, int]:
    """Extend left/right from j_best while value stays within best+eps+slack."""
    best_val = w(j_best, i)
    thresh = best_val + max(eps, 0.0) + max(slack, 0.0)
    # extend left
    jl = j_best
    j = j_best - 1
    while j >= j_lo:
        if interval_oracle is not None:
            iv = interval_oracle(j, i)
            # Keep including while lower bound cannot prove it's worse than threshold
            if iv.lo <= thresh:
                jl = j
                j -= 1
            else:
                break
        else:
            v = w(j, i)
            if not strictly_greater(v, thresh, 0.0):
                jl = j
                j -= 1
            else:
                break
    # extend right
    jr = j_best
    j = j_best + 1
    while j <= min(j_hi, i - 1):
        if interval_oracle is not None:
            iv = interval_oracle(j, i)
            if iv.lo <= thresh:
                jr = j
                j += 1
            else:
                break
        else:
            v = w(j, i)
            if not strictly_greater(v, thresh, 0.0):
                jr = j
                j += 1
            else:
                break
    return jl, jr


def cert_monotone_pilot(w, B, eps: float = 0.0, grid: int = 5, interval_oracle=None, max_pilots: int | None = None, refine_grid: int | None = None):
    """One-sided ε-monotone certifier: early guard + coarse-grid pilot and exact neighborhood checks.
    Returns tightened j-bounds for narrowing D&C when accepted.
    """
    # Early reject-only guard on a sparse grid
    if _early_monotone_guard_reject(w, B, eps, grid=max(3, grid)):
        return Cert(kind="NONE")

    jL, jR, iL, iR = B.j_lo, B.j_hi, B.i_lo, B.i_hi
    length = iR - iL + 1
    step = max(1, length // max(2, grid))
    i_positions = list(range(iL, iR + 1, step))
    if i_positions[-1] != iR:
        i_positions.append(iR)
    desired_pilots = len(i_positions)
    # Enforce pilot budget if provided by downsampling positions
    if isinstance(max_pilots, int) and max_pilots > 0 and len(i_positions) > max_pilots:
        stride = max(1, len(i_positions) // max_pilots)
        i_positions = i_positions[::stride]
        if i_positions[-1] != iR:
            i_positions.append(iR)
    # Pilot argmins on coarse grid
    j_pilots = []
    for i in i_positions:
        best_val = float('inf')
        best_j = jL
        for j in range(jL, min(jR, i - 1) + 1):
            val = w(j, i)
            if strictly_less(val, best_val, eps):
                best_val = val
                best_j = j
        j_pilots.append(best_j)
    # Check monotonicity of pilot argmins
    for k in range(len(j_pilots) - 1):
        if j_pilots[k] > j_pilots[k + 1]:
            return Cert(kind="NONE")
    # Neighborhood validation between pilot points; and build tightened bounds by intersection
    tight_min = jL
    tight_max = jR
    min_j_allowed = j_pilots[0]
    max_j_allowed = j_pilots[-1]
    for idx in range(len(i_positions) - 1):
        start, end = i_positions[idx], i_positions[idx + 1]
        min_j_allowed = min(min_j_allowed, j_pilots[idx])
        max_j_allowed = max(max_j_allowed, j_pilots[idx + 1])
        for i in (start, end):
            # compute local windows at segment boundaries and intersect
            jl, jr = _local_window_around_best(w, i, j_pilots[idx if i == start else idx + 1], jL, jR, eps, slack=0.0, interval_oracle=interval_oracle)
            tight_min = max(tight_min, jl)
            tight_max = min(tight_max, jr)
        # Validate within current allowed band
        for i in range(start, end + 1):
            best_val = float('inf')
            best_j = min_j_allowed
            for j in range(min_j_allowed, min(max_j_allowed, i - 1) + 1):
                val = w(j, i)
                if val < best_val - eps:
                    best_val = val
                    best_j = j
            if best_j < min_j_allowed or best_j > max_j_allowed:
                return Cert(kind="NONE")
    # Optional refinement: add midpoints between pilot segments to tighten bounds
    refine_points_used = 0
    if isinstance(refine_grid, int) and refine_grid > 0 and len(i_positions) >= 2:
        for idx in range(len(i_positions) - 1):
            start, end = i_positions[idx], i_positions[idx + 1]
            span = max(1, end - start)
            step = max(1, span // (refine_grid + 1))
            mids = [m for m in range(start + step, end, step)]
            for i in mids:
                # compute best within current allowed band and intersect local window
                best_val = float('inf')
                best_j = min_j_allowed
                for j in range(min_j_allowed, min(max_j_allowed, i - 1) + 1):
                    val = w(j, i)
                    if val < best_val - eps:
                        best_val = val
                        best_j = j
                jl, jr = _local_window_around_best(w, i, best_j, jL, jR, eps, slack=0.0, interval_oracle=interval_oracle)
                tight_min = max(tight_min, jl)
                tight_max = min(tight_max, jr)
                refine_points_used += 1
    # Ensure tightened bounds are consistent and non-empty
    tight_min = max(tight_min, min_j_allowed)
    tight_max = min(tight_max, max_j_allowed)
    if tight_min > tight_max:
        return Cert(kind="NONE")
    return Cert(kind="MONOTONE", eps=eps, template="pilot",
                details={"pilots": len(i_positions), "grid": int(max(3, grid)),
                         "min_j": int(min_j_allowed), "max_j": int(max_j_allowed),
                         "tight_min_j": int(tight_min), "tight_max_j": int(tight_max),
                         "budget": {"grid": int(max(3, grid)), "max_pilots": (int(max_pilots) if isinstance(max_pilots, int) else None),
                                     "refine_grid": (int(refine_grid) if isinstance(refine_grid, int) else None)},
                         "budget_used": {"pilot_points": int(len(i_positions)), "refine_points": int(refine_points_used)},
                         "budget_requested": {"pilot_points": int(desired_pilots), "refine_grid": (int(refine_grid) if isinstance(refine_grid, int) else None)},
                         "budget_truncated": {"pilots": bool(len(i_positions) < desired_pilots), "refine": bool(isinstance(refine_grid, int) and refine_grid > 0 and refine_points_used == 0)}})