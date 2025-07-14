# apl_360_parser.py
"""
APL360 Python REPL with full APL-like syntax, including array literals, CSV-style lists, 1-based indexing, and operator help.

Features:
- Numeric and array operations using core APL math primitives
- Array literals with brackets [1 2 3] or parentheses (1 2 3)
- Comma-separated lists like 1,2,3 without brackets
- Parentheses for grouping and operator precedence
- Monadic & dyadic operators (true APL symbols and ASCII)
- Variable assignment and usage
- Optional HELP menu for operator descriptions
- 1-based indexing anywhere: A[3] or A(3)
- Forgiving parsing without requiring spaces

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

# Operator precedence (higher binds tighter)
PRECEDENCE = {
    '|u':7, 'abs':7, 'sign':7, 'recip':7,
    '⌊':7, 'floor':7, '⌈':7, 'ceil':7,
    '⍟':7, 'ln':7, 'e':7, 'exp':7, '⍳':7, 'iota':7,
    '^':6, '**':6,
    '×':5, '*':5, 'x':5, '÷':5, '/':5, '%':5, 'mod':5, '|':5,
    '+':4, '-':4,
    '==':3,
    '⌈':2, '⌊':2
}

# Dyadic operations
BINARY_OPS = {
    '+': plus, '-': minus,
    '×': times, '*': times, 'x': times,
    '÷': divide, '/': divide,
    '^': power, '**': power,
    '%': lambda a,b: apply_binary(lambda x,y: x%y, a, b),
    'mod': lambda a,b: apply_binary(lambda x,y: x%y, a, b),
    '|': lambda a,b: apply_binary(lambda x,y: x%y, a, b),
    '⌈': lambda a,b: apply_binary(lambda x,y: max(x,y), a, b),
    '⌊': lambda a,b: apply_binary(lambda x,y: min(x,y), a, b),
    '==': lambda a,b: apply_binary(lambda x,y: 1 if x==y else 0, a, b)
}

# Unary operations ('|u' denotes absolute to disambiguate)
UNARY_OPS = {
    '|u': abs_val, 'abs': abs_val,
    'sign': signum, 'recip': reciprocal,
    '⌊': floor_val, 'floor': floor_val,
    '⌈': ceiling_val, 'ceil': ceiling_val,
    '⍟': ln, 'ln': ln, 'e': exp, 'exp': exp,
    '⍳': iota, 'iota': iota
}

# Help descriptions
UNARY_HELP = {
    'abs': 'Absolute value',
    'sign': 'Signum: -1, 0, 1',
    'recip': 'Reciprocal: 1/x',
    'floor': 'Floor value',
    'ceil': 'Ceiling value',
    'ln': 'Natural logarithm',
    'exp': 'Exponential (e**x)',
    'iota': 'Iota: 1..n'
}
BINARY_HELP = {
    '+': 'Addition',
    '-': 'Subtraction',
    '*': 'Multiplication',
    '×': 'Multiplication',
    'x': 'Multiplication',
    '/': 'Division',
    '÷': 'Division',
    '^': 'Exponentiation',
    '**': 'Exponentiation',
    '%': 'Modulo',
    'mod': 'Modulo',
    '|': 'Modulo',
    '⌈': 'Maximum',
    '⌊': 'Minimum',
    '==': 'Equality comparison'
}

# Regex for numbers and variable names
NUM_RE = re.compile(r'^-?\d+(?:\.\d+)?$')
VAR_RE = re.compile(r'^[A-Za-z]\w*$')

env = {}  # variable environment

# Helper: parse literal content (space or comma separated)
def parse_literal(s):
    parts = re.split(r'[\s,]+', s.strip())
    arr = []
    for p in parts:
        if NUM_RE.match(p):
            arr.append(int(p) if p.isdigit() else float(p))
        else:
            raise ValueError(f"Invalid literal element: {p}")
    return arr

# Tokenizer handles array literals, CSV, grouping, symbols

def tokenize(expr: str):
    tokens, i, L = [], 0, len(expr)
    while i < L:
        c = expr[i]
        if c.isspace() or c == ',':
            i += 1; continue
        if c == '[':
            # literal or will be replaced by eval_expr earlier
            j = expr.find(']', i)
            if j < 0: raise SyntaxError("Unclosed '['")
            tokens.append(parse_literal(expr[i+1:j]))
            i = j+1; continue
        if c == '(':
            depth, j = 1, i+1
            while j < L and depth > 0:
                depth += (expr[j] == '(') - (expr[j] == ')')
                j += 1
            if depth != 0: raise SyntaxError("Unclosed '('")
            content = expr[i+1:j-1]
            if re.fullmatch(r'[\d\.\-\s,]+', content):
                tokens.append(parse_literal(content)); i = j; continue
            tokens.append('('); i += 1; continue
        if c == ')': tokens.append(')'); i += 1; continue
        m = re.match(r"(\*\*|==|mod|abs|sign|recip|floor|ceil|ln|exp|iota|⍟|⍳|⌊|⌈|\|)", expr[i:])
        if m:
            op = m.group(1)
            tokens.append(op + 'u' if op=='|' and (not tokens or tokens[-1]=='(') else op)
            i += len(op); continue
        if c in '+-×*x÷/%^|': tokens.append(c); i += 1; continue
        m2 = re.match(r"-?\d+(?:\.\d+)?|[A-Za-z]\w*", expr[i:])
        if m2:
            tok = m2.group(0); tokens.append(tok); i += len(tok); continue
        raise SyntaxError(f"Unknown character: {c}")
    return tokens

# Infix to RPN conversion
def shunting_yard(tokens):
    output, stack = [], []
    for tok in tokens:
        if isinstance(tok, list) or NUM_RE.match(str(tok)) or VAR_RE.match(str(tok)):
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
        else:
            raise SyntaxError(f"Invalid token: {tok}")
    while stack:
        output.append(stack.pop())
    return output

# Evaluate RPN stack
def eval_rpn(rpn):
    stack = []
    for tok in rpn:
        if isinstance(tok, list):
            stack.append(tok)
        elif tok in UNARY_OPS:
            stack.append(UNARY_OPS[tok](stack.pop()))
        elif tok in BINARY_OPS:
            b, a = stack.pop(), stack.pop()
            stack.append(BINARY_OPS[tok](a,b))
        elif NUM_RE.match(str(tok)):
            t = str(tok); stack.append(int(t) if t.isdigit() else float(t))
        elif VAR_RE.match(str(tok)):
            if tok in env:
                stack.append(env[tok])
            else:
                raise NameError(f"Undefined variable: {tok}")
        else:
            raise SyntaxError(f"Unknown RPN token: {tok}")
    return stack[0]

# Evaluate expression including monadic prefix, CSV, and indexing via pre-processing

def eval_expr(expr: str):
    # handle indexing patterns first: var[idx]
    def repl_br(m):
        var, sub = m.group(1), m.group(2)
        if var not in env: raise NameError(f"Undefined variable: {var}")
        arr = env[var]
        idx = eval_expr(sub)
        return repr(arr[int(idx)-1])
    expr2 = re.sub(r"([A-Za-z]\w*)\[([^\]]+)\]", repl_br, expr)
    expr2 = re.sub(r"([A-Za-z]\w*)\((\d+)\)", repl_br, expr2)
    expr_strip = expr2.strip()
    # monadic prefix
    for op in sorted(UNARY_OPS.keys(), key=lambda x: -len(x)):
        if expr_strip.startswith(op):
            rest = expr_strip[len(op):].lstrip()
            if not rest: raise ValueError(f"Missing operand for '{op}'")
            return UNARY_OPS[op](eval_expr(rest))
    tokens = tokenize(expr_strip)
    if not tokens: return None
    # CSV literal without operators
    if all(isinstance(tok,list) or NUM_RE.match(str(tok)) for tok in tokens) and len(tokens)>1:
        arr=[]
        for tok in tokens:
            if isinstance(tok,list): arr.extend(tok)
            else: arr.append(int(tok) if tok.isdigit() else float(tok))
        return arr
    return eval_rpn(shunting_yard(tokens))

# HELP display
def print_help(arg=None):
    if arg:
        a = arg.rstrip('u')
        if a in UNARY_OPS:
            print(f"{a}: {UNARY_HELP.get(a,'No description')}")
            return
        if arg in BINARY_OPS:
            print(f"{arg}: {BINARY_HELP.get(arg,'No description')}")
            return
        if arg == '|':
            print(f"|: {UNARY_HELP.get('abs','')} or {BINARY_HELP.get('|','')}")
            return
        print(f"No help for '{arg}'")
    else:
        print("Commands:")
        print("  HELP [op] or ?    Show this message or operator help")
        print("  exit or quit      Quit REPL")
        print("  A = expr          Assign variable A")
        print("Variables can be used: A*B+(C/2), indexing with A[3]")
        print("\nMonadic operators:")
        for op in sorted(UNARY_OPS): print(f"  {op.rstrip('u')} - {UNARY_HELP.get(op.rstrip('u'),'')}")
        print("\nDyadic operators:")
        for sym in sorted(BINARY_OPS): print(f"  {sym} - {BINARY_HELP.get(sym,'')}")

# REPL loop
def repl():
    print("APL360 Python REPL. Type 'HELP [op]' for operator info, 'exit' to quit.")
    while True:
        try:
            line = input("APL360> ").strip()
            if not line: continue
            parts = line.split(maxsplit=1)
            cmd = parts[0].lower()
            if cmd in ('exit','quit'):
                print("Goodbye!")
                break
            if cmd in ('help','?'):
                arg = parts[1] if len(parts)>1 else None
                print_help(arg)
                continue
            m = re.match(r'^(?P<var>[A-Za-z]\w*)\s*=\s*(?P<expr>.+)$', line)
            if m:
                env[m.group('var')] = eval_expr(m.group('expr'))
                print(env[m.group('var')])
                continue
            print(eval_expr(line))
        except Exception as e:
            print("Error:", e)

if __name__=='__main__':
    repl()
