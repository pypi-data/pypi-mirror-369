import json
import argparse

from cameleon_dp.bench import recommended_cert_budget, make_monotone_instance
from cameleon_dp.scheduler import cameleon_dp
from cameleon_dp.ledger import export_records_json, export_proof_appendix


def main():
    parser = argparse.ArgumentParser(description="Run a monotone-first quick bench and write a ledger")
    parser.add_argument("--n", type=int, default=3000, help="Problem size n")
    parser.add_argument("--workers", type=int, default=2, help="Thread workers")
    parser.add_argument("--out", type=str, default="ledger_mono_pref.json", help="Output ledger path")
    args = parser.parse_args()

    n = args.n
    w, hints = make_monotone_instance(n)
    # Prefer monotone pilot first to avoid Monge certification overhead
    hints["prefer_monotone"] = True
    hints["force_monotone"] = False

    budget = recommended_cert_budget(n, profile="monotone_careful")
    # Further reduce Monge guard overhead (will be ignored if monotone certifies first)
    budget.update({
        "monge_samples": 3,
        "monge_guard_grid_i": None,
        "monge_guard_grid_j": None,
        "monge_tiled_max_checks": 0,
    })

    F, arg, recs, boundary_count = cameleon_dp(
        n, w, 0.0, hints=hints, workers=args.workers,
        proc_workers=0, proc_workers_monotone=0, cert_budget=budget
    )

    export_records_json(recs, args.out)
    export_proof_appendix(recs, args.out.replace('.json', '_appendix.json'))

    print(json.dumps({
        "n": n,
        "exact": True,
        "first_cert": (recs[0].cert.kind if recs else "NONE"),
        "boundary_count": boundary_count,
        "C_hat": (boundary_count / n if n > 0 else 0.0),
        "ledger": args.out,
    }, indent=2))


if __name__ == "__main__":
    main()


