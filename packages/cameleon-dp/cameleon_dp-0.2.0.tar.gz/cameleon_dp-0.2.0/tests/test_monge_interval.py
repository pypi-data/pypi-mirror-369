from cameleon_dp.scheduler import cameleon_dp


def test_monge_interval_acceptance_tm1_tm2_tm3():
    # Construct a classic Monge cost: w(j,i) = (i-j)^2 for i>j else inf
    def w(j, i):
        if j >= i:
            return float('inf')
        d = i - j
        return float(d * d)

    # Interval oracle that safely encloses w(j,i)
    def wI(j, i):
        val = w(j, i)
        # For inf, return a wide interval that won't trigger accept checks
        if val == float('inf'):
            from cameleon_dp.numeric import Interval
            return Interval(float('inf'), float('inf'))
        eps = 1e-9
        from cameleon_dp.numeric import Interval
        return Interval(val - eps, val + eps)

    n = 128
    F, arg, recs, _ = cameleon_dp(
        n, w, 0.0,
        hints={"interval_oracle": wI},  # enable interval guards + acceptance
        workers=1,
        cert_budget={
            "min_cert_I": 16,
            "monge_samples": 5,
            "monge_guard_grid_i": 6,
            "monge_guard_grid_j": 6,
            "monge_tiled_max_checks": 8,
        }
    )
    # At least one block should be certified as MONGE (via T-M1/T-M2/T-M3)
    monge = [r for r in recs if r.cert.kind == "MONGE"]
    assert len(monge) >= 1
    # Sanity: template is one of our detectors
    assert any(r.cert.template in ("T-M1", "T-M2", "T-M3", "poly3") for r in monge)


