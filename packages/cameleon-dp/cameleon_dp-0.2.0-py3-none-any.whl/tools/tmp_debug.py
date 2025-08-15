from cameleon_dp.bench import make_monotone_instance
from cameleon_dp.scheduler import cameleon_dp

def main():
    n = 128
    w, hints = make_monotone_instance(n)
    budget = {"min_cert_I": 16, "monge_samples": 5, "monge_guard_grid_i": 6, "monge_guard_grid_j": 6, "monge_tiled_max_checks": 16}
    F, arg, recs, _ = cameleon_dp(n, w, 0.0, hints=hints, workers=1, cert_budget=budget)
    kinds = [r.cert.kind for r in recs]
    print("counts:", {k: kinds.count(k) for k in set(kinds)})
    for r in recs[:10]:
        print(r.cert.kind, r.cert.template, r.cert.details and r.cert.details.get("budget"))

if __name__ == "__main__":
    main()

