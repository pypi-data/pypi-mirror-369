import math
from dataclasses import dataclass


def _ulp(x: float) -> float:
    """Return a conservative ULP for x; 0.0 for non-finite values."""
    try:
        if math.isfinite(x):
            return math.ulp(x)
        return 0.0
    except AttributeError:
        # Fallback if math.ulp is unavailable
        if not math.isfinite(x):
            return 0.0
        # Rough fallback: relative eps scaled by magnitude
        return max(1e-16, abs(x)) * 2.0 ** -52


def _tol(a: float, b: float, eps: float, ulp_scale: float = 8.0) -> float:
    """Compute a safe comparison tolerance combining user eps and ULPs."""
    ulp_bound = ulp_scale * max(_ulp(a), _ulp(b))
    return max(float(eps), ulp_bound, 0.0)


def approx_equal(a: float, b: float, eps: float) -> bool:
    """Return True if a and b are equal within a safe tolerance."""
    # Fast path handles infinities and exact equality (including inf==inf)
    if a == b:
        return True
    t = _tol(a, b, eps)
    diff = a - b
    try:
        return abs(diff) <= t
    except Exception:
        # Handle NaN from inf - inf conservatively as not equal
        return False


def strictly_less(a: float, b: float, eps: float) -> bool:
    """Return True if a < b by more than the safe tolerance."""
    t = _tol(a, b, eps)
    return a < b - t


def strictly_greater(a: float, b: float, eps: float) -> bool:
    """Return True if a > b by more than the safe tolerance."""
    t = _tol(a, b, eps)
    return a > b + t


def leq_with_tie(a: float, b: float, eps: float, key) -> bool:
    """Deterministic <= with epsilon tolerance and a stable tie-breaker by key hash."""
    if strictly_less(a, b, eps):
        return True
    if strictly_less(b, a, eps):
        return False
    return (hash(key) & 1) == 0


@dataclass
class Interval:
    lo: float
    hi: float

    def add(self, other: "Interval") -> "Interval":
        return Interval(self.lo + other.lo, self.hi + other.hi)

    def sub(self, other: "Interval") -> "Interval":
        return Interval(self.lo - other.hi, self.hi - other.lo)

    def contains_point(self, x: float, eps: float = 0.0) -> bool:
        t = _tol((self.lo + self.hi) * 0.5, x, eps)
        return (x >= self.lo - t) and (x <= self.hi + t)

    def mul(self, other: "Interval") -> "Interval":
        a, b = self.lo, self.hi
        c, d = other.lo, other.hi
        p = (a * c, a * d, b * c, b * d)
        return Interval(min(p), max(p))


def definite_greater_than(lhs: Interval, rhs: Interval, eps: float) -> bool:
    """Return True if lhs > rhs + eps is certain under intervals (reject-only safe)."""
    return lhs.lo > (rhs.hi + _tol(lhs.lo, rhs.hi, eps))


def interval_excludes_point(iv: Interval, point: float, eps: float) -> bool:
    """Return True if the interval definitively excludes 'point' within safe tolerance."""
    t = _tol((iv.lo + iv.hi) * 0.5, point, eps)
    return (point < iv.lo - t) or (point > iv.hi + t)


def interval_definitely_leq(a: Interval, b: Interval, eps: float) -> bool:
    """True if a <= b holds for all realizations (safe acceptance)."""
    return a.hi <= (b.lo + _tol(a.hi, b.lo, eps))


def interval_maybe_leq(a: Interval, b: Interval, eps: float) -> bool:
    """True if a <= b cannot be ruled out (overlaps within tolerance). Useful for non-rejecting ties."""
    return not definite_greater_than(a, b, eps)


