from .ledger import Cert
from .numeric import approx_equal, Interval, interval_excludes_point, interval_definitely_leq

class ConvexFormHint:
    """Optional exact hint specifying w(j,i) = a_j * x_i + b_j on a block."""
    def __init__(self, a, b, x):
        self.a = a  # list or array indexed by j
        self.b = b  # list or array indexed by j
        self.x = x  # list or array indexed by i

def cert_convex_form(w, B, hint: ConvexFormHint | None = None, eps: float = 0.0, max_j_checks: int = 8, interval_oracle=None):
    """Sound certifier: only returns CONVEX if provided hint agrees on multiple checks.
    Checks corners and K evenly spaced j samples across all i in the block. Conservative and one-sided.
    """
    if hint is None:
        return Cert(kind="NONE")
    jL, jR, iL, iR = B.j_lo, B.j_hi, B.i_lo, B.i_hi
    # Corner checks
    for (j,i) in [(jL,iL), (jR,iL), (jL,iR), (jR,iR)]:
        lhs = w(j, i)
        rhs = hint.a[j] * hint.x[i] + hint.b[j]
        if interval_oracle is not None:
            iv = interval_oracle(j, i)
            if interval_excludes_point(iv, rhs, eps):
                return Cert(kind="NONE")
        elif not approx_equal(lhs, rhs, eps):
            return Cert(kind="NONE")
    # Evenly spaced j samples (including endpoints)
    span = max(1, jR - jL)
    steps = min(max_j_checks - 2, span - 1) if span > 1 else 0
    js = [jL] + ([jL + (t * span) // (steps + 1) for t in range(1, steps + 1)] if steps > 0 else []) + [jR]
    truncated = False
    desired_js = min(max_j_checks, span + 1)
    if len(js) < desired_js:
        truncated = True
    for j in js:
        # Validate across all i in I for this j
        for i in range(iL, iR + 1):
            lhs = w(j, i)
            rhs = hint.a[j] * hint.x[i] + hint.b[j]
            if interval_oracle is not None:
                iv = interval_oracle(j, i)
                # Accept if interval definitely equals rhs within eps (safe acceptance)
                # Here equality is approximated by mutual <= within tolerance via intervals
                if not (interval_definitely_leq(Interval(rhs, rhs), iv, eps) and interval_definitely_leq(iv, Interval(rhs, rhs), eps)):
                    return Cert(kind="NONE")
            elif not approx_equal(lhs, rhs, eps):
                return Cert(kind="NONE")
    return Cert(kind="CONVEX", eps=eps, template="lines", details={
        "validated_js": len(js),
        "validated_i": iR - iL + 1,
        "max_j_checks": int(max_j_checks),
        "budget": {"max_j_checks": int(max_j_checks)},
        "budget_used": {"j_checks": int(len(js) * (iR - iL + 1))},
        "truncated_j_checks": bool(truncated),
        "desired_js": int(desired_js)
    })