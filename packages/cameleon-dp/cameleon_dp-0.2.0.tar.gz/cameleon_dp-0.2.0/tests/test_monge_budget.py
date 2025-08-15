from cameleon_dp.scheduler import cameleon_dp
from cameleon_dp.bench import make_monotone_instance
from cameleon_dp.ledger import summarize_records


def test_monge_budget_includes_tiled_max_checks_and_shows_in_summary():
    n = 128
    w, hints = make_monotone_instance(n)
    cert_budget = {
        "min_cert_I": 16,
        "monge_samples": 5,
        "monge_guard_grid_i": 6,
        "monge_guard_grid_j": 6,
        "monge_tiled_max_checks": 16,
    }
    F, arg, recs, _ = cameleon_dp(n, w, 0.0, hints=hints, workers=1, cert_budget=cert_budget)
    # Find at least one MONGE-certified block
    monge_recs = [r for r in recs if r.cert.kind == "MONGE"]
    assert len(monge_recs) >= 1
    # Check budget field includes tiled_max_checks
    b = monge_recs[0].cert.details.get("budget", {})
    assert "tiled_max_checks" in b
    assert b["tiled_max_checks"] in (16, None)  # None allowed if guard not invoked due to no grid
    # Summary must include budget_hist with tiled_max_checks value when present
    summary = summarize_records(recs)
    if b["tiled_max_checks"] is not None:
        assert "tiled_max_checks" in summary.get("budget_hist", {})
        assert "16" in summary["budget_hist"]["tiled_max_checks"]


