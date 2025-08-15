import json
from time import perf_counter

from cameleon_dp.bench import baseline_dp
from cameleon_dp.scheduler import cameleon_dp
from cameleon_dp.bench import make_gaussian_instance_full


def main(n: int = 10000):
    w, hints = make_gaussian_instance_full(n)
    F0 = 0.0
    t0 = perf_counter()
    F_b, _ = baseline_dp(n, w, F0)
    t1 = perf_counter()
    Fb_sec = t1 - t0
    t0 = perf_counter()
    F_c, _, recs, bc = cameleon_dp(n, w, F0)
    t1 = perf_counter()
    Fc_sec = t1 - t0
    print(json.dumps({
        "n": n,
        "baseline_sec": Fb_sec,
        "cameleon_sec": Fc_sec,
        "speedup_x": Fb_sec / max(1e-12, Fc_sec),
        "exact": F_b == F_c,
        "boundary_count": bc,
    }, indent=2))


if __name__ == "__main__":
    main()


