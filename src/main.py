from reverse_polish_calculator.rpnlanginterpreter import RpnlangInterpreter as Rpn
from argparse import ArgumentParser

print(Rpn().evaluate('2 3 * 1 +'))