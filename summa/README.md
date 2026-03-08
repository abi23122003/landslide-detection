# ReduceExp

A small Python program that parses a quadratic expression over x and y with `+`, `*`, and parentheses, simplifies it to a polynomial, and computes the minimal number of operations required after optionally applying at most one factorization from the allowed forms.

Supported factorization forms (single use at most once):
- (a1 x + b1)(a2 x + b2)
- (a1 x + b1)(a2 y + b2)
- (a1 x + b1 y)(a2 x + b2) and its y-symmetric variant

Only multiplication and addition are counted as operations. Constants are free; variable multiplication like x*x or x*y counts; multiplying by a constant 1 is free; multiplying by 0 collapses to 0.

## Usage

Run with Python 3.9+:

```
python main.py < input.txt
```

Or type directly:

```
echo x*(x+2+1)+1+1 | python main.py
```

## Examples

Input: `x*(x+2+1)+1+1`
Output: `3`

Input: `2*x*y+4*x+y+2+y*y`
Output: `6`

Input: `10*5+6*3`
Output: `0`
