# apl_360_parser.py
"""
Simple APL-like parser & REPL wiring core math primitives from the 'modules' package.

Features:
- Monadic operators (e.g. |, abs, sign, recip, floor/⌊, ceil/⌈, ln/⍟, exp, iota/⍳)
- Dyadic operators (+, -, ×, ÷, ^, %, ⌈ (max), ⌊ (min), mod)
- HELP or ? command to list available operations
- True APL tokens supported alongside ASCII fallbacks
- Forgiving token matching (case-insensitive for names)

Dependencies:
- Python 3.x (run with `python3`)
- Ensure `modules/__init__.py` exists next to this file.

Usage:
```bash
cd /Users/gross/src/GAPL
python3 apl_360_parser.py
```
"""
from modules.apl360_math_primitives import (
    plus, minus, times, divide, power,
    abs_val, signum, reciprocal, floor_val, ceiling_val, ln, exp, iota,
    apply_binary
)

# Dyadic operators mapping
BINARY_OPS = {
    '+': plus,
    '-': minus,
    '×': times, '*': times,
    '÷': divide, '/': divide,
    '^': power, '**': power,
    '%': lambda a, b: apply_binary(lambda x, y: x % y, a, b),
    'mod': lambda a, b: apply_binary(lambda x, y: x % y, a, b),
    '⌈': lambda a, b: apply_binary(lambda x, y: max(x, y), a, b),  # A⌈B = max
    '⌊': lambda a, b: apply_binary(lambda x, y: min(x, y), a, b)   # A⌊B = min
}

# Monadic operators mapping
UNARY_OPS = {
    '|': abs_val,
    'abs': abs_val,
    'sign': signum,
    'recip': reciprocal,
    'floor': floor_val,
    '⌊': floor_val,
    'ceil': ceiling_val,
    '⌈': ceiling_val,
    'ln': ln,
    '⍟': ln,
    'exp': exp,
    'e': exp,
    'iota': iota,
    '⍳': iota
}


def print_help():
    """Display available operators and usage."""
    print("Available monadic operators:")
    for op in sorted(UNARY_OPS):
        print(f"  {op}")
    print("\nAvailable dyadic operators:")
    for op in sorted(BINARY_OPS):
        print(f"  {op}")


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
    # Monadic
    raw = tokens[0]
    key = raw if raw in UNARY_OPS else raw.lower()
    if key in UNARY_OPS:
        fn = UNARY_OPS[key]
        return fn(parse_array(tokens[1:]))
    # Dyadic: find first operator token
    for i, raw_op in enumerate(tokens):
        op = raw_op if raw_op in BINARY_OPS else raw_op.lower()
        if op in BINARY_OPS:
            left = parse_array(tokens[:i])
            right = parse_array(tokens[i+1:])
            return BINARY_OPS[op](left, right)
    # Fallback: parse array/scalar
    return parse_array(tokens)


def repl():
    """Read-Eval-Print Loop for APL360 subset."""
    print("APL360 Python REPL. Type 'HELP' or '?' for a list of commands, 'exit' to leave.")
    while True:
        try:
            line = input("APL360> ").strip()
            if not line:
                continue
            low = line.lower()
            if low in ('exit', 'quit'):
                print("Goodbye!")
                break
            if low in ('help', '?'):
                print_help()
                continue
            print(eval_expr(line))
        except Exception as e:
            print("Error:", e)


if __name__ == '__main__':
    repl()
