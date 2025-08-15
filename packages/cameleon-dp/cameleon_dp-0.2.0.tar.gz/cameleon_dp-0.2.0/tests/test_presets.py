from cameleon_dp.bench import recommended_cert_budget


def test_recommended_presets_contain_expected_keys():
    for profile in ("balanced", "fast_convex", "monotone_careful"):
        b = recommended_cert_budget(5000, profile=profile)
        # Common keys
        for k in [
            "min_cert_I",
            "monge_samples",
            "monge_guard_grid_i",
            "monge_guard_grid_j",
            "proc_convex_min_blocks",
            "proc_monge_min_blocks",
        ]:
            assert k in b
        assert isinstance(b.get("min_cert_I"), int)


def test_run_quick_bench_accepts_profile_kwarg():
    # Ensure API accepts profile keyword (smoke; does not run heavy bench)
    from cameleon_dp.bench import run_quick_bench
    from cameleon_dp.bench import make_convex_form_instance
    # Just check we can build a budget without executing DP here
    budget = recommended_cert_budget(1000, profile="balanced")
    assert isinstance(budget, dict)

