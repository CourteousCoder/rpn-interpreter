from reverse_polish_calculator.calculator import Calculator
calc = Calculator()
assert calc.evaluate('1 2 +') == '3'
assert calc.evaluate('1 +') == '4'
assert calc.evaluate('2 / 3 pow') == '8'
assert calc.evaluate('') == '8'

calc = Calculator()
assert calc.evaluate('-0b1010011') == '-83'
assert calc.evaluate('-inf -0xFFFFFFFFFFFFFFFF min') == '-inf'

calc = Calculator(8)
assert calc.evaluate('-0xA') == '-0o12'
calc = Calculator(scripting=True)
script = """
/* Hello darkness my old friend
    1 2 *
    I've come to talk with you again
*/
2 3 *
"""
assert calc.evaluate(script) == '6'

calc = Calculator(scripting=True)
script = """
/* Hello darkness my old friend
    1 2 *
    I've come to talk with you again
*/
&$three 3 =
&$four { $three 1 + } =
&$kib
{ 1024 /*comment*/ * } =

$four $kib 4 swap / $kib
/**/
"""
result = calc.evaluate(script)
calc.evaluate('2 3 depth -- repeat +')
print(calc.format_stack())
