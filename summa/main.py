import sys
from typing import Dict, Tuple, List


# Polynomial represented as dict mapping (px, py) -> coeff (int), only degrees 0..2 with px+py<=2
Mon = Tuple[int, int]
Poly = Dict[Mon, int]


def poly_add(a: Poly, b: Poly) -> Poly:
    out: Poly = dict(a)
    for m, c in b.items():
        if c == 0:
            continue
        out[m] = out.get(m, 0) + c
        if out[m] == 0:
            del out[m]
    return out


def poly_mul(a: Poly, b: Poly) -> Poly:
    out: Poly = {}
    for (i1, j1), c1 in a.items():
        for (i2, j2), c2 in b.items():
            i = i1 + i2
            j = j1 + j2
            if i + j > 2:
                # Per problem statement, inputs won't produce cubic terms
                # If encountered, ignore as invalid path (shouldn't happen)
                raise ValueError("Degree > 2 encountered; invalid input per constraints")
            m = (i, j)
            out[m] = out.get(m, 0) + c1 * c2
            if out[m] == 0:
                del out[m]
    return out


def mono_const(k: int) -> Poly:
    return {(0, 0): k} if k != 0 else {}


def mono_x() -> Poly:
    return {(1, 0): 1}


def mono_y() -> Poly:
    return {(0, 1): 1}


####################
# Lexer and Parser #
####################


class Lexer:
    def __init__(self, s: str):
        self.s = s
        self.n = len(s)
        self.i = 0

    def _peek(self) -> str:
        return self.s[self.i] if self.i < self.n else ""

    def _advance(self) -> str:
        ch = self._peek()
        if ch:
            self.i += 1
        return ch

    def next_token(self) -> Tuple[str, str]:
        # Returns (type, value)
        while self.i < self.n and self.s[self.i].isspace():
            self.i += 1
        if self.i >= self.n:
            return ("EOF", "")
        ch = self._advance()
        if ch.isdigit():
            start = self.i - 1
            while self.i < self.n and self.s[self.i].isdigit():
                self.i += 1
            return ("NUM", self.s[start:self.i])
        if ch == 'x' or ch == 'y':
            return ("VAR", ch)
        if ch in '+*()':
            return (ch, ch)
        raise ValueError(f"Unexpected character: {ch}")


class Parser:
    def __init__(self, s: str):
        self.lex = Lexer(s)
        self.lookahead = self.lex.next_token()

    def _eat(self, t: str) -> str:
        if self.lookahead[0] != t:
            raise ValueError(f"Expected {t}, got {self.lookahead}")
        val = self.lookahead[1]
        self.lookahead = self.lex.next_token()
        return val

    def parse(self) -> Poly:
        res = self.parse_expr()
        if self.lookahead[0] != "EOF":
            raise ValueError("Unexpected trailing characters")
        return res

    # expr := term ('+' term)*
    def parse_expr(self) -> Poly:
        p = self.parse_term()
        while self.lookahead[0] == '+':
            self._eat('+')
            q = self.parse_term()
            p = poly_add(p, q)
        return p

    # term := factor ('*' factor)*
    def parse_term(self) -> Poly:
        p = self.parse_factor()
        while self.lookahead[0] == '*':
            self._eat('*')
            q = self.parse_factor()
            p = poly_mul(p, q)
        return p

    # factor := NUM | VAR | '(' expr ')'
    def parse_factor(self) -> Poly:
        t, v = self.lookahead
        if t == 'NUM':
            self._eat('NUM')
            return mono_const(int(v))
        if t == 'VAR':
            self._eat('VAR')
            return mono_x() if v == 'x' else mono_y()
        if t == '(':
            self._eat('(')
            p = self.parse_expr()
            self._eat(')')
            return p
        raise ValueError(f"Unexpected token in factor: {self.lookahead}")


########################
# Operation Counting   #
########################


def nonzero_terms(poly: Poly) -> List[Tuple[Mon, int]]:
    return [(m, c) for m, c in poly.items() if c != 0]


def count_ops_baseline(poly: Poly) -> int:
    # Extract coefficients
    c0 = poly.get((0, 0), 0)
    cx = poly.get((1, 0), 0)
    cy = poly.get((0, 1), 0)
    cxx = poly.get((2, 0), 0)
    cxy = poly.get((1, 1), 0)
    cyy = poly.get((0, 2), 0)

    muls = 0
    # linear
    if cx != 0 and cx != 1:
        muls += 1
    if cy != 0 and cy != 1:
        muls += 1
    # quadratic
    if cxx != 0:
        muls += 1  # x*x
        if cxx != 1:
            muls += 1  # coeff * (x*x)
    if cxy != 0:
        muls += 1  # x*y
        if cxy != 1:
            muls += 1
    if cyy != 0:
        muls += 1  # y*y
        if cyy != 1:
            muls += 1

    # additions: number of nonzero monomial terms - 1
    terms = 0
    if c0 != 0:
        terms += 1
    if cx != 0:
        terms += 1
    if cy != 0:
        terms += 1
    if cxx != 0:
        terms += 1
    if cxy != 0:
        terms += 1
    if cyy != 0:
        terms += 1

    adds = max(terms - 1, 0)
    return muls + adds


########################
# Factorization Search #
########################


def try_form1(poly: Poly, var: str) -> Tuple[bool, int]:
    # Form1 on var in {"x","y"}
    if var == 'x':
        c2 = poly.get((2, 0), 0)
        c1 = poly.get((1, 0), 0)
        c0 = poly.get((0, 0), 0)
        other_keys = [k for k in poly.keys() if k not in [(2, 0), (1, 0), (0, 0)]]
    else:
        c2 = poly.get((0, 2), 0)
        c1 = poly.get((0, 1), 0)
        c0 = poly.get((0, 0), 0)
        other_keys = [k for k in poly.keys() if k not in [(0, 2), (0, 1), (0, 0)]]

    # need all three present (can be zero but that likely doesn't help)
    # Search integer factors a1,a2 of c2 and b1,b2 of c0 such that a1*b2 + a2*b1 = c1
    best = None
    for a1 in divisors(c2):
        a2 = safe_div(c2, a1)
        for b1 in divisors(c0):
            b2 = safe_div(c0, b1)
            if a1 * b2 + a2 * b1 == c1:
                # valid factorization for this quartet
                # Build rest polynomial: remove these contributions
                if var == 'x':
                    rem = dict(poly)
                    sub(rem, (2, 0), a1 * a2)
                    sub(rem, (1, 0), a1 * b2 + a2 * b1)
                    sub(rem, (0, 0), b1 * b2)
                else:
                    rem = dict(poly)
                    sub(rem, (0, 2), a1 * a2)
                    sub(rem, (0, 1), a1 * b2 + a2 * b1)
                    sub(rem, (0, 0), b1 * b2)
                # Cost for factor
                if var == 'x':
                    cost_factor = cost_linear(a1, 'x', b1) + cost_linear(a2, 'x', b2) + cost_mul_of_two_linear(a1, 'x', b1, a2, 'x', b2)
                else:
                    cost_factor = cost_linear(a1, 'y', b1) + cost_linear(a2, 'y', b2) + cost_mul_of_two_linear(a1, 'y', b1, a2, 'y', b2)
                # Rest cost
                cost_rest = cost_rest_poly(rem)
                # Top-level additions: product treated as one addend (if not zero), plus remaining monomials; minus 1
                rest_terms_cnt = count_nonzero_terms(rem)
                total_top_adds = max(rest_terms_cnt + 1 - 1, 0)
                # Total cost combines factor internal cost, rest multiplications, and top-level additions
                total = cost_factor + cost_rest + total_top_adds
                if best is None or total < best:
                    best = total
    return (best is not None, best if best is not None else 10**9)


def try_form2(poly: Poly) -> Tuple[bool, int]:
    # (a1 x + b1)(a2 y + b2) -> xy, x, y, const
    cxy = poly.get((1, 1), 0)
    cx = poly.get((1, 0), 0)
    cy = poly.get((0, 1), 0)
    c0 = poly.get((0, 0), 0)

    best = None
    for a1 in divisors(cxy):
        a2 = safe_div(cxy, a1)
        # b2 must satisfy a1*b2 = cx
        if not is_divisible(cx, a1):
            continue
        b2 = safe_div(cx, a1)
        if not is_divisible(cy, a2):
            continue
        b1 = safe_div(cy, a2)
        if b1 * b2 != c0:
            continue
        # Build remainder
        rem = dict(poly)
        sub(rem, (1, 1), a1 * a2)
        sub(rem, (1, 0), a1 * b2)
        sub(rem, (0, 1), a2 * b1)
        sub(rem, (0, 0), b1 * b2)
        # Cost for factor
        cost_factor = cost_linear(a1, 'x', b1) + cost_linear(a2, 'y', b2) + cost_mul_of_two_linear(a1, 'x', b1, a2, 'y', b2)
        cost_restv = cost_rest_poly(rem)
        rest_terms_cnt = count_nonzero_terms(rem)
        total_top_adds = max(rest_terms_cnt + 1 - 1, 0) if not is_zero_factor(a1, b1) or not is_zero_factor(a2, b2) else max(rest_terms_cnt - 1, 0)
        total = cost_factor + cost_restv + total_top_adds
        if best is None or total < best:
            best = total
    return (best is not None, best if best is not None else 10**9)


def try_form3(poly: Poly) -> Tuple[bool, int]:
    # Try (a1 x + b1 y)(a2 x + b2) -> x^2, x, xy, y
    best = None
    # Variant A: as given
    cxx = poly.get((2, 0), 0)
    cx = poly.get((1, 0), 0)
    cxy = poly.get((1, 1), 0)
    cy = poly.get((0, 1), 0)
    for a1 in divisors(cxx):
        a2 = safe_div(cxx, a1)
        # a1*b2 = cx => b2 must be divisible
        if not is_divisible(cx, a1):
            continue
        b2 = safe_div(cx, a1)
        # a2*b1 = cxy => b1 must be divisible
        if not is_divisible(cxy, a2):
            continue
        b1 = safe_div(cxy, a2)
        # b1*b2 should equal cy
        if b1 * b2 != cy:
            continue
        rem = dict(poly)
        sub(rem, (2, 0), a1 * a2)
        sub(rem, (1, 0), a1 * b2)
        sub(rem, (1, 1), a2 * b1)
        sub(rem, (0, 1), b1 * b2)
        cost_factor = cost_linear_mixed(a1, 'x', b1, 'y') + cost_linear(a2, 'x', b2) + cost_mul_of_two_linear_mixed(a1, 'x', b1, 'y', a2, 'x', b2)
        cost_restv = cost_rest_poly(rem)
        rest_terms_cnt = count_nonzero_terms(rem)
        total_top_adds = max(rest_terms_cnt + 1 - 1, 0)
        total = cost_factor + cost_restv + total_top_adds
        if best is None or total < best:
            best = total

    # Variant B: swap x<->y in the factor with mixed
    cyy = poly.get((0, 2), 0)
    cy = poly.get((0, 1), 0)
    cxy = poly.get((1, 1), 0)
    cx = poly.get((1, 0), 0)
    for a1 in divisors(cyy):
        a2 = safe_div(cyy, a1)
        if not is_divisible(cy, a1):
            continue
        b2 = safe_div(cy, a1)
        if not is_divisible(cxy, a2):
            continue
        b1 = safe_div(cxy, a2)
        if b1 * b2 != cx:
            continue
        rem = dict(poly)
        sub(rem, (0, 2), a1 * a2)
        sub(rem, (0, 1), a1 * b2)
        sub(rem, (1, 1), a2 * b1)
        sub(rem, (1, 0), b1 * b2)
        cost_factor = cost_linear_mixed(a1, 'y', b1, 'x') + cost_linear(a2, 'y', b2) + cost_mul_of_two_linear_mixed(a1, 'y', b1, 'x', a2, 'y', b2)
        cost_restv = cost_rest_poly(rem)
        rest_terms_cnt = count_nonzero_terms(rem)
        total_top_adds = max(rest_terms_cnt + 1 - 1, 0)
        total = cost_factor + cost_restv + total_top_adds
        if best is None or total < best:
            best = total

    return (best is not None, best if best is not None else 10**9)


#############
# Utilities #
#############


def is_divisible(a: int, b: int) -> bool:
    if b == 0:
        return a == 0
    return a % b == 0


def safe_div(a: int, b: int) -> int:
    if b == 0:
        # Convention: 0/0 treated as 0 here; guarded by is_divisible
        return 0
    return a // b


def divisors(n: int) -> List[int]:
    # Return all integer factor candidates for non-negative n
    # Given only + numbers appear, consider positive divisors including 1; include n==0 case -> special: choose a1=0..??
    if n < 0:
        n = -n
    if n == 0:
        # Allow 0 and 1 as pseudo-divisors; also any k with 0*k=0; we'll try limited set {0,1}
        return [0, 1]
    res = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            res.append(i)
            if i * i != n:
                res.append(n // i)
        i += 1
    return res


def sub(rem: Poly, mon: Mon, amount: int) -> None:
    if amount == 0:
        return
    cur = rem.get(mon, 0) - amount
    if cur == 0:
        rem.pop(mon, None)
    else:
        rem[mon] = cur


def cost_linear(a: int, var: str, b: int) -> int:
    # cost (in ops) to compute a*var + b inside, counting multiplications and additions within this linear expression
    # constants are free
    if a == 0:
        # returns constant b
        return 0
    mul = 0
    add = 0
    if a != 1:
        mul += 1
    # addition with b if b != 0
    if b != 0:
        add += 1
    return mul + add


def cost_linear_mixed(a: int, var1: str, b: int, var2: str) -> int:
    # cost to compute a*var1 + b*var2
    mul = 0
    add = 0
    if a != 0 and a != 1:
        mul += 1
    if b != 0 and b != 1:
        mul += 1
    # Sum the two parts if both present
    if (a != 0) and (b != 0):
        add += 1
    return mul + add


def cost_mul_of_two_linear(a1: int, v1: str, b1: int, a2: int, v2: str, b2: int) -> int:
    # cost for the multiply itself, possibly 0 if one factor is constant 1 or 0 (can be folded)
    # determine if factor reduces to constant 0 or 1
    f1_const = (a1 == 0)
    f1_val = b1 if f1_const else None
    f2_const = (a2 == 0)
    f2_val = b2 if f2_const else None
    # If any is constant 0 -> product is constant 0 -> can be folded
    if (f1_const and f1_val == 0) or (f2_const and f2_val == 0):
        return 0
    # If one is constant 1 -> multiply unnecessary
    if (f1_const and f1_val == 1) or (f2_const and f2_val == 1):
        return 0
    # Otherwise we do need 1 multiply
    return 1


def cost_mul_of_two_linear_mixed(a1: int, v1: str, b1: int, v2b: str, a2: int, v2: str, b2: int) -> int:
    # similar to above; a linear with two variable terms plus other linear
    # Determine if either factor is a non-variable constant (only possible if a or b are zeros accordingly)
    # In mixed, first factor is a1*var + b1*var2; it is constant only if both coefficients are zero
    f1_is_const0 = (a1 == 0 and b1 == 0)
    f2_is_const0 = (a2 == 0 and b2 == 0)
    if f1_is_const0 or f2_is_const0:
        return 0
    # No chance to be constant 1 realistically
    return 1


def is_zero_factor(a: int, b: int) -> bool:
    return a == 0 and b == 0


def count_nonzero_terms(poly: Poly) -> int:
    return sum(1 for c in poly.values() if c != 0)


def cost_rest_poly(poly: Poly) -> int:
    # cost of multiplications for remaining monomials; additions handled at top-level
    muls = 0
    c0 = poly.get((0, 0), 0)
    cx = poly.get((1, 0), 0)
    cy = poly.get((0, 1), 0)
    cxx = poly.get((2, 0), 0)
    cxy = poly.get((1, 1), 0)
    cyy = poly.get((0, 2), 0)
    if cx != 0 and cx != 1:
        muls += 1
    if cy != 0 and cy != 1:
        muls += 1
    if cxx != 0:
        muls += 1
        if cxx != 1:
            muls += 1
    if cxy != 0:
        muls += 1
        if cxy != 1:
            muls += 1
    if cyy != 0:
        muls += 1
        if cyy != 1:
            muls += 1
    return muls


def solve(expr: str) -> int:
    parser = Parser(expr)
    poly = parser.parse()
    # If polynomial is constant only, no operations
    if all(deg == (0, 0) for deg in poly.keys()) or len(poly) == 0:
        return 0
    base = count_ops_baseline(poly)
    # Try each form at most once and take minimal
    best = base
    # Form 1 for x and y
    ok1x, cost1x = try_form1(poly, 'x')
    if ok1x:
        best = min(best, cost1x)
    ok1y, cost1y = try_form1(poly, 'y')
    if ok1y:
        best = min(best, cost1y)
    # Form 2
    ok2, cost2 = try_form2(poly)
    if ok2:
        best = min(best, cost2)
    # Form 3
    ok3, cost3 = try_form3(poly)
    if ok3:
        best = min(best, cost3)
    return best


def main():
    data = sys.stdin.read().strip()
    if not data:
        print(0)
        return
    try:
        ans = solve(data)
        print(ans)
    except Exception:
        # Fallback: try to parse and print baseline
        try:
            parser = Parser(data)
            poly = parser.parse()
            res = count_ops_baseline(poly)
            print(res)
        except Exception:
            print(0)


if __name__ == "__main__":
    main()
