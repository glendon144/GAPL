# apl_360_parser.py
"""
APL360 Python REPL with arithmetic parsing supporting:
- Numeric and array operations using core APL math primitives
- Parentheses grouping and operator precedence
- Monadic and dyadic operators including true APL symbols
- HELP command listing available functions

Dependencies:
- Python 3.x
- modules/apl360_math_primitives.py in the 'modules' folder
"""
import re
from modules.apl360_math_primitives import (
    plus, minus, times, divide, power,
    abs_val, signum, reciprocal, floor_val, ceiling_val, ln, exp, iota,
    apply_binary
)

# Operator definitions with precedence
# Higher number = higher precedence
PRECEDENCE = {
    '⍟': 5, 'ln': 5, 'e': 5, 'exp': 5,
    '⌊': 5, 'floor': 5, '⌈': 5, 'ceil': 5,
    '|': 5, 'abs': 5, 'sign': 5, 'recip': 5, '⍳': 5, 'iota': 5,
    '^': 4, '**': 4,
    '×': 3, '*': 3, 'x': 3,
    '÷': 3, '/': 3,
    '%': 3, 'mod': 3,
    '+': 2, '-': 2,
    '⌈': 1, '⌊': 1  # shorthand: treat max/min lower precedence if needed
}

# Dyadic operator mapping
BINARY_OPS = {
    '+': plus, '-': minus,
    '×': times, '*': times, 'x': times,
    '÷': divide, '/': divide,
    '^': power, '**': power,
    '%': lambda a,b: apply_binary(lambda x,y: x % y, a, b),
    'mod': lambda a,b: apply_binary(lambda x,y: x % y, a, b),
    '⌈': lambda a,b: apply_binary(lambda x,y: max(x,y), a, b),
    '⌊': lambda a,b: apply_binary(lambda x,y: min(x,y), a, b)
}

# Monadic operator mapping
UNARY_OPS = {
    '|': abs_val, 'abs': abs_val,
    'sign': signum,
    'recip': reciprocal,
    '⌊': floor_val, 'floor': floor_val,
    '⌈': ceiling_val, 'ceil': ceiling_val,
    '⍟': ln, 'ln': ln,
    'e': exp, 'exp': exp,
    '⍳': iota, 'iota': iota
}

# Recognize numbers
NUM_RE = re.compile(r'^-?\d+(?:\.\d+)?$')


def print_help():
    print("Available monadic operators:")
    for op in sorted(UNARY_OPS): print(f"  {op}")
    print("\nAvailable dyadic operators:")
    for op in sorted(BINARY_OPS): print(f"  {op}")


def tokenize(expr: str):
    # Surround parentheses with spaces
    expr = expr.replace('(', ' ( ').replace(')', ' ) ')
    # Split on whitespace
    tokens = expr.split()
    # Filter to numbers, operators, or parentheses
    filtered = []
    for t in tokens:
        key = t if t in BINARY_OPS or t in UNARY_OPS or t in ('(', ')') else t.lower()
        if key in BINARY_OPS or key in UNARY_OPS or key in ('(', ')') or NUM_RE.match(t):
            filtered.append(key)
    return filtered


def shunting_yard(tokens):
    output = []
    stack = []
    for tok in tokens:
        if NUM_RE.match(tok):
            output.append(tok)
        elif tok in UNARY_OPS:
            stack.append(tok)
        elif tok in BINARY_OPS:
            while stack and stack[-1] != '(' and PRECEDENCE.get(stack[-1],0) >= PRECEDENCE.get(tok,0):
                output.append(stack.pop())
            stack.append(tok)
        elif tok == '(':
            stack.append(tok)
        elif tok == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
    while stack:
        output.append(stack.pop())
    return output


def eval_rpn(rpn):
    stack = []
    for tok in rpn:
        if NUM_RE.match(tok):
            stack.append(int(tok) if tok.isdigit() else float(tok))
        elif tok in UNARY_OPS:
            a = stack.pop()
            stack.append(UNARY_OPS[tok](a))
        elif tok in BINARY_OPS:
            b = stack.pop()
            a = stack.pop()
            stack.append(BINARY_OPS[tok](a, b))
    return stack[0]


def eval_expr(expr: str):
    tokens = tokenize(expr)
    if not tokens: return None
    rpn = shunting_yard(tokens)
    return eval_rpn(rpn)


def repl():
    print("APL360 Python REPL. Type 'HELP' or '?' for commands, 'exit' to quit.")
    while True:
        try:
            line = input("APL360> ").strip()
            cmd = line.lower()
            if cmd in ('', 'exit', 'quit'): break
            if cmd in ('help', '?'):
                print_help(); continue
            print(eval_expr(line))
        except Exception as e:
            print("Error:", e)

if __name__ == '__main__':
    repl()
