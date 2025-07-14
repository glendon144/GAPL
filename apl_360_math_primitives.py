# apl360_math_primitives.py
"""
Core APL360 math primitives ported to Python.
Supports scalars and nested Python lists as arrays with APL-like broadcasting.
"""

import math
from typing import Union, List, Callable

Number = Union[int, float]
APLArray = Union[Number, List['APLArray']]


def is_scalar(x: APLArray) -> bool:
    """Check if x is a Python scalar (int or float)."""
    return not isinstance(x, list)


def apply_binary(fn: Callable[[Number, Number], Number], a: APLArray, b: APLArray) -> APLArray:
    """
    Apply a binary scalar function elementwise to a and b, with APL-like broadcasting:
    - scalar-scalar → scalar
    - scalar-list   → list
    - list-scalar   → list
    - list-list     → elementwise zip (assumes same shape)
    """
    if is_scalar(a) and is_scalar(b):
        return fn(a, b)
    elif is_scalar(a):
        return [apply_binary(fn, a, bb) for bb in b]
    elif is_scalar(b):
        return [apply_binary(fn, aa, b) for aa in a]
    else:
        return [apply_binary(fn, aa, bb) for aa, bb in zip(a, b)]


# ── Core Binary Primitives ─────────────────────────────────────────────────────

def plus(a: APLArray, b: APLArray) -> APLArray:
    """APL + : addition"""
    return apply_binary(lambda x, y: x + y, a, b)


def minus(a: APLArray, b: APLArray) -> APLArray:
    """APL - : subtraction"""
    return apply_binary(lambda x, y: x - y, a, b)


def times(a: APLArray, b: APLArray) -> APLArray:
    """APL × : multiplication"""
    return apply_binary(lambda x, y: x * y, a, b)


def divide(a: APLArray, b: APLArray) -> APLArray:
    """APL ÷ : division"""
    return apply_binary(lambda x, y: x / y, a, b)


def power(a: APLArray, b: APLArray) -> APLArray:
    """APL * : exponentiation"""
    return apply_binary(lambda x, y: x ** y, a, b)


# ── Core Unary Primitives ──────────────────────────────────────────────────────

def abs_val(a: APLArray) -> APLArray:
    """APL | : absolute value"""
    if is_scalar(a):
        return abs(a)
    return [abs_val(x) for x in a]


def signum(a: APLArray) -> APLArray:
    """Compute signum: 1 if >0, -1 if <0, 0 if zero."""
    if is_scalar(a):
        return 1 if a > 0 else -1 if a < 0 else 0
    return [signum(x) for x in a]


def reciprocal(a: APLArray) -> APLArray:
    """Reciprocal: 1 ÷ a"""
    if is_scalar(a):
        return 1 / a
    return [reciprocal(x) for x in a]


def floor_val(a: APLArray) -> APLArray:
    """APL ⌊ : floor"""
    if is_scalar(a):
        return math.floor(a)
    return [floor_val(x) for x in a]


def ceiling_val(a: APLArray) -> APLArray:
    """APL ⌈ : ceiling"""
    if is_scalar(a):
        return math.ceil(a)
    return [ceiling_val(x) for x in a]


def ln(a: APLArray) -> APLArray:
    """APL ⍟ : natural logarithm"""
    if is_scalar(a):
        return math.log(a)
    return [ln(x) for x in a]


def exp(a: APLArray) -> APLArray:
    """APL *⍟ : exponential (e**a)"""
    if is_scalar(a):
        return math.exp(a)
    return [exp(x) for x in a]


def iota(n: int) -> List[int]:
    """APL ⍳ n : generate 1..n"""
    return list(range(1, n + 1))


# Example usage & simple tests
if __name__ == "__main__":
    # Scalars
    print(plus(2, 3))         # 5
    print(times(2, 3))        # 6
    print(power(2, 3))        # 8
    print(abs_val(-7))        # 7
    print(signum(-2), signum(0), signum(5))  # -1 0 1

    # Arrays
    a = [1, 2, 3]
    b = [4, 5, 6]
    print(plus(a, b))         # [5, 7, 9]
    print(divide(a, 2))       # [0.5, 1.0, 1.5]
    print(iota(5))            # [1, 2, 3, 4, 5]
