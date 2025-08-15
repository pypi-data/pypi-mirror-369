from dataclasses import dataclass, asdict
from typing import Any
import json
import hashlib
import sys
import platform

@dataclass
class Cert:
    kind: str            # "CONVEX", "MONGE", "MONOTONE", "NONE"
    eps: float = 0.0
    template: str = ""
    details: dict | None = None

@dataclass
class BlockRecord:
    block_id: int
    j_lo: int
    j_hi: int
    i_lo: int
    i_hi: int
    cert: Cert
    runtime_sec: float
    depth: int = 0
    orientation: str = ""  # 'i' or 'j' (or 'root')


LEDGER_SCHEMA_VERSION = "1.0"


def records_to_json(records: list[BlockRecord]) -> str:
    def encode(obj: Any):
        if isinstance(obj, Cert):
            return asdict(obj)
        if isinstance(obj, BlockRecord):
            d = asdict(obj)
            # ensure cert is dict
            d["cert"] = encode(obj.cert)
            return d
        if isinstance(obj, (list, tuple)):
            return [encode(x) for x in obj]
        return obj
    records_payload = encode(records)
    # Deterministic hash of records for audit (manifest)
    try:
        records_bytes = json.dumps(records_payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        sha256 = hashlib.sha256(records_bytes).hexdigest()
    except Exception:
        sha256 = "unknown"
    # Minimal environment metadata
    try:
        py_ver = sys.version.split()[0]
        os_name = platform.system()
    except Exception:
        py_ver = "unknown"; os_name = "unknown"
    try:
        import numpy as _np  # type: ignore
        np_ver = str(_np.__version__)
    except Exception:
        np_ver = "unknown"
    payload = {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "manifest": {
            "records_sha256": sha256,
            "python": py_ver,
            "os": os_name,
            "numpy": np_ver,
        },
        "records": records_payload,
    }
    return json.dumps(payload, indent=2)


def export_records_json(records: list[BlockRecord], path: str) -> None:
    # Build base payload
    payload_str = records_to_json(records)
    try:
        payload = json.loads(payload_str)
    except Exception:
        payload = None
    # Optional signing: sign manifest hash when private key is available
    try:
        import os as _os
        sk_b64 = _os.environ.get("CAMELEON_SIGN_PRIVKEY_B64")
        if payload and sk_b64:
            sig = _sign_manifest(payload.get("manifest", {}).get("records_sha256", ""), sk_b64)
            if sig:
                payload.setdefault("signing", {})
                payload["signing"]["sig_ed25519_hex"] = sig
    except Exception:
        pass
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(payload if payload is not None else json.loads(payload_str), indent=2))


def export_proof_appendix(records: list[BlockRecord], path: str) -> None:
    """Export a concise proof appendix: per block cert + run metadata for audit/repro."""
    appendix = []
    for r in records:
        entry = {
            "block_id": r.block_id,
            "i": [r.i_lo, r.i_hi],
            "j": [r.j_lo, r.j_hi],
            "cert": r.cert.kind,
            "template": r.cert.template,
            "eps": r.cert.eps,
            "details": r.cert.details or {},
            "depth": r.depth,
            "orientation": r.orientation,
            "runtime_sec": float(r.runtime_sec),
        }
        appendix.append(entry)
    # Aggregate minimal metadata for reproducibility
    summary = summarize_records(records)
    try:
        import sys
        import platform
        py_ver = sys.version.split()[0]
        os_name = platform.system()
    except Exception:
        py_ver = "unknown"; os_name = "unknown"
    try:
        import numpy as _np  # type: ignore
        np_ver = str(_np.__version__)
    except Exception:
        np_ver = "unknown"
    meta = {
        "python": py_ver,
        "os": os_name,
        "numpy": np_ver,
        "total_blocks": summary.get("total_blocks", 0),
        "by_cert": {k: v.get("count", 0) for k, v in summary.get("by_cert", {}).items()},
        "guard_stats_total": summary.get("guard_stats_total", {}),
        "budget_hist_keys": list(summary.get("budget_hist", {}).keys()),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "appendix": appendix}, f, indent=2)


def summarize_records(records: list[BlockRecord]) -> dict:
    summary: dict[str, Any] = {
        "total_blocks": 0,
        "total_runtime_sec": 0.0,
        "by_cert": {},
        "total_w_calls": 0,
        "depth_hist": {},
        "orientation_hist": {},
        "w_calls_hist": {},
        "budget_hist": {},
        "guard_stats_total": {"sample_checks": 0, "tiled_checks": 0},
        "by_template": {},
    }
    runtimes_all: list[float] = []
    # Prepare w-call histogram bins
    def _bin(v: int) -> str:
        if v < 100:
            return "<1e2"
        if v < 1000:
            return "1e2-1e3"
        if v < 10000:
            return "1e3-1e4"
        return ">=1e4"

    for rec in records:
        summary["total_blocks"] += 1
        summary["total_runtime_sec"] += float(rec.runtime_sec)
        kind = rec.cert.kind
        summary["by_cert"].setdefault(kind, {"count": 0, "runtime_sec": 0.0, "w_calls": 0})
        entry = summary["by_cert"][kind]
        entry["count"] += 1
        entry["runtime_sec"] += float(rec.runtime_sec)
        # collect runtimes for quantiles
        runtimes_all.append(float(rec.runtime_sec))
        entry.setdefault("runtimes", [])
        entry["runtimes"].append(float(rec.runtime_sec))
        if rec.cert.details and isinstance(rec.cert.details.get("w_calls", 0), int):
            wc = int(rec.cert.details.get("w_calls", 0))
            summary["total_w_calls"] += wc
            entry["w_calls"] += wc
            # Global and per-cert histograms
            b = _bin(wc)
            summary["w_calls_hist"][b] = summary["w_calls_hist"].get(b, 0) + 1
            entry.setdefault("w_calls_hist", {})
            entry["w_calls_hist"][b] = entry["w_calls_hist"].get(b, 0) + 1
        # Budget params aggregation
        if rec.cert.details and isinstance(rec.cert.details.get("budget", {}), dict):
            budget = rec.cert.details.get("budget", {})
            for k, v in budget.items():
                try:
                    v_key = str(int(v))
                except Exception:
                    v_key = str(v)
                # global
                bh = summary["budget_hist"].setdefault(k, {})
                bh[v_key] = bh.get(v_key, 0) + 1
                # per-cert
                entry.setdefault("budget_hist", {})
                bhl = entry["budget_hist"].setdefault(k, {})
                bhl[v_key] = bhl.get(v_key, 0) + 1
        # Guard stats aggregation (Monge only but safe for any)
        if rec.cert.details and isinstance(rec.cert.details.get("guard_stats", {}), dict):
            gs = rec.cert.details.get("guard_stats", {})
            if isinstance(gs.get("sample_checks"), int):
                summary["guard_stats_total"]["sample_checks"] += int(gs["sample_checks"])
            if isinstance(gs.get("tiled_checks"), int):
                summary["guard_stats_total"]["tiled_checks"] += int(gs["tiled_checks"])
        summary["depth_hist"][rec.depth] = summary["depth_hist"].get(rec.depth, 0) + 1
        summary["orientation_hist"][rec.orientation] = summary["orientation_hist"].get(rec.orientation, 0) + 1
        # Per-template counts
        template = rec.cert.template or ""
        if template:
            tpl = summary["by_template"].setdefault(template, {"count": 0, "runtime_sec": 0.0, "w_calls": 0})
            tpl["count"] += 1
            tpl["runtime_sec"] += float(rec.runtime_sec)
            if rec.cert.details and isinstance(rec.cert.details.get("w_calls", 0), int):
                wc = int(rec.cert.details.get("w_calls", 0))
                tpl["w_calls"] += wc
                tpl.setdefault("w_calls_hist", {})
                b = _bin(wc)
                tpl["w_calls_hist"][b] = tpl["w_calls_hist"].get(b, 0) + 1
            # Per-template budget histograms
            if rec.cert.details and isinstance(rec.cert.details.get("budget", {}), dict):
                budget = rec.cert.details.get("budget", {})
                tpl.setdefault("budget_hist", {})
                for k, v in budget.items():
                    try:
                        v_key = str(int(v))
                    except Exception:
                        v_key = str(v)
                    bht = tpl["budget_hist"].setdefault(k, {})
                    bht[v_key] = bht.get(v_key, 0) + 1
    # Runtime quantiles (p50/p95/p99) overall and per cert
    def quantiles(vals: list[float]) -> dict:
        if not vals:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
        vs = sorted(vals)
        def q(p: float) -> float:
            if not vs:
                return 0.0
            idx = int(max(0, min(len(vs)-1, round((len(vs)-1) * p))))
            return float(vs[idx])
        return {"p50": q(0.5), "p95": q(0.95), "p99": q(0.99)}
    summary["runtime_quantiles"] = quantiles(runtimes_all)
    for kind, entry in summary["by_cert"].items():
        rts = entry.pop("runtimes", [])
        entry["runtime_quantiles"] = quantiles(rts)
    return summary


def summarize_records_file(path: str) -> dict:
    """Load a JSON ledger exported by export_records_json and return a summary dict."""
    recs = load_records_file(path)
    return summarize_records(recs)


def load_records_file(path: str) -> list[BlockRecord]:
    """Load a JSON ledger into BlockRecord dataclasses for downstream analysis."""
    raw = json.load(open(path, "r", encoding="utf-8"))
    # Backward-compatible: either an array (legacy) or an object with records and schema_version
    records = raw.get("records") if isinstance(raw, dict) and "records" in raw else raw
    out: list[BlockRecord] = []
    for d in records:
        cert_dict = d.get("cert", {})
        cert = Cert(kind=cert_dict.get("kind", ""),
                    eps=cert_dict.get("eps", 0.0),
                    template=cert_dict.get("template", ""),
                    details=cert_dict.get("details", {}))
        out.append(BlockRecord(
            block_id=d["block_id"],
            j_lo=d["j_lo"], j_hi=d["j_hi"],
            i_lo=d["i_lo"], i_hi=d["i_hi"],
            cert=cert, runtime_sec=float(d["runtime_sec"]),
            depth=int(d.get("depth", 0)), orientation=str(d.get("orientation", ""))
        ))
    return out


# --- Optional signing helpers (Enterprise) ---
def _sign_manifest(records_sha256: str, sk_b64: str) -> str | None:
    try:
        import base64
        from nacl.signing import SigningKey  # type: ignore
        sk = SigningKey(base64.b64decode(sk_b64))
        sig = sk.sign(records_sha256.encode("utf-8")).signature
        return sig.hex()
    except Exception:
        return None


def verify_ledger_signature(payload: dict, pk_b64: str) -> bool:
    try:
        import base64
        from nacl.signing import VerifyKey  # type: ignore
        manifest = payload.get("manifest", {})
        sig_hex = (payload.get("signing", {}) or {}).get("sig_ed25519_hex")
        if not sig_hex:
            return False
        msg = manifest.get("records_sha256", "").encode("utf-8")
        vk = VerifyKey(base64.b64decode(pk_b64))
        vk.verify(msg, bytes.fromhex(sig_hex))
        return True
    except Exception:
        return False