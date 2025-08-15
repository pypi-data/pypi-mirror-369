"""
Export Prometheus-friendly metrics from one or more ledger summaries.

Usage:
  python -m tools.perf_metrics_exporter ledger.json [ledger2.json ...] > metrics.prom
"""
import sys
import json


def summarize(path: str) -> dict:
    from cameleon_dp.ledger import summarize_records_file
    return summarize_records_file(path)


def to_prom(summary: dict, labels: dict | None = None) -> str:
    lines = []
    label_str = ""
    if labels:
        # simple label formatter key="val",...
        parts = [f'{k}="{v}"' for k, v in labels.items()]
        if parts:
            label_str = "{" + ",".join(parts) + "}"
    total_blocks = int(summary.get("total_blocks", 0))
    total_runtime = float(summary.get("total_runtime_sec", 0.0))
    lines.append(f"cameleon_blocks_total{label_str} {total_blocks}")
    lines.append(f"cameleon_runtime_seconds_total{label_str} {total_runtime:.6f}")
    # Overall runtime quantiles if present
    rq = summary.get("runtime_quantiles", {}) or {}
    for p in ("p50", "p95", "p99"):
        if p in rq:
            lines.append(f"cameleon_runtime_seconds_{p}{label_str} {float(rq[p]):.6f}")
    by_cert = summary.get("by_cert", {})
    for cert, d in by_cert.items():
        c = int(d.get("count", 0))
        rt = float(d.get("runtime_sec", 0.0))
        suffix = label_str
        if suffix:
            suffix = suffix[:-1] + f',cert="{cert}"' + "}"
        else:
            suffix = f'{{cert="{cert}"}}'
        lines.append(f"cameleon_blocks_by_cert{suffix} {c}")
        lines.append(f"cameleon_runtime_seconds_by_cert{suffix} {rt:.6f}")
        rqk = d.get("runtime_quantiles", {}) or {}
        for p in ("p50", "p95", "p99"):
            if p in rqk:
                lines.append(f"cameleon_runtime_seconds_{p}_by_cert{suffix} {float(rqk[p]):.6f}")
    guards = summary.get("guard_stats_total", {})
    lines.append(f"cameleon_guard_sample_checks_total{label_str} {int(guards.get('sample_checks', 0))}")
    lines.append(f"cameleon_guard_tiled_checks_total{label_str} {int(guards.get('tiled_checks', 0))}")
    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) < 2:
        print("usage: python -m tools.perf_metrics_exporter LEDGER.json [LEDGER2.json ...]", file=sys.stderr)
        sys.exit(2)
    for path in sys.argv[1:]:
        summary = summarize(path)
        sys.stdout.write(to_prom(summary, labels={"ledger": path}))


if __name__ == "__main__":
    main()


