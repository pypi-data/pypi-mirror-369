from dataclasses import dataclass
from typing import List, Tuple

from .cert_monge import cert_monge_templates
from .types import Block
from .ledger import Cert


def detect_monge_windows(w, n: int, j_lo: int, j_hi: int, i_lo: int, i_hi: int,
                         eps: float = 0.0, window_size: int = 256, step: int = 128,
                         samples: int = 3, hysteresis: int = 1,
                         guard_grid_i: int | None = None, guard_grid_j: int | None = None,
                         interval_oracle=None, interval_samples: int | None = None,
                         tiled_max_checks: int | None = None) -> List[Tuple[int, int, Cert]]:
    """Scan I in sliding windows; certify Monge using cert_monge_templates. Merge consecutive hits.

    Returns list of (i_lo, i_hi, cert) windows that passed. Conservative, one-sided.
    """
    hits: List[Tuple[int, int, Cert]] = []
    i = i_lo
    while i <= i_hi:
        w_lo = i
        w_hi = min(i_hi, i + window_size - 1)
        B = Block(j_lo=j_lo, j_hi=j_hi, i_lo=w_lo, i_hi=w_hi)
        cert = cert_monge_templates(
            w, B, eps, samples=samples,
            guard_grid_i=guard_grid_i, guard_grid_j=guard_grid_j,
            interval_oracle=interval_oracle, interval_samples=interval_samples,
            tiled_max_checks=tiled_max_checks
        )
        if cert.kind == "MONGE":
            hits.append((w_lo, w_hi, cert))
            i += step
        else:
            i += step
    # Merge consecutive hits with small gaps up to hysteresis windows
    if not hits:
        return []
    merged: List[Tuple[int, int, Cert]] = []
    cur_lo, cur_hi, cur_cert = hits[0]
    prev_hi = cur_hi
    for k in range(1, len(hits)):
        lo, hi, cert = hits[k]
        # if gap small in terms of windows (<= hysteresis * step), merge
        if lo - prev_hi - 1 <= hysteresis * step:
            cur_hi = hi
            prev_hi = hi
        else:
            merged.append((cur_lo, cur_hi, cur_cert))
            cur_lo, cur_hi, cur_cert = lo, hi, cert
            prev_hi = hi
    merged.append((cur_lo, cur_hi, cur_cert))
    return merged


def _max_abs_4th_diff(seq: List[float]) -> float:
    if len(seq) < 5:
        return 0.0
    d1 = [seq[i+1] - seq[i] for i in range(len(seq)-1)]
    d2 = [d1[i+1] - d1[i] for i in range(len(d1)-1)]
    d3 = [d2[i+1] - d2[i] for i in range(len(d2)-1)]
    d4 = [d3[i+1] - d3[i] for i in range(len(d3)-1)]
    return max(abs(x) for x in d4) if d4 else 0.0


def detect_poly3_windows(w, n: int, j_lo: int, j_hi: int, i_lo: int, i_hi: int,
                         eps: float = 0.0, window_size: int = 256, step: int = 128,
                         hysteresis: int = 1,
                         guard_grid_i: int | None = None, guard_grid_j: int | None = None,
                         interval_oracle=None, interval_samples: int | None = None,
                         tiled_max_checks: int | None = None) -> List[Tuple[int, int, Cert]]:
    """Heuristic pre-detector: checks if w(j, i) is nearly cubic in i for a few j samples,
    then confirms with Monge certs. Conservative; used only to seed SMAWK leaves.
    """
    hits: List[Tuple[int, int, Cert]] = []
    i = i_lo
    while i <= i_hi:
        w_lo = i
        w_hi = min(i_hi, i + window_size - 1)
        # sample 3 uniformly spaced j's
        js = [j_lo, (j_lo + j_hi)//2, j_hi]
        ok_all = True
        for j in js:
            ys = [w(j, ii) for ii in range(w_lo, w_hi + 1)]
            if _max_abs_4th_diff(ys) > max(eps, 1e-12):
                ok_all = False
                break
        if ok_all:
            B = Block(j_lo=j_lo, j_hi=j_hi, i_lo=w_lo, i_hi=w_hi)
            cert = cert_monge_templates(
                w, B, eps, samples=3,
                guard_grid_i=guard_grid_i, guard_grid_j=guard_grid_j,
                interval_oracle=interval_oracle, interval_samples=interval_samples,
                tiled_max_checks=tiled_max_checks
            )
            if cert.kind == "MONGE":
                hits.append((w_lo, w_hi, Cert(kind="MONGE", eps=eps, template="poly3", details=cert.details)))
        i += step
    # Merge consecutive hits up to hysteresis
    if not hits:
        return []
    merged: List[Tuple[int, int, Cert]] = []
    cur_lo, cur_hi, cur_cert = hits[0]
    prev_hi = cur_hi
    for k in range(1, len(hits)):
        lo, hi, cert = hits[k]
        if lo - prev_hi - 1 <= hysteresis * step:
            cur_hi = hi
            prev_hi = hi
        else:
            merged.append((cur_lo, cur_hi, cur_cert))
            cur_lo, cur_hi, cur_cert = lo, hi, cert
            prev_hi = hi
    merged.append((cur_lo, cur_hi, cur_cert))
    return merged