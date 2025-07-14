# apl360_parser.py
"""
Simple APL-like parser & REPL wiring core math primitives from apl360_math_primitives.
Supports dyadic expressions of the form:
  <array> <op> <array>
and monadic expressions:
  <op> <array>
where <array> is space-separated numbers.
"""
from apl360_math_primitives import (
    plus, minus, times, divide, power,
    abs_val, signum, reciprocal, floor_val, ceiling_val, ln, exp, iota, is_scalar
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
    'iota': iota  # usage: iota 5
}


def parse_array(tokens):
    """Convert a list of numeric tokens into a scalar or list."""
    if not tokens:
        raise ValueError("No tokens to parse as array")
    # parse numbers
    nums = []
    for t in tokens:
        try:
            if '.' in t:
                nums.append(float(t))
            else:
                nums.append(int(t))
        except ValueError:
            raise ValueError(f"Invalid number: {t}")
    # scalar if single, else list
    return nums[0] if len(nums) == 1 else nums


def eval_expr(expr: str):
    """Evaluate a simple APL expression using our primitives."""
    tokens = expr.strip().split()
    if not tokens:
        return None
    # Monadic
    if tokens[0] in UNARY_OPS:
        fn = UNARY_OPS[tokens[0]]
        operand = parse_array(tokens[1:])
        return fn(operand)
    # Dyadic
    # find first binary operator in tokens
    op_idx = None
    for i, t in enumerate(tokens):
        if t in BINARY_OPS:
            op_idx = i
            break
    if op_idx is not None:
        left = parse_array(tokens[:op_idx])
        op = tokens[op_idx]
        right = parse_array(tokens[op_idx+1:])
        fn = BINARY_OPS[op]
        return fn(left, right)
    # fallback: just parse array/scalar
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
            result = eval_expr(line)
            print(result)
        except Exception as e:
            print("Error:", e)


if __name__ == '__main__':
    repl()
