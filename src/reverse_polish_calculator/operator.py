from math import sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, asinh, acosh, atanh, ceil, floor, exp, log, pow, \
    sqrt, factorial, e, pi, tau
from random import random
from socket import htonl, htons, ntohl, ntohs


class Operator:
    def __init__(self, name, arity, operation, description=''):
        self._name = name
        self._arity = arity
        self._operation = operation
        self._description = description

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def arity(self):
        return self._arity

    def operate(self, *args):
        result = self._operation(*args)
        return result

    def __str__(self):
        return self.name


# This are operations which can be represented by pure functions.
pure_operations = {
    'Arithmetic': {
        Operator('+', 2, lambda a, b: a + b, 'Addition'),
        Operator('-', 2, lambda a, b: a - b, 'Subtraction'),
        Operator('*', 2, lambda a, b: a * b, 'Multiplication'),
        Operator('/', 2, lambda a, b: a / b, 'Division'),
        Operator('%', 2, lambda a, b: a % b, 'Modulo'),
        Operator('++', 1, lambda a: a + 1, 'Increment'),
        Operator('--', 1, lambda a: a - 1, 'Decrement'),
    },
    'Bitwise': {
        Operator('&', 2, lambda a, b: a & b, 'Bitwise AND'),
        Operator('|', 2, lambda a, b: a | b, 'Bitwise OR'),
        Operator('^', 2, lambda a, b: a ^ b, 'Bitwise XOR'),
        Operator('<<', 2, lambda a, b: a << b, 'Bitwise shift left'),
        Operator('>>', 2, lambda a, b: a >> b, 'Bitwise shift right'),
        Operator('~', 1, lambda a: ~a, 'Bitwise NOT'),
    },
    'Boolean': {
        Operator('&&', 2, lambda a, b: int(bool(a) and bool(b)), 'Boolean AND'),
        Operator('||', 2, lambda a, b: int(bool(a) or bool(b)), 'Boolean OR'),
        Operator('^^', 2, lambda a, b: int(bool(a) != bool(b)), 'Boolean XOR'),
        Operator('!', 1, lambda a: int(not bool(a)), 'Boolean NOT'),
    },
    'Comparison': {
        Operator('!=', 2, lambda a, b: int(a != b), 'Not equal to'),
        Operator('<', 2, lambda a, b: int(a < b), 'Less than'),
        Operator('>', 2, lambda a, b: int(a > b), 'Greater than'),
        Operator('<=', 2, lambda a, b: int(a <= b), 'Less than or equal to'),
        Operator('>=', 2, lambda a, b: int(a >= b), 'Greater than or equal to'),
        Operator('==', 2, lambda a, b: int(a == b), 'Equal to'),
    },
    'Trigonometric': {
        Operator('sin', 1, sin, 'Sine'),
        Operator('cos', 1, cos, 'Cosine'),
        Operator('tan', 1, tan, 'Tangent'),
        Operator('asin', 1, asin, 'Sine inverse'),
        Operator('acos', 1, acos, 'Cosine inverse'),
        Operator('atan', 1, atan, 'Tangent inverse'),
    },
    'Hyperbolic': {
        Operator('sinh', 1, sinh, 'Hyperbolic sine'),
        Operator('cosh', 1, cosh, 'Hyperbolic cosine'),
        Operator('tanh', 1, tanh, 'Hyperbolic tangent'),
        Operator('asinh', 1, asinh, 'Hyperbolic sine inverse'),
        Operator('acosh', 1, acosh, 'Hyperbolic cosine inverse'),
        Operator('atanh', 1, atanh, 'Hyperbolic tangent inverse'),
    },
    'Numeric Utilities': {
        Operator('max', 2, max, 'Maximum'),
        Operator('min', 2, min, 'Minimum'),
        Operator('ceil', 1, ceil, 'Ceiling'),
        Operator('floor', 1, floor, 'Floor'),
        Operator('round', 1, round, 'Round'),
        Operator('ip', 1, lambda a: int(a), 'Integer part'),
        Operator('fp', 1, lambda a: a - int(a), 'Fractional part'),
        Operator('sign', 1, lambda a: -1 if a < 0 else 1 if a > 0 else 0, 'Push -1 for negative, 1 for positive, or 0'),
        Operator('abs', 1, lambda a: abs(a), 'Absolute value'),
    },
    'Mathematical Functions': {
        Operator('exp', 1, exp, 'Natural exponentiation function'),
        Operator('fact', 1, factorial, 'Factorial'),
        Operator('sqrt', 1, sqrt, 'Square root'),
        Operator('ln', 1, log, 'Natural Logarithm'),
        Operator('log', 2, log, "Logarithm of x with base b, i.e. 'x b log'"),
        Operator('pow', 2, pow, "Raise x to the power of y, i.e. 'x y pow'"),
    },
    'Constants': {
        Operator('pi', 0, lambda: pi, "The ratio of a circle's circumference to its diameter, π"),
        Operator('tau', 0, lambda: tau, "The ratio of a circle's circumference to its radius, τ = 2π"),
        Operator('e', 0, lambda: e, "Euler's constant"),
        Operator('rand', 0, random, 'A random float in the range [0,1)'),
        Operator('true', 0, lambda: True, 'Boolean TRUE'),
        Operator('false', 0, lambda: False, 'Boolean FALSE'),
        Operator('inf', 0, lambda: float('inf'), 'Positive Infinity'),
        Operator('-inf', 0, lambda: float('-inf'), 'Negative Infinity'),
    },
    'Networking': {
        Operator('hnl', 1, htonl, 'Host to network long'),
        Operator('hns', 1, htons, 'Host to network short'),
        Operator('nhl', 1, ntohl, 'Network to host long'),
        Operator('nhs', 1, ntohs, 'Network to host short'),
    },
}
