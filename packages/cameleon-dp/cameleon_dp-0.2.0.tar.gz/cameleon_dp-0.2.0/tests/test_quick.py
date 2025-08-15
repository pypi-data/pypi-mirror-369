import json

from cameleon_dp.bench import run_quick_bench, run_quick_bench_monotone
from cameleon_dp.cert_monge import cert_monge_templates
from cameleon_dp.types import Block


def test_monge_interval_guard_no_crash():
    # Synthetic instance with simple bounded interval oracle
    def w(j, i):
        if j >= i:
            return float('inf')
        return (i - j) * (i - j)
    def wI(j, i):
        val = w(j, i)
        return type('I', (), {'lo': val, 'hi': val, 'add': lambda self, o: type('I2', (), {'lo': self.lo + o.lo, 'hi': self.hi + o.hi})(), 'sub': lambda self, o: type('I2', (), {'lo': self.lo - o.hi, 'hi': self.hi - o.lo})()})()
    B = Block(j_lo=0, j_hi=63, i_lo=1, i_hi=64)
    cert = cert_monge_templates(w, B, eps=0.0, samples=5, interval_oracle=wI)
    assert cert.kind in ("MONGE", "NONE")
    if cert.kind == "MONGE":
        assert isinstance(cert.details.get("guard_stats", {}), dict)


def test_convex_quick_small():
    res = run_quick_bench(n=256, repeats=1)
    assert res["exact"] is True
    assert res["cert"] in ("CONVEX", "MONGE", "NONE")


def test_monotone_quick_small():
    res = run_quick_bench_monotone(n=256, repeats=1)
    assert res["exact"] is True
    assert res["cert"] in ("MONOTONE", "MONGE", "NONE")


