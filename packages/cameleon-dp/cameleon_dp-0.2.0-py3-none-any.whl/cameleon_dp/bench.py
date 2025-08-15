from time import perf_counter
import numpy as np
from .licensing import license_status, is_pro_enabled

from .scheduler import cameleon_dp
from .cert_convex import ConvexFormHint
from .ledger import export_records_json, export_proof_appendix
from .ledger import load_records_file
import os

# --- Host-aware worker recommendations ---
def _effective_cpu_count() -> int:
    # Try process affinity first
    try:
        import psutil  # type: ignore
        p = psutil.Process()
        aff = p.cpu_affinity()
        if isinstance(aff, list) and len(aff) > 0:
            return max(1, len(aff))
    except Exception:
        pass
    # Fallback to os.cpu_count
    try:
        c = os.cpu_count() or 1
        return max(1, int(c))
    except Exception:
        return 1


def _recommended_workers(n: int) -> tuple[int, str]:
    cpus = _effective_cpu_count()
    if n <= 2000:
        w = min(2, cpus)
        return w, f"small-n heuristic (n={n}) → workers={w} with cpu_count={cpus}"
    w = min(8, cpus)
    return max(1, w), f"workers=min(8, cpu_count={cpus})"


def _recommended_proc_workers(n: int) -> tuple[int, str]:
    cpus = _effective_cpu_count()
    if cpus < 4 or n < 16000:
        return 0, f"process pools disabled (cpu_count={cpus}, n={n})"
    w = min(4, max(2, cpus // 2))
    return w, f"proc_workers≈cpu_count/2 (cpu_count={cpus}) for n={n}"

def baseline_dp(n, w, F0):
    F = [float('inf')] * (n + 1); F[0] = F0
    arg = [-1] * (n + 1)
    for i in range(1, n+1):
        best = float('inf'); bestj = 0
        for j in range(0, i):
            val = F[j] + w(j, i)
            if val < best:
                best = val; bestj = j
        F[i] = best; arg[i] = bestj
    return F, arg

def make_convex_form_instance(n):
    # w(j,i) = a_j * x_i + b_j with x_i = i, a_j = j, b_j = j*j
    x = [0.0] * (n + 1)
    a = [0.0] * (n + 1)
    b = [0.0] * (n + 1)
    for i in range(n+1): x[i] = float(i)
    for j in range(n+1):
        a[j] = float(j)
        b[j] = float(j*j)
    def w(j,i):
        return a[j] * x[i] + b[j]
    hint = ConvexFormHint(a=a, b=b, x=x)
    return w, hint

def make_monotone_instance(n):
    # Construct costs where argmins are monotone increasing in i
    # Example: w(j,i) = (i-j)^2 with penalty making j<i; argmins increase with i
    def w(j,i):
        if j >= i:
            return float('inf')
        d = i - j
        return float(d*d)
    # Do not force monotone by default; allow Monge or convex to take precedence when faster
    hints = {"prefer_monotone": False, "force_monotone": False}
    return w, hints

def recommended_cert_budget(n: int, profile: str = "balanced") -> dict:
    """Return a recommended cert/process budget for given n.

    Profiles:
    - "balanced": safe defaults with modest Monge guards and process thresholds.
    - "fast_convex": prioritize convex specialization; fewer Monge guards.
    - "monotone_careful": conservative D&C thresholds to avoid small-N overhead.
    """
    # Base across profiles
    base = {
        # Scheduler / small-I skip
        "min_cert_I": 256 if n <= 4096 else 512,
        # Monge guards
        "monge_samples": 7,
        "monge_guard_grid_i": 8,
        "monge_guard_grid_j": 8,
        "monge_tiled_max_checks": 16,
        # Process thresholds
        "proc_convex_min_blocks": 2,
        "proc_convex_min_I": 8192,
        "proc_monge_min_blocks": 2,
        "proc_monge_min_I": 8192,
        "proc_monotone_min_blocks": 2,
        "proc_monotone_min_I": 8192,
    }
    if profile == "fast_convex":
        out = dict(base)
        out.update({
            "monge_samples": 5,
            "monge_tiled_max_checks": 8,
        })
        return out
    if profile == "monotone_careful":
        out = dict(base)
        out.update({
            # Slightly higher thresholds to avoid D&C overhead on small/mid-N
            "W0_mono": 640,
            "mono_dc_min_I": 3072 if n > 4096 else 1536,
            "monotone_small_I": 1280 if n > 4096 else 640,
            "monotone_grid": 5,
            "monotone_grid_small": 3,
            "monotone_refine_grid": 1,
        })
        return out
    if profile == "low_latency":
        out = dict(base)
        # Avoid guard overhead and process setup for small/mid-N
        out.update({
            "min_cert_I": 1024 if n <= 8192 else 2048,
            "monge_samples": 0,
            "monge_guard_grid_i": None,
            "monge_guard_grid_j": None,
            "monge_tiled_max_checks": 0,
            "W0_mono": 1200,
            "mono_dc_min_I": 6144,
            "monotone_small_I": 2560,
            "monotone_grid": 3,
            "monotone_grid_small": 3,
            "monotone_refine_grid": 0,
            # Disable processes by default for minimal latency
            "proc_convex_min_I": 1_000_000,
            "proc_monge_min_I": 1_000_000,
            "proc_monotone_min_I": 1_000_000,
            # Enable p99 guard expectations (handled by benches/CLI)
            "p99_guard_enabled": True,
            "p99_guard_cap_sec": 0.0,
        })
        return out
    if profile == "fast_safe":
        out = dict(base)
        # Safe and fast: lift small skip thresholds, trim guards, enable p99 guard logic
        out.update({
            "min_cert_I": 768 if n <= 8192 else 1024,
            "monge_samples": 3,
            "monge_guard_grid_i": 6,
            "monge_guard_grid_j": 6,
            "monge_tiled_max_checks": 8,
            "W0_mono": 896,
            "mono_dc_min_I": 2560,
            "monotone_small_I": 1280,
            "monotone_grid": 4,
            "monotone_grid_small": 3,
            "monotone_refine_grid": 1,
            "p99_guard_enabled": True,
            "p99_guard_cap_sec": 0.0,
        })
        return out
    if profile == "opinionated_safe":
        out = dict(base)
        # Conservative, hides advanced knobs and prefers exact-but-cheap paths
        out.update({
            "min_cert_I": 512 if n <= 4096 else 1024,
            "monge_samples": 5,
            "monge_guard_grid_i": 8,
            "monge_guard_grid_j": 8,
            "monge_tiled_max_checks": 8,
            "W0_mono": 512,
            "mono_dc_min_I": 2048,
            "monotone_small_I": 1024,
            "monotone_grid": 5,
            "monotone_grid_small": 3,
            "monotone_refine_grid": 1,
        })
        return out
    if profile == "auto":
        # Heuristic: for n <= 4k favor low latency; for 4k<n<=12k fast_safe; else balanced
        if n <= 4000:
            return recommended_cert_budget(n, profile="low_latency")
        if n <= 12000:
            return recommended_cert_budget(n, profile="fast_safe")
        return recommended_cert_budget(n, profile="balanced")
    # balanced
    out = dict(base)
    out.update({
        "W0_mono": 640,
        "mono_dc_min_I": 1536,
        "monotone_small_I": 640,
        "monotone_grid": 5,
        "monotone_grid_small": 3,
        "monotone_refine_grid": 1,
    })
    return out

def run_quick_bench(n=5000, repeats=3, dump_ledger_path: str | None = None, workers: int | None = None,
                    proc_workers: int = 0, proc_workers_monotone: int = 0,
                    cert_budget: dict | None = None, profile: str | None = None,
                    auto_apply_suggestions_from_ledger: str | None = None,
                    suggestions_path: str | None = None):
    w, hint = make_convex_form_instance(n)
    # Baseline
    t_bas = []
    for _ in range(repeats):
        t0 = perf_counter()
        F0 = 0.0
        F_b, _ = baseline_dp(n, w, F0)
        t1 = perf_counter()
        t_bas.append(t1 - t0)
    # CAMELEON (convex-form)
    t_cam = []
    if workers is None:
        workers, w_reason = _recommended_workers(n)
    else:
        w_reason = "user override"
    workers_used = workers
    if proc_workers is None or proc_workers == 0:
        rec_pw, pw_reason = _recommended_proc_workers(n)
        proc_conv_used = rec_pw
    else:
        proc_conv_used = int(proc_workers or 0)
        pw_reason = "user override"
    if proc_workers_monotone is None or proc_workers_monotone == 0:
        rec_pwm, pwm_reason = _recommended_proc_workers(n)
        proc_mono_used = rec_pwm
    else:
        proc_mono_used = int(proc_workers_monotone or 0)
        pwm_reason = "user override"
    for _ in range(repeats):
        t0 = perf_counter()
        F0 = 0.0
        budget = cert_budget
        if budget is None and profile is not None:
            budget = recommended_cert_budget(n, profile=profile)
        # Apply persisted suggestions if provided
        if suggestions_path:
            try:
                import os as _os
                if _os.path.exists(suggestions_path):
                    budget = load_persisted_suggestions(suggestions_path, base_profile=(profile or "balanced"))
            except Exception:
                pass
        if auto_apply_suggestions_from_ledger and is_pro_enabled():
            try:
                from .bench import suggested_budget_from_ledger as _sugg
                import os as _os
                if _os.path.exists(auto_apply_suggestions_from_ledger):
                    budget = _sugg(auto_apply_suggestions_from_ledger, base_profile=(profile or "balanced"))
            except Exception:
                pass
        F_c, _, recs, boundary_count = cameleon_dp(
            n, w, F0, hints={"convex_form": hint}, workers=workers,
            proc_workers=proc_workers, proc_workers_monotone=proc_workers_monotone,
            cert_budget=(budget or {})
        )
        t1 = perf_counter()
        t_cam.append(t1 - t0)
    # Correctness check
    ok = np.allclose(F_b, F_c, atol=0.0, rtol=0.0)
    if dump_ledger_path:
        export_records_json(recs, dump_ledger_path)
        export_proof_appendix(recs, dump_ledger_path.replace('.json', '_appendix.json'))
    # Optional p99 guard metadata
    _cb = (cert_budget or {}) if cert_budget is not None else {}
    p99_guard_enabled = bool(_cb.get("p99_guard_enabled"))
    p99_cap = None
    if p99_guard_enabled:
        cap_val = _cb.get("p99_guard_cap_sec")
        p99_cap = float(cap_val) if isinstance(cap_val, (int, float)) and cap_val > 0 else None
    fallback_to_baseline = False
    if p99_cap is not None:
        p99 = float(np.quantile(t_cam, 0.99)) if len(t_cam) > 2 else float(np.median(t_cam))
        if p99 > p99_cap:
            fallback_to_baseline = True
    # Determine p99 mode from budget
    p99_mode = "off"
    if p99_guard_enabled and p99_cap:
        p99_mode = "enforce" if isinstance(_cb.get("p99_enforce_sec"), (int, float)) and float(_cb.get("p99_enforce_sec")) > 0 else "report"
    # Friendly notice if enforcement triggered mid-run
    exactness_notice = None
    if bool(_cb.get("p99_enforce_sec")):
        # Enforcement flips remaining blocks to baseline path; numerical exactness is preserved
        exactness_notice = "p99 enforcement active: remaining blocks forced to baseline; exactness preserved but specialist routing may differ."
    why_settings = {
        "workers": workers_used,
        "workers_reason": w_reason,
        "proc_workers": proc_conv_used,
        "proc_workers_reason": pw_reason,
        "proc_workers_monotone": proc_mono_used,
        "proc_workers_monotone_reason": pwm_reason,
        "profile": profile or None,
        "p99": {"mode": p99_mode, "cap_sec": p99_cap, "enforcement_active": bool(_cb.get("p99_enforce_sec"))},
    }
    return {
        "n": n,
        "baseline_sec": float(np.median(t_bas)),
        "cameleon_sec": float(np.median(t_cam)),
        "baseline_quantiles": {"p50": float(np.median(t_bas)), "p95": float(np.quantile(t_bas, 0.95)), "p99": float(np.quantile(t_bas, 0.99)) if len(t_bas) > 2 else float(np.median(t_bas))},
        "cameleon_quantiles": {"p50": float(np.median(t_cam)), "p95": float(np.quantile(t_cam, 0.95)), "p99": float(np.quantile(t_cam, 0.99)) if len(t_cam) > 2 else float(np.median(t_cam))},
        "speedup_x": float(np.median(t_bas) / max(1e-12, np.median(t_cam))),
        "exact": bool(ok),
        "cert": recs[0].cert.kind if recs else "NONE",
        "boundary_count": boundary_count,
        "C_hat": float(boundary_count) / n,
        "license_tier": license_status().get("tier", "COMMUNITY"),
        "p99_cap": p99_cap,
        "p99_mode": p99_mode,
        "fallback_to_baseline": bool(fallback_to_baseline),
        "p99_enforced": bool(fallback_to_baseline),
        "exactness_notice": exactness_notice,
        "workers_used": workers_used,
        "proc_workers_used": proc_conv_used,
        "proc_workers_monotone_used": proc_mono_used,
        "why_settings": why_settings,
    }

def run_quick_bench_monotone(n=5000, repeats=3, dump_ledger_path: str | None = None, workers: int | None = None,
                             proc_workers_monotone: int = 0, cert_budget: dict | None = None, profile: str | None = None,
                             prefer_monotone: bool = False, force_monotone: bool = False,
                             auto_apply_suggestions_from_ledger: str | None = None,
                             suggestions_path: str | None = None):
    w, hints = make_monotone_instance(n)
    # Baseline
    t_bas = []
    for _ in range(repeats):
        t0 = perf_counter()
        F0 = 0.0
        F_b, _ = baseline_dp(n, w, F0)
        t1 = perf_counter()
        t_bas.append(t1 - t0)
    # CAMELEON (monotone)
    t_cam = []
    import os
    if workers is None:
        workers, w_reason = _recommended_workers(n)
    else:
        w_reason = "user override"
    workers_used = workers
    if proc_workers_monotone is None or proc_workers_monotone == 0:
        rec_pwm, pwm_reason = _recommended_proc_workers(n)
        proc_mono_used = rec_pwm
    else:
        proc_mono_used = int(proc_workers_monotone or 0)
        pwm_reason = "user override"
    for _ in range(repeats):
        t0 = perf_counter()
        F0 = 0.0
        # Use provided budget or a recommended one
        budget = cert_budget
        if budget is None:
            budget = recommended_cert_budget(n, profile=(profile or "monotone_careful"))
        # Apply persisted suggestions if provided
        if suggestions_path:
            try:
                import os as _os
                if _os.path.exists(suggestions_path):
                    budget = load_persisted_suggestions(suggestions_path, base_profile=(profile or "monotone_careful"))
            except Exception:
                pass
        if auto_apply_suggestions_from_ledger and is_pro_enabled():
            try:
                from .bench import suggested_budget_from_ledger as _sugg
                import os as _os
                if _os.path.exists(auto_apply_suggestions_from_ledger):
                    budget = _sugg(auto_apply_suggestions_from_ledger, base_profile=(profile or "monotone_careful"))
            except Exception:
                pass
        hh = dict(hints)
        if prefer_monotone:
            hh["prefer_monotone"] = True
        if force_monotone:
            hh["force_monotone"] = True
        F_c, _, recs, boundary_count = cameleon_dp(
            n, w, F0, hints=hh, workers=workers, proc_workers_monotone=proc_workers_monotone,
            cert_budget=budget
        )
        t1 = perf_counter()
        t_cam.append(t1 - t0)
    ok = np.allclose(F_b, F_c, atol=0.0, rtol=0.0)
    if dump_ledger_path:
        export_records_json(recs, dump_ledger_path)
        export_proof_appendix(recs, dump_ledger_path.replace('.json', '_appendix.json'))
    # Optional p99 guard metadata
    _cbm = (cert_budget or {}) if cert_budget is not None else {}
    p99_guard_enabled = bool(_cbm.get("p99_guard_enabled"))
    p99_cap = None
    if p99_guard_enabled:
        cap_val = _cbm.get("p99_guard_cap_sec")
        p99_cap = float(cap_val) if isinstance(cap_val, (int, float)) and cap_val > 0 else None
    fallback_to_baseline = False
    if p99_cap is not None:
        p99 = float(np.quantile(t_cam, 0.99)) if len(t_cam) > 2 else float(np.median(t_cam))
        if p99 > p99_cap:
            fallback_to_baseline = True
    p99_mode = "off"
    if p99_guard_enabled and p99_cap:
        p99_mode = "enforce" if isinstance(_cbm.get("p99_enforce_sec"), (int, float)) and float(_cbm.get("p99_enforce_sec")) > 0 else "report"
    exactness_notice = None
    if bool(_cbm.get("p99_enforce_sec")):
        exactness_notice = "p99 enforcement active: remaining blocks forced to baseline; exactness preserved but specialist routing may differ."
    why_settings = {
        "workers": workers_used,
        "workers_reason": w_reason,
        "proc_workers_monotone": proc_mono_used,
        "proc_workers_monotone_reason": pwm_reason,
        "profile": profile or None,
        "p99": {"mode": p99_mode, "cap_sec": p99_cap, "enforcement_active": bool(_cbm.get("p99_enforce_sec"))},
    }
    return {
        "n": n,
        "baseline_sec": float(np.median(t_bas)),
        "cameleon_sec": float(np.median(t_cam)),
        "baseline_quantiles": {"p50": float(np.median(t_bas)), "p95": float(np.quantile(t_bas, 0.95)), "p99": float(np.quantile(t_bas, 0.99)) if len(t_bas) > 2 else float(np.median(t_bas))},
        "cameleon_quantiles": {"p50": float(np.median(t_cam)), "p95": float(np.quantile(t_cam, 0.95)), "p99": float(np.quantile(t_cam, 0.99)) if len(t_cam) > 2 else float(np.median(t_cam))},
        "speedup_x": float(np.median(t_bas) / max(1e-12, np.median(t_cam))),
        "exact": bool(ok),
        "cert": recs[0].cert.kind if recs else "NONE",
        "boundary_count": boundary_count,
        "C_hat": float(boundary_count) / n,
        "license_tier": license_status().get("tier", "COMMUNITY"),
        "p99_cap": p99_cap,
        "p99_mode": p99_mode,
        "fallback_to_baseline": bool(fallback_to_baseline),
        "p99_enforced": bool(fallback_to_baseline),
        "exactness_notice": exactness_notice,
        "workers_used": workers_used,
        "proc_workers_monotone_used": proc_mono_used,
        "why_settings": why_settings,
    }

# --- Full Benchmark Suite ---
import math

def make_gaussian_instance_full(n, segments=5, sigma=5.0, penalty=10.0):
    import numpy as np
    rng = np.random.RandomState(0)
    # Generate piecewise-constant means
    breaks = np.sort(rng.choice(np.arange(1, n), segments - 1, replace=False))
    breaks = np.concatenate(([0], breaks, [n]))
    data = np.empty(n)
    for k in range(segments):
        start, end = breaks[k], breaks[k+1]
        mu = rng.randn() * sigma
        data[start:end] = mu + rng.randn(end - start)
    # Prefix sums for O(1) cost queries
    S = np.concatenate(([0.0], np.cumsum(data)))
    SS = np.concatenate(([0.0], np.cumsum(data * data)))
    def w(j, i):
        L = i - j
        if L <= 0:
            return float('inf')
        sum_x = S[i] - S[j]
        sum_x2 = SS[i] - SS[j]
        # SSE + penalty
        cost = sum_x2 - (sum_x * sum_x) / L + penalty
        return cost
    return w, {}


def make_poisson_instance_full(n, segments=5, lam=5.0, penalty=10.0):
    import numpy as np
    rng = np.random.RandomState(1)
    breaks = np.sort(rng.choice(np.arange(1, n), segments - 1, replace=False))
    breaks = np.concatenate(([0], breaks, [n]))
    data = np.empty(n)
    for k in range(segments):
        start, end = breaks[k], breaks[k+1]
        rate = lam * (1 + 0.5 * rng.randn())
        data[start:end] = rng.poisson(rate, size=end - start)
    # Prefix sums
    S = np.concatenate(([0.0], np.cumsum(data)))
    Slog = np.concatenate(([0.0], np.cumsum(data * np.log(data + 1e-8))))
    def w(j, i):
        L = i - j
        if L <= 0:
            return float('inf')
        sum_x = S[i] - S[j]
        mean = sum_x / L
        sum_log = Slog[i] - Slog[j]
        # Poisson deviance (approx): 2 * [x*log(x/mean) - (x-mean)]
        # Using prefix sums for x*log(x)
        dev = 2 * (sum_log - sum_x * math.log(mean + 1e-8) - (sum_x - L * mean))
        return dev + penalty
    return w, {}


def make_adversarial_instance(n):
    # Deterministic no-structure weights
    def w(j, i):
        if j >= i:
            return float('inf')
        # Simple hash-based pseudo-random cost
        return (((j * 73856093) ^ (i * 19349663)) & 0xFFFFFFFF) / 2**32
    return w, {}


def run_full_bench(repeats=2, sizes=(5_000, 10_000, 20_000), large_n=False, p99_cap=None,
                   dump_dir: str | None = None, cpu_affinity_count: int | None = None,
                   profile: str | None = None, suggestions_path: str | None = None,
                   p99_mode: str = "report"):
    import numpy as np
    import json
    import os
    # Optionally pin CPU affinity for more stable results
    if isinstance(cpu_affinity_count, int) and cpu_affinity_count > 0:
        try:
            import psutil  # type: ignore
            p = psutil.Process()
            cpus = list(range(min(cpu_affinity_count, psutil.cpu_count() or cpu_affinity_count)))
            if cpus:
                p.cpu_affinity(cpus)
        except Exception:
            pass
    datasets = [
        ("Gaussian", make_gaussian_instance_full),
        ("Poisson", make_poisson_instance_full),
        ("Adversarial", make_adversarial_instance),
    ]
    results = {}
    for name, maker in datasets:
        results[name] = []
        size_list = sizes
        if large_n:
            size_list = tuple(sorted(set(list(sizes) + [10_000, 30_000, 100_000])))
        for n in size_list:
            w, hints = maker(n)
            # Baseline timing
            t_bas = []
            for _ in range(repeats):
                t0 = perf_counter()
                F0 = 0.0
                _, _ = baseline_dp(n, w, F0)
                t_bas.append(perf_counter() - t0)
            # CAMELEON timing
            t_cam = []
            rec_sample = None
            boundary_count = 0
            for rep_idx in range(repeats):
                t0 = perf_counter()
                F0 = 0.0
                # Build a cert budget per size if requested
                cert_budget = None
                if profile is not None:
                    cert_budget = recommended_cert_budget(n, profile=profile)
                # Apply p99 enforcement into budget when requested
                if isinstance(p99_cap, (int, float)) and float(p99_cap) > 0 and isinstance(cert_budget, dict):
                    if (p99_mode or "report").lower() == "enforce":
                        try:
                            cert_budget["p99_guard_enabled"] = True
                            cert_budget["p99_guard_cap_sec"] = float(p99_cap)
                            cert_budget["p99_enforce_sec"] = float(p99_cap)
                        except Exception:
                            pass
                if suggestions_path:
                    try:
                        import os as _os
                        if _os.path.exists(suggestions_path):
                            cert_budget = load_persisted_suggestions(suggestions_path, base_profile=(profile or "balanced"))
                    except Exception:
                        pass
                F_c, _, recs, bc = cameleon_dp(n, w, F0, hints=hints, cert_budget=(cert_budget or {}))
                t_cam.append(perf_counter() - t0)
                boundary_count = bc
                if rec_sample is None and recs:
                    rec_sample = recs[0]
                # Optionally dump ledgers for the first repeat per size
                if dump_dir and rep_idx == 0 and recs:
                    try:
                        from .ledger import export_records_json, export_proof_appendix
                        os.makedirs(dump_dir, exist_ok=True)
                        base = os.path.join(dump_dir, f"{name.lower()}_{n}")
                        export_records_json(recs, base + ".json")
                        export_proof_appendix(recs, base + "_appendix.json")
                    except Exception:
                        pass
            # Subsampled exactness check to avoid full O(n^2) on very large n
            F_b_sample, _ = baseline_dp(n, w, 0.0)
            ok = np.allclose(F_b_sample, F_c, atol=0.0, rtol=0.0)
            median_bas = float(np.median(t_bas))
            median_cam = float(np.median(t_cam))
            # Optional p99 latency cap auto-fallback indicator
            lat_caps = {
                "baseline_quantiles": {"p50": float(np.median(t_bas)), "p95": float(np.quantile(t_bas, 0.95)), "p99": float(np.quantile(t_bas, 0.99)) if len(t_bas) > 2 else float(np.median(t_bas))},
                "cameleon_quantiles": {"p50": float(np.median(t_cam)), "p95": float(np.quantile(t_cam, 0.95)), "p99": float(np.quantile(t_cam, 0.99)) if len(t_cam) > 2 else float(np.median(t_cam))},
            }
            fallback_to_baseline = False
            if isinstance(p99_cap, (int, float)) and lat_caps["cameleon_quantiles"]["p99"] > float(p99_cap):
                fallback_to_baseline = True
            results[name].append({
                "n": n,
                "baseline_sec": median_bas,
                "cameleon_sec": median_cam,
                "speedup_x": median_bas / max(1e-12, median_cam),
                "exact": bool(ok),
                "cert": rec_sample.cert.kind,
                "boundary_count": boundary_count,
                "C_hat": boundary_count / n,
                "quantiles": lat_caps,
                "p99_cap": float(p99_cap) if isinstance(p99_cap, (int, float)) else None,
                "p99_mode": (p99_mode or "report"),
                "fallback_to_baseline": bool(fallback_to_baseline),
            })
    return results


def suggested_budget_from_ledger(ledger_path: str, base_profile: str = "balanced") -> dict:
    """Build a cert/process budget by starting from a profile and applying suggestions from a ledger.

    - Sets proc_*_min_I to ~2x median I-length per cert kind (min 8192)
    - Suggests min_cert_I as ~2x median size of small-skip leaves (min 256)
    """
    recs = load_records_file(ledger_path)
    budget = recommended_cert_budget(max((r.i_hi for r in recs), default=0), profile=base_profile)
    # Median I-length by cert kind
    from statistics import median
    by_kind: dict[str, list[int]] = {}
    small_leaves: list[int] = []
    for r in recs:
        L = int(r.i_hi - r.i_lo + 1)
        by_kind.setdefault(r.cert.kind, []).append(L)
        if isinstance(r.cert.details, dict) and r.cert.details.get("small_skip_min_cert_I") is not None:
            small_leaves.append(L)
    def suggest_min_I(m: int, fallback: int) -> int:
        if m <= 0:
            return fallback
        return max(fallback, int(m * 2))
    med_conv = int(median(by_kind.get("CONVEX", []))) if by_kind.get("CONVEX") else 0
    med_monge = int(median(by_kind.get("MONGE", []))) if by_kind.get("MONGE") else 0
    med_mono = int(median(by_kind.get("MONOTONE", []))) if by_kind.get("MONOTONE") else 0
    budget["proc_convex_min_I"] = suggest_min_I(med_conv, int(budget.get("proc_convex_min_I", 8192)))
    budget["proc_monge_min_I"] = suggest_min_I(med_monge, int(budget.get("proc_monge_min_I", 8192)))
    budget["proc_monotone_min_I"] = suggest_min_I(med_mono, int(budget.get("proc_monotone_min_I", 8192)))
    if small_leaves:
        med_small = int(median(small_leaves))
        budget["min_cert_I"] = max(int(budget.get("min_cert_I", 256)), suggest_min_I(med_small, 256))
    return budget


def suggested_budget_from_ledgers(ledger_paths: list[str], base_profile: str = "balanced") -> dict:
    recs_all = []
    for p in ledger_paths:
        try:
            recs_all.extend(load_records_file(p))
        except Exception:
            continue
    if not recs_all:
        return recommended_cert_budget(0, profile=base_profile)
    # Reuse the single-ledger logic by temporarily writing aggregated medians
    # Build a pseudo-budget based on medians across combined records
    from statistics import median
    budget = recommended_cert_budget(max((r.i_hi for r in recs_all), default=0), profile=base_profile)
    by_kind: dict[str, list[int]] = {}
    small_leaves: list[int] = []
    for r in recs_all:
        L = int(r.i_hi - r.i_lo + 1)
        by_kind.setdefault(r.cert.kind, []).append(L)
        if isinstance(r.cert.details, dict) and r.cert.details.get("small_skip_min_cert_I") is not None:
            small_leaves.append(L)
    def suggest_min_I(m: int, fallback: int) -> int:
        if m <= 0:
            return fallback
        return max(fallback, int(m * 2))
    med_conv = int(median(by_kind.get("CONVEX", []))) if by_kind.get("CONVEX") else 0
    med_monge = int(median(by_kind.get("MONGE", []))) if by_kind.get("MONGE") else 0
    med_mono = int(median(by_kind.get("MONOTONE", []))) if by_kind.get("MONOTONE") else 0
    budget["proc_convex_min_I"] = suggest_min_I(med_conv, int(budget.get("proc_convex_min_I", 8192)))
    budget["proc_monge_min_I"] = suggest_min_I(med_monge, int(budget.get("proc_monge_min_I", 8192)))
    budget["proc_monotone_min_I"] = suggest_min_I(med_mono, int(budget.get("proc_monotone_min_I", 8192)))
    if small_leaves:
        med_small = int(median(small_leaves))
        budget["min_cert_I"] = max(int(budget.get("min_cert_I", 256)), suggest_min_I(med_small, 256))
    return budget


def persist_suggestions_from_ledgers(ledger_paths: list[str], out_path: str, base_profile: str = "balanced") -> dict:
    budget = suggested_budget_from_ledgers(ledger_paths, base_profile=base_profile)
    payload = {
        "schema": "cameleon_suggestions.v1",
        "base_profile": base_profile,
        "suggested": budget,
        "source_ledgers": list(ledger_paths),
    }
    try:
        import json as _json
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            _json.dump(payload, f, indent=2)
    except Exception:
        pass
    return payload


def load_persisted_suggestions(path: str, base_profile: str = "balanced") -> dict:
    try:
        import json as _json
        data = _json.load(open(path, "r", encoding="utf-8"))
        if isinstance(data, dict) and data.get("schema") == "cameleon_suggestions.v1" and isinstance(data.get("suggested"), dict):
            base = recommended_cert_budget(0, profile=data.get("base_profile", base_profile))
            base.update({k: v for k, v in data["suggested"].items()})
            return base
    except Exception:
        pass
    # Fallback: treat as a ledger and compute suggestions
    try:
        return suggested_budget_from_ledger(path, base_profile=base_profile)
    except Exception:
        return recommended_cert_budget(0, profile=base_profile)


if __name__ == "__main__":
    import json
    res = run_full_bench()
    print(json.dumps(res, indent=2))