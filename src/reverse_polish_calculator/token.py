from enum import Enum, auto
from re import match
from .helpers import parse_float


class TokenType(Enum):
    REFERENCE = auto()
    SYMBOL = auto()
    BLOCK = auto()
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
    def parse_value_token(cls, token):
        if match(r'^&?\$[a-zA-Z0-9_]+$', token):
            return cls(token, TokenType.REFERENCE if cls._is_reference(token) else TokenType.SYMBOL)
        elif '.' in token:
            return cls._parse_float_token(token)
        elif match(r'^-?(0|[1-9][0-9]*)$', token):
            return cls(int(token), TokenType.DEC_INT)
        elif match(r'^-?0o[0-7]+$', token):
            return cls(int(token, 8), TokenType.OCT_INT)
        elif match(r'^-?0b[01]+$', token):
            return cls(int(token, 2), TokenType.BIN_INT)
        elif match(r'^-?0x[0-9a-fA-F]+$', token):
            return cls(int(token, 16), TokenType.HEX_INT)
        else:
            raise SyntaxError(f"Syntax Error: Token '{token}' is not a valid symbol name, value, or operation.")

    @staticmethod
    def _is_reference(token):
        return str(token).startswith('&')

    @classmethod
    def _parse_float_token(cls, token):
        if match(r'^-?[0-9]+\.[0-9]+$', token):
            return cls(float(token), TokenType.DEC_FLOAT)
        elif match(r'^-?0o[0-7]+\.[0-7]+$', token):
            return cls(parse_float(token.replace('0o', ''), 8), TokenType.OCT_FLOAT)
        elif match(r'^-?0b[01]+\.[0-1]+$', token):
            return cls(parse_float(token.replace('0b', ''), 2), TokenType.BIN_FLOAT)
        elif match(r'^-?0x[0-9a-fA-F]+\.[0-9a-fA-F]+$', token):
            return cls(float.fromhex(token), TokenType.HEX_FLOAT)
        else:
            raise SyntaxError(f"Syntax Error: Token '{token}' is not a valid floating point value.")

    def __iter__(self):
        yield self.value
        yield self.token_type

    def __str__(self):
        return str(self.value)
