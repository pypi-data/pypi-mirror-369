from bisect import bisect_left

class LiChao:
    def __init__(self, xs):
        # Preserve original order mapping for stability, but sort for tree domain
        self.xs = sorted(xs)                     # discrete domain for queries
        self.N = len(self.xs)
        self.line = [None] * (4 * self.N)        # segment tree of lines (m,b,j)
        # Precompute positions for faster queries
        self._pos = {x: i for i, x in enumerate(self.xs)}

    @staticmethod
    def f(line, x):
        m, b, _j = line
        return m * x + b

    def _add(self, node, l, r, newline):
        if self.line[node] is None:
            self.line[node] = newline
            return
        cur = self.line[node]
        mid = (l + r) // 2
        xL = self.xs[l]; xM = self.xs[mid]; xR = self.xs[r]

        # Ensure line[node] is the better one at xM
        if self.f(newline, xM) < self.f(cur, xM):
            self.line[node], newline = newline, cur
            cur = self.line[node]

        if l == r:
            return
        if self.f(newline, xL) < self.f(cur, xL):
            self._add(node*2, l, mid, newline)
        elif self.f(newline, xR) < self.f(cur, xR):
            self._add(node*2+1, mid+1, r, newline)

    def add_line(self, m, b, j_id):
        self._add(1, 0, self.N-1, (m, b, j_id))

    def _query(self, node, l, r, x):
        if node >= len(self.line) or self.line[node] is None:
            return float('inf'), -1
        val = self.f(self.line[node], x)
        best_j = self.line[node][2]
        if l == r:
            return val, best_j
        mid = (l + r) // 2
        if x <= self.xs[mid]:
            sub_val, sub_j = self._query(node*2, l, mid, x)
        else:
            sub_val, sub_j = self._query(node*2+1, mid+1, r, x)
        if sub_val < val:
            return sub_val, sub_j
        return val, best_j

    def query(self, x):
        # returns (value, argmin_j); assumes x is one of xs
        # If x not exactly in domain (due to float), snap to nearest known index
        if x not in self._pos:
            # binary search for nearest
            from bisect import bisect_left
            idx = bisect_left(self.xs, x)
            if idx <= 0:
                x = self.xs[0]
            elif idx >= self.N:
                x = self.xs[-1]
            else:
                # choose nearer of neighbors
                left = self.xs[idx-1]; right = self.xs[idx]
                x = left if abs(x-left) <= abs(right-x) else right
        return self._query(1, 0, self.N-1, x)