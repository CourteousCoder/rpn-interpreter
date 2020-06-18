from argparse import ArgumentParser, FileType
from sys import stderr, stdout

from reverse_polish_calculator.rpnlanginterpreter import RpnlangInterpreter as Rpn

from signal import signal, SIGINT
from sys import exit


def sigint_handler(signal_received=None, frame=None):
    # Handle any cleanup here
    print("SIGINT or CTRL-C detected. Attempting to exit gracefully... You can also type 'exit' to quit.")
    exit(0)


def get_args():
    parser = ArgumentParser(prog='RPN Interpreter',
                            description='Interprets a program written in the stack-based '
                                        'RPN language, given as either: '
                                        'a file, an expression, or via the interactive shell '
                                        'and outputs the final calculation')
    parser.add_argument('expression',
                        help='the expression to evaluate. If -f or -i is used, this expression will be evaluated first.'
                             ' A common use-case for this is to pass arguments to a program given by -f.',
                        nargs='*',
                        type=str)
    parser.add_argument('-H', '--command-help', action='store_true', help="show the help page for commands")
    parser.add_argument('-v', '--verbosity', help='indicate how many characters to display for stack abbreviations'
                                                  'this only has an effect in interactive mode', type=int, default=0)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dec', help='output/display values as decimal numbers (default)', default=True,
                       action='store_true')
    group.add_argument('-o', '--oct', help='output/display values as octal numbers', action='store_true')
    group.add_argument('-x', '--hex', help='output/display values as octal numbers', action='store_true')
    group.add_argument('-b', '--bin', help='output/display values as octal numbers', action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f', '--file',
                       help="run the specified file as a script, or read from stdin if a dash '-' is given",
                       type=FileType('r'))
    group.add_argument('-i', '--interactive', help='enter the interactive shell after parsing the expression',
                       action='store_true')
    args = parser.parse_args()
    return args


def run_interactive(rpn):
    while rpn.running:
        try:
            expression = input(rpn.interactive_prompt)
            if expression == chr(3):
                sigint_handler()
            rpn.evaluate(expression)
        except Exception as e:
            print(str(e), file=stderr)
    return rpn


def run(args):
    base = get_base(args)
    rpn = Rpn(base, args.verbosity, ' '.join(args.expression))
    if args.file:
        f = args.file.read()
        rpn.evaluate(f)
    elif args.interactive:
        run_interactive(rpn)
    return rpn


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
    Rpn().help()


def main():
    signal(SIGINT, sigint_handler)
    args = get_args()
    if args.command_help:
        show_help()
        return
    result = run(args).result
    print(result, file=stdout)


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        stderr.writelines([str(error)])
        exit(1)
