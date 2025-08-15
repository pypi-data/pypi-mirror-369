import argparse
import json
import sys
import os
from .ledger import summarize_records_file, load_records_file
from .bench import run_quick_bench, run_quick_bench_monotone, recommended_cert_budget
from .licensing import activate_license, deactivate_license, license_status, is_pro_enabled


def main():
    parser = argparse.ArgumentParser(prog="cameleon-dp")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logs and Numba warnings (default: off)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("summarize", help="Summarize a ledger JSON file")
    s.add_argument("path", help="Path to ledger.json")
    s.add_argument("--highlights-only", action="store_true", help="Print only the highlight section (budgets/guards/templates)")
    s.add_argument("--insights", action="store_true", help="Print top actionable knob suggestions")
    s.add_argument("--export-csv", type=str, default=None, help="Export key tables to CSV at the given directory path")
    s.add_argument("--plot", type=str, default=None, help="Write quick matplotlib PNGs to directory (requires matplotlib)")
    s.add_argument("--export-parquet", type=str, default=None, help="Export ledger records and key summaries as Parquet to DIR (requires pyarrow)")
    s.add_argument("--verify-signature", action="store_true", help="Verify signature on ledger (if present) using CAMELEON_PUBKEY_B64 env var")
    s2 = sub.add_parser("suggest-thresholds", help="Suggest process thresholds based on a ledger")
    s2.add_argument("path", help="Path to ledger.json")
    s6 = sub.add_parser("run-full", help="Run the full benchmark suite and optionally dump ledgers")
    s6.add_argument("--repeats", type=int, default=1)
    s6.add_argument("--large-n", action="store_true")
    s6.add_argument("--dump-dir", type=str, default=None)
    s6.add_argument("--cpu-affinity", type=int, default=None, help="Optionally pin to first K CPUs for stability")
    s6.add_argument("--profile", type=str, default="auto", help="Profile to build cert budgets per size (default: auto)")
    s6.add_argument("--suggestions", type=str, default=None, help="Optional suggestions.json to apply in full bench")
    s6.add_argument("--export-csv", type=str, default=None, help="Directory to export full-bench CSV tables")
    s6.add_argument("--plot", type=str, default=None, help="Directory to write simple PNG plots (requires matplotlib)")
    s6.add_argument("--export-parquet", type=str, default=None, help="Directory to export full-bench results as Parquet (requires pyarrow)")
    s6.add_argument("--p99-cap", type=float, default=None, help="Optional p99 cap (seconds) to enforce in full bench")
    s6.add_argument("--p99-mode", type=str, choices=["report","enforce"], default="report")
    # run-quick (convex-form instance) with dry-run
    s3 = sub.add_parser("run-quick", help="Run a quick convex-form bench or preview config with --dry-run")
    s3.add_argument("--n", type=int, default=4000)
    s3.add_argument("--repeats", type=int, default=1)
    s3.add_argument("--profile", type=str, default="auto")
    s3.add_argument("--dump-ledger", type=str, default="ledger_convex.json")
    s3.add_argument("--workers", type=int, default=None)
    s3.add_argument("--proc-workers", type=int, default=0)
    s3.add_argument("--proc-workers-monotone", type=int, default=0)
    s3.add_argument("--auto-apply-suggestions-from-ledger", type=str, default=None)
    s3.add_argument("--suggestions", type=str, default=None, help="Path to persisted suggestions.json (from tune persist)")
    s3.add_argument("--p99-cap", type=float, default=None)
    s3.add_argument("--p99-mode", type=str, choices=["report","enforce"], default="report")
    s3.add_argument("--dry-run", action="store_true")
    # run-quick-monotone with dry-run
    s4 = sub.add_parser("run-quick-monotone", help="Run a quick monotone bench or preview config with --dry-run")
    s4.add_argument("--n", type=int, default=3000)
    s4.add_argument("--repeats", type=int, default=1)
    s4.add_argument("--profile", type=str, default="auto")
    s4.add_argument("--dump-ledger", type=str, default="ledger_mono.json")
    s4.add_argument("--workers", type=int, default=None)
    s4.add_argument("--proc-workers-monotone", type=int, default=0)
    s4.add_argument("--auto-apply-suggestions-from-ledger", type=str, default=None)
    s4.add_argument("--suggestions", type=str, default=None, help="Path to persisted suggestions.json (from tune persist)")
    s4.add_argument("--prefer-monotone", action="store_true", help="Prefer monotone certification over Monge when available")
    s4.add_argument("--force-monotone", action="store_true", help="Force monotone path (skip Monge/convex certs)")
    s4.add_argument("--p99-cap", type=float, default=None)
    s4.add_argument("--p99-mode", type=str, choices=["report","enforce"], default="report")
    s4.add_argument("--dry-run", action="store_true")
    # license management
    s5 = sub.add_parser("license", help="Manage license (activate|status|deactivate)")
    s5.add_argument("action", choices=["activate", "status", "deactivate"], help="Action to perform")
    s5.add_argument("--key", help="License key for activation (CAMELEON-PRO-YYYYMMDD-NAME)")
    s7 = sub.add_parser("tune", help="Persist or apply self-tuning suggestions from one or more ledgers")
    s7.add_argument("action", choices=["persist", "apply"], help="persist suggestions to JSON or print a merged budget")
    s7.add_argument("--ledgers", nargs="+", help="Input ledger JSON paths", required=True)
    s7.add_argument("--base-profile", type=str, default="balanced")
    s7.add_argument("--out", type=str, default="suggestions.json")
    s9 = sub.add_parser("plot-ledgers", help="Plot longitudinal metrics across multiple ledgers")
    s9.add_argument("--ledgers", nargs="+", required=True, help="Ledger JSON files in chronological order")
    s9.add_argument("--out", type=str, required=True, help="Directory to write PNG plots")
    s9.add_argument("--export-csv", type=str, default=None, help="Directory to export a longitudinal CSV table")
    s8 = sub.add_parser("package", help="Build and/or publish wheels to PyPI")
    s8.add_argument("action", choices=["build", "publish"], help="Build wheels/sdist or publish dist/* via twine")
    s8.add_argument("--repository", type=str, default=None, help="Twine repository name (per .pypirc) e.g., pypi or testpypi")
    s8.add_argument("--repository-url", type=str, default=None, help="Override repository URL (e.g., https://upload.pypi.org/legacy/)")
    s8.add_argument("--skip-existing", action="store_true", help="Skip existing files on upload")
    s8.add_argument("--sign", action="store_true", help="GPG sign distributions")
    s8.add_argument("--identity", type=str, default=None, help="GPG identity to use when signing")
    s10 = sub.add_parser("evidence-pack", help="Create a signed evidence ZIP with ledger, appendix, CSV/Parquet, plots, and SBOM")
    s11 = sub.add_parser("verify", help="Verify an evidence ZIP or ledger against a public key")
    s11.add_argument("path", help="Path to evidence.zip or ledger.json")
    s11.add_argument("--pubkey", type=str, default=None, help="Base64 public key (falls back to CAMELEON_PUBKEY_B64)")
    s10.add_argument("ledger", help="Path to ledger.json")
    s10.add_argument("--out", type=str, default="evidence.zip")
    s10.add_argument("--tmpdir", type=str, default=None)
    # Curate evidence packs for large-N sizes
    s12 = sub.add_parser("curate-evidence", help="Run curated large-N benches, dump ledgers, and build evidence ZIPs")
    s12.add_argument("--out-ledgers", type=str, default="curated_ledgers", help="Directory to write curated ledgers")
    s12.add_argument("--out-evidence", type=str, default="evidence_packs", help="Directory to write evidence ZIPs")
    s12.add_argument("--profile", type=str, default="auto", help="Profile for cert budgets (default: auto)")
    s12.add_argument("--repeats", type=int, default=1)
    # run: vertical changepoint flow over CSV/Parquet with audit bundle
    s13 = sub.add_parser("run", help="Run exact changepoint over CSV/Parquet and optionally emit an audit bundle")
    s13.add_argument("--input", type=str, required=True, help="Input CSV/Parquet path")
    s13.add_argument("--column", type=str, default="y", help="Column name to use (CSV header or Parquet column)")
    s13.add_argument("--penalty", type=float, default=10.0, help="Per-segment penalty")
    s13.add_argument("--profile", type=str, default="auto", help="Budget profile (default: auto)")
    s13.add_argument("--p99-limit", type=float, default=None, help="Enforce p99 latency cap (seconds); exactness preserved via fallback")
    s13.add_argument("--audit", type=str, default=None, help="Directory to write audit bundle (ledger, appendix, histograms, env, checksums)")
    s13.add_argument("--dump-ledger", type=str, default=None, help="Optional path to also write ledger.json alongside run")
    # demo-changepoint: synthetic demo with report out/
    s14 = sub.add_parser("demo-changepoint", help="Run a synthetic changepoint demo and write a small report directory")
    s14.add_argument("--out", type=str, default="out_demo", help="Output directory for demo artifacts")
    s14.add_argument("--n", type=int, default=4000, help="Demo size")
    # doctor: environment diagnostics
    s15 = sub.add_parser("doctor", help="Print environment diagnostics for support")
    s15.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()
    # Suppress noisy Numba warnings by default; enable with --verbose
    if not getattr(args, 'verbose', False):
        try:
            import warnings as _warnings
            _warnings.filterwarnings("ignore", module="numba.*")
            _warnings.filterwarnings("ignore", module="llvmlite.*")
        except Exception:
            pass
    # License banner (stderr, non-intrusive for JSON output). Set CAMELEON_SILENT_BANNER=1 to suppress.
    try:
        from .licensing import license_status
        if not bool(int(os.environ.get("CAMELEON_SILENT_BANNER", "0"))):
            st = license_status()
            tier = st.get("tier", "COMMUNITY")
            valid = st.get("valid", False)
            msg = f"[CAMELEON-DP {tier}{' (valid)' if valid else ''}]"
            print(msg, file=sys.stderr)
    except Exception:
        pass
    if args.cmd == "summarize":
        summary = summarize_records_file(args.path)
        # Add a compact human-readable section highlighting budgets and guards
        highlight = {}
        bh = summary.get("budget_hist", {})
        # Focus on common knobs
        for k in [
            "convex_max_j_checks",
            "samples",
            "interval_samples",
            "guard_grid_i",
            "guard_grid_j",
            "tiled_max_checks",
            "grid",
            "max_pilots",
            "refine_grid",
        ]:
            if k in bh and isinstance(bh[k], dict) and bh[k]:
                # Show top 3 most frequent values
                items = sorted(bh[k].items(), key=lambda kv: (-kv[1], kv[0]))[:3]
                highlight[k] = {v: c for v, c in items}
        guards_total = summary.get("guard_stats_total", {})
        # Per-template summary highlights (counts and top budgets per template)
        by_template = summary.get("by_template", {})
        tpl_highlights = {}
        for tpl_name, tpl in by_template.items():
            tpl_entry = {"count": tpl.get("count", 0), "w_calls": tpl.get("w_calls", 0)}
            bht = tpl.get("budget_hist", {})
            tops = {}
            for k, hist in bht.items():
                items = sorted(hist.items(), key=lambda kv: (-kv[1], kv[0]))[:2]
                tops[k] = {v: c for v, c in items}
            if tops:
                tpl_entry["budget_top_values"] = tops
            highlight.setdefault("templates", {})[tpl_name] = tpl_entry
        out_highlight = {
            "budget_top_values": {k: v for k, v in highlight.items() if k != "templates"},
            "guard_stats_total": guards_total,
            "by_template": highlight.get("templates", {}),
        }
        try:
            from .licensing import license_status as _ls
            out_highlight["license"] = _ls()
        except Exception:
            pass
        if getattr(args, 'export_csv', None):
            import os, csv
            os.makedirs(args.export_csv, exist_ok=True)
            # budget_hist CSV
            with open(os.path.join(args.export_csv, 'budget_hist.csv'), 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(["key", "value", "count"])
                for k, hist in (summary.get("budget_hist", {}) or {}).items():
                    for v, c in hist.items():
                        w.writerow([k, v, c])
            # by_cert CSV
            with open(os.path.join(args.export_csv, 'by_cert.csv'), 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(["cert", "count", "runtime_sec", "w_calls"])
                for cert, d in (summary.get("by_cert", {}) or {}).items():
                    w.writerow([cert, d.get("count", 0), d.get("runtime_sec", 0.0), d.get("w_calls", 0)])
        if getattr(args, 'plot', None):
            try:
                import os
                import matplotlib.pyplot as plt  # type: ignore
                os.makedirs(args.plot, exist_ok=True)
                # Simple bar of cert counts
                bc = summary.get("by_cert", {})
                labels = list(bc.keys())
                vals = [bc[k].get("count", 0) for k in labels]
                plt.figure(figsize=(6,3))
                plt.bar(labels, vals)
                plt.title("Blocks by cert kind")
                plt.tight_layout()
                plt.savefig(os.path.join(args.plot, 'by_cert_counts.png'))
                plt.close()
            except Exception:
                pass
        if getattr(args, 'export_parquet', None):
            # Export full records and a couple of summary tables to Parquet
            try:
                os.makedirs(args.export_parquet, exist_ok=True)
                from .ledger import load_records_file
                recs = load_records_file(args.path)
                try:
                    import pyarrow as pa  # type: ignore
                    import pyarrow.parquet as pq  # type: ignore
                    try:
                        import pyarrow.dataset as ds  # type: ignore
                    except Exception:
                        ds = None  # type: ignore
                except Exception:
                    import sys
                    print("pyarrow not installed; cannot export Parquet", file=sys.stderr)
                else:
                    # Records parquet
                    cols = {
                        "block_id": [], "j_lo": [], "j_hi": [], "i_lo": [], "i_hi": [],
                        "cert": [], "template": [], "eps": [], "runtime_sec": [], "depth": [], "orientation": []
                    }
                    # Flatten a few detail fields when present
                    extra_keys = set()
                    for r in recs:
                        cols["block_id"].append(r.block_id)
                        cols["j_lo"].append(r.j_lo); cols["j_hi"].append(r.j_hi)
                        cols["i_lo"].append(r.i_lo); cols["i_hi"].append(r.i_hi)
                        cols["cert"].append(r.cert.kind); cols["template"].append(r.cert.template); cols["eps"].append(r.cert.eps)
                        cols["runtime_sec"].append(float(r.runtime_sec)); cols["depth"].append(r.depth); cols["orientation"].append(r.orientation)
                        if isinstance(r.cert.details, dict):
                            for k, v in r.cert.details.items():
                                key = f"detail_{k}"
                                extra_keys.add(key)
                    for k in extra_keys:
                        cols.setdefault(k, [])
                    for r in recs:
                        if isinstance(r.cert.details, dict):
                            d = r.cert.details
                        else:
                            d = {}
                        for k in extra_keys:
                            kk = k.replace("detail_", "")
                            val = d.get(kk)
                            cols[k].append(val if (isinstance(val, (int, float, str)) or val is None) else str(val))
                    table = pa.table(cols)
                    # Flat file for simple consumers
                    pq.write_table(table, os.path.join(args.export_parquet, 'records.parquet'))
                    # Partitioned dataset by cert/template for scalable ETL
                    try:
                        out_ds = os.path.join(args.export_parquet, 'records_by_partition')
                        os.makedirs(out_ds, exist_ok=True)
                        if hasattr(pq, 'write_to_dataset'):
                            pq.write_to_dataset(table, root_path=out_ds, partition_cols=["cert", "template"])  # type: ignore
                        elif ds is not None and hasattr(ds, 'write_dataset'):
                            ds.write_dataset(table, base_dir=out_ds, format="parquet", partitioning=["cert", "template"])  # type: ignore
                    except Exception:
                        # Best-effort; continue even if partitioned export fails
                        pass
                    # by_cert parquet
                    bc = summary.get("by_cert", {}) or {}
                    rows = [{"cert": k, "count": v.get("count", 0), "runtime_sec": v.get("runtime_sec", 0.0), "w_calls": v.get("w_calls", 0)} for k, v in bc.items()]
                    if rows:
                        t2 = pa.Table.from_pylist(rows)
                        pq.write_table(t2, os.path.join(args.export_parquet, 'by_cert.parquet'))
            except Exception:
                pass
        if getattr(args, 'verify_signature', False):
            try:
                import os as _os
                from .ledger import verify_ledger_signature
                raw = json.load(open(args.path, 'r', encoding='utf-8'))
                pk_b64 = _os.environ.get('CAMELEON_PUBKEY_B64')
                verified = bool(pk_b64 and verify_ledger_signature(raw, pk_b64))
                print(json.dumps({"verified": verified}, indent=2))
            except Exception:
                print(json.dumps({"verified": False}, indent=2))
            return
        if getattr(args, 'insights', False):
            # Heuristic suggestions based on summary
            suggestions = []
            bh = summary.get("budget_hist", {})
            guards = summary.get("guard_stats_total", {})
            by_cert = summary.get("by_cert", {})
            if (by_cert.get("MONOTONE", {}).get("count", 0) > 0) and (by_cert.get("MONGE", {}).get("count", 0) == 0):
                suggestions.append("Prefer monotone: set profile=monotone_careful or increase monotone_small_I to skip D&C on small blocks.")
            if int(guards.get("sample_checks", 0)) > 0 and not bh.get("tiled_max_checks"):
                suggestions.append("Cap Monge tiled checks: set monge_tiled_max_checks=8 to bound guard overhead.")
            if by_cert.get("CONVEX", {}).get("count", 0) > 0 and not bh.get("convex_max_j_checks"):
                suggestions.append("Record convex j-check cap: ensure convex_max_j_checks is set (e.g., 8).")
            print(json.dumps({"highlight": out_highlight, "insights": suggestions}, indent=2))
        else:
            if getattr(args, 'highlights_only', False):
                print(json.dumps({"highlight": out_highlight}, indent=2))
            else:
                out = {"summary": summary, "highlight": out_highlight}
                print(json.dumps(out, indent=2))
    elif args.cmd == "suggest-thresholds":
        recs = load_records_file(args.path)
        # Compute median I-length per cert kind
        from statistics import median
        by_kind: dict[str, list[int]] = {}
        for r in recs:
            L = int(r.i_hi - r.i_lo + 1)
            by_kind.setdefault(r.cert.kind, []).append(L)
        meds = {k: (int(median(v)) if v else 0) for k, v in by_kind.items()}
        def suggest_min_I(m: int, fallback: int) -> int:
            if m <= 0:
                return fallback
            return max(fallback, int(m * 2))
        sugg = {
            "proc_convex_min_blocks": 2,
            "proc_monge_min_blocks": 2,
            "proc_monotone_min_blocks": 2,
            "proc_convex_min_I": suggest_min_I(meds.get("CONVEX", 0), 8192),
            "proc_monge_min_I": suggest_min_I(meds.get("MONGE", 0), 8192),
            "proc_monotone_min_I": suggest_min_I(meds.get("MONOTONE", 0), 8192),
            "_medians": meds,
        }
        print(json.dumps({"suggested": sugg}, indent=2))
    elif args.cmd == "run-quick":
        # Compute budget preview
        budget = recommended_cert_budget(args.n, profile=args.profile)
        if args.auto_apply_suggestions_from_ledger and is_pro_enabled():
            try:
                from .bench import suggested_budget_from_ledger as _sugg
                import os as _os
                if _os.path.exists(args.auto_apply_suggestions_from_ledger):
                    budget = _sugg(args.auto_apply_suggestions_from_ledger, base_profile=args.profile)
            except Exception:
                pass
        if args.dry_run:
            print(json.dumps({
                "n": args.n,
                "repeats": args.repeats,
                "profile": args.profile,
                "dump_ledger": args.dump_ledger,
                "workers": args.workers,
                "proc_workers": args.proc_workers,
                "proc_workers_monotone": args.proc_workers_monotone,
                "budget": budget,
                "suggestions": args.suggestions,
                "p99_cap": args.p99_cap,
                "p99_mode": args.p99_mode,
            }, indent=2))
            return
        # Merge p99 guard/enforce into budget and pass through
        _b = dict(budget or {})
        if args.p99_cap is not None:
            try:
                _b["p99_guard_enabled"] = True
                _b["p99_guard_cap_sec"] = float(args.p99_cap)
                if args.p99_mode == "enforce":
                    _b["p99_enforce_sec"] = float(args.p99_cap)
            except Exception:
                pass
        # Warn prominently when enforcement is requested
        try:
            if args.p99_cap is not None and args.p99_mode == "enforce":
                print("[p99 enforce] Remaining blocks may switch to baseline during the run; exactness is preserved but specialist routing and speedups may change.", file=sys.stderr)
        except Exception:
            pass
        res = run_quick_bench(
            n=args.n,
            repeats=args.repeats,
            dump_ledger_path=args.dump_ledger,
            workers=args.workers,
            proc_workers=args.proc_workers,
            proc_workers_monotone=args.proc_workers_monotone,
            cert_budget=_b,
            profile=args.profile,
            auto_apply_suggestions_from_ledger=args.auto_apply_suggestions_from_ledger,
            suggestions_path=args.suggestions,
        )
        # Always surface p99 info and why-settings in CLI output
        out = dict(res)
        print(json.dumps(out, indent=2))
    elif args.cmd == "run-quick-monotone":
        budget = recommended_cert_budget(args.n, profile=args.profile)
        if args.auto_apply_suggestions_from_ledger and is_pro_enabled():
            try:
                from .bench import suggested_budget_from_ledger as _sugg
                import os as _os
                if _os.path.exists(args.auto_apply_suggestions_from_ledger):
                    budget = _sugg(args.auto_apply_suggestions_from_ledger, base_profile=args.profile)
            except Exception:
                pass
        if args.dry_run:
            print(json.dumps({
                "n": args.n,
                "repeats": args.repeats,
                "profile": args.profile,
                "dump_ledger": args.dump_ledger,
                "workers": args.workers,
                "proc_workers_monotone": args.proc_workers_monotone,
                "budget": budget,
                "prefer_monotone": bool(args.prefer_monotone),
                "force_monotone": bool(args.force_monotone),
                "suggestions": args.suggestions,
                "p99_cap": args.p99_cap,
                "p99_mode": args.p99_mode,
            }, indent=2))
            return
        _bm = dict(budget or {})
        if args.p99_cap is not None:
            try:
                _bm["p99_guard_enabled"] = True
                _bm["p99_guard_cap_sec"] = float(args.p99_cap)
                if args.p99_mode == "enforce":
                    _bm["p99_enforce_sec"] = float(args.p99_cap)
            except Exception:
                pass
        try:
            if args.p99_cap is not None and args.p99_mode == "enforce":
                print("[p99 enforce] Remaining blocks may switch to baseline during the run; exactness is preserved but specialist routing and speedups may change.", file=sys.stderr)
        except Exception:
            pass
        res = run_quick_bench_monotone(
            n=args.n,
            repeats=args.repeats,
            dump_ledger_path=args.dump_ledger,
            workers=args.workers,
            proc_workers_monotone=args.proc_workers_monotone,
            cert_budget=_bm,
            profile=args.profile,
            prefer_monotone=bool(args.prefer_monotone),
            force_monotone=bool(args.force_monotone),
            auto_apply_suggestions_from_ledger=args.auto_apply_suggestions_from_ledger,
            suggestions_path=args.suggestions,
        )
        out = dict(res)
        print(json.dumps(out, indent=2))
    # p99 enforce on quick benches via args to run-full; for quick runs, honor p99_guard in budget
    elif args.cmd == "run-full":
        from .bench import run_full_bench
        try:
            if args.p99_cap is not None and args.p99_mode == "enforce":
                print("[p99 enforce] Full bench will report p99_mode=enforce; individual runs may switch to baseline; exactness preserved.", file=sys.stderr)
        except Exception:
            pass
        res = run_full_bench(repeats=args.repeats, large_n=bool(args.large_n), p99_cap=args.p99_cap,
                             dump_dir=args.dump_dir, cpu_affinity_count=args.cpu_affinity,
                             profile=args.profile, suggestions_path=args.suggestions, p99_mode=args.p99_mode)
        # Optional exports/plots
        if getattr(args, 'export_csv', None):
            try:
                import os, csv
                os.makedirs(args.export_csv, exist_ok=True)
                # Flatten results into rows
                rows = []
                for dataset, entries in (res or {}).items():
                    for e in entries:
                        bq = e.get('quantiles', {}).get('baseline_quantiles', {}) if isinstance(e.get('quantiles'), dict) else {}
                        cq = e.get('quantiles', {}).get('cameleon_quantiles', {}) if isinstance(e.get('quantiles'), dict) else {}
                        rows.append({
                            'dataset': dataset,
                            'n': e.get('n'),
                            'baseline_sec': e.get('baseline_sec'),
                            'cameleon_sec': e.get('cameleon_sec'),
                            'speedup_x': e.get('speedup_x'),
                            'exact': e.get('exact'),
                            'cert_sample': e.get('cert'),
                            'boundary_count': e.get('boundary_count'),
                            'C_hat': e.get('C_hat'),
                            'baseline_p50': bq.get('p50'),
                            'baseline_p95': bq.get('p95'),
                            'baseline_p99': bq.get('p99'),
                            'cameleon_p50': cq.get('p50'),
                            'cameleon_p95': cq.get('p95'),
                            'cameleon_p99': cq.get('p99'),
                            'p99_cap': e.get('p99_cap'),
                            'fallback_to_baseline': e.get('fallback_to_baseline'),
                        })
                # Write CSV
                with open(os.path.join(args.export_csv, 'full_results.csv'), 'w', newline='', encoding='utf-8') as f:
                    if rows:
                        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                        w.writeheader(); w.writerows(rows)
                    else:
                        f.write('')
                # Per-template aggregates if ledger dumps present
                try:
                    from .ledger import load_records_file, summarize_records
                    tpl_rows = []
                    # Heuristically locate dumped ledgers in dump_dir if provided
                    if getattr(args, 'dump_dir', None) and os.path.isdir(args.dump_dir):
                        for name in os.listdir(args.dump_dir):
                            if name.endswith('.json') and not name.endswith('_appendix.json'):
                                path = os.path.join(args.dump_dir, name)
                                recs = load_records_file(path)
                                summ = summarize_records(recs)
                                for tpl, d in (summ.get('by_template', {}) or {}).items():
                                    tpl_rows.append({
                                        'ledger': name,
                                        'template': tpl,
                                        'count': d.get('count', 0),
                                        'runtime_sec': d.get('runtime_sec', 0.0),
                                        'w_calls': d.get('w_calls', 0),
                                    })
                    if tpl_rows:
                        with open(os.path.join(args.export_csv, 'by_template.csv'), 'w', newline='', encoding='utf-8') as f2:
                            w2 = csv.DictWriter(f2, fieldnames=list(tpl_rows[0].keys()))
                            w2.writeheader(); w2.writerows(tpl_rows)
                except Exception:
                    pass
            except Exception:
                pass
        if getattr(args, 'export_parquet', None):
            try:
                import os
                import pyarrow as pa  # type: ignore
                import pyarrow.parquet as pq  # type: ignore
                os.makedirs(args.export_parquet, exist_ok=True)
                # Build a table similar to CSV rows
                cols = { 'dataset': [], 'n': [], 'baseline_sec': [], 'cameleon_sec': [], 'speedup_x': [], 'exact': [], 'cert_sample': [], 'boundary_count': [], 'C_hat': [], 'baseline_p50': [], 'baseline_p95': [], 'baseline_p99': [], 'cameleon_p50': [], 'cameleon_p95': [], 'cameleon_p99': [], 'p99_cap': [], 'fallback_to_baseline': [] }
                for dataset, entries in (res or {}).items():
                    for e in entries:
                        bq = e.get('quantiles', {}).get('baseline_quantiles', {}) if isinstance(e.get('quantiles'), dict) else {}
                        cq = e.get('quantiles', {}).get('cameleon_quantiles', {}) if isinstance(e.get('quantiles'), dict) else {}
                        cols['dataset'].append(dataset)
                        cols['n'].append(e.get('n'))
                        cols['baseline_sec'].append(e.get('baseline_sec'))
                        cols['cameleon_sec'].append(e.get('cameleon_sec'))
                        cols['speedup_x'].append(e.get('speedup_x'))
                        cols['exact'].append(bool(e.get('exact')))
                        cols['cert_sample'].append(e.get('cert'))
                        cols['boundary_count'].append(e.get('boundary_count'))
                        cols['C_hat'].append(e.get('C_hat'))
                        cols['baseline_p50'].append(bq.get('p50'))
                        cols['baseline_p95'].append(bq.get('p95'))
                        cols['baseline_p99'].append(bq.get('p99'))
                        cols['cameleon_p50'].append(cq.get('p50'))
                        cols['cameleon_p95'].append(cq.get('p95'))
                        cols['cameleon_p99'].append(cq.get('p99'))
                        cols['p99_cap'].append(e.get('p99_cap'))
                        cols['fallback_to_baseline'].append(bool(e.get('fallback_to_baseline')))
                table = pa.table(cols)
                pq.write_table(table, os.path.join(args.export_parquet, 'full_results.parquet'))
                # Partitioned dataset by dataset name
                try:
                    pq.write_to_dataset(table, root_path=os.path.join(args.export_parquet, 'by_dataset'), partition_cols=['dataset'])  # type: ignore
                except Exception:
                    pass
                # Optional by-template parquet from dumped ledgers
                try:
                    from .ledger import load_records_file, summarize_records
                    tpl_cols = { 'ledger': [], 'template': [], 'count': [], 'runtime_sec': [], 'w_calls': [] }
                    if getattr(args, 'dump_dir', None) and os.path.isdir(args.dump_dir):
                        for name in os.listdir(args.dump_dir):
                            if name.endswith('.json') and not name.endswith('_appendix.json'):
                                path = os.path.join(args.dump_dir, name)
                                recs = load_records_file(path)
                                summ = summarize_records(recs)
                                for tpl, d in (summ.get('by_template', {}) or {}).items():
                                    tpl_cols['ledger'].append(name)
                                    tpl_cols['template'].append(tpl)
                                    tpl_cols['count'].append(d.get('count', 0))
                                    tpl_cols['runtime_sec'].append(d.get('runtime_sec', 0.0))
                                    tpl_cols['w_calls'].append(d.get('w_calls', 0))
                    if tpl_cols['ledger']:
                        ttpl = pa.table(tpl_cols)
                        pq.write_table(ttpl, os.path.join(args.export_parquet, 'by_template.parquet'))
                except Exception:
                    pass
            except Exception:
                pass
        if getattr(args, 'plot', None):
            try:
                import os
                import matplotlib.pyplot as plt  # type: ignore
                os.makedirs(args.plot, exist_ok=True)
                # For each dataset, plot speedup vs n
                for dataset, entries in (res or {}).items():
                    xs = [e.get('n') for e in entries]
                    ys = [e.get('speedup_x') for e in entries]
                    plt.figure(figsize=(6,3))
                    plt.plot(xs, ys, marker='o')
                    plt.title(f"Speedup vs n ({dataset})")
                    plt.xlabel('n'); plt.ylabel('speedup_x')
                    plt.tight_layout()
                    plt.savefig(os.path.join(args.plot, f'speedup_{dataset}.png'))
                    plt.close()
            except Exception:
                pass
        print(json.dumps(res, indent=2))
    elif args.cmd == "license":
        if args.action == "status":
            print(json.dumps(license_status(), indent=2))
        elif args.action == "activate":
            if not args.key:
                print(json.dumps({"ok": False, "error": "missing_key"}, indent=2))
            else:
                print(json.dumps(activate_license(args.key), indent=2))
        elif args.action == "deactivate":
            print(json.dumps(deactivate_license(), indent=2))
    elif args.cmd == "tune":
        from .bench import persist_suggestions_from_ledgers, suggested_budget_from_ledgers
        if args.action == "persist":
            payload = persist_suggestions_from_ledgers(args.ledgers, args.out, base_profile=args.base_profile)
            print(json.dumps({"ok": True, "out": args.out, "payload": payload}, indent=2))
        else:
            budget = suggested_budget_from_ledgers(args.ledgers, base_profile=args.base_profile)
            print(json.dumps({"ok": True, "budget": budget}, indent=2))
    elif args.cmd == "package":
        import subprocess, glob
        if args.action == "build":
            try:
                res = subprocess.run([sys.executable, "-m", "build", "--sdist", "--wheel"], check=False, capture_output=True, text=True)
                ok = (res.returncode == 0)
                print(json.dumps({"ok": ok, "stdout": res.stdout, "stderr": res.stderr}, indent=2))
            except Exception as e:
                print(json.dumps({"ok": False, "error": str(e)}, indent=2))
    elif args.cmd == "plot-ledgers":
        # Longitudinal plots: total runtime, blocks by cert, runtime quantiles per run
        try:
            import os
            os.makedirs(args.out, exist_ok=True)
            import matplotlib.pyplot as plt  # type: ignore
            rows = []
            for idx, path in enumerate(args.ledgers):
                try:
                    s = summarize_records_file(path)
                except Exception:
                    continue
                by_cert = s.get('by_cert', {}) or {}
                q = s.get('runtime_quantiles', {}) or {}
                rows.append({
                    'run_idx': idx,
                    'path': path,
                    'total_blocks': s.get('total_blocks', 0),
                    'total_runtime_sec': s.get('total_runtime_sec', 0.0),
                    'baseline_p50': q.get('p50', 0.0),
                    'baseline_p95': q.get('p95', 0.0),
                    'baseline_p99': q.get('p99', 0.0),
                    'convex_blocks': (by_cert.get('CONVEX', {}) or {}).get('count', 0),
                    'monge_blocks': (by_cert.get('MONGE', {}) or {}).get('count', 0),
                    'monotone_blocks': (by_cert.get('MONOTONE', {}) or {}).get('count', 0),
                })
            # Plots
            if rows:
                xs = [r['run_idx'] for r in rows]
                # Total runtime
                plt.figure(figsize=(6,3))
                plt.plot(xs, [r['total_runtime_sec'] for r in rows], marker='o')
                plt.title('Total runtime by run index')
                plt.xlabel('run_idx'); plt.ylabel('total_runtime_sec')
                plt.tight_layout(); plt.savefig(os.path.join(args.out, 'total_runtime.png')); plt.close()
                # Blocks by cert
                plt.figure(figsize=(6,3))
                plt.plot(xs, [r['convex_blocks'] for r in rows], label='CONVEX')
                plt.plot(xs, [r['monge_blocks'] for r in rows], label='MONGE')
                plt.plot(xs, [r['monotone_blocks'] for r in rows], label='MONOTONE')
                plt.title('Blocks by cert over runs')
                plt.xlabel('run_idx'); plt.ylabel('blocks'); plt.legend()
                plt.tight_layout(); plt.savefig(os.path.join(args.out, 'blocks_by_cert.png')); plt.close()
                # Runtime quantiles
                plt.figure(figsize=(6,3))
                plt.plot(xs, [r['baseline_p50'] for r in rows], label='p50')
                plt.plot(xs, [r['baseline_p95'] for r in rows], label='p95')
                plt.plot(xs, [r['baseline_p99'] for r in rows], label='p99')
                plt.title('Runtime quantiles over runs')
                plt.xlabel('run_idx'); plt.ylabel('seconds'); plt.legend()
                plt.tight_layout(); plt.savefig(os.path.join(args.out, 'runtime_quantiles.png')); plt.close()
            if getattr(args, 'export_csv', None):
                try:
                    import csv
                    os.makedirs(args.export_csv, exist_ok=True)
                    with open(os.path.join(args.export_csv, 'longitudinal.csv'), 'w', newline='', encoding='utf-8') as f:
                        if rows:
                            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                            w.writeheader(); w.writerows(rows)
                        else:
                            f.write('')
                except Exception:
                    pass
            print(json.dumps({"ok": True, "runs": len(rows), "out": args.out}, indent=2))
        except Exception as e:
            print(json.dumps({"ok": False, "error": str(e)}, indent=2))
    elif args.cmd == "evidence-pack":
        # Build an evidence bundle ZIP for a single ledger
        try:
            import os, io, zipfile, shutil
            from .ledger import load_records_file, export_records_json, export_proof_appendix, verify_ledger_signature
            # Prepare working dir
            tmpdir = args.tmpdir or os.path.join(os.getcwd(), "_evidence_tmp")
            if os.path.isdir(tmpdir):
                shutil.rmtree(tmpdir)
            os.makedirs(tmpdir, exist_ok=True)
            # 1) Copy or (re)write ledger and appendix
            recs = load_records_file(args.ledger)
            ledger_copy = os.path.join(tmpdir, "ledger.json")
            export_records_json(recs, ledger_copy)
            appendix = os.path.join(tmpdir, "appendix.json")
            export_proof_appendix(recs, appendix)
            # 2) Summaries: CSV/plots/Parquet
            csv_dir = os.path.join(tmpdir, "csv"); os.makedirs(csv_dir, exist_ok=True)
            plot_dir = os.path.join(tmpdir, "plots"); os.makedirs(plot_dir, exist_ok=True)
            parquet_dir = os.path.join(tmpdir, "parquet"); os.makedirs(parquet_dir, exist_ok=True)
            # Reuse earlier summarize logic for CSV and plots
            # CSVs: budget_hist, by_cert, by_template (if present)
            summary = summarize_records_file(ledger_copy)
            try:
                import csv
                with open(os.path.join(csv_dir, 'budget_hist.csv'), 'w', newline='', encoding='utf-8') as f:
                    w = csv.writer(f); w.writerow(["key","value","count"])
                    for k, hist in (summary.get("budget_hist", {}) or {}).items():
                        for v, c in hist.items(): w.writerow([k, v, c])
                with open(os.path.join(csv_dir, 'by_cert.csv'), 'w', newline='', encoding='utf-8') as f:
                    w = csv.writer(f); w.writerow(["cert","count","runtime_sec","w_calls"])
                    for cert, d in (summary.get("by_cert", {}) or {}).items():
                        w.writerow([cert, d.get("count",0), d.get("runtime_sec",0.0), d.get("w_calls",0)])
                if summary.get("by_template"):
                    with open(os.path.join(csv_dir, 'by_template.csv'), 'w', newline='', encoding='utf-8') as f:
                        w = csv.writer(f); w.writerow(["template","count","runtime_sec","w_calls"])
                        for tpl, d in (summary.get("by_template", {}) or {}).items():
                            w.writerow([tpl, d.get("count",0), d.get("runtime_sec",0.0), d.get("w_calls",0)])
            except Exception:
                pass
            # Plots (simple): by_cert counts
            try:
                import matplotlib.pyplot as plt  # type: ignore
                bc = summary.get("by_cert", {})
                labels = list(bc.keys()); vals = [bc[k].get("count",0) for k in labels]
                plt.figure(figsize=(6,3)); plt.bar(labels, vals); plt.title("Blocks by cert kind"); plt.tight_layout()
                plt.savefig(os.path.join(plot_dir, 'by_cert_counts.png')); plt.close()
            except Exception:
                pass
            # Parquet export (records + by_cert)
            try:
                import pyarrow as pa  # type: ignore
                import pyarrow.parquet as pq  # type: ignore
                cols = {"block_id":[],"j_lo":[],"j_hi":[],"i_lo":[],"i_hi":[],"cert":[],"template":[],"eps":[],"runtime_sec":[],"depth":[],"orientation":[]}
                extra=set()
                for r in recs:
                    cols["block_id"].append(r.block_id)
                    cols["j_lo"].append(r.j_lo); cols["j_hi"].append(r.j_hi)
                    cols["i_lo"].append(r.i_lo); cols["i_hi"].append(r.i_hi)
                    cols["cert"].append(r.cert.kind); cols["template"].append(r.cert.template); cols["eps"].append(r.cert.eps)
                    cols["runtime_sec"].append(float(r.runtime_sec)); cols["depth"].append(r.depth); cols["orientation"].append(r.orientation)
                    if isinstance(r.cert.details, dict):
                        for k in r.cert.details.keys(): extra.add("detail_"+k)
                for k in extra: cols.setdefault(k, [])
                for r in recs:
                    d = r.cert.details if isinstance(r.cert.details, dict) else {}
                    for k in extra:
                        kk=k.replace("detail_",""); v=d.get(kk)
                        cols[k].append(v if isinstance(v,(int,float,str)) or v is None else str(v))
                pq.write_table(pa.table(cols), os.path.join(parquet_dir,'records.parquet'))
                bc = summary.get("by_cert", {}) or {}
                rows = [{"cert":k, "count":v.get("count",0), "runtime_sec":v.get("runtime_sec",0.0), "w_calls":v.get("w_calls",0)} for k,v in bc.items()]
                if rows:
                    pq.write_table(pa.Table.from_pylist(rows), os.path.join(parquet_dir,'by_cert.parquet'))
            except Exception:
                pass
            # SBOM
            try:
                from tools import sbom_generate as _sbom
                _sbom.main.__wrapped__  # type: ignore
            except Exception:
                pass
            try:
                import subprocess
                sbom_path = os.path.join(tmpdir, 'sbom.json')
                subprocess.run([sys.executable, "-m", "tools.sbom_generate", "--out", sbom_path], check=False)
            except Exception:
                pass
            # Verify signature if pubkey is set
            verified = False
            try:
                import json as _json
                pk = os.environ.get('CAMELEON_PUBKEY_B64')
                raw = _json.load(open(ledger_copy,'r',encoding='utf-8'))
                verified = bool(pk and verify_ledger_signature(raw, pk))
            except Exception:
                pass
            # Zip it
            with zipfile.ZipFile(args.out, 'w', compression=zipfile.ZIP_DEFLATED) as z:
                for root, _, files in os.walk(tmpdir):
                    for f in files:
                        p = os.path.join(root,f)
                        arc = os.path.relpath(p, tmpdir)
                        z.write(p, arcname=arc)
            print(json.dumps({"ok": True, "out": args.out, "verified": bool(verified)}, indent=2))
        except Exception as e:
            print(json.dumps({"ok": False, "error": str(e)}, indent=2))
    elif args.cmd == "verify":
        try:
            import os, json as _json, zipfile
            from .ledger import verify_ledger_signature
            pk = args.pubkey or os.environ.get('CAMELEON_PUBKEY_B64')
            if not pk:
                print(json.dumps({"ok": False, "error": "missing_pubkey"}, indent=2)); return
            if args.path.endswith('.zip'):
                with zipfile.ZipFile(args.path, 'r') as z:
                    with z.open('ledger.json') as f:
                        raw = _json.load(f)
                verified = verify_ledger_signature(raw, pk)
                print(json.dumps({"ok": True, "verified": bool(verified)}, indent=2))
            else:
                if os.path.isdir(args.path):
                    bundle = args.path
                    man_path = os.path.join(bundle, 'manifest.json')
                    sig_path = os.path.join(bundle, 'manifest.json.sig')
                    led_path = os.path.join(bundle, 'ledger.json')
                    verified = False
                    if os.path.exists(man_path) and os.path.exists(sig_path):
                        try:
                            man = _json.load(open(man_path, 'r', encoding='utf-8'))
                            sig_hex = open(sig_path, 'r', encoding='utf-8').read().strip()
                            payload = {"manifest": man, "signing": {"sig_ed25519_hex": sig_hex}}
                            verified = verify_ledger_signature(payload, pk)
                        except Exception:
                            verified = False
                    if not verified and os.path.exists(led_path):
                        try:
                            raw = _json.load(open(led_path, 'r', encoding='utf-8'))
                            verified = verify_ledger_signature(raw, pk)
                        except Exception:
                            verified = False
                    checksums_ok = True
                    cs_path = os.path.join(bundle, 'checksum.txt')
                    if os.path.exists(cs_path):
                        try:
                            import hashlib as _hashlib
                            for line in open(cs_path, 'r', encoding='utf-8'):
                                line = line.strip()
                                if not line:
                                    continue
                                parts = line.split()
                                if len(parts) < 2:
                                    continue
                                h = parts[0]
                                name = parts[-1]
                                p = os.path.join(bundle, name)
                                if os.path.exists(p):
                                    hh = _hashlib.sha256(open(p, 'rb').read()).hexdigest()
                                    if hh != h:
                                        checksums_ok = False
                                        break
                        except Exception:
                            checksums_ok = False
                    print(json.dumps({"ok": True, "verified": bool(verified), "checksums_ok": bool(checksums_ok)}, indent=2))
                else:
                    raw = _json.load(open(args.path, 'r', encoding='utf-8'))
                    verified = verify_ledger_signature(raw, pk)
                    print(json.dumps({"ok": True, "verified": bool(verified)}, indent=2))
        except Exception as e:
            print(json.dumps({"ok": False, "error": str(e)}, indent=2))
        else:
            # twine upload dist/* with optional repo args; avoid globs by expanding
            try:
                files = []
                try:
                    import os as _os
                    d = _os.path.join(_os.getcwd(), "dist")
                    if _os.path.isdir(d):
                        for name in _os.listdir(d):
                            if name.endswith((".whl", ".tar.gz")):
                                files.append(_os.path.join(d, name))
                except Exception:
                    pass
                if not files:
                    print(json.dumps({"ok": False, "error": "no_files_in_dist"}, indent=2))
                    return
                cmd = [sys.executable, "-m", "twine", "upload", "--non-interactive"]
                if args.skip_existing:
                    cmd.append("--skip-existing")
                if args.sign:
                    cmd.append("--sign")
                    if args.identity:
                        cmd += ["--identity", args.identity]
                if args.repository_url:
                    cmd += ["--repository-url", args.repository_url]
                elif args.repository:
                    cmd += ["--repository", args.repository]
                cmd += files
                res = subprocess.run(cmd, check=False, capture_output=True, text=True)
                ok = (res.returncode == 0)
                print(json.dumps({"ok": ok, "stdout": res.stdout, "stderr": res.stderr, "files": files}, indent=2))
            except Exception as e:
                print(json.dumps({"ok": False, "error": str(e)}, indent=2))
    elif args.cmd == "curate-evidence":
        # Run large-N full bench with ledger dumps, then package each ledger into an evidence ZIP
        try:
            import os, json as _json
            from .bench import run_full_bench
            os.makedirs(args.out_ledgers, exist_ok=True)
            res = run_full_bench(repeats=args.repeats, large_n=True, p99_cap=None, dump_dir=args.out_ledgers, profile=args.profile)
            # Build evidence zips
            os.makedirs(args.out_evidence, exist_ok=True)
            from .ledger import load_records_file, export_records_json, export_proof_appendix
            packed = []
            for name in os.listdir(args.out_ledgers):
                if not (name.endswith('.json') and not name.endswith('_appendix.json')):
                    continue
                ledger_path = os.path.join(args.out_ledgers, name)
                appendix_path = ledger_path.replace('.json', '_appendix.json')
                try:
                    # Ensure ledger/appendix are re-written with current manifest
                    recs = load_records_file(ledger_path)
                    export_records_json(recs, ledger_path)
                    export_proof_appendix(recs, appendix_path)
                except Exception:
                    pass
                # Write evidence zip alongside
                zip_path = os.path.join(args.out_evidence, name.replace('.json', '.zip'))
                try:
                    import zipfile
                    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
                        z.write(ledger_path, arcname='ledger.json')
                        if os.path.exists(appendix_path):
                            z.write(appendix_path, arcname='appendix.json')
                    packed.append(zip_path)
                except Exception:
                    continue
            # Write a small CSV summary focusing on SMAWK coverage and w-calls
            try:
                import csv
                summary_csv = os.path.join(args.out_evidence, 'curated_summary.csv')
                with open(summary_csv, 'w', newline='', encoding='utf-8') as f:
                    w = csv.writer(f)
                    w.writerow(['ledger','dataset','n','convex_blocks','monge_blocks','monotone_blocks','total_blocks','total_w_calls'])
                    for name in os.listdir(args.out_ledgers):
                        if not (name.endswith('.json') and not name.endswith('_appendix.json')):
                            continue
                        ledger_path = os.path.join(args.out_ledgers, name)
                        try:
                            s = summarize_records_file(ledger_path)
                        except Exception:
                            continue
                        bc = s.get('by_cert', {}) or {}
                        total = int(s.get('total_blocks', 0))
                        twc = int(s.get('total_w_calls', 0))
                        # Parse dataset and n from filename pattern <dataset>_<n>.json
                        base = os.path.splitext(os.path.basename(ledger_path))[0]
                        parts = base.split('_')
                        dataset = parts[0] if parts else ''
                        try:
                            nn = int(parts[-1]) if parts and parts[-1].isdigit() else None
                        except Exception:
                            nn = None
                        w.writerow([
                            name,
                            dataset,
                            nn,
                            (bc.get('CONVEX', {}) or {}).get('count', 0),
                            (bc.get('MONGE', {}) or {}).get('count', 0),
                            (bc.get('MONOTONE', {}) or {}).get('count', 0),
                            total,
                            twc,
                        ])
            except Exception:
                pass
            print(_json.dumps({"ok": True, "ledgers": args.out_ledgers, "evidence": args.out_evidence, "packed": len(packed)}, indent=2))
        except Exception as e:
            print(json.dumps({"ok": False, "error": str(e)}, indent=2))
    elif args.cmd == "run":
        # Load series from CSV/Parquet
        import os as _os
        import math as _math
        path = args.input
        col = args.column
        if not _os.path.exists(path):
            print(json.dumps({"ok": False, "error": "input_not_found", "path": path}, indent=2)); return
        series: list[float] = []
        try:
            if path.lower().endswith('.csv') or path.lower().endswith('.tsv'):
                import csv as _csv
                delim = ',' if path.lower().endswith('.csv') else '\t'
                with open(path, 'r', encoding='utf-8') as f:
                    rd = _csv.DictReader(f, delimiter=delim)
                    # Fall back to first column if not present
                    field = col if (rd.fieldnames and col in rd.fieldnames) else (rd.fieldnames[0] if rd.fieldnames else None)
                    if field is None:
                        raise ValueError('no_columns')
                    for row in rd:
                        try:
                            v = float(row[field])
                            if _math.isfinite(v):
                                series.append(v)
                        except Exception:
                            continue
            elif path.lower().endswith('.parquet'):
                try:
                    import pyarrow.parquet as pq  # type: ignore
                    t = pq.read_table(path)
                    if col in t.column_names:
                        arr = t.column(col).to_pylist()
                    else:
                        arr = t.to_pydict()[t.column_names[0]]
                    for v in arr:
                        try:
                            vv = float(v)
                            if _math.isfinite(vv):
                                series.append(vv)
                        except Exception:
                            continue
                except Exception:
                    print(json.dumps({"ok": False, "error": "parquet_reader_missing", "hint": "pip install pyarrow"}, indent=2)); return
            else:
                print(json.dumps({"ok": False, "error": "unsupported_input", "hint": "use .csv/.tsv or .parquet"}, indent=2)); return
        except Exception as e:
            print(json.dumps({"ok": False, "error": "load_failed", "detail": str(e)}, indent=2)); return
        n = len(series)
        if n <= 0:
            print(json.dumps({"ok": False, "error": "empty_series"}, indent=2)); return
        # Build SSE cost with per-segment penalty
        import numpy as _np
        S = _np.concatenate(([0.0], _np.cumsum(_np.array(series, dtype=float))))
        SS = _np.concatenate(([0.0], _np.cumsum(_np.array(series, dtype=float) ** 2)))
        penalty = float(args.penalty)
        def w(j, i):
            L = i - j
            if L <= 0:
                return float('inf')
            sum_x = S[i] - S[j]
            sum_x2 = SS[i] - SS[j]
            cost = sum_x2 - (sum_x * sum_x) / L + penalty
            return float(cost)
        # Build budget
        from .bench import _recommended_workers, _recommended_proc_workers  # type: ignore
        budget = recommended_cert_budget(n, profile=args.profile)
        # Apply p99 limit (enforce)
        if isinstance(args.p99_limit, (int, float)) and args.p99_limit is not None:
            try:
                budget["p99_guard_enabled"] = True
                budget["p99_guard_cap_sec"] = float(args.p99_limit)
                budget["p99_enforce_sec"] = float(args.p99_limit)
            except Exception:
                pass
        # Workers recommendations
        try:
            workers, _ = _recommended_workers(n)
            proc_workers, _ = _recommended_proc_workers(n)
        except Exception:
            workers = 1; proc_workers = 0
        # Run solver
        from .scheduler import cameleon_dp as _solve
        F0 = 0.0
        F, arg, recs, boundary_count = _solve(n, w, F0, hints={}, workers=workers, proc_workers=proc_workers, cert_budget=budget)
        # Extract segments by backtracking
        segs = []
        i = n
        while i > 0:
            j = int(arg[i])
            if j < 0 or j >= i:
                break
            segs.append({"start": j, "end": i, "len": i - j})
            i = j
        segs = list(reversed(segs))
        out = {"ok": True, "n": n, "segments": segs, "boundary_count": boundary_count}
        # Write ledger and audit when requested
        if args.dump_ledger or args.audit:
            from .ledger import export_records_json, export_proof_appendix, summarize_records
            if args.audit:
                _os.makedirs(args.audit, exist_ok=True)
                ledger_path = _os.path.join(args.audit, 'ledger.json')
            else:
                ledger_path = args.dump_ledger or 'ledger.json'
            export_records_json(recs, ledger_path)
            appendix_path = ledger_path.replace('ledger.json', 'appendix.json') if ledger_path.endswith('ledger.json') else ledger_path + '.appendix.json'
            export_proof_appendix(recs, appendix_path)
            # Histograms/quantiles and env summary
            try:
                import json as _json
                summ = summarize_records(recs)
                if args.audit:
                    with open(_os.path.join(args.audit, 'histograms.json'), 'w', encoding='utf-8') as f:
                        _json.dump({k: v for k, v in summ.items() if k in ("by_cert","budget_hist","guard_stats_total","runtime_quantiles")}, f, indent=2)
                    # Simple env.json
                    env = {"python": sys.version.split()[0], "os": sys.platform}
                    with open(_os.path.join(args.audit, 'env.json'), 'w', encoding='utf-8') as f:
                        _json.dump(env, f, indent=2)
                    # Write manifest.json and detached signature if present
                    try:
                        lp = _json.load(open(ledger_path, 'r', encoding='utf-8'))
                        manifest = lp.get('manifest', {}) if isinstance(lp, dict) else {}
                        with open(_os.path.join(args.audit, 'manifest.json'), 'w', encoding='utf-8') as f:
                            _json.dump(manifest, f, indent=2)
                        sig_hex = (lp.get('signing', {}) or {}).get('sig_ed25519_hex') if isinstance(lp, dict) else None
                        if sig_hex:
                            with open(_os.path.join(args.audit, 'manifest.json.sig'), 'w', encoding='utf-8') as f:
                                f.write(sig_hex.strip() + "\n")
                    except Exception:
                        pass
                    # Checksums
                    import hashlib as _hashlib
                    files = ['ledger.json', 'appendix.json', 'histograms.json', 'env.json', 'manifest.json', 'manifest.json.sig']
                    with open(_os.path.join(args.audit, 'checksum.txt'), 'w', encoding='utf-8') as f:
                        for name in files:
                            p = _os.path.join(args.audit, name)
                            if _os.path.exists(p):
                                h = _hashlib.sha256(open(p, 'rb').read()).hexdigest()
                                f.write(f"{h}  {name}\n")
                else:
                    pass
            except Exception:
                pass
        print(json.dumps(out, indent=2))
    elif args.cmd == "demo-changepoint":
        try:
            import os as _os
            _os.makedirs(args.out, exist_ok=True)
            from .bench import make_gaussian_instance_full
            w, _ = make_gaussian_instance_full(args.n)
            from .scheduler import cameleon_dp as _solve
            from .bench import _recommended_workers, _recommended_proc_workers  # type: ignore
            workers, _ = _recommended_workers(args.n)
            proc_workers, _ = _recommended_proc_workers(args.n)
            F, arg, recs, bc = _solve(args.n, w, 0.0, hints={}, workers=workers, proc_workers=proc_workers, cert_budget=recommended_cert_budget(args.n, profile='auto'))
            ledger = _os.path.join(args.out, 'ledger.json')
            from .ledger import export_records_json, export_proof_appendix
            export_records_json(recs, ledger)
            export_proof_appendix(recs, _os.path.join(args.out, 'appendix.json'))
            print(json.dumps({"ok": True, "out": args.out, "n": args.n, "boundary_count": bc}, indent=2))
        except Exception as e:
            print(json.dumps({"ok": False, "error": str(e)}, indent=2))
    elif args.cmd == "doctor":
        info = {}
        try:
            info["python"] = sys.version.split()[0]
            info["os"] = sys.platform
            import numpy as _np  # type: ignore
            info["numpy"] = str(_np.__version__)
        except Exception:
            pass
        try:
            import numba  # type: ignore
            info["numba"] = str(getattr(numba, "__version__", "present"))
        except Exception:
            info["numba"] = None
        try:
            import pyarrow  # type: ignore
            info["pyarrow"] = str(getattr(pyarrow, "__version__", "present"))
        except Exception:
            info["pyarrow"] = None
        try:
            import os as _os
            info["cpu_count"] = int(_os.cpu_count() or 1)
        except Exception:
            pass
        if args.json:
            print(json.dumps({"ok": True, "doctor": info}, indent=2))
        else:
            for k, v in info.items():
                print(f"{k}: {v}")
    # Future commands could load and auto-tune thresholds using load_records_file


if __name__ == "__main__":
    main()


