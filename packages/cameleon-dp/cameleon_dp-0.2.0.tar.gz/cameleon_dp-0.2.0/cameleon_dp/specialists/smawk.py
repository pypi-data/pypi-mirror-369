from ..numeric import leq_with_tie as leq_with_eps


def solve_smawk(F, w, i_lo, i_hi, j_lo, j_hi, out_F, out_arg, eps: float = 0.0):
    """SMAWK algorithm for row minima over an implicitly totally monotone matrix with ε-aware tie-breaks."""
    rows = list(range(i_lo, i_hi+1))
    cols = list(range(j_lo, j_hi+1))

    def f(i, j):
        # only valid for j < i
        if j < i:
            return F[j] + w(j, i)
        return float('inf')

    # Run SMAWK to get argmins per row
    assignment = _smawk(rows, cols, f, eps)

    # Write results
    for i in rows:
        j = assignment[i]
        out_arg[i] = j
        out_F[i] = f(i, j)


def _smawk(rows, cols, f, eps):
    if not rows:
        return {}
    # Reduce columns
    col_stack = []
    for c in cols:
        while col_stack:
            r_idx = len(col_stack) - 1
            r = rows[r_idx]
            prev_c = col_stack[-1]
            if leq_with_eps(f(r, c), f(r, prev_c), eps, (r, c, prev_c)):
                col_stack.pop()
            else:
                break
        if len(col_stack) < len(rows):
            col_stack.append(c)
    # Recurse on odd rows
    odd_rows = rows[1::2]
    result = {}
    result.update(_smawk(odd_rows, col_stack, f, eps))
    # Fill even rows
    col_pos = {c: idx for idx, c in enumerate(col_stack)}
    for idx, r in enumerate(rows):
        if idx % 2 == 0:
            # determine search range between neighbors
            left = 0
            right = len(col_stack) - 1
            if idx - 1 >= 0:
                prev_r = rows[idx - 1]
                left = col_pos[result[prev_r]]
            if idx + 1 < len(rows):
                next_r = rows[idx + 1]
                right = col_pos[result[next_r]]
            # find best in range
            best_j = col_stack[left]
            best_val = f(r, best_j)
            for c in col_stack[left:right+1]:
                val = f(r, c)
                if leq_with_eps(val, best_val, eps, (r, c, best_j)):
                    best_val = val
                    best_j = c
            result[r] = best_j
    return result