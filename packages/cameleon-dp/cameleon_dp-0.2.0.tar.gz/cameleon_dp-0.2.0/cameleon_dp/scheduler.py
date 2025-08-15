from dataclasses import dataclass
from collections import deque
from time import perf_counter
import itertools
from types import SimpleNamespace
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor

from .ledger import Cert, BlockRecord
from .cert_convex import cert_convex_form, ConvexFormHint
from .cert_monge import cert_monge_templates
from .cert_monotone import cert_monotone_pilot
from .specialists.li_chao import LiChao
from .specialists.smawk import solve_smawk
from .specialists.dc_opt import solve_dc_opt
from .window_detector import detect_monge_windows, detect_poly3_windows
from .types import Block
from .numeric import approx_equal
from .numba_utils import maybe_jit

@dataclass
class Block(Block):
    pass

def small(B: Block, W0: int) -> bool:
    return (B.i_hi - B.i_lo + 1) <= W0

@maybe_jit(nopython=False, cache=True)
def _baseline_inner(F, arg, j_lo, j_hi, i_lo, i_hi, w):
    for i in range(i_lo, i_hi + 1):
        best_val = 1e300
        best_j = j_lo
        j_hi_eff = j_hi if j_hi < i else i - 1
        for j in range(j_lo, j_hi_eff + 1):
            v = F[j] + w(j, i)
            if v < best_val:
                best_val = v
                best_j = j
        F[i] = best_val
        arg[i] = best_j

def solve_baseline(F, arg, w, B: Block):
    _baseline_inner(F, arg, B.j_lo, B.j_hi, B.i_lo, B.i_hi, w)

def validate_block_exact(F, w, B: Block, eps: float) -> bool:
    """Validate that F[i] equals min_{0<=j<i} F[j]+w(j,i) for i in B.I (full DP domain)."""
    for i in range(B.i_lo, B.i_hi + 1):
        best = float('inf')
        for j in range(0, i):
            val = F[j] + w(j, i)
            if val < best:
                best = val
        if not approx_equal(F[i], best, eps):
            return False
    return True

def solve_convex(F, arg, w, B: Block, hint: ConvexFormHint):
    """Exact convex-form block solver using incremental Li Chao insertion.
    Preload lines for j < i_lo (already computed). Then iterate i increasing,
    querying at x[i] and inserting line for j=i when available.
    """
    xs = [hint.x[i] for i in range(B.i_lo, B.i_hi + 1)]
    lct = LiChao(xs)
    # Preload lines for j strictly before this block's i range
    j_pre_hi = min(B.j_hi, B.i_lo - 1)
    for j in range(B.j_lo, j_pre_hi + 1):
        lct.add_line(hint.a[j], hint.b[j] + F[j], j)
    # Sweep i and add newly computed rows as lines for future i
    for i in range(B.i_lo, B.i_hi + 1):
        val, j_star = lct.query(hint.x[i])
        F[i] = val
        arg[i] = j_star
        if i <= B.j_hi:
            # Insert line corresponding to j=i for subsequent rows
            lct.add_line(hint.a[i], hint.b[i] + F[i], i)

# Top-level worker for process-based convex block solving
def _convex_block_job(a, b, x, F_j, j_lo, j_hi, i_lo, i_hi, block_id):
    t0 = perf_counter()
    xs = [x[i] for i in range(i_lo, i_hi + 1)]
    lct = LiChao(xs)
    # Helper to access F for absolute j
    def F_at(j):
        if j < i_lo:
            return F_j[j - j_lo]
        else:
            return out_F[j - i_lo]
    # Preload lines for j < i_lo
    pre_hi = min(j_hi, i_lo - 1)
    for j in range(j_lo, pre_hi + 1):
        lct.add_line(a[j], b[j] + F_at(j), j)
    out_F = [0.0] * (i_hi - i_lo + 1)
    out_arg = [-1] * (i_hi - i_lo + 1)
    for off, i in enumerate(range(i_lo, i_hi + 1)):
        val, j_star = lct.query(x[i])
        out_F[off] = val
        out_arg[off] = j_star
        if i <= j_hi:
            lct.add_line(a[i], b[i] + F_at(i), i)
    t1 = perf_counter()
    return (block_id, i_lo, i_hi, out_F, out_arg, t1 - t0)

# Process-based D&C job using serialized w via cloudpickle
def _dc_block_job(w_ser, F_j, j_lo, j_hi, i_lo, i_hi, block_id):
    import cloudpickle  # type: ignore
    w = cloudpickle.loads(w_ser)
    # reconstruct F accessor for absolute j
    def F_at(j):
        return F_j[j - j_lo]
    def _best_local(i, jl, jh):
        best_j = jl
        best_val = F_at(jl) + w(jl, i)
        for j in range(jl + 1, jh + 1):
            val = F_at(j) + w(j, i)
            if val < best_val:
                best_val = val
                best_j = j
        return best_val, best_j
    def _dc_local(i_lo_l, i_hi_l, jl, jh, out_F, out_arg):
        if i_lo_l > i_hi_l:
            return
        i_mid = (i_lo_l + i_hi_l) // 2
        val, arg = _best_local(i_mid, jl, jh)
        out_F[i_mid - i_lo] = val
        out_arg[i_mid - i_lo] = arg
        _dc_local(i_lo_l, i_mid - 1, jl, arg, out_F, out_arg)
        _dc_local(i_mid + 1, i_hi_l, arg, jh, out_F, out_arg)
    t0 = perf_counter()
    out_F = [float('inf')] * (i_hi - i_lo + 1)
    out_arg = [-1] * (i_hi - i_lo + 1)
    _dc_local(i_lo, i_hi, j_lo, j_hi, out_F, out_arg)
    t1 = perf_counter()
    return (block_id, i_lo, i_hi, out_F, out_arg, t1 - t0)


def _smawk_block_job(w_ser, F_j, j_lo, j_hi, i_lo, i_hi, eps, block_id):
    import cloudpickle  # type: ignore
    w = cloudpickle.loads(w_ser)
    def F_at(j):
        return F_j[j - j_lo]
    # SMAWK computation in process scope
    rows = list(range(i_lo, i_hi + 1))
    cols = list(range(j_lo, j_hi + 1))
    def f(i, j):
        if j < i:
            return F_at(j) + w(j, i)
        return float('inf')
    # local SMAWK implementation (reuse algorithm structure)
    def leq(a, b, key):
        if a < b - eps:
            return True
        if b < a - eps:
            return False
        return (hash(key) & 1) == 0
    def smawk(rows_l, cols_l):
        if not rows_l:
            return {}
        col_stack = []
        for c in cols_l:
            while col_stack:
                r_idx = len(col_stack) - 1
                r = rows_l[r_idx]
                prev_c = col_stack[-1]
                if leq(f(r, c), f(r, prev_c), (r, c, prev_c)):
                    col_stack.pop()
                else:
                    break
            if len(col_stack) < len(rows_l):
                col_stack.append(c)
        odd_rows = rows_l[1::2]
        result = {}
        result.update(smawk(odd_rows, col_stack))
        col_pos = {c: idx for idx, c in enumerate(col_stack)}
        for idx, r in enumerate(rows_l):
            if idx % 2 == 0:
                left = 0
                right = len(col_stack) - 1
                if idx - 1 >= 0:
                    prev_r = rows_l[idx - 1]
                    left = col_pos[result[prev_r]]
                if idx + 1 < len(rows_l):
                    next_r = rows_l[idx + 1]
                    right = col_pos[result[next_r]]
                best_j = col_stack[left]
                best_val = f(r, best_j)
                for c in col_stack[left:right + 1]:
                    val = f(r, c)
                    if leq(val, best_val, (r, c, best_j)):
                        best_val = val
                        best_j = c
                result[r] = best_j
        return result
    assignment = smawk(rows, cols)
    out_F = [0.0] * (i_hi - i_lo + 1)
    out_arg = [-1] * (i_hi - i_lo + 1)
    for off, i in enumerate(range(i_lo, i_hi + 1)):
        j = assignment[i]
        out_arg[off] = j
        out_F[off] = f(i, j)
    return (block_id, i_lo, i_hi, out_F, out_arg, 0.0)

def count_w_calls(w):
    counter = SimpleNamespace(count=0)
    def w_counted(j, i):
        counter.count += 1
        return w(j, i)
    return w_counted, counter

def _copy_cert(cert: Cert) -> Cert:
    return Cert(kind=cert.kind, eps=cert.eps, template=cert.template, details=(dict(cert.details) if isinstance(cert.details, dict) else cert.details))


def certify_block(w, B: Block, eps: float, hints: dict, budget: dict, cache: dict | None = None):
    # Try convex cert if a hint is provided
    hint = hints.get("convex_form")
    if hint is not None:
        max_j_checks = int(budget.get("convex_max_j_checks", 8))
        cert = cert_convex_form(w, B, hint=hint, eps=eps, interval_oracle=hints.get("interval_oracle"), max_j_checks=max_j_checks)
        if cert.kind != "NONE":
            if cert.details is None:
                cert.details = {}
            cert.details.setdefault("budget", {"max_j_checks": int(max_j_checks)})
            return cert
    # Ordering control between Monge and Monotone
    prefer_monotone = bool(hints.get("prefer_monotone", False))
    force_monotone = bool(hints.get("force_monotone", False))
    # Use grid budget for monotone pilot (smaller grid for small blocks)
    lengthI = B.i_hi - B.i_lo + 1
    mono_small_I = int(budget.get("monotone_small_I", 256))
    mono_grid = int(budget.get("monotone_grid", 5))
    if lengthI <= mono_small_I:
        mono_grid = int(budget.get("monotone_grid_small", max(3, mono_grid // 2)))
    # Use sampling budget for Monge guard
    monge_samples = int(budget.get("monge_samples", 5))
    monge_interval_samples = budget.get("monge_interval_samples")
    guard_i = budget.get("monge_guard_grid_i")
    guard_j = budget.get("monge_guard_grid_j")
    if force_monotone or prefer_monotone:
        max_pilots = budget.get("monotone_max_pilots")
        refine_grid = budget.get("monotone_refine_grid")
        cert = cert_monotone_pilot(w, B, eps, grid=mono_grid, interval_oracle=hints.get("interval_oracle"), max_pilots=max_pilots, refine_grid=refine_grid)
        if cert.kind != "NONE":
            if cert.details is None:
                cert.details = {}
            cert.details.setdefault("budget", {"grid": int(mono_grid), "monotone_small_I": int(mono_small_I), "max_pilots": (int(max_pilots) if max_pilots is not None else None)})
            return cert
        if force_monotone:
            return Cert(kind="NONE")
    # Monge certs
    cert = cert_monge_templates(
        w, B, eps, samples=monge_samples, guard_grid_i=guard_i, guard_grid_j=guard_j,
        interval_oracle=hints.get("interval_oracle"), interval_samples=monge_interval_samples,
        tiled_max_checks=int(budget.get("monge_tiled_max_checks", 0)) if isinstance(budget.get("monge_tiled_max_checks", 0), int) else None
    )
    if cert.kind != "NONE":
        if cert.details is None:
            cert.details = {}
        cert.details.setdefault("budget", {"samples": int(monge_samples),
                                            "interval_samples": (int(monge_interval_samples) if monge_interval_samples is not None else None),
                                            "guard_grid_i": (guard_i if guard_i is not None else 8),
                                            "guard_grid_j": (guard_j if guard_j is not None else 8),
                                            "tiled_max_checks": (int(budget.get("monge_tiled_max_checks")) if isinstance(budget.get("monge_tiled_max_checks"), int) else None)})
        return cert
    if not prefer_monotone:
        max_pilots = budget.get("monotone_max_pilots")
        refine_grid = budget.get("monotone_refine_grid")
        cert = cert_monotone_pilot(w, B, eps, grid=mono_grid, interval_oracle=hints.get("interval_oracle"), max_pilots=max_pilots, refine_grid=refine_grid)
        if cert.kind != "NONE":
            if cert.details is None:
                cert.details = {}
            cert.details.setdefault("budget", {"grid": int(mono_grid), "monotone_small_I": int(mono_small_I), "max_pilots": (int(max_pilots) if max_pilots is not None else None)})
            return cert
    return Cert(kind="NONE")

def cameleon_dp(n, w, F0, W0=16, eps=0.0, hints: dict | None = None, workers: int = 1, cert_budget: dict | None = None, proc_workers: int = 0, proc_workers_monotone: int = 0):
    """Recursive orchestrator: certifies, refines blocks by the longer dimension, and schedules wavefronts."""
    if hints is None:
        hints = {}
    # Initialize DP arrays (NumPy)
    F = np.full((n + 1,), float('inf'), dtype=float)
    arg = np.full((n + 1,), -1, dtype=int)
    F[0] = float(F0)

    # Block generation: recursive refinement
    block_id_counter = itertools.count(1)
    root = Block(j_lo=0, j_hi=n-1, i_lo=1, i_hi=n, block_id=next(block_id_counter), depth=0, orientation="root")
    queue = deque()
    leaves: list[tuple[Block, Cert]] = []
    # Track boundary-charging events for overhead estimation
    boundary_count = 0
    if cert_budget is None:
        cert_budget = {}

    covered = []
    # Simple cert cache to avoid repeated certification on identical blocks within a run
    cert_cache: dict[tuple, Cert] = {}
    if ('convex_form' not in hints) and (not hints.get('force_monotone')) and (not hints.get('prefer_monotone')):
        # Pre-detect Monge windows to seed certified leaves
        win_size = int(cert_budget.get("pre_monge_window_size", 256))
        win_step = int(cert_budget.get("pre_monge_step", max(1, win_size // 2)))
        win_samples = int(cert_budget.get("pre_monge_samples", 3))
        win_hyst = int(cert_budget.get("pre_monge_hysteresis", 1))
        monge_windows = detect_monge_windows(
            w, n, root.j_lo, root.j_hi, root.i_lo, root.i_hi,
            eps=eps, window_size=win_size, step=win_step, samples=win_samples, hysteresis=win_hyst
        )
        # Optional polynomial windows pre-detection
        poly_enable = bool(cert_budget.get("pre_poly3_enable", True))
        poly_win_size = int(cert_budget.get("pre_poly3_window_size", win_size))
        poly_step = int(cert_budget.get("pre_poly3_step", win_step))
        poly_hyst = int(cert_budget.get("pre_poly3_hysteresis", 1))
        poly_windows = []
        if poly_enable:
            poly_windows = detect_poly3_windows(
                w, n, root.j_lo, root.j_hi, root.i_lo, root.i_hi,
                eps=eps, window_size=poly_win_size, step=poly_step, hysteresis=poly_hyst
            )
        for i_lo_w, i_hi_w, cert in monge_windows + poly_windows:
            Bm = Block(j_lo=root.j_lo, j_hi=root.j_hi, i_lo=i_lo_w, i_hi=i_hi_w,
                       block_id=next(block_id_counter), depth=0, orientation='i')
            leaves.append((Bm, cert))
            covered.append((i_lo_w, i_hi_w))
    # Compute uncovered intervals of I to push into refinement queue
    def subtract_intervals(total_lo: int, total_hi: int, ranges: list[tuple[int, int]]):
        if not ranges:
            return [(total_lo, total_hi)]
        ranges = sorted(ranges)
        cur = total_lo
        gaps = []
        for lo, hi in ranges:
            if lo > cur:
                gaps.append((cur, lo - 1))
            cur = max(cur, hi + 1)
            if cur > total_hi:
                break
        if cur <= total_hi:
            gaps.append((cur, total_hi))
        return [(lo, hi) for lo, hi in gaps if lo <= hi]

    gaps = subtract_intervals(root.i_lo, root.i_hi, covered)
    if not covered:
        # No pre-detected structure; start with root
        queue.append(root)
    else:
        for lo, hi in gaps:
            queue.append(Block(j_lo=root.j_lo, j_hi=root.j_hi, i_lo=lo, i_hi=hi,
                               block_id=next(block_id_counter), depth=0, orientation='i'))
    # Track boundary-charging events for overhead estimation
    boundary_count = 0
    if cert_budget is None:
        cert_budget = {}
    while queue:
        B = queue.popleft()
        # Recursion depth cap
        max_depth = int(cert_budget.get("max_depth", 10))
        if B.depth >= max_depth:
            leaves.append((B, Cert(kind="NONE", details={"depth_capped_max_depth": int(max_depth)})))
            continue
        # Skip cert for very small I to avoid overhead
        # Increase min block size before certifying to reduce overhead on small blocks
        min_cert_I = int(cert_budget.get("min_cert_I", 256))
        if (B.i_hi - B.i_lo + 1) <= min_cert_I:
            leaves.append((B, Cert(kind="NONE", details={"small_skip_min_cert_I": int(min_cert_I)})))
            continue
        # Attempt to reuse a cached cert result
        cache_key = (
            B.j_lo, B.j_hi, B.i_lo, B.i_hi, int(eps * 1e12),
            bool('convex_form' in hints), bool(hints.get('prefer_monotone', False)), bool(hints.get('force_monotone', False)),
            int(cert_budget.get('monge_samples', 0)), cert_budget.get('monge_guard_grid_i'), cert_budget.get('monge_guard_grid_j'),
            int(cert_budget.get('monge_tiled_max_checks', 0)) if isinstance(cert_budget.get('monge_tiled_max_checks', 0), int) else None,
            int(cert_budget.get('monotone_grid', 0)), int(cert_budget.get('monotone_grid_small', 0)), int(cert_budget.get('monotone_small_I', 0)),
            int(cert_budget.get('monotone_max_pilots', 0)) if isinstance(cert_budget.get('monotone_max_pilots', 0), int) else None,
            int(cert_budget.get('monotone_refine_grid', 0)) if isinstance(cert_budget.get('monotone_refine_grid', 0), int) else None,
        )
        cert = None
        if cache_key in cert_cache:
            cert = _copy_cert(cert_cache[cache_key])
        else:
            cert = certify_block(w, B, eps=eps, hints=hints, budget=cert_budget)
            cert_cache[cache_key] = _copy_cert(cert)
        # If certified or small, mark as leaf
        if cert.kind != 'NONE' or small(B, W0):
            leaves.append((B, cert))
            continue
        # Uncertified: split by longer dimension (boundary event occurs)
        len_i = B.i_hi - B.i_lo + 1
        len_j = B.j_hi - B.j_lo + 1
        if len_i >= len_j:
            # Splitting along i dimension; one boundary event at i_mid
            mid = (B.i_lo + B.i_hi) // 2
            boundary_count += 1
            B1 = Block(j_lo=B.j_lo, j_hi=B.j_hi, i_lo=B.i_lo, i_hi=mid,
                       block_id=next(block_id_counter), depth=B.depth+1, orientation='i')
            B2 = Block(j_lo=B.j_lo, j_hi=B.j_hi, i_lo=mid+1, i_hi=B.i_hi,
                       block_id=next(block_id_counter), depth=B.depth+1, orientation='i')
        else:
            # Splitting along j dimension; one boundary event at j_mid
            mid = (B.j_lo + B.j_hi) // 2
            boundary_count += 1
            B1 = Block(j_lo=B.j_lo, j_hi=mid, i_lo=B.i_lo, i_hi=B.i_hi,
                       block_id=next(block_id_counter), depth=B.depth+1, orientation='j')
            B2 = Block(j_lo=mid+1, j_hi=B.j_hi, i_lo=B.i_lo, i_hi=B.i_hi,
                       block_id=next(block_id_counter), depth=B.depth+1, orientation='j')
        queue.extend([B1, B2])

    # Schedule and solve leaves by wavefront level
    records: list[BlockRecord] = []
    # p99 enforcement (mid-run fallback) based on wall-clock seconds
    p99_cap_enforce = None
    try:
        val = (cert_budget or {}).get("p99_enforce_sec") if cert_budget is not None else None
        if isinstance(val, (int, float)) and float(val) > 0:
            p99_cap_enforce = float(val)
    except Exception:
        p99_cap_enforce = None
    t_run_start = perf_counter()
    def _p99_enforce_active() -> bool:
        if p99_cap_enforce is None:
            return False
        return (perf_counter() - t_run_start) > p99_cap_enforce
    # Group leaves by their i_lo level
    levels: dict[int, list[tuple[Block, Cert]]] = {}
    for B, cert in leaves:
        levels.setdefault(B.i_lo, []).append((B, cert))

    # J-range shaper: promote SMAWK applicability when safe.
    def shape_for_smawk(level_key: int, tasks: list[tuple[Block, Cert]]) -> list[tuple[Block, Cert]]:
        shaped: list[tuple[Block, Cert]] = []
        for B, cert in tasks:
            # If MONGE but j_hi >= i_lo, SMAWK would be invalid; keep as-is
            if cert.kind != 'MONGE' or B.j_hi < B.i_lo:
                shaped.append((B, cert))
                continue
            # Try to carve out an early i segment where j_hi < i_lo holds without changing j range
            i_start = max(B.i_lo, B.j_hi + 1)
            # Loosened threshold: allow carving even a single-row pre-segment to unlock SMAWK sooner
            if i_start <= B.i_hi and (i_start - B.i_lo) >= 1:
                # Split into [i_lo, i_start-1] (baseline/monotone) and [i_start, i_hi] (SMAWK eligible)
                B1 = Block(j_lo=B.j_lo, j_hi=B.j_hi, i_lo=B.i_lo, i_hi=i_start - 1,
                           block_id=B.block_id, depth=B.depth, orientation=B.orientation)
                B2 = Block(j_lo=B.j_lo, j_hi=B.j_hi, i_lo=i_start, i_hi=B.i_hi,
                           block_id=B.block_id, depth=B.depth, orientation=B.orientation)
                shaped.append((B1, Cert(kind='NONE')))  # leave as non-certified, baseline path
                # Requeue B2 at its proper future level to respect dependencies
                levels.setdefault(B2.i_lo, []).append((B2, cert))
            else:
                shaped.append((B, cert))
        return shaped

    def process_block(B: Block, cert: Cert):
        t0 = perf_counter()
        w_used, c = count_w_calls(w)
        # If enforcement is active, force baseline for remaining work
        if _p99_enforce_active():
            solve_baseline(F, arg, w_used, B)
            t1 = perf_counter()
            if cert.details is None:
                cert.details = {}
            cert.details["p99_enforced"] = True
            cert.details["w_calls"] = c.count
            return BlockRecord(block_id=B.block_id,
                               j_lo=B.j_lo, j_hi=B.j_hi,
                               i_lo=B.i_lo, i_hi=B.i_hi,
                               cert=cert, runtime_sec=t1 - t0,
                               depth=B.depth, orientation=B.orientation)
        if cert.kind == 'CONVEX':
            solve_convex(F, arg, w, B, hints['convex_form'])
        elif cert.kind == 'MONGE':
            # Ensure j domain lies strictly before i domain for exactness
            if B.j_hi < B.i_lo:
                solve_smawk(F, w_used, B.i_lo, B.i_hi, B.j_lo, B.j_hi, F, arg, eps=eps)
            else:
                solve_baseline(F, arg, w, B)
        elif cert.kind == 'MONOTONE':
            # Narrow j-range using pilot bounds if available
            j_lo_n = B.j_lo
            j_hi_n = B.j_hi
            if cert.details and "min_j" in cert.details and "max_j" in cert.details:
                j_lo_n = max(j_lo_n, int(cert.details["min_j"]))
                j_hi_n = min(j_hi_n, int(cert.details["max_j"]))
            if cert.details and "tight_min_j" in cert.details and "tight_max_j" in cert.details:
                j_lo_n = max(j_lo_n, int(cert.details["tight_min_j"]))
                j_hi_n = min(j_hi_n, int(cert.details["tight_max_j"]))
            # Adaptive baseline for small MONOTONE blocks
            # More conservative thresholds to avoid D&C overhead on small/problem cases
            W0_mono = int(cert_budget.get("W0_mono", 512))
            mono_dc_min_I = int(cert_budget.get("mono_dc_min_I", 1024))
            lengthI = B.i_hi - B.i_lo + 1
            if lengthI <= W0_mono or lengthI <= mono_dc_min_I or j_lo_n > j_hi_n:
                solve_baseline(F, arg, w, B)
                ok = True
                if cert.details is None:
                    cert.details = {}
                cert.details["dc_skipped_small"] = True
            else:
                # Rows i must satisfy i > j_lo_n; solve earlier rows via baseline
                i_start = max(B.i_lo, j_lo_n + 1)
                if i_start > B.i_lo:
                    solve_baseline(F, arg, w, Block(j_lo=B.j_lo, j_hi=B.j_hi, i_lo=B.i_lo, i_hi=i_start-1, block_id=B.block_id, depth=B.depth, orientation=B.orientation))
                if i_start <= B.i_hi:
                    solve_dc_opt(F, w_used, i_start, B.i_hi, j_lo_n, j_hi_n, F, arg)
                # Exact validation; fallback to baseline if invalid
                ok = validate_block_exact(F, w, B, eps)
                if cert.details is None:
                    cert.details = {}
                cert.details["dc_validated"] = bool(ok)
                if not ok:
                    solve_baseline(F, arg, w, B)
                    cert.details["fallback_baseline"] = True
        else:
            solve_baseline(F, arg, w_used, B)
        t1 = perf_counter()
        if cert.details is None:
            cert.details = {}
        cert.details["w_calls"] = c.count
        rec = BlockRecord(block_id=B.block_id,
                          j_lo=B.j_lo, j_hi=B.j_hi,
                          i_lo=B.i_lo, i_hi=B.i_hi,
                          cert=cert, runtime_sec=t1 - t0,
                          depth=B.depth, orientation=B.orientation)
        return rec

    def coalesce_simple(tasks: list[tuple[Block, Cert]]):
        if not tasks:
            return tasks
        tasks_sorted = sorted(tasks, key=lambda bc: (bc[0].i_lo, bc[0].i_hi))
        merged: list[tuple[Block, Cert]] = []
        cur_B, cur_c = tasks_sorted[0]
        for B, c in tasks_sorted[1:]:
            contiguous = (B.i_lo == cur_B.i_hi + 1)
            same_cert = (c.kind == cur_c.kind)
            same_j = (B.j_lo == cur_B.j_lo and B.j_hi == cur_B.j_hi)
            if contiguous and same_cert and same_j:
                cur_B = Block(j_lo=cur_B.j_lo, j_hi=cur_B.j_hi,
                              i_lo=cur_B.i_lo, i_hi=B.i_hi,
                              block_id=cur_B.block_id, depth=min(cur_B.depth, B.depth), orientation=cur_B.orientation)
            else:
                merged.append((cur_B, cur_c))
                cur_B, cur_c = B, c
        merged.append((cur_B, cur_c))
        return merged

    def coalesce_adaptive(tasks: list[tuple[Block, Cert]], workers_local: int | None, budget_local: dict):
        if not tasks:
            return tasks
        enabled = bool(budget_local.get("coalesce_enabled", False))
        if not enabled:
            return coalesce_simple(tasks)
        policy = str(budget_local.get("coalesce_policy", "simple")).lower()
        max_merge_I_conf = budget_local.get("coalesce_max_merge_I")
        # Determine max merge size
        if policy == "auto" and workers_local and len(tasks) > max(2, workers_local * 2):
            max_merge_I = None
        else:
            max_merge_I = int(max_merge_I_conf) if isinstance(max_merge_I_conf, int) and max_merge_I_conf > 0 else None
        tasks_sorted = sorted(tasks, key=lambda bc: (bc[0].i_lo, bc[0].i_hi))
        merged: list[tuple[Block, Cert]] = []
        cur_B, cur_c = tasks_sorted[0]
        for B, c in tasks_sorted[1:]:
            contiguous = (B.i_lo == cur_B.i_hi + 1)
            same_cert = (c.kind == cur_c.kind)
            same_j = (B.j_lo == cur_B.j_lo and B.j_hi == cur_B.j_hi)
            allow_merge = contiguous and same_cert and same_j
            if allow_merge:
                merged_len = B.i_hi - cur_B.i_lo + 1
                if (max_merge_I is None) or (merged_len <= max_merge_I):
                    cur_B = Block(j_lo=cur_B.j_lo, j_hi=cur_B.j_hi,
                                  i_lo=cur_B.i_lo, i_hi=B.i_hi,
                                  block_id=cur_B.block_id, depth=min(cur_B.depth, B.depth), orientation=cur_B.orientation)
                    continue
            merged.append((cur_B, cur_c))
            cur_B, cur_c = B, c
        merged.append((cur_B, cur_c))
        return merged

    # Process levels in ascending order, including any new levels added by shaper
    while levels:
        level_keys = sorted(levels.keys())
        if not level_keys:
            break
        level = level_keys[0]
        # Barrier: all F[j] for j < level are ready
        pending = levels.pop(level)
        tasks = coalesce_adaptive(pending, workers, cert_budget)
        # Optionally enable j-range shaper when budget flag is set
        if bool(cert_budget.get('enable_j_shaper', True)):
            try:
                tasks = shape_for_smawk(level, tasks)
            except Exception:
                pass
        # If enforcement is active, skip process pools entirely for this level
        if _p99_enforce_active():
            remaining = tasks
            for B, cert in remaining:
                records.append(process_block(B, cert))
            continue
        # Split tasks into convex/monge/monotone (eligible for proc) and others
        convex_tasks = [(B, cert) for (B, cert) in tasks if cert.kind == 'CONVEX']
        monge_tasks = [(B, cert) for (B, cert) in tasks if cert.kind == 'MONGE']
        monotone_tasks = [(B, cert) for (B, cert) in tasks if cert.kind == 'MONOTONE']
        other_tasks = [(B, cert) for (B, cert) in tasks if cert.kind not in ('CONVEX','MONOTONE','MONGE')]
        # Determine if we will use process pools (convex/Monge share proc_workers; monotone may use its own)
        no_pickle_mode = bool(cert_budget.get("no_pickle_mode", False))
        min_blocks_conv = int(cert_budget.get("proc_convex_min_blocks", 2))
        min_I_conv = int(cert_budget.get("proc_convex_min_I", 8192))
        use_proc_conv = bool((not no_pickle_mode) and proc_workers and proc_workers > 1 and len(convex_tasks) >= min_blocks_conv and sum((B.i_hi - B.i_lo + 1) for B, _ in convex_tasks) >= min_I_conv)

        min_blocks_monge = int(cert_budget.get("proc_monge_min_blocks", 2))
        min_I_monge = int(cert_budget.get("proc_monge_min_I", 8192))
        use_proc_monge = bool((not no_pickle_mode) and proc_workers and proc_workers > 1 and len(monge_tasks) >= min_blocks_monge and sum((B.i_hi - B.i_lo + 1) for B, _ in monge_tasks) >= min_I_monge)

        min_blocks_dc = int(cert_budget.get("proc_monotone_min_blocks", 2))
        min_I_dc = int(cert_budget.get("proc_monotone_min_I", 8192))
        use_proc_dc = bool((not no_pickle_mode) and proc_workers_monotone and proc_workers_monotone > 1 and len(monotone_tasks) >= min_blocks_dc and sum((B.i_hi - B.i_lo + 1) for B, _ in monotone_tasks) >= min_I_dc)

        used_proc_monge = False
        used_proc_dc = False

        # Case A: single shared pool for all eligible kinds when worker counts match
        if (use_proc_conv or use_proc_monge or (use_proc_dc and proc_workers_monotone == proc_workers and (use_proc_conv or use_proc_monge))):
            try:
                import cloudpickle  # type: ignore
                w_ser = cloudpickle.dumps(w)
                a = hints['convex_form'].a if 'convex_form' in hints else None
                b = hints['convex_form'].b if 'convex_form' in hints else None
                x = hints['convex_form'].x if 'convex_form' in hints else None
                id_to_task_any: dict[int, tuple[Block, Cert]] = {}
                fut_to_kind: dict[object, str] = {}
                with ProcessPoolExecutor(max_workers=proc_workers) as ex:
                    # Submit convex
                    if use_proc_conv:
                        for B, cert in convex_tasks:
                            F_j = F[B.j_lo:B.j_hi+1].tolist()
                            fut = ex.submit(_convex_block_job, a, b, x, F_j, B.j_lo, B.j_hi, B.i_lo, B.i_hi, B.block_id)
                            fut_to_kind[fut] = "CONVEX"
                            id_to_task_any[B.block_id] = (B, cert)
                    # Submit monge (only valid ranges)
                    if use_proc_monge:
                        for B, cert in monge_tasks:
                            if B.j_hi >= B.i_lo:
                                continue
                            F_j = F[B.j_lo:B.j_hi+1].tolist()
                            fut = ex.submit(_smawk_block_job, w_ser, F_j, B.j_lo, B.j_hi, B.i_lo, B.i_hi, eps, B.block_id)
                            fut_to_kind[fut] = "MONGE"
                            id_to_task_any[B.block_id] = (B, cert)
                    # Submit monotone if sharing workers
                    if use_proc_dc and proc_workers_monotone == proc_workers:
                        for B, cert in monotone_tasks:
                            F_j = F[B.j_lo:B.j_hi+1].tolist()
                            j_lo_n = B.j_lo
                            j_hi_n = B.j_hi
                            if cert.details and "min_j" in cert.details and "max_j" in cert.details:
                                j_lo_n = max(j_lo_n, int(cert.details["min_j"]))
                                j_hi_n = min(j_hi_n, int(cert.details["max_j"]))
                            fut = ex.submit(_dc_block_job, w_ser, F_j, j_lo_n, j_hi_n, B.i_lo, B.i_hi, B.block_id)
                            fut_to_kind[fut] = "MONOTONE"
                            id_to_task_any[B.block_id] = (B, cert)
                    # Collect and apply in stable order by (i_lo, i_hi, block_id)
                    results = []
                    for fut in as_completed(list(fut_to_kind.keys())):
                        block_id, i_lo_b, i_hi_b, out_F, out_arg, elapsed = fut.result()
                        results.append((block_id, i_lo_b, i_hi_b, out_F, out_arg, elapsed))
                    results.sort(key=lambda t: (t[1], t[2], t[0]))
                    for block_id, i_lo_b, i_hi_b, out_F, out_arg, elapsed in results:
                        B, cert = id_to_task_any[block_id]
                        for off, i in enumerate(range(i_lo_b, i_hi_b + 1)):
                            F[i] = out_F[off]
                            arg[i] = out_arg[off]
                        if cert.details is None:
                            cert.details = {}
                        cert.details["w_calls"] = 0
                        records.append(BlockRecord(block_id=B.block_id,
                                                   j_lo=B.j_lo, j_hi=B.j_hi,
                                                   i_lo=B.i_lo, i_hi=B.i_hi,
                                                   cert=cert, runtime_sec=elapsed,
                                                   depth=B.depth, orientation=B.orientation))
                used_proc_monge = bool(use_proc_monge)
                used_proc_dc = bool(use_proc_dc and proc_workers_monotone == proc_workers)
                use_proc_conv = False
            except Exception:
                used_proc_monge = False
                used_proc_dc = False
                use_proc_conv = False

        # Case B: separate pool for monotone when not sharing
        if (not used_proc_dc) and use_proc_dc and proc_workers_monotone != proc_workers:
            try:
                import cloudpickle  # type: ignore
                w_ser = cloudpickle.dumps(w)
                jobs_dc = []
                id_to_task_dc: dict[int, tuple[Block, Cert]] = {}
                for B, cert in monotone_tasks:
                    F_j = F[B.j_lo:B.j_hi+1].tolist()
                    j_lo_n = B.j_lo
                    j_hi_n = B.j_hi
                    if cert.details and "min_j" in cert.details and "max_j" in cert.details:
                        j_lo_n = max(j_lo_n, int(cert.details["min_j"]))
                        j_hi_n = min(j_hi_n, int(cert.details["max_j"]))
                    jobs_dc.append((w_ser, F_j, j_lo_n, j_hi_n, B.i_lo, B.i_hi, B.block_id))
                    id_to_task_dc[B.block_id] = (B, cert)
                with ProcessPoolExecutor(max_workers=proc_workers_monotone) as ex:
                    futs_dc = [ex.submit(_dc_block_job, *args) for args in jobs_dc]
                    # Collect all, then apply in stable order
                    results = [f.result() for f in as_completed(futs_dc)]
                    results.sort(key=lambda t: (t[1], t[2], t[0]))
                    for block_id, i_lo_b, i_hi_b, out_F, out_arg, elapsed in results:
                        B, cert = id_to_task_dc[block_id]
                        for off, i in enumerate(range(i_lo_b, i_hi_b + 1)):
                            F[i] = out_F[off]
                            arg[i] = out_arg[off]
                        if cert.details is None:
                            cert.details = {}
                        cert.details["w_calls"] = 0
                        records.append(BlockRecord(block_id=B.block_id,
                                                   j_lo=B.j_lo, j_hi=B.j_hi,
                                                   i_lo=B.i_lo, i_hi=B.i_hi,
                                                   cert=cert, runtime_sec=elapsed,
                                                   depth=B.depth, orientation=B.orientation))
                used_proc_dc = True
            except Exception:
                used_proc_dc = False

        # Handle remaining tasks with threads or sequential
        remaining = []
        # Include convex tasks only if not processed in processes
        if not use_proc_conv:
            remaining += convex_tasks
        # Include monge tasks only if not processed in processes
        if not used_proc_monge:
            remaining += monge_tasks
        # Include monotone tasks only if not processed in processes
        if not used_proc_dc:
            remaining += monotone_tasks
        # Always include others
        remaining += other_tasks
        if workers and workers > 1 and len(remaining) > 1:
            with ThreadPoolExecutor(max_workers=workers) as ex:
                futs = [ex.submit(process_block, B, cert) for B, cert in remaining]
                for fut in as_completed(futs):
                    records.append(fut.result())
        else:
            for B, cert in remaining:
                records.append(process_block(B, cert))
    return F.tolist(), arg.tolist(), records, boundary_count