from math import sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, asinh, acosh, atanh, ceil, floor, exp, log, pow, \
    sqrt, factorial, e, pi, tau
from random import random
from socket import htonl, htons, ntohl, ntohs


class Operator:
    def __init__(self, arity, operation, description=''):
        self._arity = arity
        self._operation = operation
        self._description = description

    @property
    def description(self):
        return self._description

    @property
    def arity(self):
        return self._arity

    def operate(self, *args):
        # Truncate extraneous arguments
        args = args[:self.arity]
        result = self._operation(*args)
        return result

    def __str__(self):
        return self.description


# This are operations which can be represented by pure functions.
pure_operations = {
    'Arithmetic': {
        '+': Operator(2, lambda a, b: a + b, 'Addition'),
        '-': Operator(2, lambda a, b: a - b, 'Subtraction'),
        '*': Operator(2, lambda a, b: a * b, 'Multiplication'),
        '/': Operator(2, lambda a, b: a / b, 'Division'),
        '%': Operator(2, lambda a, b: a % b, 'Modulo'),
        '++': Operator(1, lambda a: a + 1, 'Increment'),
        '--': Operator(1, lambda a: a - 1, 'Decrement'),
    },
    'Bitwise': {
        '&': Operator(2, lambda a, b: a & b, 'Bitwise AND'),
        '|': Operator(2, lambda a, b: a | b, 'Bitwise OR'),
        '^': Operator(2, lambda a, b: a ^ b, 'Bitwise XOR'),
        '<<': Operator(2, lambda a, b: a << b, 'Bitwise shift left'),
        '>>': Operator(2, lambda a, b: a >> b, 'Bitwise shift right'),
        '~': Operator(1, lambda a: ~a, 'Bitwise NOT'),
    },
    'Boolean': {
        '&&': Operator(2, lambda a, b: int(bool(a) and bool(b)), 'Boolean AND'),
        '||': Operator(2, lambda a, b: int(bool(a) or bool(b)), 'Boolean OR'),
        '^^': Operator(2, lambda a, b: int(bool(a) != bool(b)), 'Boolean XOR'),
        '!': Operator(1, lambda a: int(not bool(a)), 'Boolean NOT'),
    },
    'Comparison': {
        '!=': Operator(2, lambda a, b: int(a != b), 'Not equal to'),
        '<': Operator(2, lambda a, b: int(a < b), 'Less than'),
        '>': Operator(2, lambda a, b: int(a > b), 'Greater than'),
        '<=': Operator(2, lambda a, b: int(a <= b), 'Less than or equal to'),
        '>=': Operator(2, lambda a, b: int(a >= b), 'Greater than or equal to'),
        '==': Operator(2, lambda a, b: int(a == b), 'Equal to'),
    },
    'Trigonometric': {
        'sin': Operator(1, sin, 'Sine'),
        'cos': Operator(1, cos, 'Cosine'),
        'tan': Operator(1, tan, 'Tangent'),
        'asin': Operator(1, asin, 'Sine inverse'),
        'acos': Operator(1, acos, 'Cosine inverse'),
        'atan': Operator(1, atan, 'Tangent inverse'),
    },
    'Hyperbolic': {
        'sinh': Operator(1, sinh, 'Hyperbolic sine'),
        'cosh': Operator(1, cosh, 'Hyperbolic cosine'),
        'tanh': Operator(1, tanh, 'Hyperbolic tangent'),
        'asinh': Operator(1, asinh, 'Hyperbolic sine inverse'),
        'acosh': Operator(1, acosh, 'Hyperbolic cosine inverse'),
        'atanh': Operator(1, atanh, 'Hyperbolic tangent inverse'),
    },
    'Numeric Utilities': {
        'max': Operator(2, max, 'Maximum'),
        'min': Operator(2, min, 'Minimum'),
        'ceil': Operator(1, ceil, 'Ceiling'),
        'floor': Operator(1, floor, 'Floor'),
        'round': Operator(1, round, 'Round'),
        'ip': Operator(1, lambda a: int(a), 'Integer part'),
        'fp': Operator(1, lambda a: a - int(a), 'Fractional part'),
        'sign': Operator(1, lambda a: -1 if a < 0 else 1 if a > 0 else 0, 'Push -1 for negative, 1 for positive, or 0'),
        'abs': Operator(1, lambda a: abs(a), 'Absolute value'),
    },
    'Mathematical Functions': {
        'exp': Operator(1, exp, 'Natural exponentiation function'),
        'fact': Operator(1, factorial, 'Factorial'),
        'sqrt': Operator(1, sqrt, 'Square root'),
        'ln': Operator(1, log, 'Natural Logarithm'),
        'log': Operator(2, log, "Logarithm of x with base b, i.e. 'x b log'"),
        'pow': Operator(2, pow, "Raise x to the power of y, i.e. 'x y pow'"),
    },
    'Constants': {
        'pi': Operator(0, lambda: pi, "The ratio of a circle's circumference to its diameter, π"),
        'tau': Operator(0, lambda: tau, "The ratio of a circle's circumference to its radius, τ = 2π"),
        'e': Operator(0, lambda: e, "Euler's constant"),
        'rand': Operator(0, random, 'A random float in the range [0,1)'),
        'true': Operator(0, lambda: True, 'Boolean TRUE'),
        'false': Operator(0, lambda: False, 'Boolean FALSE'),
        'inf': Operator(0, lambda: float('inf'), 'Positive Infinity'),
        '-inf': Operator(0, lambda: float('-inf'), 'Negative Infinity'),
    },
    'Networking': {
        'hnl': Operator(1, htonl, 'Host to network long'),
        'hns': Operator(1, htons, 'Host to network short'),
        'nhl': Operator(1, ntohl, 'Network to host long'),
        'nhs': Operator(1, ntohs, 'Network to host short'),
    },
}
