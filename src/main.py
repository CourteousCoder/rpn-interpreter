from reverse_polish_calculator.rpnlanginterpreter import RpnlangInterpreter as Rpn
from argparse import ArgumentParser
from sys import stderr


def get_args():
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dec', help='output/display values as decimal numbers (default)', default=True,
                       action='store_true')
    group.add_argument('-o', '--oct', help='output/display values as octal numbers', action='store_true')
    group.add_argument('-x', '--hex', help='output/display values as octal numbers', action='store_true')
    group.add_argument('-b', '--bin', help='output/display values as octal numbers', action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-H', '--command-help', action='store_true', help="show the help page for commands")
    group.add_argument('-f', '--file', help='run the specified file as a script', type=str)
    group.add_argument('-e', '--expression', help='evaluate the specified expression string', type=str)
    group.add_argument('-v', '--verbosity', help='indicate how many characters to display for stack abbreviations'
                                                 'this only has an effect in interactive mode', type=int, default=0)
    return parser.parse_args()


def run_interactive(base, verbosity):
    rpn = Rpn(base, True, verbosity)
    while rpn.interactive:
        try:
            rpn.evaluate(input(rpn.interactive_prompt))
        except BaseException as error:
            print(str(error), file=stderr)
    return ''


def run(args):
    base = get_base(args)
    if args.expression:
        return Rpn(base, False, args.verbosity).evaluate(args.expression)
    elif args.file:
        with open(args.file, 'r') as f:
            return Rpn(base, False, args.verbosity).evaluate(f.read())
    else:
        return run_interactive(base, args.verbosity)


def get_base(args):
    base = 10
    if args.bin:
        base = 2
    elif args.oct:
        base = 8
    elif args.hex:
        base = 16
    return base


def show_help():
    Rpn(interactive=True).help()


def main():
    args = get_args()
    if args.command_help:
        show_help()
        return
    result = run(args)
    # print(result)


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        print(str(error), file=stderr)
