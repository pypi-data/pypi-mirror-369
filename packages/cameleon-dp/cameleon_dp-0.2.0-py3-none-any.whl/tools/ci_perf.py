import os
import json

from cameleon_dp.bench import (
    run_quick_bench,
    run_quick_bench_monotone,
    baseline_dp,
    make_gaussian_instance_full,
    make_poisson_instance_full,
    make_adversarial_instance,
)
from cameleon_dp.scheduler import cameleon_dp


def load_targets(path: str | None = None) -> dict:
    if path is None:
        path = os.environ.get("PERF_TARGETS_PATH", "perf_targets.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    # Default conservative targets if none provided
    return {
        "convex_quick": {"2000": 1.2},
        "monotone_quick": {"exact": True},
    }


def run_checks(targets: dict, repeats: int = 1) -> dict:
    results: dict = {"ok": True, "checks": []}
    # Convex quick thresholds by n
    convex_targets = targets.get("convex_quick", {})
    for n_str, min_speed in convex_targets.items():
        try:
            n = int(n_str)
        except Exception:
            continue
        res = run_quick_bench(n=n, repeats=repeats, profile=os.environ.get("PERF_PROFILE_CONVEX"))
        ok = float(res.get("speedup_x", 0.0)) >= float(min_speed)
        results["checks"].append({
            "kind": "convex_quick",
            "n": n,
            "speedup_x": float(res.get("speedup_x", 0.0)),
            "min_speedup": float(min_speed),
            "ok": bool(ok),
            "res": res,
        })
        results["ok"] = results["ok"] and ok
    # Monotone correctness only (perf can be slower at small N)
    mono_targets = targets.get("monotone_quick", {})
    if mono_targets:
        n_mono = max([int(k) for k in mono_targets.keys() if k.isdigit()] + [1500])
    res_m = run_quick_bench_monotone(n=n_mono, repeats=repeats, profile=os.environ.get("PERF_PROFILE_MONO"))
        ok_m = bool(res_m.get("exact", False)) is True
        results["checks"].append({
            "kind": "monotone_quick",
            "n": n_mono,
            "ok": bool(ok_m),
            "res": res_m,
        })
        results["ok"] = results["ok"] and ok_m
    # Dataset-specific targets (Gaussian/Poisson/Adversarial)
    ds_targets = targets.get("datasets", {})
    strict_datasets = os.environ.get("CI_PERF_DATASETS_STRICT", "0") in ("1", "true", "True")
    # Optional worker controls
    try:
        workers = int(os.environ.get("PERF_WORKERS", "0"))
    except Exception:
        workers = 0
    try:
        proc_workers = int(os.environ.get("PERF_PROC_WORKERS", "0"))
    except Exception:
        proc_workers = 0
    try:
        proc_workers_monotone = int(os.environ.get("PERF_PROC_WORKERS_MONO", "0"))
    except Exception:
        proc_workers_monotone = 0
    makers = {
        "Gaussian": make_gaussian_instance_full,
        "Poisson": make_poisson_instance_full,
        "Adversarial": make_adversarial_instance,
    }
    for ds_name, sz_map in ds_targets.items():
        if ds_name not in makers:
            continue
        maker = makers[ds_name]
        for n_str, min_speed in sz_map.items():
            try:
                n = int(n_str)
            except Exception:
                continue
            w, hints = maker(n)
            # Baseline timing (median of repeats)
            from time import perf_counter
            import numpy as np
            t_bas = []
            for _ in range(repeats):
                t0 = perf_counter()
                _ = baseline_dp(n, w, 0.0)
                t_bas.append(perf_counter() - t0)
            # CAMELEON timing
            t_cam = []
            rec_sample = None
            for _ in range(repeats):
                t0 = perf_counter()
                cb = {
                    # Reasonable defaults to reduce overhead and enable guards
                    "min_cert_I": 256,
                    "monge_samples": 7,
                    "monge_guard_grid_i": 8,
                    "monge_guard_grid_j": 8,
                    "monge_tiled_max_checks": 16,
                    # Process thresholds (will only kick in if proc_workers>1)
                    "proc_convex_min_blocks": 2,
                    "proc_convex_min_I": 8192,
                    "proc_monge_min_blocks": 2,
                    "proc_monge_min_I": 8192,
                }
                ds_profile = os.environ.get("PERF_PROFILE_DATASET", "balanced")
                try:
                    from cameleon_dp.bench import recommended_cert_budget as _rcb
                    cb = _rcb(n, profile=ds_profile)
                except Exception:
                    pass
                kwargs = {}
                if workers and workers > 0:
                    kwargs["workers"] = workers
                if proc_workers and proc_workers > 1:
                    kwargs["proc_workers"] = proc_workers
                if proc_workers_monotone and proc_workers_monotone > 1:
                    kwargs["proc_workers_monotone"] = proc_workers_monotone
                F_c, _, recs, _ = cameleon_dp(n, w, 0.0, hints=hints, cert_budget=cb, **kwargs)
                t_cam.append(perf_counter() - t0)
                if rec_sample is None and recs:
                    rec_sample = recs[0]
            median_bas = float(np.median(t_bas))
            median_cam = float(np.median(t_cam))
            speed = median_bas / max(1e-12, median_cam)
            ok = speed >= float(min_speed)
            results["checks"].append({
                "kind": "dataset",
                "dataset": ds_name,
                "n": n,
                "speedup_x": speed,
                "min_speedup": float(min_speed),
                "ok": bool(ok),
            })
            # Only gate overall OK when strict flag for datasets is enabled
            if strict_datasets:
                results["ok"] = results["ok"] and ok
    return results


def main():
    repeats = int(os.environ.get("PERF_REPEATS", "1"))
    strict = os.environ.get("CI_PERF_STRICT", "0") in ("1", "true", "True")
    targets = load_targets()
    results = run_checks(targets, repeats=repeats)
    print(json.dumps(results, indent=2))
    if strict:
        assert bool(results.get("ok", False)), "Performance guardrails failed"


if __name__ == "__main__":
    main()


