# apl_360_parser.py
"""
APL360 Python REPL with arithmetic parsing, variable assignment, and full APL-like syntax.

Features:
- Numeric and array operations using core APL math primitives
- Parentheses grouping and operator precedence
- Monadic and dyadic operators including true APL symbols
- HELP command listing available functions
- Forgiving parsing with or without spaces
- Variable assignment (`A=5` or `A = expr`) and usage in expressions
- Equality comparison (`==`) as elementwise or scalar

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

# Operator precedence (higher = bind tighter)
PRECEDENCE = {
    '|u':7, 'abs':7, 'sign':7, 'recip':7, '⌊':7, 'floor':7, '⌈':7, 'ceil':7,
    '⍟':7, 'ln':7, 'e':7, 'exp':7, '⍳':7, 'iota':7,
    '^':6, '**':6,
    '×':5, '*':5, 'x':5, '÷':5, '/':5, '%':5, 'mod':5,
    '+':4, '-':4,
    '==':3,
    '⌈':2, '⌊':2
}

# Dyadic operator mapping
BINARY_OPS = {
    '+': plus, '-': minus,
    '×': times, '*': times, 'x': times,
    '÷': divide, '/': divide,
    '^': power, '**': power,
    '%': lambda a,b: apply_binary(lambda x,y: x%y, a, b),
    'mod': lambda a,b: apply_binary(lambda x,y: x%y, a, b),
    '⌈': lambda a,b: apply_binary(lambda x,y: max(x,y), a, b),
    '⌊': lambda a,b: apply_binary(lambda x,y: min(x,y), a, b),
    '==': lambda a,b: apply_binary(lambda x,y: 1 if x==y else 0, a, b)
}

# Monadic operator mapping (suffix 'u' distinguishes '|')
UNARY_OPS = {
    '|u': abs_val, 'abs': abs_val,
    'sign': signum, 'recip': reciprocal,
    '⌊': floor_val, 'floor': floor_val,
    '⌈': ceiling_val, 'ceil': ceiling_val,
    '⍟': ln, 'ln': ln, 'e': exp, 'exp': exp,
    '⍳': iota, 'iota': iota
}

# Regex pattern to tokenize numbers, ids, ops, parentheses, with or without spaces
TOK_PATTERN = re.compile(
    r"\s*(?:(?P<number>-?\d+(?:\.\d+)?)"
    r"|(?P<id>[A-Za-z]\w*)"
    r"|(?P<op>\*\*|==|mod|abs|sign|recip|floor|ceil|ln|exp|iota|⍟|⍳|⌊|⌈|[+\-×\*x÷/%\^])"
    r"|(?P<paren>[()]))"
)

NUM_RE = re.compile(r'^-?\d+(?:\.\d+)?$')
VAR_RE = re.compile(r'^[A-Za-z]\w*$')  # valid variable names

env = {}  # variable environment


def print_help():
    print("Commands:")
    print("  HELP or ?          Show this message")
    print("  exit or quit       Quit REPL")
    print("  A = expr or A=expr Assign variable A")
    print("  Use variables (A, B, etc.) in expressions, e.g., A*B+(C/2)")
    print("\nMonadic operators:")
    for op in sorted(UNARY_OPS): print(f"  {op.rstrip('u')}")
    print("\nDyadic operators:")
    for op in sorted(BINARY_OPS): print(f"  {op}")


def tokenize(expr: str):
    """Split expression into numbers, identifiers, operators, and parentheses."""
    tokens = []
    for m in TOK_PATTERN.finditer(expr):
        if m.group('number'):
            tokens.append(m.group('number'))
        elif m.group('id'):
            tokens.append(m.group('id'))
        elif m.group('op'):
            op = m.group('op')
            # disambiguate '|' as unary if at start or after '('
            tokens.append(op + 'u' if op == '|' and (not tokens or tokens[-1] == '(') else op)
        elif m.group('paren'):
            tokens.append(m.group('paren'))
    return tokens


def shunting_yard(tokens):
    output, stack = [], []
    for tok in tokens:
        if NUM_RE.match(tok) or VAR_RE.match(tok):
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
        elif VAR_RE.match(tok):
            if tok in env:
                stack.append(env[tok])
            else:
                raise NameError(f"Undefined variable: {tok}")
        elif tok in UNARY_OPS:
            a = stack.pop()
            stack.append(UNARY_OPS[tok](a))
        elif tok in BINARY_OPS:
            b = stack.pop()
            a = stack.pop()
            stack.append(BINARY_OPS[tok](a,b))
        else:
            raise SyntaxError(f"Unknown token in RPN: {tok}")
    return stack[0]


def eval_expr(expr: str):
    tokens = tokenize(expr)
    if not tokens:
        return None
    rpn = shunting_yard(tokens)
    return eval_rpn(rpn)


def repl():
    print("APL360 Python REPL. Type 'HELP' or '?' for commands, 'exit' to quit.")
    while True:
        try:
            line = input("APL360> ").strip()
            if not line:
                continue
            low = line.lower()
            if low in ('exit','quit'):
                print("Goodbye!")
                break
            if low in ('help','?'):
                print_help()
                continue
            m = re.match(r'^(?P<var>[A-Za-z]\w*)\s*=\s*(?P<expr>.+)$', line)
            if m:
                var = m.group('var')
                val = eval_expr(m.group('expr'))
                env[var] = val
                print(val)
                continue
            result = eval_expr(line)
            print(result)
        except Exception as e:
            print("Error:", e)

if __name__ == '__main__':
    repl()
