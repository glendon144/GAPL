# apl_360_parser.py
"""
Simple APL-like parser & REPL wiring core math primitives from the 'modules' package.

Dependencies:
- Python 3.x (run with `python3`)
- Ensure `modules/__init__.py` exists (even if empty) next to this file.

Usage:
```bash
cd /Users/gross/src/GAPL
python3 apl_360_parser.py
```
Supports dyadic expressions of the form:
  <array> <op> <array>
and monadic expressions:
  <op> <array>
where <array> is space-separated numbers.
"""

from modules.apl360_math_primitives import (
    plus, minus, times, divide, power,
    abs_val, signum, reciprocal, floor_val, ceiling_val, ln, exp, iota
)

# Map APL symbols (and ASCII fallbacks) to primitive functions
BINARY_OPS = {
    '+': plus,
    '-': minus,
    '×': times, '*': times,
    '÷': divide, '/': divide,
    '^': power, '**': power
}
UNARY_OPS = {
    '|': abs_val,
    'abs': abs_val,
    'sign': signum,
    'recip': reciprocal,
    'floor': floor_val,
    'ceil': ceiling_val,
    'ln': ln,
    'exp': exp,
    'iota': iota
}

def parse_array(tokens):
    """Convert a list of numeric tokens into a scalar or list."""
    if not tokens:
        raise ValueError("No tokens to parse as array")
    nums = []
    for t in tokens:
        try:
            nums.append(float(t) if '.' in t else int(t))
        except ValueError:
            raise ValueError(f"Invalid number: {t}")
    return nums[0] if len(nums) == 1 else nums

def eval_expr(expr: str):
    """Evaluate a simple APL expression using our primitives."""
    tokens = expr.strip().split()
    if not tokens:
        return None
    # Monadic operator
    if tokens[0] in UNARY_OPS:
        fn = UNARY_OPS[tokens[0]]
        return fn(parse_array(tokens[1:]))
    # Dyadic operator
    for i, t in enumerate(tokens):
        if t in BINARY_OPS:
            left = parse_array(tokens[:i])
            right = parse_array(tokens[i+1:])
            return BINARY_OPS[t](left, right)
    # Just an array or scalar
    return parse_array(tokens)

def repl():
    """Read-Eval-Print Loop for APL360 subset."""
    print("APL360 Python REPL. Type 'exit' or 'quit' to leave.")
    while True:
        try:
            line = input("APL360> ").strip()
            if line in ('exit', 'quit'):
                print("Goodbye!")
                break
            print(eval_expr(line))
        except Exception as e:
            print("Error:", e)

if __name__ == '__main__':
    repl()
