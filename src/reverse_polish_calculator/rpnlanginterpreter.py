import re

from tabulate import tabulate

from .bracketparser import BracketParser
from .helpers import identity, float_to_bin, float_to_oct, float_to_hex, clamp
from .operator import Operator, pure_operations
from .token import Token, TokenType


class RpnlangInterpreter:
    def __init__(self, display_mode_number_base=10, verbosity=0, expression=None):
        self._verbosity = verbosity
        self._display_mode_number_base = 0
        self.set_display_mode_number_base(display_mode_number_base)
        self._clear_stack()
        self._clear_symbols()
        self._tokens = []
        self._bracket_parser = BracketParser('{', '}')
        self._operations = {}
        self._include_operation_groups(pure_operations)
        self._include_operation_groups(self._get_scripting_operations())
        self._include_operation_groups(self._get_interactive_operations())
        self._running = True
        if expression:
            self.evaluate(expression)

    @property
    def running(self):
        return self._running

    def set_display_mode_number_base(self, base):
        options = (2, 8, 10, 16)
        if base not in options:
            options = ', '.join(map(str, options))
            raise ValueError(f"Value Error: Unsupported number base: '{base}'. Please use any one of: {options}.")
        self._display_mode_number_base = base

    @property
    def result(self):
        return self._format_output(self._stack[-1]) if self._stack else ''

    @property
    def interactive_prompt(self) -> str:
        return ' '.join([self._format_output(item) for item in self._stack]) + '>'

    def evaluate(self, expression: str):
        """
        Evaluates the given expression_string thus:

        Parse the expresion into a stack of tokens.
        Pop off items from the token stack, expanding references to defined macros.
        Values are pushed to the memory stack.
        Operators pop values from the memory stack and push their return values (if any)

        :param expression:
        :return: self
        """
        self._tokenize(expression)
        while self._tokens:
            token = self._tokens.pop()
            contents, token_type = tuple(token)
            if token_type == TokenType.OPERATOR:
                calculated_value = self._compute(contents)
                if calculated_value is not None:
                    self._stack.append(calculated_value)
            elif token_type == TokenType.SYMBOL:
                self._expand_symbol(contents)
            else:
                self._stack.append(contents)

        return self

    def _compute(self, operation: Operator):
        if len(self._stack) < operation.arity:
            raise TypeError(f"Stack Error: Not enough arguments to compute: '{operation.name}'.")
        args = self._pop_many(operation.arity)
        return operation.operate(*args)

    def _expand_symbol(self, symbol):
        if symbol not in self._symbol_table:
            self._assign('{ }', symbol)
        expanded_symbol = str(self._symbol_table[symbol])
        if self._is_block(expanded_symbol):
            expanded_symbol = self._unblock(expanded_symbol)
        self._tokenize(expanded_symbol)

    def _tokenize(self, expression: str):
        expression = self._preprocess_comments(expression)
        bracket_parser = self._bracket_parser

        # Allow space between blocks to be optional.
        expression = expression \
            .replace(bracket_parser.opening, bracket_parser.opening + ' ') \
            .replace(bracket_parser.closing, ' ' + bracket_parser.closing)

        tokens = [self._parse_token(token) for token in re.findall(r'\S+', expression)]
        self._tokens.extend([token for token in reversed(tokens) if token is not None])

    def _parse_token(self, token: str) -> Token:
        supported_operators = self._operations
        bracket_parser = self._bracket_parser
        if token in (bracket_parser.opening, bracket_parser.closing) or not bracket_parser.valid:
            return self._parse_block_token(token)
        elif token in supported_operators:
            return Token(supported_operators[token], TokenType.OPERATOR)
        else:
            return Token.parse_value_token(token)

    def _parse_block_token(self, token: str) -> Token:
        if self._bracket_parser.parse(token).valid:
            token = Token(self._bracket_parser.contents, TokenType.BLOCK)
            self._bracket_parser.reset()
            return token

    @staticmethod
    def _preprocess_comments(expression_string):
        """
        Remove comments from expression_string.
        :return: This returns a new string and does not modify the original.
        """
        return re.sub(r'/\*.*?\*/', '', expression_string, flags=re.DOTALL)

    def _push(self, *items):
        self._stack.extend(items)

    def _pop_many(self, items: int = 1) -> list:
        """
        Pop `items` number of items off the stack
        :param items:
        :return: The removed items as a list.
        """
        if items == 0:
            return []
        popped_items = self._stack[-items:]  # the last `items` number of items
        self._stack = self._stack[:-items]  # everything but the last `items` number of items.
        return popped_items

    def _include_operation_groups(self, operation_groups):
        operations = set().union(*operation_groups.values())
        operations = {op.name: op for op in operations}
        self._operations.update(operations)

    def _format_block(self, block: str) -> str:
        if self._verbosity <= 0:
            return '{...}'
        # Get the first self._verbosity characters of the block.
        abbreviation = self._unblock(block)[:int(clamp(self._verbosity, 0, len(block)))]
        return '{' + abbreviation + '...}'

    def _format_output(self, stack_item):
        if stack_item in (float('inf'), float('-inf')):
            return str(stack_item)
        format_int = identity
        format_float = identity
        if self._display_mode_number_base == 2:
            format_int = bin
            format_float = float_to_bin
        elif self._display_mode_number_base == 8:
            format_int = oct
            format_float = float_to_oct
        elif self._display_mode_number_base == 10:
            format_int = str
            format_float = str
        elif self._display_mode_number_base == 16:
            format_int = hex
            format_float = float_to_hex

        data_type = type(stack_item)
        # Truncate '.0' if present.
        stack_item = int(stack_item) if data_type == float and int(stack_item) * 1.0 == stack_item else stack_item
        if data_type == int:
            return format_int(stack_item)
        elif data_type == float:
            return format_float(stack_item)
        elif self._is_block(stack_item):
            return self._format_block(stack_item)
        else:
            return str(stack_item)

    def _clear_stack(self):
        self._stack = []

    def _clear_symbols(self):
        self._symbol_table = {}

    def _clear_all_memory(self):
        self._clear_stack()
        self._clear_symbols()

    def _depth(self):
        return len(self._stack)

    def _peek(self, n=1):
        if len(self._stack) < n:
            raise ValueError('Stack Error: Not enough values')
        return self._stack[-int(n)]

    def _duplicate(self, n=1):
        """
        Duplicates the top n items on the stack, in order
        :param n:
        :return:
        """
        if not self._stack:
            raise ValueError('stack is empty')
        items = self._stack[-1 - n:]
        self._push(*items)

    def _drop(self, n=1):
        self._pop_many(n)

    def _swap(self, a, b):
        self._push(b, a)

    def _roll_up(self, n):
        rotations = n % len(self._stack)
        self._stack = self._stack[-rotations:] + self._stack[:-rotations]

    def _roll_down(self, n):
        rotations = n % len(self._stack)
        self._stack = self._stack[rotations:] + self._stack[:rotations]

    @staticmethod
    def _unblock(value: str) -> str:
        """
        Return the inner expression of a block
        :param value:
        :return:
        """
        value = str(value).strip()
        return ' '.join(value[1:-1].split())

    def _is_block(self, value):
        value = str(value)
        return value.startswith(self._bracket_parser.opening) and value.endswith(self._bracket_parser.closing)

    def _assign(self, value, reference):
        self._symbol_table[reference[1:]] = value

    def _symbols(self):
        print(tabulate(sorted([[k, v] for k, v in self._symbol_table.items()], key=lambda row: row[0]),
                       headers=('Symbol', 'Value')))

    def _puts(self):
        def to_unicode(number):
            if type(number) != int or not (0 <= number <= 0x10ffff):
                raise ValueError("Value Error: Tried to print non-unicode value '{number}' from stack")
            return chr(number)

        chars = [to_unicode(val) for val in self._stack]
        print(''.join(chars))

    def help(self):
        command_reference = {}
        command_reference.update(pure_operations)
        command_reference.update(self._get_scripting_operations())
        command_reference.update(self._get_interactive_operations())
        for category, commands in command_reference.items():
            command_reference[category] = tabulate(sorted([
                [command.name, command.arity, command.description]
                for command in commands
            ], key=lambda row: row[0]), headers=('Operator', 'Arguments', 'Description'))
        command_reference = '\n\n'.join([
            f'{category}:\n{table}'
            for category, table in command_reference.items()
        ])
        print(command_reference)

    def _if_else(self, condition, true_block=None, false_block=None):
        expression = ''
        if bool(condition) and true_block is not None:
            expression = self._unblock(true_block)
        elif false_block is not None:
            expression = self._unblock(false_block)
        self._tokenize(expression)

    def _repeat(self, n, block):
        expression = ' '.join([self._unblock(block)] * n)
        self._tokenize(expression)

    def _exit(self):
        self._running = False

    def _delete(self, reference):
        symbol = reference[1:]
        if symbol in self._symbol_table:
            self._symbol_table.pop(symbol)

    def _get_interactive_operations(self):
        return {
            'Interactive Display Commands': {
                Operator('dec', 0, lambda: self.set_display_mode_number_base(10), 'Display decimal values'),
                Operator('bin', 0, lambda: self.set_display_mode_number_base(2), 'Display binary values'),
                Operator('oct', 0, lambda: self.set_display_mode_number_base(8), 'Display octal values'),
                Operator('hex', 0, lambda: self.set_display_mode_number_base(16), 'Display hexadecimal values'),
                Operator('symbols', 0, self._symbols, 'Display all defined symbols'),
                Operator('help', 0, self.help, 'Show this help text'),
                Operator('exit', 0, self._exit, 'Exit interactive mode')
            },
        }

    def _get_scripting_operations(self):
        return {
            'Memory Manipulation': {
                Operator('del', 1, self._delete, "Delete a symbol from memory by name, e.g. '&$deleteMe del'"),
                Operator('=', 2, self._assign, 'Assignment, assigns a global symbol name to a block or value, '
                                               'symbol name must be passed as a reference, '
                                               "e.g. '{ 1024 * } &$kb ='"),
                Operator('clr', 0, self._clear_stack, 'Clear the stack'),
                Operator('cls', 0, self._clear_symbols, 'Clear all defined symbols'),
                Operator('cla', 0, self._clear_all_memory, 'Clear all defined symbols and the stack'),
                Operator('depth', 0, self._depth, 'Push the current depth of the stack to the stack'),
                Operator('peek', 1, self._peek, 'Duplicate the n-th item from the top of the stack'),
                Operator('dup', 0, self._peek, 'Duplicate the top item from the stack'),
                Operator('dupn', 1, self._duplicate, 'Duplicate the top n items on the stack, in order'),
                Operator('drop', 0, self._drop, 'Drop the top item from the stack'),
                Operator('dropn', 1, self._drop, 'Drop the top n items from the stack'),
                Operator('swap', 2, self._swap, 'Swap the top 2 items on the top of the stack'),
                Operator('roll', 1, self._roll_up, 'Roll the stack upwards by n'),
                Operator('rolld', 1, self._roll_down, 'Roll the stack downwards by n'),
                Operator('reverse', 0, self._stack.reverse, 'Reverse the stack'),
                Operator('puts', 0, self._puts,
                         'Treat the stack as a sequence of unicode values, and print it as a string.')
            },
            'Control Flow': {
                Operator('ifelse', 3, self._if_else,
                         'Execute the contents of true_block if condition is true, '
                         'otherwise execute the contents of false_block '
                         "i.e. '<condition> <true_block> <false_block> ifelse'"),
                Operator('if', 2, lambda condition, value: self._if_else(condition, true_block=value),
                         'Execute the contents of block if condition is true, otherwise, do nothing,'
                         "i.e. '<condition> <block> if'"),
                Operator('unless', 2, lambda condition, value: self._if_else(condition, false_block=value),
                         'Execute the contents of block if condition is false, otherwise, do nothing,'
                         "i.e. '<condition> <block> unless'"),
                Operator('repeat', 2, self._repeat, 'Execute the contents of block exactly n number of times, '
                                                    'where int n > 0 '
                                                    "i.e. '<n> <block> repeat'")
            },
            # Language structures are defined here only for documentation purposes since
            # they are technically not operations.
            'Language Structures': {
                Operator('/* [comment] */', None, None,
                         "Multiline comment, ignore everything between"
                         " the first '/*' and the first '*/'"),
                Operator('{ <expression> }', None, None,
                         "Block, encapsulates a sequence of operations, values, and/or other blocks, "
                         "e.g. '{ dup * }'"),
                Operator('$<symbol name>', None, None, 'Symbol, get the value of an existing symbol, '
                                                       'If the symbol has not been set'
                                                       'then it sets it to an empty block,'),
                Operator('&$<symbol name>', None, None,
                         'Reference, refers to a symbol name, must match /[a-zA-Z0-9_]+/'),
            },
        }
