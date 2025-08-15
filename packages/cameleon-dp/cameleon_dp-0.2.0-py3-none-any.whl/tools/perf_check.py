import os
import json

from cameleon_dp.bench import run_quick_bench, run_quick_bench_monotone


def main():
    # Convex quick bench perf check
    n = int(os.environ.get("PERF_N", "2000"))
    repeats = int(os.environ.get("PERF_REPEATS", "1"))
    res = run_quick_bench(n=n, repeats=repeats)
    print(json.dumps({"convex": res}, indent=2))
    min_speedup = float(os.environ.get("MIN_SPEEDUP", "0"))
    if min_speedup > 0:
        speed = float(res.get("speedup_x", 0.0))
        assert speed >= min_speedup, f"Convex speedup {speed:.2f} < required {min_speedup:.2f}"
    # Monotone demo correctness (conservative settings may be slower; only check exactness)
    res_m = run_quick_bench_monotone(n=max(1000, n), repeats=repeats)
    print(json.dumps({"monotone": res_m}, indent=2))
    assert bool(res_m.get("exact", False)) is True


if __name__ == "__main__":
    main()



