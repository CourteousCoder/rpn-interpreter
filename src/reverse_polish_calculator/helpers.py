def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


def parse_float(number: str, base: int) -> float:
    sign = ''
    if number.startswith('-'):
        sign = '-'
        number = number[1:].strip('0')
    integer_part, fraction_part = number.split('.')
    scale = -int(len(fraction_part))
    return int(sign + integer_part + fraction_part, base) * base ** scale


def float_to_base(number: float, base: int, convert_int, precision=25) -> str:
    integer_part, fraction_part = str(abs(float(number))).split('.')
    sign = ''
    if number < 0:
        sign = '-'
    integer_part = sign + convert_int(int(integer_part))
    decimal_fraction = float('0.' + fraction_part)
    fraction_part = []
    while decimal_fraction > 0 and len(fraction_part) < precision:
        decimal_fraction *= base
        digit = convert_int(int(decimal_fraction))
        decimal_fraction -= int(decimal_fraction)
        # remove 0x, 0b, or 0o
        digit = digit[2:]
        fraction_part.append(digit)
    fraction_part = ''.join(fraction_part).rstrip('0')
    if not fraction_part:
        return integer_part
    return f'{integer_part}.{fraction_part}'


def float_to_hex(number: float) -> str:
    return float_to_base(number, 16, hex)


def float_to_bin(number: float) -> str:
    return float_to_base(number, 2, bin)


def float_to_oct(number: float) -> str:
    return float_to_base(number, 8, oct)


def identity(x):
    return x
