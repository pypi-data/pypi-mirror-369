from cameleon_dp.scheduler import cameleon_dp
from cameleon_dp.bench import make_convex_form_instance
from cameleon_dp.ledger import summarize_records


def test_ledger_summary_contains_expected_keys():
    n = 128
    w, hint = make_convex_form_instance(n)
    F, arg, recs, bc = cameleon_dp(n, w, 0.0, hints={"convex_form": hint})
    summary = summarize_records(recs)
    assert isinstance(summary, dict)
    for key in [
        "total_blocks",
        "total_runtime_sec",
        "by_cert",
        "total_w_calls",
        "depth_hist",
        "orientation_hist",
    ]:
        assert key in summary


