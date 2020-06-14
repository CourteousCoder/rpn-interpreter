from ast import literal_eval
from enum import Enum, auto
from re import match, findall


class TokenType(Enum):
    SYMBOL = auto()
    OPERATOR = auto()
    DEC_INT = auto()
    BIN_INT = auto()
    OCT_INT = auto()
    HEX_INT = auto()
    DEC_FLOAT = auto()
    BIN_FLOAT = auto()
    OCT_FLOAT = auto()
    HEX_FLOAT = auto()


class Token:
    def __init__(self, value, token_type):
        self._value = value
        self._token_type = token_type

    @property
    def value(self):
        return self._value

    @property
    def token_type(self):
        return self._token_type

    @classmethod
    def parse_expression(cls, expression_string, supported_operators):
        return [cls.parse_token(token, supported_operators) for token in
                findall(r'\S+', expression_string)]

    @classmethod
    def parse_token(cls, token, supported_operators):
        if token in supported_operators:
            return cls(supported_operators[token], TokenType.OPERATOR)
        elif '$' in token and match(r'^\$[a-zA-Z0-9_]+$', token):
            return cls(token, TokenType.SYMBOL)
        elif '.' in token:
            return cls.parse_float_token(token)
        elif match(r'^-?(0|[1-9][0-9]*)$', token):
            return cls(int(token), TokenType.DEC_INT)
        elif match(r'^-?0o[0-7]+$', token):
            return cls(int(token, 8), TokenType.OCT_INT)
        elif match(r'^-?0b[01]+$', token):
            return cls(int(token, 2), TokenType.BIN_INT)
        elif match(r'^-?0x[0-9a-fA-F]+$', token):
            return cls(int(token, 16), TokenType.HEX_INT)
        else:
            raise SyntaxError(f'Token {token} is not a valid symbol name, value, or function.')

    @classmethod
    def parse_float_token(cls, token):
        if match(r'^-?[1-9][0-9]*\.[0-9]+$', token):
            return cls(float(token), TokenType.DEC_FLOAT)
        elif match(r'^-?0o[0-7]+\.[0-7]+$', token):
            return cls(literal_eval(token), TokenType.OCT_FLOAT)
        elif match(r'^-?0b[01]+\.[0-1]+$', token):
            return cls(literal_eval(token), TokenType.BIN_FLOAT)
        elif match(r'^-?0x[0-9a-fA-F]+\.[0-9a-fA-F]+$', token):
            return cls(float.fromhex(token), TokenType.HEX_FLOAT)
        else:
            raise SyntaxError(f'Token {token} is not a valid floating point value.')

    def __iter__(self):
        yield self.value
        yield self.token_type

    def __str__(self):
        return str(tuple(self))