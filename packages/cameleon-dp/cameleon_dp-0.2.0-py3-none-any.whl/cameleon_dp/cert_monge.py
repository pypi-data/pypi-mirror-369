import random
import math
from .numba_utils import maybe_jit
from .ledger import Cert
from .numeric import strictly_greater, approx_equal, strictly_less, Interval, definite_greater_than, interval_excludes_point


def _sample_guard_reject(w, jL, jR, iL, iR, eps: float, samples: int) -> tuple[bool, int]:
    checks = 0
    for _ in range(samples):
        j0 = random.randint(jL, jR)
        j1 = random.randint(jL, jR)
        i0 = random.randint(iL, iR)
        i1 = random.randint(iL, iR)
        if j0 >= j1 or i0 >= i1:
            continue
        # Only consider valid terms where j < i for all pairs
        if not (j0 < i0 and j1 < i1 and j0 < i1 and j1 < i0):
            continue
        lhs = w(j0, i0) + w(j1, i1)
        rhs = w(j0, i1) + w(j1, i0)
        checks += 1
        if strictly_greater(lhs, rhs, eps):
            return True, checks
    return False, checks


def _tiled_guard_reject(w, jL, jR, iL, iR, eps: float, grid_i: int, grid_j: int, max_checks: int | None = None) -> tuple[bool, int, int]:
    grid_i = max(3, grid_i)
    grid_j = max(3, grid_j)
    step_i = max(1, (iR - iL) // (grid_i - 1))
    step_j = max(1, (jR - jL) // (grid_j - 1))
    I = list(range(iL, iR + 1, step_i))
    J = list(range(jL, jR + 1, step_j))
    if I[-1] != iR:
        I.append(iR)
    if J[-1] != jR:
        J.append(jR)
    # Check Monge inequality on all adjacent 2x2 sub-squares of the grid
    checks = 0
    for ai in range(len(I) - 1):
        for bj in range(len(J) - 1):
            i0, i1 = I[ai], I[ai + 1]
            j0, j1 = J[bj], J[bj + 1]
            # Only evaluate valid 2x2 where all pairs satisfy j < i
            if not (j0 < i0 and j1 < i1 and j0 < i1 and j1 < i0):
                continue
            lhs = w(j0, i0) + w(j1, i1)
            rhs = w(j0, i1) + w(j1, i0)
            checks += 1
            if isinstance(max_checks, int) and max_checks > 0 and checks >= max_checks:
                # Budget cap reached without a definite reject
                return False, checks, (len(I) - 1) * (len(J) - 1)
            if strictly_greater(lhs, rhs, eps):
                return True, checks, (len(I) - 1) * (len(J) - 1)
    return False, checks, (len(I) - 1) * (len(J) - 1)


def _interval_guard_reject(wI, jL, jR, iL, iR, eps: float, samples: int = 8) -> tuple[bool, int]:
    """Reject-only guard using an interval oracle wI(j,i)->Interval.
    If the Monge inequality is definitely violated for any sampled 2x2, reject.
    """
    if wI is None:
        return False, 0
    checks = 0
    for _ in range(samples):
        j0 = random.randint(jL, jR)
        j1 = random.randint(jL, jR)
        i0 = random.randint(iL, iR)
        i1 = random.randint(iL, iR)
        if j0 >= j1 or i0 >= i1:
            continue
        lhs = wI(j0, i0).add(wI(j1, i1))
        rhs = wI(j0, i1).add(wI(j1, i0))
        checks += 1
        if definite_greater_than(lhs, rhs, eps):
            return True, checks
    return False, checks


def _detect_T_M1(w, jL, jR, iL, iR, eps: float, interval_oracle=None):
    # Template T-M1: φ(k) = w(jL, jL+k) over k in [iL-jL .. iR-jL]
    kL = iL - jL
    kR = iR - jL
    phi = []
    for k in range(kL, kR + 1):
        phi.append(w(jL, jL + k))
    # Check independence: w(j, j+k) == φ[k-kL]
    for j in range(jL, jR + 1):
        for idx, k in enumerate(range(kL, kR + 1)):
            i = j + k
            if i < iL or i > iR:
                continue
            if interval_oracle is not None:
                iv = interval_oracle(j, i)
                # Reject if interval definitively excludes expected phi value
                if interval_excludes_point(iv, phi[idx], eps):
                    break
                # else accept this position and continue
            elif not approx_equal(w(j, i), phi[idx], eps):
                break
        else:
            continue
        break
    else:
        # Independence holds; now check convexity of φ
        for idx in range(1, len(phi) - 1):
            d2 = phi[idx + 1] - 2 * phi[idx] + phi[idx - 1]
            if strictly_less(d2, 0.0, eps):
                return None
        return Cert(kind="MONGE", eps=eps, template="T-M1", details={"k_len": len(phi)})
    return None


def _rank1_cross_diff_ok(w, i_list, j_list, i0, j0, eps: float, interval_oracle=None):
    # Build matrix M(i,j) = w(j,i) - w(j,i0) - w(j0,i) + w(j0,i0)
    M = [[0.0 for _ in j_list] for _ in i_list]
    if interval_oracle is None:
        base = w(j0, i0)
        if not math.isfinite(base):
            return None
        for ai, i in enumerate(i_list):
            wi0 = w(j0, i)
            for bj, j in enumerate(j_list):
                wji = w(j, i)
                wji0 = w(j, i0)
                # Avoid invalid arithmetic; mark as NaN sentinel when any term is non-finite
                if not (math.isfinite(wji) and math.isfinite(wji0) and math.isfinite(wi0)):
                    M[ai][bj] = float('nan')
                else:
                    M[ai][bj] = wji - wji0 - wi0 + base
    else:
        baseI = interval_oracle(j0, i0)
        for ai, i in enumerate(i_list):
            wi0I = interval_oracle(j0, i)
            for bj, j in enumerate(j_list):
                wjiI = interval_oracle(j, i)
                wji0I = interval_oracle(j, i0)
                # M = w(j,i) - w(j,i0) - w(j0,i) + w(j0,i0)
                M[ai][bj] = wjiI.sub(wji0I).sub(wi0I).add(baseI)
    # Check all 2x2 minors approximately zero (rank 1)
    valid_minors = 0
    for a in range(len(i_list) - 1):
        for b in range(len(j_list) - 1):
            A = M[a][b]
            B = M[a + 1][b + 1]
            C = M[a][b + 1]
            D = M[a + 1][b]
            if interval_oracle is None:
                # Skip minors with non-finite values to avoid invalid arithmetic (reject-only behavior)
                if not (math.isfinite(A) and math.isfinite(B) and math.isfinite(C) and math.isfinite(D)):
                    continue
                valid_minors += 1
                det = A * B - C * D
                if not approx_equal(det, 0.0, eps):
                    return None
            else:
                # det interval = A*B - C*D
                detI = A.mul(B).sub(C.mul(D))
                valid_minors += 1
                # If interval excludes 0, reject
                if detI.lo > 0.0 or detI.hi < 0.0:
                    return None
    # If we couldn't evaluate any finite minors, fail to certify conservatively
    if valid_minors == 0:
        return None
    # Recover psi and chi up to scale from first row/col
    # Use first nonzero as pivot
    pivot = None
    for val in M[0]:
        if not math.isfinite(val):
            continue
        if not approx_equal(val, 0.0, eps):
            pivot = val
            break
    if pivot is None:
        # All zeros → trivial rank-1; treat as T-M2 with constant factors
        psi = [0.0 for _ in i_list]
        chi = [0.0 for _ in j_list]
    else:
        psi = [M[a][0] for a in range(len(i_list))]
        if any(not math.isfinite(v) for v in psi):
            return None
        chi = [0.0 for _ in j_list]
        denom = psi[0] if (math.isfinite(psi[0]) and not approx_equal(psi[0], 0.0, eps)) else (pivot if (pivot is not None and math.isfinite(pivot)) else 0.0)
        for b in range(len(j_list)):
            mb = M[0][b]
            if not math.isfinite(mb) or approx_equal(denom, 0.0, eps) or not math.isfinite(denom):
                chi[b] = 0.0
            else:
                chi[b] = mb / denom
    return psi, chi


def _is_monotone(seq, eps: float) -> bool:
    for a in range(1, len(seq)):
        if strictly_less(seq[a], seq[a - 1], eps):
            return False
    return True


def _is_convex(seq, eps: float) -> bool:
    for a in range(1, len(seq) - 1):
        d2 = seq[a + 1] - 2 * seq[a] + seq[a - 1]
        if strictly_less(d2, 0.0, eps):
            return False
    return True


def _detect_T_M2(w, jL, jR, iL, iR, eps: float, interval_oracle=None):
    # Sample coarse grids
    grid_i = max(3, min(8, (iR - iL + 1)))
    grid_j = max(3, min(8, (jR - jL + 1)))
    step_i = max(1, (iR - iL) // (grid_i - 1))
    step_j = max(1, (jR - jL) // (grid_j - 1))
    i_list = list(range(iL, iR + 1, step_i))
    j_list = list(range(jL, jR + 1, step_j))
    if i_list[-1] != iR:
        i_list.append(iR)
    if j_list[-1] != jR:
        j_list.append(jR)
    i0 = i_list[0]
    j0 = j_list[0]
    # First, interval-safe minors check if interval_oracle provided
    if interval_oracle is not None:
        res_intervals = _rank1_cross_diff_ok(w, i_list, j_list, i0, j0, eps, interval_oracle=interval_oracle)
        if res_intervals is None:
            return None
        # Recompute numerically for psi/chi monotonicity/convexity checks (safe, non-accepting)
        res = _rank1_cross_diff_ok(w, i_list, j_list, i0, j0, eps, interval_oracle=None)
        if res is None:
            return None
        psi, chi = res
    else:
        res = _rank1_cross_diff_ok(w, i_list, j_list, i0, j0, eps, interval_oracle=None)
        if res is None:
            return None
        psi, chi = res
    # Enforce psi convex over i and chi monotone over j (same direction as psi monotone)
    psi_mono = _is_monotone(psi, eps)
    chi_mono = _is_monotone(chi, eps)
    if not (psi_mono and chi_mono):
        return None
    if not _is_convex(psi, eps):
        return None
    return Cert(kind="MONGE", eps=eps, template="T-M2", details={"grid_i": len(i_list), "grid_j": len(j_list)})


def _detect_T_M3(w, jL, jR, iL, iR, eps: float, interval_oracle=None):
    # Coarse grids
    grid_i = max(5, min(16, (iR - iL + 1)))
    grid_j = max(5, min(16, (jR - jL + 1)))
    step_i = max(1, (iR - iL) // (grid_i - 1))
    step_j = max(1, (jR - jL) // (grid_j - 1))
    i_list = list(range(iL, iR + 1, step_i))
    j_list = list(range(jL, jR + 1, step_j))
    if i_list[-1] != iR:
        i_list.append(iR)
    if j_list[-1] != jR:
        j_list.append(jR)
    # Check convexity in i for each sampled j
    for j in j_list:
        for t in range(1, len(i_list) - 1):
            i0, i1, i2 = i_list[t - 1], i_list[t], i_list[t + 1]
            if interval_oracle is not None:
                iv0 = interval_oracle(j, i0)
                iv1 = interval_oracle(j, i1)
                iv2 = interval_oracle(j, i2)
                # d2 = iv2 - 2*iv1 + iv0
                iv2m2 = iv1.add(iv1)  # 2*iv1
                d2_iv = iv2.sub(iv2m2).add(iv0)
                # If definitely negative, reject
                if d2_iv.hi < 0.0:
                    return None
            else:
                v2 = w(j, i2); v1 = w(j, i1); v0 = w(j, i0)
                # Reject-only: if any non-finite encountered, fail to certify conservatively
                if not (math.isfinite(v2) and math.isfinite(v1) and math.isfinite(v0)):
                    return None
                d2 = (v2 - 2 * v1 + v0)
                if strictly_less(d2, 0.0, eps):
                    return None
    # For each sampled i, check that first differences in j are nondecreasing (monotone)
    for i in i_list:
        if interval_oracle is not None:
            prev_iv = None
            for idx in range(1, len(j_list)):
                j0, j1 = j_list[idx - 1], j_list[idx]
                iv = interval_oracle(j1, i).sub(interval_oracle(j0, i))
                if prev_iv is not None:
                    # If next difference definitely < previous, reject
                    if iv.hi < prev_iv.lo:
                        return None
                prev_iv = iv
        else:
            diffs = []
            for idx in range(1, len(j_list)):
                j0, j1 = j_list[idx - 1], j_list[idx]
                v1 = w(j1, i); v0 = w(j0, i)
                if not (math.isfinite(v1) and math.isfinite(v0)):
                    return None
                diffs.append(v1 - v0)
            if not _is_monotone(diffs, eps):
                return None
    return Cert(kind="MONGE", eps=eps, template="T-M3", details={"grid_i": len(i_list), "grid_j": len(j_list)})


def cert_monge_templates(w, B, eps: float = 0.0, samples: int = 5, guard_grid_i: int | None = None, guard_grid_j: int | None = None, interval_oracle=None, interval_samples: int | None = None, tiled_max_checks: int | None = None):
    """One-sided ε-Monge certifier: detects T-M1/T-M2/T-M3.
    Guards: random sampling reject + deterministic tiled 2x2 reject (coarse grids).
    """
    jL, jR, iL, iR = B.j_lo, B.j_hi, B.i_lo, B.i_hi
    sample_rej, sample_checks = _sample_guard_reject(w, jL, jR, iL, iR, eps, samples)
    if sample_rej:
        return Cert(kind="NONE")
    # Optional interval guard (reject-only)
    isamp = interval_samples if isinstance(interval_samples, int) and interval_samples > 0 else max(3, samples // 2)
    interval_rej, interval_checks = _interval_guard_reject(interval_oracle, jL, jR, iL, iR, eps, samples=isamp)
    if interval_rej:
        return Cert(kind="NONE")
    tiled_rej = False
    tiled_checks = 0
    tiled_desired = 0
    if guard_grid_i is not None or guard_grid_j is not None:
        gi = guard_grid_i if guard_grid_i is not None else 8
        gj = guard_grid_j if guard_grid_j is not None else 8
        tiled_rej, tiled_checks, tiled_desired = _tiled_guard_reject(w, jL, jR, iL, iR, eps, gi, gj, max_checks=tiled_max_checks)
        if tiled_rej:
            return Cert(kind="NONE")
    # Try T-M1
    cert = _detect_T_M1(w, jL, jR, iL, iR, eps, interval_oracle=interval_oracle)
    if cert is not None and isinstance(cert, Cert) and cert.kind == "MONGE":
        if cert.details is None:
            cert.details = {}
        cert.details.update({
            "budget": {"samples": int(samples),
                        "interval_samples": int(isamp) if isinstance(isamp, int) else None,
                        "guard_grid_i": (guard_grid_i if guard_grid_i is not None else 8),
                        "guard_grid_j": (guard_grid_j if guard_grid_j is not None else 8),
                        "tiled_max_checks": (int(tiled_max_checks) if isinstance(tiled_max_checks, int) else None)},
            "guards": {"sample_reject": bool(sample_rej), "tiled_reject": bool(tiled_rej), "interval_reject": bool(interval_rej)},
            "guard_params": {"samples": int(samples), "grid_i": guard_grid_i, "grid_j": guard_grid_j},
            "guard_stats": {"sample_checks": int(sample_checks), "tiled_checks": int(tiled_checks), "interval_checks": int(interval_checks)},
            "budget_used": {"sample_checks": int(sample_checks), "tiled_checks": int(tiled_checks), "interval_checks": int(interval_checks)},
            "budget_requested": {"sample_checks": int(samples), "interval_checks": int(isamp), "tiled_checks": int(tiled_desired)},
            "budget_truncated": {"sample": bool(sample_checks < samples), "interval": bool(interval_checks < isamp), "tiled": bool(tiled_desired > 0 and tiled_checks < tiled_desired)}
        })
        return cert
    # Try T-M2 (conservative)
    cert = _detect_T_M2(w, jL, jR, iL, iR, eps, interval_oracle=interval_oracle)
    if cert is not None:
        if cert.details is None:
            cert.details = {}
        cert.details.update({
            "budget": {"samples": int(samples),
                        "interval_samples": int(isamp) if isinstance(isamp, int) else None,
                        "guard_grid_i": (guard_grid_i if guard_grid_i is not None else 8),
                        "guard_grid_j": (guard_grid_j if guard_grid_j is not None else 8),
                        "tiled_max_checks": (int(tiled_max_checks) if isinstance(tiled_max_checks, int) else None)},
            "guards": {"sample_reject": bool(sample_rej), "tiled_reject": bool(tiled_rej), "interval_reject": bool(interval_rej)},
            "guard_params": {"samples": int(samples), "grid_i": guard_grid_i, "grid_j": guard_grid_j},
            "guard_stats": {"sample_checks": int(sample_checks), "tiled_checks": int(tiled_checks), "interval_checks": int(interval_checks)},
            "budget_used": {"sample_checks": int(sample_checks), "tiled_checks": int(tiled_checks), "interval_checks": int(interval_checks)},
            "budget_requested": {"sample_checks": int(samples), "interval_checks": int(isamp), "tiled_checks": int(tiled_desired)},
            "budget_truncated": {"sample": bool(sample_checks < samples), "interval": bool(interval_checks < isamp), "tiled": bool(tiled_desired > 0 and tiled_checks < tiled_desired)}
        })
        return cert
    # Try T-M3 (conservative)
    cert = _detect_T_M3(w, jL, jR, iL, iR, eps, interval_oracle=interval_oracle)
    if cert is not None:
        if cert.details is None:
            cert.details = {}
        cert.details.update({
            "budget": {"samples": int(samples),
                        "interval_samples": int(isamp) if isinstance(isamp, int) else None,
                        "guard_grid_i": (guard_grid_i if guard_grid_i is not None else 8),
                        "guard_grid_j": (guard_grid_j if guard_grid_j is not None else 8),
                        "tiled_max_checks": (int(tiled_max_checks) if isinstance(tiled_max_checks, int) else None)},
            "guards": {"sample_reject": bool(sample_rej), "tiled_reject": bool(tiled_rej), "interval_reject": bool(interval_rej)},
            "guard_params": {"samples": int(samples), "grid_i": guard_grid_i, "grid_j": guard_grid_j},
            "guard_stats": {"sample_checks": int(sample_checks), "tiled_checks": int(tiled_checks), "interval_checks": int(interval_checks)},
            "budget_used": {"sample_checks": int(sample_checks), "tiled_checks": int(tiled_checks), "interval_checks": int(interval_checks)},
            "budget_requested": {"sample_checks": int(samples), "interval_checks": int(isamp), "tiled_checks": int(tiled_desired)},
            "budget_truncated": {"sample": bool(sample_checks < samples), "interval": bool(interval_checks < isamp), "tiled": bool(tiled_desired > 0 and tiled_checks < tiled_desired)}
        })
        return cert
    return Cert(kind="NONE")