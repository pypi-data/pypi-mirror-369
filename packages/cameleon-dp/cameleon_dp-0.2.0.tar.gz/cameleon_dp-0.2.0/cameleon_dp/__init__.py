from .scheduler import cameleon_dp, Block
from .bench import run_quick_bench, recommended_cert_budget

def solve(n, w, F0=0.0, profile: str = "auto", hints: dict | None = None,
          workers: int | None = None, proc_workers: int = 0, proc_workers_monotone: int = 0,
          cert_budget: dict | None = None, p99_cap: float | None = None, p99_mode: str = "report"):
    """Simple, safe wrapper for solving the 1-D DP exactly with smart defaults.

    - Uses the "auto" profile by default for a balanced, latency-aware budget
    - Optionally enforces a p99 cap by switching remaining work to the baseline path
    - Returns (F, arg, records, boundary_count)
    """
    if hints is None:
        hints = {}
    # Build a budget starting from a profile, then allow user overrides
    budget = dict(cert_budget or {})
    try:
        if profile:
            base = recommended_cert_budget(n, profile=profile)
            base.update(budget)
            budget = base
    except Exception:
        pass
    # Optional p99 guard/enforce
    if isinstance(p99_cap, (int, float)) and p99_cap is not None:
        try:
            budget["p99_guard_enabled"] = True
            budget["p99_guard_cap_sec"] = float(p99_cap)
            if str(p99_mode or "report").lower() == "enforce":
                budget["p99_enforce_sec"] = float(p99_cap)
        except Exception:
            pass
    # Auto workers/proc counts when not provided (reuse bench heuristics)
    if workers is None:
        try:
            from .bench import _recommended_workers  # type: ignore
            workers, _ = _recommended_workers(n)
        except Exception:
            workers = 1
    if not proc_workers:
        try:
            from .bench import _recommended_proc_workers  # type: ignore
            proc_workers, _ = _recommended_proc_workers(n)
        except Exception:
            proc_workers = 0
    if not proc_workers_monotone:
        try:
            from .bench import _recommended_proc_workers  # type: ignore
            proc_workers_monotone, _ = _recommended_proc_workers(n)
        except Exception:
            proc_workers_monotone = 0
    return cameleon_dp(n, w, F0, hints=hints, workers=int(workers or 1),
                       cert_budget=budget, proc_workers=int(proc_workers or 0),
                       proc_workers_monotone=int(proc_workers_monotone or 0))